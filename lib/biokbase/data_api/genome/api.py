"""
Simple example client.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/13/15'

# Imports

# Stdlib
import abc
import sys
# Third-party
import spec_pb2 as pb
# Local
from biokbase.data_api.util import get_logger
from biokbase.data_api.util import log_start, log_end

# Logging

_log = get_logger('genome.api')

# Exceptions

class APIError(Exception):
    pass

class ClientTypeNotFound(APIError):
    pass

class ClientTypeNotAllowed(APIError):
    pass

# Constants

CLIENT_TYPE_AVRO = 'avro'
CLIENT_TYPE_GRPC = 'grpc'

# Classes and functions

class GenomeAnnotationClient:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get(self, ref):
        pass

    @abc.abstractmethod
    def get_taxon(self, ref):
        pass

# TODO: move this up a level
class ClientRegistry(object):
    """Factory and registry."""

    def __init__(self, allowed_types):
        self._clients = {}
        self._allowed_types = allowed_types

    def list_client_types(self):
        return self._clients.keys()

    def register(self, client_type, client_class):
        t0 = log_start(_log, 'register_client')
        assert issubclass(client_class, GenomeAnnotationClient)
        if client_type not in self._allowed_types:
            raise ClientTypeNotAllowed(str(client_type))
        self._clients[client_type] = client_class
        log_end(_log, t0, 'register_client')

    def get_client(self, client_type, *args, **kwargs):
        if client_type not in self._clients:
            raise ClientTypeNotFound(str(client_type))
        return self._clients[client_type](*args, **kwargs)

genome_annotation_clients = ClientRegistry((
    CLIENT_TYPE_AVRO, CLIENT_TYPE_GRPC))

