# Stdlib
import traceback

# Third-party
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# Local
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.data_api.taxonomy.taxon.service import thrift_service
from doekbase.data_api.taxonomy.taxon.service import ttypes

class TaxonClientConnection(object):
    """
    Provides a client connection to the running Taxon API service.
    """
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


class TaxonService(thrift_service.Iface):
    def __init__(self, services=None):
        if services is None or type(services) != type({}):
            raise TypeError("You must provide a service configuration " +
                            "dictionary! Found {0}".format(type(services)))
        elif not services.has_key("workspace_service_url"):
            raise KeyError("Expecting workspace_service_url key!")
        
        self.services = services

    def get_parent(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_parent(ref_only=True)
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_parent", {"ref": str(ref)})

    def get_children(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_children(ref_only=True)
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_children", {"ref": str(ref)})

    def get_genome_annotations(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_genome_annotations(ref_only=True)
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_genome_annotation", {"ref": str(ref)})

    def get_scientific_lineage(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_scientific_lineage()
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_scientific_lineage", {"ref": str(ref)})

    def get_scientific_name(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_scientific_name()
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_scientific_name", {"ref": str(ref)})

    def get_taxonomic_id(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_taxonomic_id()
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_taxonomic_id", {"ref": str(ref)})

    def get_kingdom(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_kingdom()
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_kingdom", {"ref": str(ref)})

    def get_domain(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_domain()
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_domain", {"ref": str(ref)})

    def get_aliases(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_aliases()
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_aliases", {"ref": str(ref)})

    def get_genetic_code(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_genetic_code()
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_genetic_code", {"ref": str(ref)})

