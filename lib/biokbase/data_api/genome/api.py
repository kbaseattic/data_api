"""
Simple example client.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/13/15'

import sys
import spec_pb2 as pb
from biokbase.data_api.util import get_logger, Timer, logged

_log = get_logger('genome.api')

class GenomeAnnotationClient(object):
    def __init__(self, host='localhost', port=50051, timeout=300):
        self._host, self._port = host, port
        self._timeout = timeout # in seconds
        self._stub = pb.early_adopter_create_GenomeAnnotationAPI_stub(
            self._host, self._port)

    @logged(_log)
    def get(self, ref):
        with self._stub as stub:
            response = stub.get(pb.ObjRef(ref=ref), self._timeout)
            print('get: got response')
        print('returning')
        return response

    @logged(_log)
    def get_taxon(self, ref):
        with self._stub as stub:
            response = stub.get_taxon(pb.ObjRef(ref=ref), self._timeout)
            print('get_taxon: got response: {}'.format(response))
        print('return response')
        return response

def main(ref):
    client = GenomeAnnotationClient()
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