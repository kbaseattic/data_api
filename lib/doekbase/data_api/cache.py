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
from doekbase.workspace import client
from doekbase.data_api import wsfile
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
        return namespace + "_" + name + "_".join(str(s) for s in arg)

    return generate_key

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

class WorkspaceCached(object):
    """Caching version of workspace client.

    Should be 100% backwards-compatible with the standard client.

    In addition, this class provides some basic performance information
    for each of its operations.

    Some useful data structures to know (from the workspace spec.):
    * workspace_info (tuple): 0) ws_name id, 1) username owner,
        2) timestamp moddate, 3) int objects, 4) permission user_permission,
        5) permission global_permission, 6) ws_id num_id
    * workspace identity (WSI): a dict with two possible forms
      {'workspace': '<string workspace name>'} or {'id': <integer-id>}
    """
    class ConnectionError(Exception):
        def __init__(self, *args):
            msg = str(args[0]).split('\n')[0]
            Exception.__init__(self, msg)

    # List of methods directly delegated to client
    _delegated = ('administer', 'alter_workspace_metadata',
                  'clone_workspace', 'create_workspace', 'delete_workspace',
                  'get_permissions',
                  'get_workspace_description', 'get_workspace_info',
                  'lock_workspace', 'set_global_permission', 'set_permissions',
                  'save_object', 'save_objects',
                  'set_workspace_description',
                  'ver')

    def __init__(self, cache_create_fn=None, cache_params=None,
                 ws_create_fn=None, ws_params=None):
        """Create cache, instantiating given workspace class to handle
        initial retrieval of data.

        Both the caching object and the workspace object are pluggable.

        Keywords:
          cache_create_fn (function): Function to create cache instance
          cache_params (dict): Parameters for cache instance
          ws_create_fn (function): Function to create workspace instance
          ws_params (dict): Parameters for workspace instance
        """
        self._cache = cache_create_fn(**(cache_params or {}))
        self._ws = ws_create_fn(**(ws_params or {}))
        self._get_ref_from_params = lambda p: p['objects'][0]['ref']
        self._stats = PerfCollector(self.__class__.__name__)
        self._known_cacheable_refs = set()

###

    def __getattr__(self, item):
        """If this is one of the delegated methods, return a wrapper
        function so it will call the underlying workspace.
        """
        if item in self._delegated:
            return lambda *a: getattr(self._ws, item)(*a)
        raise AttributeError(item)

###

    def get_object(self, params):
        """Get (possibly cached) object.

        Returns:
           Single object instance
        Raises:
           self.ConnectionError
        """
        self._safe_call(self._get_object, params)

    def get_objects(self, object_ids):
        """Get one or more (possibly cached) objects.

        Args:
            object_ids: List of references
        Returns:
            list of object instances
        """
        self._safe_call(self._get_objects, object_ids)


###

    def _cacheable(self, ref):
        """Is this reference (really, its workspace) globally readable
        and therefore cacheable?

        Args:
          ref (str): Workspace reference string.
        Returns:
           True if this reference is globally readable, otherwise False.
        """
        ws_name = self._get_ref_workspace(ref)
        # Cache the knowledge of cacheability in memory.
        # This assumes that 'reference data' doesn't become user data,
        # really ever.
        if ws_name in self._known_cacheable_refs:
            return True
        info = self._ws.get_workspace_info({'workspace': ws_name})
        globalread = info[6]  # ugh
        cacheable = (globalread == 'r')
        if cacheable:
            self._known_cacheable_refs.add(ws_name)
        return cacheable

    @property
    def stats(self):
        return self._stats

    def _get_object(self, params):
        ref = self._get_ref_from_params(params)
        self._stats.start_event('get_objects', ref)  # see get_objects()
        should_cache = self._cacheable(ref)
        was_in_cache = False
        if should_cache:
            obj = self._cache.get(ref)
            if obj is NO_VALUE:
                obj = self._ws.get_object(self, params)
                self._cache.set(ref, obj)
            else:
                was_in_cache = True
        else:
            obj = self._ws.get_object(params)
        self._stats.end_event('get_objects', ref, num=1, num_cached=int(
            was_in_cache))
        return obj

    def _normalize_oid(self, oid):
        if 'ref' in oid:
            ref = oid['ref']
        else:
            if 'wsid' in oid:
                ws = oid['ws_id']
            elif 'workspace' in oid:
                ws = oid['ws_name']
            else:
                raise KeyError('wsid OR workspace')
            if 'objid' in oid:
                objid = oid['objid']
            elif 'name' in oid:
                objid = oid['name']
            else:
                raise KeyError('objid OR name')
            if 'ver' in oid:
                ref = '/'.join([ws, objid, oid['ver']])
            else:
                ref = '/'.join([ws, objid])
        return ref

    def _get_ref_workspace(self, ref):
        """Extract workspace name from an object reference.
        """
        parts = ref.split('/')
        if len(parts) < 2:
            raise ValueError('Invalid format for object reference: {'
                             'r}'.format(r=ref))
        return parts[0]

    def _get_objects(self, object_ids):
        object_refs = map(self._normalize_oid, object_ids)
        objkey = ';'.join(object_refs)
        self._stats.start_event('get_objects', objkey)
        if len(object_ids) == 0:
            self._stats.end_event('get_objects', objkey, num_cached=0, num=0)
            return []
        result, gaps, cacheable = [], [], []
        # pull what we can from cache, add indexes to gaps
        # list for those we don't have
        for i, ref in enumerate(object_refs):
            should_cache = self._cacheable(ref)
            cached_object = self._cache.get(ref) if should_cache else NO_VALUE
            cacheable.append(should_cache)
            if cached_object is NO_VALUE:
                gaps.append(i)
                result.append(None)
            else:
                result.append(cached_object)
        # fill in missing objects
        if len(gaps) > 0:
            # get all the missing objects at once
            missing_ids = [object_ids[i] for i in gaps]
            result2 = self._ws.get_objects(missing_ids)
            if len(result2) != len(object_ids):
                raise ValueError('Workspace objects not found: {}'.format(
                    ', '.join([r for r in object_refs])))
            # fill objects into gaps
            if len(gaps) == len(object_ids):  # nothing came from cache
                result = result2
            else:
                for index, item in zip(gaps, result2):
                    result[index] = item
        # cache all results
        #print("@@ object_refs={} len(result)={:d}".format(object_refs,
        # len(result)))
        for i in range(len(object_refs)):
            if cacheable[i]:
                self._cache.set(object_refs[i], result[i])
        self._stats.end_event('get_objects', objkey, num=len(
            object_ids), num_cached=len(object_ids) - len(gaps))

    def _safe_call(self, method, *args):
        """Standardize exception handling for a workspace call.
        """
        try:
            return method(*args)
        except (requests.ConnectionError, client.ServerError) as err:
            raise self.ConnectionError(err)


