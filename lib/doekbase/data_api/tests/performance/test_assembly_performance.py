"""
Revised version of assembly performance tests.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '10/21/15'

# Imports

# System
import csv
import json
import logging
import os
import subprocess
import time
import unittest
# Third-party
import redis
# Local
from doekbase.data_api.util import get_logger
from doekbase.data_api.annotation import genome_annotation as ga_api
#from doekbase.data_api.sequence import assembly as asm_api
from doekbase.data_api import cache
from doekbase.data_api.tests import shared
from doekbase.data_api.util import PerfCollector

# Logging

_log = get_logger(__name__)
_log.setLevel(logging.DEBUG)

# Global constants and variables

g_redis_process = None


# Classes and functions

def setup():
    shared.setup()

def teardown():
    shared.teardown()
    control_redis(stop=True)

# ----------------------------------------------------

def calc_size(obj):
    """Return size of an object in bytes.
    """
    return len(json.dumps(obj))

def control_redis(start=False, stop=False):
    """Start and/or stop Redis server.
    """
    global g_redis_process
    if stop:
        if g_redis_process:
            _log.info('Stopping Redis server')
            g_redis_process.terminate()
            g_redis_process.wait()
        else:
            _log.info('Stop Redis server: Redis server not running')
    if start:
        if not g_redis_process:
            _log.info('Starting Redis server')
            g_redis_process = subprocess.Popen([shared.g_redis_bin,
                                                shared.g_redis_conf],
                                               close_fds=True)
            wait_for_redis_to_start(shared.services["redis_host"], shared.services["redis_port"])
        else:
            _log.info('Start Redis server: Redis server already running')

def wait_for_redis_to_start(host, port):
    max_wait = 5
    elapsed = 0
    success = False
    while not success and (elapsed < max_wait):
        try:
            redis.Redis(host=host, port=port).ping()
            success = True
        except redis.ConnectionError:
            time.sleep(0.1)
            elapsed += 0.1
    if not success:
        raise RuntimeError("Cannot connect to Redis")

def set_redis(flag):
    """Set Redis to on/off.

    Assumes Redis server is not already running.

    Args:
      flag (bool): True is on, False is off
    """
    global g_redis_process
    if flag:
        control_redis(start=True)
        cache.ObjectCache.cache_class = cache.RedisCache
        cache.ObjectCache.cache_params = {
            'redis_host': shared.services["redis_host"],
            'redis_port': shared.services["redis_port"]}
    else:
        control_redis(stop=True)
        cache.ObjectCache.cache_class = cache.NullCache
        cache.ObjectCache.cache_params = {}

class WriteNow(object):
    """Flush all writes to underlying stream immediately.
    """
    def __init__(self, strm):
        self._stream = strm

    def write(self, *args, **kwargs):
        r = self._stream.write(*args, **kwargs)
        self._stream.flush()
        return r

# ----------------------------------------------------

g_travis = shared.in_travis()
g_nocache = shared.get_services()["redis_host"] is None

@unittest.skipIf(g_travis, "Do not run in TravisCI")
@unittest.skipIf(g_nocache, "Do not run if caching is disabled")
class TestPerformance(unittest.TestCase):

    def setUp(self):
        self.public_workspace_name = "testOriginalGenome"
        self.public_workspace_id = 641
        self.genomes_order = ["kb|g.244916", "kb|g.0", "kb|g.3899",
                             "kb|g.140106"]
        self.genomes = {'kb|g.166819': '1013/340/4'}
        self.fetch_contigs = {'kb|g.166819': ['kb|g.166819.c.{:d}'.format(i)
                              for i in (2, 5)]}
        opath = __name__ + '.csv'
        opath = os.path.realpath(opath)
        ofile = WriteNow(open(opath, 'w'))
        _log.info('Writing CSV output to: {}'.format(opath))
        self.csv_out = csv.writer(ofile)

    def test_get_contigs(self):

        self.csv_out.writerow(['ts', 'event', 'dur.sec', 'data.sec',
                               'op', 'sz.bytes', 'redis', 'cache', 'id'])
        def print_stats(event, pevent):
            #print('Completed: {}'.format(str(event)))
            md = pevent.metadata  # alias
            row = [pevent.start, event, pevent.duration, md['get_data'],
                   md['op'], md['size'], md['redis'], md['cached'],
                   md['genome']]
            self.csv_out.writerow(row)

        perf = PerfCollector('get_contigs')
        perf.add_observer('*', None, print_stats)

        warmed_up = False

        for redis_flag in (False, True, True):
            set_redis(redis_flag)  # both redis server and config. in cache
            for genome, ref in self.genomes.items():
                ga_obj = ga_api.GenomeAnnotationAPI(
                    shared.get_services(),
                    shared.token,
                    ref)
                print("@@ REDIS={}".format(redis_flag))
                asm_obj = ga_obj.get_assembly()
                for type_, obj in (('assembly', asm_obj),):
                    for operation in ('SUBSET', 'ALL'):
                        event_key = '/'.join([genome, type_, operation])

                        perf.start_event('get_contigs', event_key)

                        if operation == 'ALL':
                            _log.debug('Get all contigs')
                            contigs = asm_obj.get_contigs()
                            nc = 0  # all
                            # timing of last get_data() call
                            get_data_sec = asm_obj.stats.get_event(
                                'ObjectAPI.get_data', limit=1)[0].duration
                        else:
                            contig_list = self.fetch_contigs[genome]
                            nc = len(contig_list)
                            _log.debug('Get {:d} contigs'.format(nc))
                            contigs = asm_obj.get_contigs(contig_list)
                            # timing of last get_data() call
                            get_data_sec = asm_obj.stats.get_event(
                                'ObjectAPI.get_data', limit=1)[0].duration

                        cached = 1 if (redis_flag and warmed_up) else 0

                        perf.set_metadata({'redis': redis_flag,
                                           'cached': cached,
                                           'op': operation,
                                           'size': calc_size(contigs),
                                           'genome': genome,
                                           'num_contigs': nc,
                                           'ref': ref,
                                           'get_data': get_data_sec})
                        perf.end_event('get_contigs', event_key)

            warmed_up = redis_flag
