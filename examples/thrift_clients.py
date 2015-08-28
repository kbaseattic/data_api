"""
Example Thrift clients.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/25/15'

# Import

# Stdlib
import argparse
import json
import sys
import time
# Third-party
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
# Local
from biokbase.data_api.baseobj import thrift_service
from biokbase.data_api.baseobj.ttypes import *
from biokbase.data_api.baseobj.api import ObjectAPI

def connect(host='localhost', port=9090):
    client = None
    try:
        # Make socket
        transport = TSocket.TSocket(host, port)
        # Buffering is critical. Raw sockets are very slow
        transport = TTransport.TBufferedTransport(transport)
        # Wrap in a protocol
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        # Create a client to use the protocol encoder
        client = thrift_service.Client(protocol)
        # Connect!
        transport.open()
    except Thrift.TException as err:
        print('{}'.format(err.message))
        raise RuntimeError('Cannot connect to remote Thrift service at {}:{:d}'
                           .format(host, port))
    return transport, client

def get_object():
    ap = argparse.ArgumentParser()
    ap.add_argument('ref', help='Object reference ID, e.g. 1019/4/1')
    ap.add_argument('--host', dest='host', default='localhost',
                    metavar='ADDR', help='Remote server host '
                                         '(default=%(default)s)')
    ap.add_argument('--port', dest='port', default=9090,
                    metavar='PORT', help='Remote server port '
                                         '(default=%(default)d)')
    args = ap.parse_args()
    kw = {'host': args.host, 'port': args.port}

    transport, client = connect(**kw)
    api = ObjectAPI(client, args.ref)
    print('{}'.format(api))  # dump default
    print("Getting data..")
    t0 = time.time()
    d = api.data
    dt = time.time() - t0
    print("Got and parsed data in {:g} seconds".format(dt))
    f = open('thrift_data.json', 'w')
    json.dump(d, f)
    f.close()
    print("Dumped data to: {}".format(f.name))

    # Close!
    transport.close()

if __name__ == '__main__':
    get_object() # XXX: choose one with top-level args
    sys.exit(0)