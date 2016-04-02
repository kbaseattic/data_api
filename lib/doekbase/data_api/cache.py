"""
Add simple, flexible caching layer.

Uses [dogpile caching](http://dogpilecache.readthedocs.org/en/latest/index.html).
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/26/15'

## Imports

# System
import hashlib
import logging
import os
import time
import uuid
# Third-party
from dogpile.cache import make_region
import redis
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
    # Maximum timeout to fetch a cached value, in seconds
    MAX_FETCH_TIMEOUT = 5

    # You can set these at the class level, and they will
    # be used for parameters of the same name to the constructor
    # if those parameters are empty (None).
    cache_class = NullCache   #: Class for cache backend
    cache_params = {}         #: Constructor parameters for cache backend

    def __init__(self, ref, stats=None, cache_class=None, cache_params=None, is_public=True):
        """Constructor.

        Args:
          ref (str): Key for caching
          stats (PerfCollector): Shared statistics object
          cache_class (class): Subclass of `Cache`
          cache_params (dict): Parameters for cache constructor
        """
        self._key = ref
        self._public = is_public
        # init performance statistics
        self._stats = stats or PerfCollector(self.__class__.__name__)
        self._stats.start_event('cache.init', self._key)
        # init cache
        cc = cache_class or self.cache_class
        cp = cache_params or self.cache_params
        self._cache = cc(**cp)  # workers of the world unite!
        self._stats.end_event('cache.init', self._key)
        _log.debug('ObjectCache.init.end cache_class={}'.format(
            cc.__name__))

    def get_derived_data(self, parent_method, name):
        key = self._key + '::' + name  # store separately from 'raw' data
        self._stats.start_event('cache.get_derived_data', key)
        data = self._cache.get_or_create(key, parent_method,
                                         should_cache_fn=self._should_cache)
        self._stats.end_event('cache.get_derived_data', key)
        return data

    def get_data(self, parent_method):
        """Get data from cache or the callee's method.
        """
        self._stats.start_event('cache.get_data', self._key)
        data = self._cache.get_or_create(self._key, parent_method)
        self._stats.end_event('cache.get_data', self._key)
        return data

    def get_data_subset(self, parent_method, path_list=None):
        """Get data subset from cache or the callee's method.
        """
        self._stats.start_event('cache.get_data_subset', self._key)
        # save a little time for a no-op
        if path_list is None:
            self._stats.end_event('cache.get_data_subset', self._key,
                                  msg='empty-path-list')
            return {}
        # create unique key for object + path
        key = '{}:{}'.format(self._key, self.path_hash(path_list))
        # creator function, currying path_list arg.
        creator = lambda : parent_method(path_list=path_list)
        # get from cache, or create
        data = self.cache_get_or_create(key, creator)
        self._stats.end_event('cache.get_data_subset', self._key)
        return data

    def cache_get_or_create(self, key, creator):
        """Get from cache, or create, with extra logic to handle
        a Redis server that is not yet fully up and running.

        Args:
            key (str): Cache item key
            creator (function): Called to create the item if not found
        Return:
            (object) value Will return a value unless MAX_FETCH_TIMEOUT
            seconds is exceeded
        Raises:
            RuntimeError: on timeout
        """
        kw = dict(should_cache_fn=self._should_cache)
        data, total_sleep = None, 0
        while data is None and total_sleep < self.MAX_FETCH_TIMEOUT:
            try:
                data = self._cache.get_or_create(key, creator, **kw)
            except redis.BusyLoadingError:
                _log.warn('Redis is busy, sleep for 0.1s and try again')
                time.sleep(0.1)
                total_sleep += 0.1
        if data is None and total_sleep >= self.MAX_FETCH_TIMEOUT:
            raise RuntimeError('Timeout while fetching {} from cache'
                               .format(key))
        return data

    def _should_cache(self, data):
        """Whether this data should be cached, or fetched new every time.

        Args:
          data (dict): Result from ``get_data`` or ``get_data_subset`` in
                       :class:`doekbase.data_api.core.ObjectAPI`.
        Return:
          (bool) True if this object should be cached, False otherwise.
        """
        result = self._public
        _log.debug("should_cache result={:d}".format(int(result)))
        return result

    @staticmethod
    def path_hash(plist):
        return hashlib.sha1(';'.join(plist)).hexdigest()

    @property
    def stats(self):
        return self._stats




    # @staticmethod
    # def extract_paths(data, path_list):
    #     """Extract all matching paths from `path_list` that
    #     are found in `data`.
    #
    #     Note: Not used right now, since all retrievals of data by
    #     subset use the full path as the key (thus caching the exact
    #     subset of data, and not needing to subset the object manually)
    #
    #     Args:
    #        data (dict): Source data
    #        path_list (list): List of path strings, which use a '/'
    #                          separator between items of the path.
    #     Return:
    #        (dict) All data subsets matching the paths
    #     """
    #     result = {}
    #     # Extract data for each path in path_list
    #     for p in path_list:
    #         extracted = {}  # create extracted path
    #         cur_ex = extracted  # current position in extracted path
    #         path = p.split('/')  # split path into its parts
    #         # Traverse nodes matching path in `data`, building the
    #         # nested dict in `extracted` as we go. Stop on missing nodes.
    #         cur_data, had_path = data, True
    #         # Loop over all (internal) nodes in the path
    #         for node in path[:-1]:
    #             # If the current node is not found, or it is a leaf,
    #             # then this path is not in the data: stop.
    #             if not node in cur_data or \
    #                     not isinstance(cur_data[node], dict):
    #                 had_path = False
    #                 break
    #             cur_ex[node] = {}  # create nested dict
    #             cur_ex = cur_ex[node]  # descend in extracted path
    #             cur_data = cur_data[node]  # descend in data
    #         # Done with nodes, now let's look for the leaf
    #         leaf = path[-1]
    #         # If the full path was not in data, go to next path
    #         if not had_path or not leaf in cur_data:
    #             continue
    #         cur_ex[leaf] = cur_data[leaf]  # copy leaf to extracted path
    #         result.update(extracted)  # add extracted path to result
    #         print("@@ update result with {}: NEW VALUE = {}".format(extracted,
    #                                                                 result))
    #         # Repeat this process with the next path
    #     print("@@ return result: {}".format(result))
    #     return result
