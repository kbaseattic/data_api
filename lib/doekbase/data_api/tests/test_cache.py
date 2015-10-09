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
from doekbase.data_api import util
from doekbase.data_api.core import ObjectAPI
from . import shared

_log = util.get_logger(__name__)

# Uncomment this line to turn off DBM tests
USE_DBM = False

class TestCache(unittest.TestCase):
    """Test the cache.
    """
    dbm_path = None

## Setup / teardown

    @classmethod
    def setUpClass(cls):
        if USE_DBM:
            cls.dbm_path = '/tmp/test_cache-{:d}'.format(int(time.time()))
            os.mkdir(cls.dbm_path)
            cls.dbm_region = cache.get_dbm_region(path=cls.dbm_path)

    def setUp(self):
        self.regions = {}
        # DBM
        if USE_DBM:
            self.regions['DBM'] = self.dbm_region
        # Redis
        try:
            redis_region = cache.get_redis_region()
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
        if USE_DBM:
            for f in os.listdir(cls.dbm_path):
                os.unlink(os.path.join(cls.dbm_path, f))
            os.rmdir(cls.dbm_path)

## Tests

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

    def test_large(self):
        for key, region in self.regions.items():
            _log.info('large_objects.{}'.format(key))
            self.put_large_objects(region)

    def put_large_objects(self, region):
        """Try putting large objects into the cache."""
        return
        # z = []
        # for i in range(2):
        #     _log.info('Put large object with {:d}M zeroes'.format(
        #         (i + 1)*50))
        #     z.extend([0] * 50000000)  # add 10M zeros
        #     region.set('zeroes_{:d}M'.format(i), z)

class TestCachedObjectAPI(unittest.TestCase):

    genome_new = "PrototypeReferenceGenomes/kb|g.166819"
    genome_old = "OriginalReferenceGenomes/kb|g.166819"

    def setUp(self):
        cache.ObjectCache.cache_class = cache.RedisCache
        cache.ObjectCache.cache_params = {'redis_host': 'localhost'}

    def test_extract_paths(self):
        data = {'a1': {'b1': {'c1': 1, 'c2': 2}, 'b2': {'d1': 3}}}
        paths = ['a1/b1', 'a1/b1/c2', 'a1/b2/d1', 'a1/b1/N', 'N', 'a1/N']
        r = cache.ObjectCache.extract_paths(data, paths)
        assert len(r) == 3, 'Wrong number of results, got {:d} expected {:d}'.\
            format(len(r), 3)
        msg = 'Invalid result "{r}" for path "{p}"'
        assert r[0] == {'a1': {'b1': {'c1': 1, 'c2': 2}}}, \
            msg.format(r=r[0], p=paths[0])
        assert r[1] == {'a1': {'b1': {'c2': 2}}}, msg.format(r=r[1], p=paths[1])
        assert r[2] == {'a1': {'b2':{'d1': 3}}}, msg.format(r=r[2], p=paths[2])

    def test_get_new_genome(self):
        g = ObjectAPI(services=shared.get_services(), ref=self.genome_new)
        g.get_data()
        event = g.stats.get_last()
        _log.info('Get new genome #1 (cached={}): {:.3f}'.format(
            event['cached'], event.duration))
        g.get_data()
        event = g.stats.get_last()
        _log.info('Get new genome #2 (cached={}): {:.3f}'.format(
            event['cached'], event.duration))

    def test_get_old_genome(self):
        g = ObjectAPI(services=shared.get_services(), ref=self.genome_old)
        g.get_data()
        event = g.stats.get_last()
        _log.info('Get old genome #1 (cached={}): {:.3f}'.format(
            event['cached'], event.duration))
        g.get_data()
        event = g.stats.get_last()
        _log.info('Get old genome #2 (cached={}): {:.3f}'.format(
            event['cached'], event.duration))

    def test_get_referrers(self):
        g = ObjectAPI(services=shared.get_services(), ref=self.genome_old)
        r = g.get_referrers()
        g = ObjectAPI(services=shared.get_services(), ref=self.genome_new)
        r = g.get_referrers()
