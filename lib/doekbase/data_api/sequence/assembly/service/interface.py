# Stdlib
import traceback

# Third-party
import zope.interface

from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# Local
from doekbase.data_api import exceptions
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.sequence.assembly.service import thrift_service
from doekbase.data_api.sequence.assembly.service import thrift_client
from doekbase.data_api.sequence.assembly.service import ttypes

import doekbase.data_api.util

class AssemblyClientConnection(object):
    """
    Provides a client connection to the running Assembly API service.
    """
    def __init__(self, url="http://localhost:9102"):
        self.client = None
        self.transport = None
        self.protocol = None

        try:
            self.transport = THttpClient.THttpClient(url)
            self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
            self.client = thrift_client.Client(self.protocol)
        except TTransport.TTransportException as err:
            raise RuntimeError('Cannot connect to remote Thrift service at {}: {}'
                               .format(url, err.message))

    def get_client(self):
        return self.transport, self.client


class AssemblyService:
    zope.interface.implements(thrift_service.Iface)

    def server_method(func):
        def wrapper(self, token, ref, *args, **kwargs):
            try:
                return func(self, token, ref, *args, **kwargs)
            except AttributeError, e:
                raise ttypes.AttributeException(e.message, traceback.print_exc())
            except exceptions.AuthenticationError, e:
                raise ttypes.AuthenticationException(e.message, traceback.print_exc())
            except exceptions.AuthorizationError, e:
                raise ttypes.AuthorizationException(e.message, traceback.print_exc())
            except exceptions.TypeError, e:
                raise ttypes.TypeException(e.message, traceback.print_exc())
            except Exception, e:
                raise ttypes.ServiceException(e.message, traceback.print_exc(), {"ref": str(ref)})
        return wrapper

    def __init__(self, services=None):
        if services is None or not isinstance(services, dict):
            raise TypeError("You must provide a service configuration " +
                            "dictionary! Found {0}".format(type(services)))
        elif not services.has_key("workspace_service_url"):
            raise KeyError("Expecting workspace_service_url key!")

        self.services = services
        self.logger = doekbase.data_api.util.get_logger("AssemblyService")

    @server_method
    def get_assembly_id(self, token=None, ref=None):
        assembly_api = AssemblyAPI(self.services, token, ref)
        result = assembly_api.get_assembly_id()

        return result

    @server_method
    def get_genome_annotations(self, token=None, ref=None):
        assembly_api = AssemblyAPI(self.services, token, ref)
        result = assembly_api.get_genome_annotations(ref_only=True)

        return result

    @server_method
    def get_external_source_info(self, token=None, ref=None):
        assembly_api = AssemblyAPI(self.services, token, ref)
        result = assembly_api.get_external_source_info()

        return ttypes.AssemblyExternalSourceInfo(**result)

    @server_method
    def get_stats(self, token=None, ref=None):
        assembly_api = AssemblyAPI(self.services, token, ref)
        result = assembly_api.get_stats()

        return ttypes.AssemblyStats(**result)

    @server_method
    def get_number_contigs(self, token=None, ref=None):
        assembly_api = AssemblyAPI(self.services, token, ref)
        result = assembly_api.get_number_contigs()

        return result

    @server_method
    def get_gc_content(self, token=None, ref=None):
        assembly_api = AssemblyAPI(self.services, token, ref)
        result = assembly_api.get_gc_content()

        return result

    @server_method
    def get_dna_size(self, token=None, ref=None):
        assembly_api = AssemblyAPI(self.services, token, ref)
        result = assembly_api.get_dna_size()

        return result

    @server_method
    def get_contig_ids(self, token=None, ref=None):
        assembly_api = AssemblyAPI(self.services, token, ref)
        result = assembly_api.get_contig_ids()

        return result

    @server_method
    def get_contig_lengths(self, token=None, ref=None, contig_id_list=None):
        assembly_api = AssemblyAPI(self.services, token, ref)

        if contig_id_list is None:
            result = assembly_api.get_contig_lengths()
        else:
            result = assembly_api.get_contig_lengths(contig_id_list)

        return result

    @server_method
    def get_contig_gc_content(self, token=None, ref=None, contig_id_list=None):
        assembly_api = AssemblyAPI(self.services, token, ref)

        if contig_id_list is None:
            result = assembly_api.get_contig_gc_content()
        else:
            result = assembly_api.get_contig_gc_content(contig_id_list)

        return result

    @server_method
    def get_contigs(self, token=None, ref=None, contig_id_list=None):
        assembly_api = AssemblyAPI(self.services, token, ref)

        if contig_id_list is None:
            result = assembly_api.get_contigs()
        else:
            result = assembly_api.get_contigs(contig_id_list)

        return {x: ttypes.AssemblyContig(**result[x]) for x in result}

