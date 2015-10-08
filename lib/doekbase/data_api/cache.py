"""
Add simple, flexible caching layer.

Uses `dogpile caching http://dogpilecache.readthedocs.org/en/latest/index.html`_.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/26/15'

## Imports
# System
import os
import requests  # for errors
import uuid
# Third-party
from dogpile.cache import make_region
from dogpile.cache.api import NO_VALUE
# Local
from doekbase.data_api.core import ObjectAPI
from doekbase.data_api.util import PerfCollector, PerfEvent

## Functions and Classes

def ref_key_generator(namespace, fn, **kw):
    """Return a function that generates a key.

    Args:
        namespace (str): Namespace for all keys
        ref (str): KBase reference
        kw (dict): Additional keywords
    Return:
        Function taking variable number of arguments, each of which
        will be converted to a string and concatenated with underscores,
        prefixed by the namespace and reference string, to create the key.
    """
    name = fn.__name__
    def generate_key(*arg):
        #return namespace + "_" + name + "_".join(str(s) for s in arg)
        return "-".join([str(s) for s in arg])

    return generate_key

class Cache(object):
    def __init__(self):
        self.region = None

    def __getattr__(self, item):
        return getattr(self.region, item)

class RedisCache(Cache):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__()
        self.region = get_redis_cache(**kwargs)

class DBMCache(Cache):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__()
        self.region = get_dbm_cache(**kwargs)

def get_redis_cache(redis_host='localhost', redis_port=6379):
    """Get a new redis cache 'region' object.

    Args:
        redis_host (str): Hostname or IP for Redis server
        redis_port (int): Redis server listening port
    Returns:
        An object, of type CacheRegion
    """
    region = make_region(function_key_generator=ref_key_generator)
    region.configure(
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

def get_dbm_cache(path='/tmp', name=''):
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
    region = make_region(
        function_key_generator=ref_key_generator
    ).configure(
        'dogpile.cache.dbm',
        arguments={
            'filename': filename
        }
    )
    return region

class CachedObjectAPI(ObjectAPI):
    """Caching version of ObjectAPI.

    Should be 100% backwards-compatible with the standard class.

    In addition, this class provides some basic performance information
    for each of its operations.
    """

    # You can set these at the class level, and they will
    # be used for parameters of the same name to the constructor
    # if those parameters are empty (None).
    cache_class = None
    cache_params = None

    def __init__(self, services=None, token=None, ref=None,
                 cache_class=None, cache_params=None):
        """Constructor.

        Args:
          services (dict): see :class:`ObjectAPI`
          token (str): see :class:`ObjectAPI`
          ref (str): see :class:`ObjectAPI`
          cache_create_fn (function): Function to create cache instance
          cache_params (dict): Parameters for cache instance
        """
        # Init superclass, which includes talking to the Workspace
        # and pulling back some object metadata
        super(self.__class__, self).__init__(services=services,
                                             token=token,
                                             ref=ref)
        # cache the reference and versioned reference
        self._ref, self._vref = ref, self._info['object_reference_versioned']
        # init performance statistics
        self._stats = PerfCollector(self.__class__.__name__)
        self._cache_key = self._vref #str(self._id)
        self._stats.start_event('init', self._cache_key)
        # init cache
        CC = cache_class or self.cache_class
        cp = cache_params or self.cache_params or {}
        self._cache = CC(**cp)
        self._stats.end_event('init', self._cache_key)

    def get_data(self):
        from_cache = False
        self._stats.start_event('get_data', self._vref)
        #print('@@ cache-key "{}"'.format(self._cache_key))
        data = self._cache.get(self._cache_key)
        if data is NO_VALUE:
            data = self.ws_client.get_objects([{"ref": self.ref}])[0]['data']
            self._cache.set(self._cache_key, data)
        else:
            from_cache = True
        self._stats.end_event('get_data', self._vref, cached=from_cache)
        return data

    def get_data_subset(self, path_list=None):
        result, from_cache = [], False
        self._stats.start_event('get_data_subset', self._vref)
        data = self._cache.get(self._cache_key)
        if data is NO_VALUE:
            result = self.ws_client.get_object_subset(
                [{'ref': self.ref, 'included': path_list}])[0]['data']
            self._cache.set(self._cache_key, data)
        elif path_list is not None:
            result = self.extract_paths(data, path_list)
        self._stats.end_event('get_data_subset', self._vref, cached=from_cache)
        return result

    @staticmethod
    def extract_paths(data, path_list):
        result = []
        # extract data for each path in path_list
        for p in path_list:
            extracted = {}  # full extracted path
            cur_ex = extracted  # current position in extracted path
            path = p.split('/')  # paths are just strings
            # Traverse nodes matching path in `data`, building the
            # nested dict in `extracted` as we go. Stop on missing nodes.
            cur_data, had_path = data, True
            # Loop over all (internal) nodes in the path
            for node in path[:-1]:
                #print("@@ node {} in path {}".format(node, p))
                if not node in cur_data or \
                        not isinstance(cur_data[node], dict):
                    had_path = False
                    break
                # create nested dict
                cur_ex[node] = {}
                # descend in extracted path
                cur_ex = cur_ex[node]
                # descend in data
                cur_data = cur_data[node]
            #print("@@ had_path = {}, data={}".format(had_path, cur_data))
            # Leaf is last element of path
            leaf = path[-1]
            # if the full path was not in data, go to next path
            if not had_path or not leaf in cur_data:
                continue
            # copy leaf to extracted path
            cur_ex[leaf] = cur_data[leaf]
            # add extracted path to result
            result.append(extracted)
            #print("@@ extracted: {}".format(extracted))
            # repeat this process with the next path
        return result


    @property
    def stats(self):
        return self._stats

    # def _get_object(self, params):
    #     ref = self._get_ref_from_params(params)
    #     should_cache = self._cacheable(ref)
    #     was_in_cache = False
    #     if should_cache:
    #             obj = self._ws.get_object(self, params)
    #             self._cache.set(ref, obj)
    #         else:
    #             was_in_cache = True
    #     else:
    #         obj = self._ws.get_object(params)
    #     self._stats.end_event('get_objects', ref, num=1, num_cached=int(
    #         was_in_cache))
    #     return obj
    #
    # def _normalize_oid(self, oid):
    #     if 'ref' in oid:
    #         ref = oid['ref']
    #     else:
    #         if 'wsid' in oid:
    #             ws = oid['ws_id']
    #         elif 'workspace' in oid:
    #             ws = oid['ws_name']
    #         else:
    #             raise KeyError('wsid OR workspace')
    #         if 'objid' in oid:
    #             objid = oid['objid']
    #         elif 'name' in oid:
    #             objid = oid['name']
    #         else:
    #             raise KeyError('objid OR name')
    #         if 'ver' in oid:
    #             ref = '/'.join([ws, objid, oid['ver']])
    #         else:
    #             ref = '/'.join([ws, objid])
    #     return ref
    #
    # def _get_ref_workspace(self, ref):
    #     """Extract workspace name from an object reference.
    #     """
    #     parts = ref.split('/')
    #     if len(parts) < 2:
    #         raise ValueError('Invalid format for object reference: {'
    #                          'r}'.format(r=ref))
    #     return parts[0]
    #
    # def _get_objects(self, object_ids):
    #     object_refs = map(self._normalize_oid, object_ids)
    #     objkey = ';'.join(object_refs)
    #     self._stats.start_event('get_objects', objkey)
    #     if len(object_ids) == 0:
    #         self._stats.end_event('get_objects', objkey, num_cached=0, num=0)
    #         return []
    #     result, gaps, cacheable = [], [], []
    #     # pull what we can from cache, add indexes to gaps
    #     # list for those we don't have
    #     for i, ref in enumerate(object_refs):
    #         should_cache = self._cacheable(ref)
    #         cached_object = self._cache.get(ref) if should_cache else NO_VALUE
    #         cacheable.append(should_cache)
    #         if cached_object is NO_VALUE:
    #             gaps.append(i)
    #             result.append(None)
    #         else:
    #             result.append(cached_object)
    #     # fill in missing objects
    #     if len(gaps) > 0:
    #         # get all the missing objects at once
    #         missing_ids = [object_ids[i] for i in gaps]
    #         result2 = self._ws.get_objects(missing_ids)
    #         if len(result2) != len(object_ids):
    #             raise ValueError('Workspace objects not found: {}'.format(
    #                 ', '.join([r for r in object_refs])))
    #         # fill objects into gaps
    #         if len(gaps) == len(object_ids):  # nothing came from cache
    #             result = result2
    #         else:
    #             for index, item in zip(gaps, result2):
    #                 result[index] = item
    #     # cache all results
    #     #print("@@ object_refs={} len(result)={:d}".format(object_refs,
    #     # len(result)))
    #     for i in range(len(object_refs)):
    #         if cacheable[i]:
    #             self._cache.set(object_refs[i], result[i])
    #     self._stats.end_event('get_objects', objkey, num=len(
    #         object_ids), num_cached=len(object_ids) - len(gaps))
    #
    # def _safe_call(self, method, *args):
    #     """Standardize exception handling for a workspace call.
    #     """
    #     try:
    #         return method(*args)
    #     except (requests.ConnectionError, client.ServerError) as err:
    #         raise self.ConnectionError(err)
    #
    #
