#!/usr/bin/env python

# Stdlib
import argparse
import os
import sys
import time

# Third-party

# Local
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationClientAPI

def test_client():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', default='ReferenceGenomeAnnotations/kb|g.166819',
                    help='Object reference ID, e.g. 1019/4/1')
    ap.add_argument('--url', dest='url', default='http://localhost:9103',
                    metavar='URL', help='Remote server url '
                                         '(default=%(default)s)')
    args = ap.parse_args()

    api = GenomeAnnotationClientAPI(args.url, os.environ["KB_AUTH_TOKEN"], args.ref)

    print("Getting data..")

    t0 = time.time()
    taxon_ref = api.get_taxon()
    dt = time.time() - t0
    print taxon_ref
    print("Got and parsed data from get_taxon in {:g} seconds".format(dt))

    t0 = time.time()
    assembly_ref = api.get_assembly()
    dt = time.time() - t0
    print assembly_ref
    print("Got and parsed data from get_assembly in {:g} seconds".format(dt))

    t0 = time.time()
    feature_types = api.get_feature_types()
    dt = time.time() - t0
    print feature_types
    print("Got and parsed data from get_feature_types() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_type_descriptions = api.get_feature_type_descriptions()
    dt = time.time() - t0
    print feature_type_descriptions
    print("Got and parsed data from get_feature_type_descriptions() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_type_counts = api.get_feature_type_counts()
    dt = time.time() - t0
    print feature_type_counts
    print("Got and parsed data from get_feature_type_counts() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_ids = api.get_feature_ids(filters={"type_list": ["CDS"]})
    dt = time.time() - t0
    print feature_ids["by_type"]["CDS"][0:2]
    print("Got and parsed data from get_feature_ids() in {:g} seconds".format(dt))

    locations = api.get_feature_locations(feature_ids["by_type"]["CDS"][0:2])
    regions = list()
    for x in locations:
        regions.extend(locations[x])

    t0 = time.time()
    feature_ids = api.get_feature_ids(filters={"region_list": regions}, group_by="region")
    dt = time.time() - t0
    print feature_ids["by_region"].items()[0]
    print("Got and parsed data from get_feature_ids() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_ids = api.get_feature_ids(filters={"function_list": ["protein"]}, group_by="function")
    dt = time.time() - t0
    print feature_ids["by_function"].items()[0]
    print("Got and parsed data from get_feature_ids() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_ids = api.get_feature_ids(filters={"alias_list": ["29216","93082"]}, group_by="alias")
    dt = time.time() - t0
    print feature_ids["by_alias"]
    print("Got and parsed data from get_feature_ids() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_ids = api.get_feature_ids(group_by="type")
    dt = time.time() - t0
    print feature_ids.keys()
    print("Got and parsed data from get_feature_ids() in {:g} seconds".format(dt))

    t0 = time.time()
    features = api.get_features(feature_ids["by_type"]["CDS"][0:2])
    dt = time.time() - t0
    print features
    print("Got and parsed data from get_features() in {:g} seconds".format(dt))

    t0 = time.time()
    proteins = api.get_proteins()
    dt = time.time() - t0
    print proteins.items()[0]
    print("Got and parsed data from get_proteins() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_locations = api.get_feature_locations(feature_ids["by_type"]["CDS"][0:2])
    dt = time.time() - t0
    print feature_locations
    print("Got and parsed data from get_feature_locations() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_dna = api.get_feature_dna(feature_ids["by_type"]["CDS"][0:2])
    dt = time.time() - t0
    print feature_dna
    print("Got and parsed data from get_feature_dna() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_functions = api.get_feature_functions(feature_ids["by_type"]["CDS"][0:2])
    dt = time.time() - t0
    print feature_functions
    print("Got and parsed data from get_feature_functions() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_aliases = api.get_feature_aliases(feature_ids["by_type"]["CDS"][0:2])
    dt = time.time() - t0
    print feature_aliases
    print("Got and parsed data from get_feature_aliases() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_pubs = api.get_feature_publications(feature_ids["by_type"]["CDS"][0:2])
    dt = time.time() - t0
    print feature_pubs
    print("Got and parsed data from get_feature_publications() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_ids_cds = api.get_cds_by_mrna(feature_ids["by_type"]["mRNA"][0:2])
    dt = time.time() - t0
    print feature_ids_cds
    print("Got and parsed data from get_cds_by_mrna() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_ids_mrna = api.get_mrna_by_cds(feature_ids["by_type"]["CDS"][0:2])
    dt = time.time() - t0
    print feature_ids_mrna
    print("Got and parsed data from get_mrna_by_cds() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_ids_gene = api.get_gene_by_cds(feature_ids["by_type"]["CDS"][0:2])
    dt = time.time() - t0
    print feature_ids_gene
    print("Got and parsed data from get_gene_by_cds() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_ids_gene = api.get_gene_by_mrna(feature_ids["by_type"]["mRNA"][0:2])
    dt = time.time() - t0
    print feature_ids_gene
    print("Got and parsed data from get_gene_by_mrna() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_ids_cds = api.get_cds_by_gene(feature_ids["by_type"]["gene"][0:2])
    dt = time.time() - t0
    print feature_ids_cds
    print("Got and parsed data from get_cds_by_gene() in {:g} seconds".format(dt))

    t0 = time.time()
    feature_ids_mrna = api.get_mrna_by_gene(feature_ids["by_type"]["gene"][0:2])
    dt = time.time() - t0
    print feature_ids_mrna
    print("Got and parsed data from get_mrna_by_gene() in {:g} seconds".format(dt))

if __name__ == '__main__':
    test_client() # XXX: choose one with top-level args
    sys.exit(0)