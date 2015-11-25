#!/usr/bin/env python

# Stdlib
import argparse
import os
import sys
import time

# Third-party

# Local
from doekbase.data_api.sequence.assembly.api import AssemblyClientAPI

def test_client():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', default='PrototypeReferenceGenomes/kb|g.166819_assembly', help='Object reference ID, e.g. 1019/4/1')
    ap.add_argument('--url', dest='url', default='http://localhost:9102',
                    metavar='URL', help='Remote server url '
                                         '(default=%(default)s)')
    args = ap.parse_args()

    token='';
    if os.environ.has_key('KB_AUTH_TOKEN'):
        token = os.environ['KB_AUTH_TOKEN']

    api = AssemblyClientAPI(args.url, token, args.ref)

    print("Getting data..")

    t0 = time.time()
    assembly_id = api.get_assembly_id()
    dt = time.time() - t0
    print assembly_id
    print("Got and parsed data from get_assembly_id in {:g} seconds".format(dt))

    t0 = time.time()
    annotations = api.get_genome_annotations()
    dt = time.time() - t0
    print annotations
    print("Got and parsed data from get_genome_annotations in {:g} seconds".format(dt))

    t0 = time.time()
    external_info = api.get_external_source_info()
    dt = time.time() - t0
    print external_info
    print("Got and parsed data from get_external_source_info in {:g} seconds".format(dt))

    t0 = time.time()
    stats = api.get_stats()
    dt = time.time() - t0
    print stats
    print("Got and parsed data from get_stats in {:g} seconds".format(dt))

    t0 = time.time()
    num_contigs = api.get_number_contigs()
    dt = time.time() - t0
    print num_contigs
    print("Got and parsed data from get_number_contigs in {:g} seconds".format(dt))

    t0 = time.time()
    gc_content = api.get_gc_content()
    dt = time.time() - t0
    print gc_content
    print("Got and parsed data from get_gc_content in {:g} seconds".format(dt))

    t0 = time.time()
    dna_size = api.get_dna_size()
    dt = time.time() - t0
    print dna_size
    print("Got and parsed data from get_dna_size in {:g} seconds".format(dt))

    t0 = time.time()
    contig_ids = api.get_contig_ids()
    dt = time.time() - t0
    print contig_ids
    print("Got and parsed data from get_contig_ids in {:g} seconds".format(dt))

    t0 = time.time()
    contig_lengths = api.get_contig_lengths()
    dt = time.time() - t0
    print contig_lengths
    print("Got and parsed data from get_contig_lengths in {:g} seconds".format(dt))

    t0 = time.time()
    contig_gc_content = api.get_contig_gc_content()
    dt = time.time() - t0
    print contig_gc_content
    print("Got and parsed data from get_contig_gc_content in {:g} seconds".format(dt))

    t0 = time.time()
    contigs = api.get_contigs()
    dt = time.time() - t0
    print contigs
    print("Got and parsed data from get_contigs in {:g} seconds".format(dt))


if __name__ == '__main__':
    test_client() # XXX: choose one with top-level args
    sys.exit(0)