"""
Test caching.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/30/15'

import time
from doekbase.data_api import cache

region = None

def setup():
    global region
    region = cache.get_redis_cache()

def test_cache_simple():
    t0 = time.time()
    v1 = wait_1_sec(1)
    t1 = time.time()
    v2 = wait_1_sec(1)
    t2 = time.time()
    v3 = wait_1_sec(2)

    assert v1 == v2
    assert v3 != v2
    assert t1 - t0 > 0.9
    assert t2 - t1 < 0.1

@region.cache_on_arguments()
def wait_1_sec(x):
    time.sleep(1)
    return x

