# Stdlib
import traceback

# Third-party
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# Local
import thrift_service, ttypes
from doekbase.data_api.simple.api import SimpleTypeAPI

class SimpleTypeClientConnection(object):
    def __init__(self, host=None, port=None):
        self.client = None
        self.transport = None

        try:
            # Make socket
            socket = TSocket.TSocket(host, port)
            # Buffering is critical. Raw sockets are very slow
            self.transport = TTransport.TBufferedTransport(socket)
            # Wrap in a protocol
            protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
            # Create a client to use the protocol encoder
            self.client = thrift_service.Client(protocol)
        except Thrift.TException as err:
            print('{}'.format(err.message))
            raise RuntimeError('Cannot connect to remote Thrift service at {}:{:d}'
                               .format(host, port))

    def get_client(self):
        return self.transport, self.client


class SimpleTypeService(thrift_service.Iface):
    def __init__(self, config):
        # any necessary setup when the service starts

    def get_property(self, token=None, ref=None):
        try:
            simple_object = SimpleTypeAPI(self.services, ref, token)
            return simple_object.get_property(ref_only=True)
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_property", {"ref": str(ref)})

    def get_count(self, token=None, ref=None):
        try:
            simple_object = SimpleTypeAPI(self.services, ref, token)
            return simple_object.get_count(ref_only=True)
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_count", {"ref": str(ref)})