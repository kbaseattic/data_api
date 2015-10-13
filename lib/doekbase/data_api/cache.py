"""
Add simple, flexible caching layer.

Uses `dogpile caching http://dogpilecache.readthedocs.org/en/latest/index.html`_.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/26/15'

## Imports

# System
import hashlib
import os
import uuid
# Third-party
from dogpile.cache import make_region
from dogpile.cache.api import NO_VALUE
# Local
from doekbase.data_api.util import PerfCollector, get_logger

_log = get_logger(__name__)

## Functions and Classes

class Cache(object):
    def __init__(self):
        self.region = None

    def __getattr__(self, item):
        return getattr(self.region, item)

class RedisCache(Cache):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__()
        self.region = get_redis_region(**kwargs)

class DBMCache(Cache):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__()
        self.region = get_dbm_region(**kwargs)

class NullCache(Cache):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__()
        self.region = get_null_region()

def get_redis_region(redis_host='localhost', redis_port=6379):
    """Get a new redis cache 'region' object.

    Args:
        redis_host (str): Hostname or IP for Redis server
        redis_port (int): Redis server listening port
    Returns:
        An object, of type CacheRegion
    """
    region = make_region().configure(
        'dogpile.cache.redis',
        arguments={
            'host': redis_host,
            'port': redis_port,
            'db': 0,
            'redis_expiration_time': 60 * 60 * 2,  # 2 hours
            'distributed_lock': True
        }
    )
    return region

def get_dbm_region(path='/tmp', name=''):
    """Get a new anydbm (DBM) cache 'region' object.

    Args:
        path (str): Path to directory with cache file
        name (str): Name of cache file. if empty a random name
                    will be generated.
    Returns:
        An object, of type CacheRegion
    """
    if not name:
        name = str(uuid.uuid1())
    filename = os.path.join(path, name)
    region = make_region().configure(
        'dogpile.cache.dbm',
        arguments={
            'filename': filename
        }
    )
    return region

def get_null_region():
    """Region for a "NULL" cache that doesn't really cache at all.

    Returns:
       (CacheRegion) object
    """
    return make_region().configure('dogpile.cache.null')

class ObjectCache(object):
    """Caching for ObjectAPI.

    This class provides some basic performance information
    for each of its operations.
    """

    # You can set these at the class level, and they will
    # be used for parameters of the same name to the constructor
    # if those parameters are empty (None).
    cache_class = NullCache
    cache_params = {}

    def __init__(self, ref, stats=None, cache_class=None, cache_params=None):
        """Constructor.

        Args:
          ref (str): Key for caching
          stats (PerfCollector): Shared statistics object
          cache_class (class): Subclass of `Cache`
          cache_params (dict): Parameters for cache constructor
        """
        self._cache_key = ref
        # init performance statistics
        self._stats = stats or PerfCollector(self.__class__.__name__)
        self._stats.start_event('cache.init', self._cache_key)
        # init cache
        cc = cache_class or self.cache_class
        cp = cache_params or self.cache_params
        self._cache = cc(**cp)  # workers of the world unite!
        self._stats.end_event('cache.init', self._cache_key)
        _log.info('ObjectCache.init.end cache_class={}'.format(
            cc.__name__))

    def get_data(self, parent_method):
        from_cache = False
        self._stats.start_event('cache.get_data', self._cache_key)
        data = self._cache.get(self._cache_key)
        if data is NO_VALUE:
            data = parent_method()
            self._cache.set(self._cache_key, data)
            print("@@ Main CACHING ({}): {} => keys => {}".format(
                self._cache.__class__.__name__, self._cache_key, data.keys()))
        else:
            from_cache = True
            print("@@ Main FROM CACHE: {} => keys {}".format(
                self._cache_key, data.keys()))
        self._stats.end_event('cache.get_data', self._cache_key, cached=from_cache)
        return data

    def get_data_subset(self, parent_method, path_list=None):
        """
        :param parent_method:
        :param path_list:
        :return:
        """
        if path_list is None:
            return {}
        result, from_cache = None, False
        # build extended key using the path list
        path_cache_key = '{}:{}'.format(self._cache_key, self.path_hash(path_list))
        self._stats.start_event('cache.get_data_subset', path_cache_key)
        data = self._cache.get(path_cache_key)
        if data is NO_VALUE:
            data = parent_method(path_list=path_list)
            self._cache.set(path_cache_key, data)
            print("@@ Subset CACHING ({}): {} => keys => {}".format(self._cache.__class__.__name__, path_cache_key, data.keys()))
            for k in data.keys():
                if isinstance(data[k], dict):
                    print("@@ data[{}] keys => {}".format(k, data[k].keys()))
        else:
            print("@@ Subset FROM CACHE: {} => {} TYPE {}".format(
                path_cache_key, path_list, type(data)))
            if isinstance(data, dict):
                print("@@ Subset FROM CACHE: dict keys = {}".format(
                    data.keys()))
            from_cache = True
            #result = self.extract_paths(data, path_list)
        self._stats.end_event('cache.get_data_subset', path_cache_key,
                              cached=from_cache)
        return data

    @staticmethod
    def path_hash(plist):
        return hashlib.sha1(';'.join(plist)).hexdigest()

    @staticmethod
    def extract_paths(data, path_list):
        """Extract all matching paths from `path_list` that
        are found in `data`.

        Args:
           data (dict): Source data
           path_list (list): List of path strings, which use a '/'
                             separator between items of the path.
        Return:
           (dict) All data subsets matching the paths
        """
        result = {}
        # Extract data for each path in path_list
        for p in path_list:
            extracted = {}       # create extracted path
            cur_ex = extracted   # current position in extracted path
            path = p.split('/')  # split path into its parts
            # Traverse nodes matching path in `data`, building the
            # nested dict in `extracted` as we go. Stop on missing nodes.
            cur_data, had_path = data, True
            # Loop over all (internal) nodes in the path
            for node in path[:-1]:
                # If the current node is not found, or it is a leaf,
                # then this path is not in the data: stop.
                if not node in cur_data or \
                        not isinstance(cur_data[node], dict):
                    had_path = False
                    break
                cur_ex[node] = {}          # create nested dict
                cur_ex = cur_ex[node]      # descend in extracted path
                cur_data = cur_data[node]  # descend in data
            # Done with nodes, now let's look for the leaf
            leaf = path[-1]
            # If the full path was not in data, go to next path
            if not had_path or not leaf in cur_data:
                continue
            cur_ex[leaf] = cur_data[leaf]  # copy leaf to extracted path
            result.update(extracted)       # add extracted path to result
            print("@@ update result with {}: NEW VALUE = {}".format(extracted, result))
            # Repeat this process with the next path
        print("@@ return result: {}".format(result))
        return result


    @property
    def stats(self):
        return self._stats
