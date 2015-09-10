"""
Description.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/20/15'

import spec_pb2 as pb
from doekbase.data_api.util import get_logger
from doekbase.data_api.util import log_start, log_end
from doekbase.data_api.genome import api

_log = get_logger('genome.api.grpc_client')

class GenomeAnnotationGrpc(api.GenomeAnnotationClient):
    def __init__(self, host='localhost',
                 port=50051, timeout=300):
        self._host, self._port = host, port
        self._timeout = timeout  # in seconds
        self._stub = pb.early_adopter_create_GenomeAnnotationAPI_stub(
            self._host, self._port)
        super(GenomeAnnotation_grpc, self).__init__()

    def get(self, ref):
        log_start(_log, 'get')
        with self._stub as stub:
            response = stub.get(pb.ObjRef(ref=ref), self._timeout)
            print('get: got response: {}'.format(response))
        log_end(_log, 'get')
        return response

    def get_taxon(self, ref):
        log_start(_log, 'get_taxon')
        with self._stub as stub:
            response = stub.get_taxon(pb.ObjRef(ref=ref), self._timeout)
            print('get_taxon: got response: {}'.format(response))
        log_end(_log, 'get_taxon')
        return response

api.genome_annotation_clients.register(api.CLIENT_TYPE_GRPC,
                                       GenomeAnnotationGrpc)

def main(ref):
    client = api.genome_annotation_clients.get_client('grpc')
    gen_ann = client.get(ref)
    print('got annotation')
    print('Got genome annotation id={} version={}'.format(
        gen_ann.ident, gen_ann.version.version
    ))
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: {} <genome_reference>".format(sys.argv[0]))
        sys.exit(1)
    reference = sys.argv[1]
    sys.exit(main(reference))