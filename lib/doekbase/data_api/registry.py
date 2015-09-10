"""
Description.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/21/15'

from doekbase.data_api.util import get_logger
from doekbase.data_api.util import log_start, log_end

# Logging

_log = get_logger('registry')

# Exceptions

class RegistryError(Exception):
    pass

class NamespaceNotFound(RegistryError):
    pass

class ClientTypeNotFound(RegistryError):
    pass

class ClientTypeNotAllowed(RegistryError):
    pass

# Constants

AVRO = 'avro'
GRPC = 'grpc'

# Classes and functions

class ClientRegistry(object):
    """Factory and registry.
    """
    allowed_types = (AVRO, GRPC)

    def __init__(self):
        self._ns = {}

    def list_client_types(self, ns):
        if ns not in self._ns:
            raise NamespaceNotFound(ns)
        return self._ns[ns].keys()

    def register(self, ns, client_type, client_class):
        t0 = log_start(_log, 'register_client')
        if client_type not in self.allowed_types:
            raise ClientTypeNotAllowed(str(client_type))
        if not ns in self._ns:
            self._ns[ns] = {}
        self._ns[ns][client_type] = client_class
        log_end(_log, t0, 'register_client')

    def get_client(self, ns, client_type, *args, **kwargs):
        if ns not in self._ns:
            raise NamespaceNotFound(ns)
        clients = self._ns[ns]
        if client_type not in clients:
            raise ClientTypeNotFound(str(client_type))
        # Create an instance of the registered class
        instance = clients[client_type](*args, **kwargs)
        return instance

# Modules are imported once, so a module var is a singleton
g_registry = ClientRegistry()