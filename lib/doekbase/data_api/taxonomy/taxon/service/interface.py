# Stdlib
import traceback

# Third-party
import zope.interface

from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# Local
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.data_api.taxonomy.taxon.service import thrift_service
from doekbase.data_api.taxonomy.taxon.service import thrift_client
from doekbase.data_api.taxonomy.taxon.service import ttypes

import doekbase.data_api.util

class TaxonClientConnection(object):
    """
    Provides a client connection to the running Taxon API service.
    """
    def __init__(self, host='localhost', port=9091):
        self.client = None
        self.transport = None
        self.protocol = None

        try:
            self.transport = THttpClient.THttpClient("http://" + host + ":" + str(port))
            self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
            self.client = thrift_client.Client(self.protocol)
        except TTransport.TTransportException as err:
            print('{}'.format(err.message))
            raise RuntimeError('Cannot connect to remote Thrift service at {}:{:d}'
                               .format(host, port))

    def get_client(self):
        return self.transport, self.client


class TaxonService:
    zope.interface.implements(thrift_service.Iface)

    def __init__(self, services=None):
        if services is None or not isinstance(services, dict):
            raise TypeError("You must provide a service configuration " +
                            "dictionary! Found {0}".format(type(services)))
        elif not services.has_key("workspace_service_url"):
            raise KeyError("Expecting workspace_service_url key!")
        
        self.services = services
        self.logger = doekbase.data_api.util.get_logger("TaxonService")

    def get_info(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            result = taxon_api.get_info()
            #if result["object_metadata"] is None:
            #    result["object_metadata"] = dict()

            return ttypes.ObjectInfo(**result)
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_info", {"ref": str(ref)})

    def get_history(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            result = taxon_api.get_history()

            self.logger.info(result)

            return [ttypes.ObjectInfo(**x) for x in result]
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_history", {"ref": str(ref)})

    def get_provenance(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            result =  taxon_api.get_provenance()

            self.logger.info(result)

            return [ttypes.ObjectProvenanceAction(**x) for x in result]
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_provenance", {"ref": str(ref)})

    def get_id(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_id()
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_id", {"ref": str(ref)})

    def get_name(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_name()
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_name", {"ref": str(ref)})

    def get_version(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_version()
        except Exception, e:
            raise ttypes.ServiceException(e.message, traceback.print_exc(), "get_version", {"ref": str(ref)})

    def get_parent(self, token=None, ref=None):
        try:
            taxon_api = TaxonAPI(self.services, token, ref)
            return taxon_api.get_parent(ref_only=True)
        except AttributeError, e:
            raise ttypes.AttributeException(e.message)
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

