#!/usr/bin/env python

# Stdlib
import argparse
import os
import sys
import time

# Third-party

# Local
from doekbase.data_api.taxonomy.taxon.api import TaxonClientAPI

def test_client():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', default='ReferenceTaxons/242159_taxon', help='Object reference ID, e.g. 1019/4/1')
    ap.add_argument('--url', dest='url', default='http://localhost:9101',
                    metavar='URL', help='Remote server url '
                                         '(default=%(default)s)')
    args = ap.parse_args()

    token='';
    if os.environ.has_key('KB_AUTH_TOKEN'):
        token = os.environ['KB_AUTH_TOKEN']

    api = TaxonClientAPI(args.url, token, args.ref)

    print("Getting data..")

    t0 = time.time()
    object_info = api.get_info()
    dt = time.time() - t0
    print object_info
    print("Got and parsed data from get_info in {:g} seconds".format(dt))

    t0 = time.time()
    history = api.get_history()
    dt = time.time() - t0
    print history
    print("Got and parsed data from get_history in {:g} seconds".format(dt))

    t0 = time.time()
    provenance = api.get_provenance()
    dt = time.time() - t0
    print provenance
    print("Got and parsed data from get_provenance in {:g} seconds".format(dt))

    t0 = time.time()
    id = api.get_id()
    dt = time.time() - t0
    print id
    print("Got and parsed data from get_id in {:g} seconds".format(dt))

    t0 = time.time()
    name = api.get_name()
    dt = time.time() - t0
    print name
    print("Got and parsed data from get_name in {:g} seconds".format(dt))

    t0 = time.time()
    version = api.get_version()
    dt = time.time() - t0
    print version
    print("Got and parsed data from get_version in {:g} seconds".format(dt))

    t0 = time.time()
    genetic_code = api.get_genetic_code()
    dt = time.time() - t0
    print genetic_code
    print("Got and parsed data from get_genetic_code in {:g} seconds".format(dt))

    t0 = time.time()
    aliases = api.get_aliases()
    dt = time.time() - t0
    print aliases
    print("Got and parsed data from get_aliases in {:g} seconds".format(dt))

    t0 = time.time()
    domain = api.get_domain()
    dt = time.time() - t0
    print domain
    print("Got and parsed data from get_domain in {:g} seconds".format(dt))

    try:
        t0 = time.time()
        kingdom = api.get_kingdom()
        dt = time.time() - t0
        print kingdom
        print("Got and parsed data from get_kingdom in {:g} seconds".format(dt))
    except:
        pass

    t0 = time.time()
    taxonomic_id = api.get_taxonomic_id()
    dt = time.time() - t0
    print taxonomic_id
    print("Got and parsed data from get_taxonomic_id in {:g} seconds".format(dt))

    t0 = time.time()
    scientific_lineage = api.get_scientific_lineage()
    dt = time.time() - t0
    print scientific_lineage
    print("Got and parsed data from get_scientific_lineage in {:g} seconds".format(dt))

    t0 = time.time()
    genome_annotations = api.get_genome_annotations()
    dt = time.time() - t0
    print genome_annotations
    print("Got and parsed data from get_genome_annotations in {:g} seconds".format(dt))

    t0 = time.time()
    parent = api.get_parent()
    dt = time.time() - t0
    print parent
    print("Got and parsed data from get_parent in {:g} seconds".format(dt))

    t0 = time.time()
    children = api.get_children()
    dt = time.time() - t0
    print children
    print("Got and parsed data from get_children in {:g} seconds".format(dt))


if __name__ == '__main__':
    test_client() # XXX: choose one with top-level args
    sys.exit(0)
