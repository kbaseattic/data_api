"""
Test caching.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/30/15'

# System
import logging
import os
import threading
import time
import unittest
# Third-party
from dogpile.cache.api import NO_VALUE
# Local
from doekbase.data_api import cache
from . import shared

_log = logging.getLogger('doekbase.tests.test_cache')

# def setup():
#     shared.setup()

class TestCache(unittest.TestCase):
    """
    """
    dbm_path = None

    @classmethod
    def setUpClass(cls):
        cls.dbm_path = '/tmp/test_cache-{:d}'.format(int(time.time()))
        os.mkdir(cls.dbm_path)
        cls.dbm_region = cache.get_dbm_cache(path=cls.dbm_path)

    def setUp(self):
        self.regions = {}
        # DBM
        self.regions['DBM'] = self.dbm_region
        # Redis
        try:
            redis_region = cache.get_redis_cache()
            redis_region.get('foo')
            self.regions['Redis'] = redis_region
        except Exception as err:
            _log.warn('Skipping Redis tests, simple get gave error: {'
                      'e}'.format(e=err))
        self._clear_keys = []

    def tearDown(self):
        # clear data on persistent redis cache
        region = self.regions['Redis']
        for key in list(set(self._clear_keys)):
            _log.debug('Deleting key "{}" from Redis'.format(key))
            region.delete(key)

    @classmethod
    def tearDownClass(cls):
        for f in os.listdir(cls.dbm_path):
            os.unlink(os.path.join(cls.dbm_path, f))
        os.rmdir(cls.dbm_path)

    def test_get(self):
        for key, region in self.regions.items():
            _log.info('get.{}'.format(key))
            region.set('x', 1)
            x = region.get('x')
            assert x == 1

    def test_parallel(self):
        for key, region in self.regions.items():
            _log.info('parallel.{}'.format(key))
            self.parallel_simple(region)

    def parallel_simple(self, region):
        n, nthreads = 10, 100
        region.set('x', 0)
        threads = [threading.Thread(target=self.reader_thread,
                                    args=(region, n, 0))
                   for n in range(nthreads)]
        [thr.start() for thr in threads]
        [thr.join() for thr in threads]

    def reader_thread(self, region, n, expected_value):
        for i in range(n):
            x = region.get('x')
            assert x == expected_value

    def test_basic(self):
        for key, region in self.regions.items():
            _log.info('wait.{}'.format(key))
            self.basic(region)

    def basic(self, region):
        self._clear_keys.extend(['a', 'b'])
        # get/set some values
        v1 = self.get_set(region, 'a')
        v2 = self.get_set(region, 'a')
        v3 = self.get_set(region, 'b')
        # cached value is the same
        assert v1 == v2
        # different values are different
        assert v3 != v2


    def get_set(self, region, x):
        val = region.get(x)
        if val == NO_VALUE:
            region.set(x, x)
            val = x
        return val
