#!/usr/bin/env python

def test_api_service(service_name='assembly',apiurl='http://localhost',token=None):
    try:
        if service_name == "taxon":
            #from doekbase.data_api.taxonomy.taxon.service import thrift_client
            from doekbase.data_api.taxonomy.taxon.api import TaxonClientAPI
            api = TaxonClientAPI(apiurl, token, None)
        elif service_name == "assembly":
            #from doekbase.data_api.sequence.assembly.service import thrift_client
            from doekbase.data_api.sequence.assembly.api import AssemblyClientAPI
            api = AssemblyClientAPI(apiurl, token, 'ReferenceGenomeAnnotations/kb|g.166819_assembly')
        else:
            raise Exception("Service not activated: {}".format(service_name))
    except:
        print '3 ' + service_name + '_api - UNKNOWN - could not load client library'

    if service_name == 'taxon':
        try:
            #lineage=client.get_scientific_lineage(token,'ReferenceTaxons/511145_taxon')
            print '3 ' + service_name + '_api - UNKNOWN - check not yet defined for ' + service_name
        except:
            print '2 ' + service_name + '_api - CRITICAL'

    if service_name == 'assembly':
        stats = api.get_stats()
        ref_num_contigs=21
        # would be better to be in a try block
        if stats['num_contigs']==ref_num_contigs:
            print '0 ' + service_name + '_api - OK - ' + str(ref_num_contigs) + ' contigs found'
        else:
            print '2 ' + service_name + '_api - CRITICAL - ' + str(stats['num_contigs']) + ' contigs found, not ' + str(ref_num_contigs)


if __name__ == "__main__":
    import os
    import sys
    import argparse

    # should argparse these
    service_name=sys.argv[1]
    apiurl=sys.argv[2]
    token=os.environ['KB_AUTH_TOKEN']
    test_api_service(service_name,apiurl,token)
