"""
Test caching.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/30/15'

# System
import glob
import os
import sys
import threading
import time
from unittest import skipUnless
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

def test_ver():
    assert False

def test_create_workspace():
    assert False

def test_alter_workspace_metadata():
    assert False

def test_clone_workspace():
    assert False

def test_lock_workspace():
    assert False

def test_get_workspacemeta():
    assert False

def test_get_workspace_info():
    assert False

def test_get_workspace_description():
    assert False

def test_set_permissions():
    assert False

def test_set_global_permission():
    assert False

def test_set_workspace_description():
    assert False

def test_get_permissions():
    assert False

def test_save_object():
    assert False

def test_save_objects():
    assert False

def test_get_object():
    assert False

def test_get_object_provenance():
    assert False

def test_get_objects():
    assert False

def test_get_object_subset():
    assert False

def test_get_object_history():
    assert False

def test_list_referencing_objects():
    assert False

def test_list_referencing_object_counts():
    assert False

def test_get_referenced_objects():
    assert False

def test_list_workspaces():
    assert False

def test_list_workspace_info():
    assert False

def test_list_workspace_objects():
    assert False

def test_list_objects():
    assert False

def test_get_objectmeta():
    assert False

def test_get_object_info():
    assert False

def test_get_object_info_new():
    assert False

def test_rename_workspace():
    assert False

def test_rename_object():
    assert False

def test_copy_object():
    assert False

def test_revert_object():
    assert False

def test_hide_objects():
    assert False

def test_unhide_objects():
    assert False

def test_delete_objects():
    assert False

def test_undelete_objects():
    assert False

def test_delete_workspace():
    assert False

def test_undelete_workspace():
    assert False

def test_request_module_ownership():
    assert False

def test_register_typespec():
    assert False

def test_register_typespec_copy():
    assert False

def test_release_module():
    assert False

def test_list_modules():
    assert False

def test_list_module_versions():
    assert False

def test_get_module_info():
    assert False

def test_get_jsonschema():
    assert False

def test_translate_from_MD5_types():
    assert False

def test_translate_to_MD5_types():
    assert False

def test_get_type_info():
    assert False

def test_get_all_type_info():
    assert False

def test_get_func_info():
    assert False

def test_get_all_func_info():
    assert False

def test_grant_module_ownership():
    assert False

def test_remove_module_ownership():
    assert False

def test_list_all_types():
    assert False

def test_administer():
    assert False
