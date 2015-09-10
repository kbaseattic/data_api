# Stdlib
import abc

# Third-party

# Local
from doekbase.data_api.core import ObjectAPI
from doekbase.data_api.simple.service.interface import SimpleTypeClientConnection

# KBase types this API will wrap
TYPES = ['MyNamespace.SimpleType']


class SimpleTypeInterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_property(self):
        """
        Retrieve specific property of the SimpleType.

        Returns:
          string"""
        pass

    @abc.abstractmethod
    def get_count(self):
        """
        Retrieve a count of some values from the SimpleType.

        Returns:
          int"""
        pass


class SimpleTypeAPI(ObjectAPI, SimpleTypeInterface):
    """
    Local module implementation.
    """
    def __init__(self, ref=None, token=None):
        super(SimpleTypeAPI, self).__init__(services, ref, token)

        self._data = self.get_data()["property"]

    def get_property(self):
        return self._data["property"]

    def get_count(self):
        return len(self._data["values"])


class SimpleTypeClientAPI(object, SimpleTypeInterface):
    """
    Service client implementation.
    """
    def __init__(self, host='localhost', port=9090, ref=None, token=None):
        self.host = host
        self.port = port
        self.transport, self.client = SimpleTypeClientConnection(host, port).get_client()
        self.ref = ref
        self._token = token

    def get_property(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_property(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_count(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_count(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()
