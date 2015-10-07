"""
Test caching.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/30/15'

# System
import logging
import os
import sys
import threading
import time
from unittest import skipUnless, TestCase
# Third-party
from dogpile.cache.api import NO_VALUE
# Local
from doekbase.data_api import cache, core, wsfile
from doekbase.workspace import client as ws_client
from . import shared

dbm_path = None

genome_new = "PrototypeReferenceGenomes/kb|g.166819"
genome_old = "OriginalReferenceGenomes/kb|g.166819"
taxon_new = "ReferenceTaxons/242159_taxon"
taxon_old = "OriginalReferenceGenomes/kb|g.166819"
g_token = ''

g_workspace_objects = {}  # key is cache type, value is object

_log = logging.getLogger('doekbase.tests.test_cache')

def setup():
    global g_token, dbm_path

    shared.setup()

    # Token token on the wall, who's the authiest of them all?
    g_token = os.environ.get('KB_AUTH_TOKEN', 'No token in environment')

    # Create  dir. for DBM cache
    dbm_path = '/tmp/test_cache-{:d}'.format(int(time.time()))
    os.mkdir(dbm_path)

    # Set up all the cached workspace objects
    for type_, fn, params in (('dbm', cache.get_dbm_cache, {'path': dbm_path}),
                              ('redis', cache.get_redis_cache, {})):
        do_load = False
        if '://' in core.g_ws_url:
            ws_ctor = ws_client.Workspace
            ws_params = dict(url=shared.g_ws_url, token=g_token)
        else:
            ws_ctor = wsfile.WorkspaceFile
            ws_params = dict(working_directory=shared.g_ws_url)
            do_load = True
        ws = cache.WorkspaceCached(fn, params, ws_ctor, ws_params)
        if do_load:
            for ref in (genome_new, genome_old, taxon_new, taxon_old):
                ws._ws.load(ref.replace('/', '_'))
        ws.stats.add_observer(ws.stats.EVENT_WILDCARD, print_ws_cached_start, None)
        g_workspace_objects[type_] = ws

def teardown():
    global g_workspace_objects
    g_workspace_objects = {}
    for f in os.listdir(dbm_path):
        os.unlink(os.path.join(dbm_path, f))
    os.rmdir(dbm_path)

def test_dbm_get():
    dbm_region = cache.get_dbm_cache(path=dbm_path)
    dbm_region.set('x', 1)
    x = dbm_region.get('x')
    assert x == 1

def test_dbm_parallel_simple():
    dbm_region = cache.get_dbm_cache(path=dbm_path)
    n, nthreads = 10, 100
    dbm_region.set('x', 0)
    threads = [threading.Thread(target=reader_thread, args=(dbm_region, n, 0))
               for n in range(nthreads)]
    [thr.start() for thr in threads]
    [thr.join() for thr in threads]

def reader_thread(dbm_region, n, expected_value):
    for i in range(n):
        x = dbm_region.get('x')
        assert x == expected_value

def test_dbm_wait():
    dbm_region = cache.get_dbm_cache(path=dbm_path)
    t0 = time.time()
    v1 = dbm_wait_1_sec(dbm_region, 'a')
    t1 = time.time()
    v2 = dbm_wait_1_sec(dbm_region, 'a')
    t2 = time.time()
    v3 = dbm_wait_1_sec(dbm_region, 'b')

    # cached value is the same
    assert v1 == v2
    # different values are different
    assert v3 != v2
    # first time it wasn't cached
    assert t1 - t0 > 0.9
    # second time it used the cache
    assert t2 - t1 < 0.1

def dbm_wait_1_sec(dbm_region, x):
    val = dbm_region.get(x)
    if val == NO_VALUE:
        dbm_region.set(x, x)
        time.sleep(1)
        val = x
    return val

@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_ws_cached_get_object_dbm():
    _test_ws_cached_get_object(g_workspace_objects['dbm'])

@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_ws_cached_get_object_redis():
    _test_ws_cached_get_object(g_workspace_objects['redis'])

def _test_ws_cached_get_object(ws):
    timings = []
    objlist = lambda items: [{'ref': x} for x in items]
    # Taxon
    try:
        # New
        ws.get_objects(objlist([taxon_new]))
        timings.append(('new + no-cache', ws.stats.get_last()['duration']))
        ws.get_objects(objlist([taxon_new]))
        timings.append(('new + cache', ws.stats.get_last()['duration']))
        # Old
        # ws.get_objects(objlist([taxon_old]))
        # timings.append(('old + no-cache', ws.stats.get_last()['duration']))
        # ws.get_objects(objlist([taxon_old]))
        # timings.append(('old + cache', ws.stats.get_last()['duration']))
    except ws.ConnectionError:
        raise
    # cache should be faster, always
    for i in range(0, len(timings), 2):
        assert timings[i] > timings[i + 1]
    # dump timings at end
    ws.stats.dump(sys.stdout)

def print_ws_cached_start(event, key, timestamp):
    print("Start: {e} for <{k}>".format(e=event, k=key))

#################################
# Comprehensive workspace tests #
#################################

class CachedWorkspaceTests(TestCase):

    # maximum allowable version of workspace for this
    # test suite to be valid
    MAX_WS_VERSION = (0, 999, 999)

    def setUp(self):
        self.ws = g_workspace_objects
        self._delete_ws = set()

    def tearDown(self):
        # delete temporary workspaces
        for ws in self._delete_ws:
            _log.info('deleting temporary workspace: {}'.format(ws))
            g_workspace_objects['redis'].delete_workspace({'workspace': ws})

    def test_all(self):
        """Run all tests
        """
        test_methods = filter(lambda s: s.startswith('_t_'),
                              dir(self))
        sys.stdout.write('\n')

        default_ws = {}
        for t in g_workspace_objects:
            self.ws = g_workspace_objects[t]
            default_ws[t] = self._t_create_workspace()

        for meth_name in test_methods:
            test_method = getattr(self, meth_name)
            friendly_name = meth_name[3:]  # strip prefix
            for cache_type in g_workspace_objects:
                self.ws = g_workspace_objects[cache_type]
                self.default_ws = default_ws[cache_type]
                self._start(type_=cache_type,
                            name=friendly_name)
                try:
                    test_method()
                    self._succeeded()
                except AssertionError as err:
                    self._failed(err)
                except ws_client.ServerError as err:
                    self._server_error(err)

    def _start(self, type_=None, name=None):
        m = ".  Cached workspace ({:6s}) {:30s} "
        sys.stdout.write(m.format(type_, name))
        sys.stdout.flush()

    def _succeeded(self):
        sys.stdout.write("OK\n")

    def _failed(self, err):
        sys.stdout.write("FAILED: {}\n".format(err))

    def _server_error(self, err):
        err = str(err).split('\n')[0]
        sys.stdout.write("FAILED: (ServerError) {}\n".format(err))

    def generic_object(self):
        return {'type': 'Empty.AType-1.0',
                'data': {'hello': 'world'}}

    def _t_ver(self):
        value = self.ws.ver()
        p = value.split('.')
        assert len(p) == 3
        for i in range(3):
            assert int(p[i]) <= self.MAX_WS_VERSION[i], \
                "Version mismatch: {ver} > {expected}".format(
                    ver=value, expected='.'.join(map(str, self.MAX_WS_VERSION)))


    def _t_create_workspace(self):
        name = 'foo-{:.3f}'.format(time.time())
        self.ws.create_workspace({'workspace': name})
        self._delete_ws.add(name)
        return name  # for re-use elsewhere

    def _t_alter_workspace_metadata(self):
        name = self._t_create_workspace()
        self.ws.alter_workspace_metadata({'wsi': {'workspace': name},
                                          'new': {'trump': 'idiot'}})

    def _t_clone_workspace(self):
        name = self.default_ws
        name2 = 'bar-{:.3f}'.format(time.time())
        self.ws.clone_workspace({'wsi': {'workspace': name},
                                 'workspace': name2})
        self._delete_ws.add(name2)

    def _t_lock_workspace(self):
        # this is not reversible and the workspace cannot
        # be deleted (!), so running this as a test against a
        # real workspace creates cruft.
        # name = self._t_create_workspace()
        # self.ws.lock_workspace({'workspace': name})
        return

    def _t_get_workspacemeta(self):
        # deprecated form of get_workspace_info
        return

    def _t_get_workspace_info(self):
        self.ws.get_workspace_info({'workspace': self.default_ws})

    def _t_get_workspace_description(self):
        self.ws.get_workspace_description({'workspace': self.default_ws})

    def _t_set_permissions(self):
        name = self._t_create_workspace()
        self.ws.set_permissions({'workspace': name,
                                 'new_permission': 'r',
                                 'users': ['kbasetest']})

    def _t_set_global_permission(self):
        name = self._t_create_workspace()
        self.ws.set_global_permission({'workspace': name,
                                 'new_permission': 'r'})

    def _t_set_workspace_description(self):
        self.ws.set_workspace_description(
            {'workspace': self.default_ws,
             'description': 'quite lame'})

    def _t_get_permissions(self):
        self.ws.get_permissions({'workspace': self.default_ws})

    def _t_save_object(self):
        # deprecated for save_objects
        return

    def _t_save_objects(self):
        name = self._t_create_workspace()
        self.ws.save_objects({
            'workspace': name,
            'objects': [self.generic_object()]
        })

    def _t_get_object(self):
        # deprecated for get_objects
        return

    def _t_get_object_provenance(self):
        assert False

    def _t_get_objects(self):
        assert False

    def _t_get_object_subset(self):
        assert False

    def _t_get_object_history(self):
        assert False

    def _t_list_referencing_objects(self):
        assert False

    def _t_list_referencing_object_counts(self):
        assert False

    def _t_get_referenced_objects(self):
        assert False

    def _t_list_workspaces(self):
        assert False

    def _t_list_workspace_info(self):
        assert False

    def _t_list_workspace_objects(self):
        assert False

    def _t_list_objects(self):
        assert False

    def _t_get_objectmeta(self):
        assert False

    def _t_get_object_info(self):
        assert False

    def _t_get_object_info_new(self):
        assert False

    def _t_rename_workspace(self):
        assert False

    def _t_rename_object(self):
        assert False

    def _t_copy_object(self):
        assert False

    def _t_revert_object(self):
        assert False

    def _t_hide_objects(self):
        assert False

    def _t_unhide_objects(self):
        assert False

    def _t_delete_objects(self):
        assert False

    def _t_undelete_objects(self):
        assert False

    def _t_delete_workspace(self):
        assert False

    def _t_undelete_workspace(self):
        assert False

    def _t_request_module_ownership(self):
        assert False

    def _t_register_typespec(self):
        assert False

    def _t_register_typespec_copy(self):
        assert False

    def _t_release_module(self):
        assert False

    def _t_list_modules(self):
        assert False

    def _t_list_module_versions(self):
        assert False

    def _t_get_module_info(self):
        assert False

    def _t_get_jsonschema(self):
        assert False

    def _t_translate_from_MD5_types(self):
        assert False

    def _t_translate_to_MD5_types(self):
        assert False

    def _t_get_type_info(self):
        assert False

    def _t_get_all_type_info(self):
        assert False

    def _t_get_func_info(self):
        assert False

    def _t_get_all_func_info(self):
        assert False

    def _t_grant_module_ownership(self):
        assert False

    def _t_remove_module_ownership(self):
        assert False

    def _t_list_all_types(self):
        assert False

    def _t_administer(self):
        try:
            self.ws.administer({})
        except ws_client.ServerError as err:
            # fail if this is NOT the "normal" error
            # caused by lack of admin. permissions
            assert 'not an admin' in str(err)
