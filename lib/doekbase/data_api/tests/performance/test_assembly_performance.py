"""
Revised version of assembly performance tests.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '10/21/15'

# Imports

# System
import json
import os
import subprocess
import unittest

# Local
from doekbase.data_api.util import get_logger
#from doekbase.data_api.annotation import genome_annotation as ga_api
from doekbase.data_api.sequence import assembly as asm_api
from doekbase.data_api import cache
from doekbase.data_api.tests import shared
from doekbase.data_api.util import PerfCollector

# Logging

_log = get_logger(__name__)

# Global constants and variables

MB = 2 ** 20 * 1.0

g_redis_process = None


# Classes and functions

def calc_size(obj):
    """Return size of an object in megabytes.
    """
    return len(json.dumps(obj)) / MB

def control_redis(start=False, stop=False):
    """Start and/or stop Redis server.
    """
    global g_redis_process
    if stop:
        if g_redis_process:
            g_redis_process.terminate()
            g_redis_process.wait()
    if start:
        if not g_redis_process:
            g_redis_process = subprocess.Popen([shared.g_redis_bin,
                                                shared.g_redis_conf],
                                               close_fds=True)

def setup():
    shared.setup()

def set_redis(flag):
    global g_redis_process
    if flag:
        control_redis(start=True)
        cache.ObjectCache.cache_class = cache.RedisCache
        cache.ObjectCache.cache_params = {
            'redis_host': shared.g_redis_host,
            'redis_port': shared.g_redis_port}
    else:
        control_redis(stop=True)
        cache.ObjectCache.cache_class = cache.NullCache
        cache.ObjectCache.cache_params = {}

class TestPerformance(unittest.TestCase):

    def setUp(self):
        self.public_workspace_name = "testOriginalGenome"
        self.public_workspace_id = 641
        self.genomes_order = ["kb|g.244916", "kb|g.0", "kb|g.3899",
                             "kb|g.140106"]
        self.genomes = {"kb|g.244916": "641/5/1",
                       "kb|g.0": "641/2/1",
                       "kb|g.3899":  "641/7/1",
                       "kb|g.140106": "641/3/1"}
        self.fetch_contigs = {"kb|g.3899": ["kb|g.3899.c.2", "kb|g.3899.c.5"],
                             "kb|g.0": ["kb|g.0.c.1"],
                             "kb|g.244916": ["kb|g.244916.c.0"],
                             "kb|g.140106": ["kb|g.140106.c.0",
                                             "kb|g.140106.c.10",
                                             "kb|g.140106.c.100",
                                             "kb|g.140106.c.1000",
                                             "kb|g.140106.c.10000",
                                             "kb|g.140106.c.100000",
                                             "kb|g.140106.c.200000",
                                             "kb|g.140106.c.300000",
                                             "kb|g.140106.c.400000",
                                             "kb|g.140106.c.500000",
                                             "kb|g.140106.c.600000",
                                             "kb|g.140106.c.700000"]}

    def test_get_contigs(self):
        def print_stats(event):
            print('EVENT: {}'.format(str(event)))

        perf = PerfCollector('get_contigs')
        perf.add_observer('*', None, print_stats)

        for redis_flag in (False, True):
            set_redis(redis_flag)  # both redis server and config. in cache
            for genome, ref in self.genomes.items():
                # ga_obj = ga_api.GenomeAnnotationAPI(shared.get_services(),
                #                                     shared.token,
                #                                     ref)
                asm_obj = asm_api.AssemblyAPI(shared.get_services(),
                                              shared.token,
                                              ref)
                for type_, obj in (('assembly', asm_obj),):
                    for operation in ('ALL', 'SUBSET'):
                        event_key = '/'.join([genome, type_, operation])
                        perf.start_event('get_contigs', event_key)
                        if operation == 'ALL':
                            contigs = asm_obj.get_contigs()
                        else:
                            contig_list = self.fetch_contigs[genome]
                            contigs = asm_obj.get_contigs(contig_list)
                        perf.set_metadata({'redis': int(redis_flag),
                                           'op': operation,
                                           'size': calc_size(contigs),
                                           'genome': genome,
                                           'ref': ref})
                        perf.end_event('get_contigs', event_key)

