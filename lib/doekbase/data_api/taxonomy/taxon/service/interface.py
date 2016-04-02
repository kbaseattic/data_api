# Stdlib
import logging

# Third-party
import zope.interface

# Local
from doekbase.data_api import service_core
from doekbase.data_api.service_core import server_method
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.data_api.taxonomy.taxon.service import thrift_service
from doekbase.data_api.taxonomy.taxon.service import thrift_client
from doekbase.data_api.taxonomy.taxon.service import ttypes

_log = logging.getLogger('.'.join([__name__, 'service']))

class TaxonClientConnection(service_core.BaseClientConnection):
    """Provides a client connection to the running Taxon API service.
    """
    def __init__(self, url="http://localhost:9101"):
        service_core.BaseClientConnection.__init__(self, thrift_client, url)


class TaxonService(service_core.BaseService):
    zope.interface.implements(thrift_service.Iface)

    def __init__(self, services=None):
        service_core.BaseService.__init__(self, _log, ttypes,
                                          TaxonAPI, services=services)

    @server_method
    def get_info(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        result = taxon_api.get_info()

        return ttypes.ObjectInfo(**result)

    @server_method
    def get_history(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        result = taxon_api.get_history()
        return [ttypes.ObjectInfo(**x) for x in result]

    @server_method
    def get_provenance(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        result =  taxon_api.get_provenance()
        return [ttypes.ObjectProvenanceAction(**x) for x in result]

    @server_method
    def get_id(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        return taxon_api.get_id()

    @server_method
    def get_name(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        return taxon_api.get_name()

    @server_method
    def get_version(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        return taxon_api.get_version()

    @server_method
    def get_parent(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        return taxon_api.get_parent(ref_only=True)

    @server_method
    def get_children(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        return taxon_api.get_children(ref_only=True)

    @server_method
    def get_genome_annotations(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        return taxon_api.get_genome_annotations(ref_only=True)

    @server_method
    def get_scientific_lineage(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        return taxon_api.get_scientific_lineage()

    @server_method
    def get_scientific_name(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        return taxon_api.get_scientific_name()

    @server_method
    def get_taxonomic_id(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        return taxon_api.get_taxonomic_id()

    @server_method
    def get_kingdom(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        return taxon_api.get_kingdom()

    @server_method
    def get_domain(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        return taxon_api.get_domain()

    @server_method
    def get_aliases(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        return taxon_api.get_aliases()

    @server_method
    def get_genetic_code(self, token=None, ref=None):
        taxon_api = self._get_instance(token, ref)
        return taxon_api.get_genetic_code()

