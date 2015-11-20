#!/usr/bin/env python

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.protocol import TJSONProtocol
from thrift.transport import THttpClient
import os
import sys


def test_api_service(service_name='assembly',apiurl='http://localhost',token=None):
    try:
        if service_name == "taxon":
            from doekbase.data_api.taxonomy.taxon.service import thrift_client
        elif service_name == "assembly":
            from doekbase.data_api.sequence.assembly.service import thrift_client
        else:
            raise Exception("Service not activated: {}".format(service_name))
    except:
        print '3 ' + service_name + '_api - UNKNOWN - could not load client library'

    transport=THttpClient.THttpClient(apiurl)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    client = thrift_client.Client(protocol)

    transport.open()

    if service_name == 'taxon':
        try:
            #lineage=client.get_scientific_lineage(token,'ReferenceTaxons/511145_taxon')
            print '3 ' + service_name + '_api - UNKNOWN - check not yet defined for ' + service_name
        except:
            print '2 ' + service_name + '_api - CRITICAL'

    if service_name == 'assembly':
        stats = client.get_stats(os.environ['KB_AUTH_TOKEN'],'PrototypeReferenceGenomes/kb|g.166819_assembly')
        if stats.num_contigs==21:
            print '0 ' + service_name + '_api - OK - 21 contigs found'

if __name__ == "__main__":
    # should argparse these
    service_name=sys.argv[1]
    apiurl=sys.argv[2]
    token=os.environ['KB_AUTH_TOKEN']
    test_api_service(service_name,apiurl,token)
