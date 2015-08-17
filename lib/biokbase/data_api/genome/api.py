"""
Simple example client.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/13/15'

import sys
import time
import spec_pb2 as pb

class Timer(object):
    def __init__(self):
        self._timings = []
        self._start = time.time()
    def __enter__(self):
        self._start = time.time()
    def __exit__(self, exc_type, exc_val, exc_tb):
        t = time.time()
        dt, self._start = t - self._start, t
        self._timings.append(dt)
    def pop(self):
        return self._timings.pop()


class GenomeAnnotationClient(object):
    def __init__(self, host='localhost', port=50051, timeout=300):
        self._stub = pb.early_adopter_create_GenomeAnnotationAPI_stub(
            host, port)
        self._timeout = timeout # in seconds

    def get(self, ref):
        response = self._stub.get(pb.ObjRef(ref=ref), self._timeout)
        return response.message


def main(ref):
    client = GenomeAnnotationClient()
    with Timer() as timer:
        gen_ann = client.get(ref)
    dt = timer.pop()
    print('{.3f}s  Got genome annotation {}, version={}'.format(
        dt, gen_ann.ident, gen_ann.version
    ))
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: {} <genome_reference>".format(sys.argv[0]))
        sys.exit(1)
    reference = sys.argv[1]
    sys.exit(main(reference))