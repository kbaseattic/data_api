# Stdlib
import traceback

# Third-party
import zope.interface

from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# Local
from doekbase.data_api import exceptions
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.data_api.taxonomy.taxon.service import thrift_service
from doekbase.data_api.taxonomy.taxon.service import thrift_client
from doekbase.data_api.taxonomy.taxon.service import ttypes

import doekbase.data_api.util

_log = doekbase.data_api.util.get_logger("TaxonService")

class TaxonClientConnection(object):
    """
    Provides a client connection to the running Taxon API service.
    """
    def __init__(self, url="http://localhost:9101"):
        self.client = None
        self.transport = None
        self.protocol = None

        try:
            self.transport = THttpClient.THttpClient(url)
            self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
            #self.client = thrift_client.Client(self.protocol)
            self.client = thrift_client.Client(self.transport,
                                               TBinaryProtocol.TBinaryProtocolFactory())
        except TTransport.TTransportException as err:
            raise RuntimeError('Cannot connect to remote Thrift service at {}: {}'
                               .format(url, err.message))

    def get_client(self):
        return self.transport, self.client


class TaxonService:
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
        self.logger = doekbase.data_api.util.get_logger("TaxonService")

    @server_method
    def get_info(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        result = taxon_api.get_info()

        return ttypes.ObjectInfo(**result)

    @server_method
    def get_history(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        result = taxon_api.get_history()

        self.logger.info(result)

        return [ttypes.ObjectInfo(**x) for x in result]

    @server_method
    def get_provenance(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        result =  taxon_api.get_provenance()

        self.logger.info(result)

        return [ttypes.ObjectProvenanceAction(**x) for x in result]

    @server_method
    def get_id(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        return taxon_api.get_id()

    @server_method
    def get_name(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        return taxon_api.get_name()

    @server_method
    def get_version(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        return taxon_api.get_version()

    @server_method
    def get_parent(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        return taxon_api.get_parent(ref_only=True)

    @server_method
    def get_children(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        return taxon_api.get_children(ref_only=True)

    @server_method
    def get_genome_annotations(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        return taxon_api.get_genome_annotations(ref_only=True)

    @server_method
    def get_scientific_lineage(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        return taxon_api.get_scientific_lineage()

    @server_method
    def get_scientific_name(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        return taxon_api.get_scientific_name()

    @server_method
    def get_taxonomic_id(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        return taxon_api.get_taxonomic_id()

    @server_method
    def get_kingdom(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        return taxon_api.get_kingdom()

    @server_method
    def get_domain(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        return taxon_api.get_domain()

    @server_method
    def get_aliases(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        return taxon_api.get_aliases()

    @server_method
    def get_genetic_code(self, token=None, ref=None):
        taxon_api = TaxonAPI(self.services, token, ref)
        return taxon_api.get_genetic_code()

