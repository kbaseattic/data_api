"""
Test caching.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/30/15'

# System
import os
import sys
import threading
import time
from unittest import skipUnless
# Third-party
from dogpile.cache.api import NO_VALUE
# Local
from doekbase.data_api import cache
from . import shared

dbm_region = None
redis_region = None

genome_new = "PrototypeReferenceGenomes/kb|g.166819"
genome_old = "OriginalReferenceGenomes/kb|g.166819"
taxon_new = "ReferenceTaxons/242159_taxon"
taxon_old = "OriginalReferenceGenomes/kb|g.166819"
g_token = ''

def setup():
    global dbm_region, redis_region, g_token
    dbm_region = cache.get_dbm_cache()
#    redis_region = cache.get_redis_cache()
    shared.setup()
    g_token = os.environ.get('KB_AUTH_TOKEN', 'No token in environment')
    #print('@@ Got token = "{}"'.format(g_token))

def teardown():
    global dbm_region
    filename = dbm_region.backend.filename
    for ext in 'db', 'dogpile.lock', 'rw.lock':
        f = filename + '.' + ext
        if os.path.exists(f):
            os.unlink(f)
    del dbm_region
    dbm_region = None

def test_dbm_get():
    dbm_region.set('x', 1)
    x = dbm_region.get('x')
    assert x == 1

def test_dbm_parallel_simple():
    n, nthreads = 10, 100
    dbm_region.set('x', 0)
    threads = [threading.Thread(target=reader_thread, args=(n, 0))
               for n in range(nthreads)]
    [thr.start() for thr in threads]
    [thr.join() for thr in threads]

def reader_thread(n, expected_value):
    for i in range(n):
        x = dbm_region.get('x')
        assert x == expected_value

def test_dbm_wait():
    t0 = time.time()
    v1 = dbm_wait_1_sec('a')
    t1 = time.time()
    v2 = dbm_wait_1_sec('a')
    t2 = time.time()
    v3 = dbm_wait_1_sec('b')

    # cached value is the same
    assert v1 == v2
    # different values are different
    assert v3 != v2
    # first time it wasn't cached
    assert t1 - t0 > 0.9
    # second time it used the cache
    assert t2 - t1 < 0.1

def dbm_wait_1_sec(x):
    val = dbm_region.get(x)
    if val == NO_VALUE:
        dbm_region.set(x, x)
        time.sleep(1)
        val = x
    return val

# Caching version of Workspace client

@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_ws_cached_get_object_dbm():
    _test_ws_cached_get_object(cache.get_dbm_cache, {})

@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_ws_cached_get_object_redis():
    _test_ws_cached_get_object(cache.get_redis_cache, {})

def _test_ws_cached_get_object(fn, params):
    ws = cache.WorkspaceCached(fn, params,
                               url=shared.g_ws_url, token=g_token)
    ws.stats.add_observer(ws.stats.EVENT_WILDCARD, print_ws_cached_start, None)
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
        #ws.get_objects(objlist([taxon_old]))
        #timings.append(('old + no-cache', ws.stats.get_last()['duration']))
        #ws.get_objects(objlist([taxon_old]))
        #timings.append(('old + cache', ws.stats.get_last()['duration']))
    except ws.ConnectionError:
         raise
    # cache should be faster, always
    for i in range(0, len(timings), 2):
        assert timings[i] > timings[i + 1]
    # dump timings at end
    ws.stats.dump(sys.stdout)

def print_ws_cached_start(event, key, timestamp):
    print("Start: {e} for <{k}>".format(e=event, k=key))