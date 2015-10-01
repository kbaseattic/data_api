"""
Test caching.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/30/15'

import os
import threading
import time
from doekbase.data_api import cache
from dogpile.cache.api import NO_VALUE

dbm_region = None

def setup():
    global dbm_region
    dbm_region = cache.get_dbm_cache()

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
