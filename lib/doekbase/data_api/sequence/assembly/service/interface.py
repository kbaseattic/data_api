# Stdlib
import logging

# Third-party
import zope.interface

# Local
from doekbase.data_api import service_core
from doekbase.data_api.service_core import server_method
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.sequence.assembly.service import thrift_service
from doekbase.data_api.sequence.assembly.service import thrift_client
from doekbase.data_api.sequence.assembly.service import ttypes

_log = logging.getLogger('.'.join([__name__, 'service']))

class AssemblyClientConnection(service_core.BaseClientConnection):
    """Provides a client connection to the running Assembly API service.
    """
    def __init__(self, url="http://localhost:9102"):
        service_core.BaseClientConnection.__init__(self, thrift_client, url)

class AssemblyService(service_core.BaseService):
    zope.interface.implements(thrift_service.Iface)

    def __init__(self, services=None):
        service_core.BaseService.__init__(self, _log, ttypes,
                                          AssemblyAPI, services=services)

    @server_method
    def get_assembly_id(self, token=None, ref=None):
        assembly_api = self._get_instance(token, ref)
        result = assembly_api.get_assembly_id()

        return result

    @server_method
    def get_genome_annotations(self, token=None, ref=None):
        assembly_api = self._get_instance(token, ref)
        result = assembly_api.get_genome_annotations(ref_only=True)

        return result

    @server_method
    def get_external_source_info(self, token=None, ref=None):
        assembly_api = self._get_instance(token, ref)
        result = assembly_api.get_external_source_info()

        return ttypes.AssemblyExternalSourceInfo(**result)

    @server_method
    def get_stats(self, token=None, ref=None):
        assembly_api = self._get_instance(token, ref)
        result = assembly_api.get_stats()

        return ttypes.AssemblyStats(**result)

    @server_method
    def get_number_contigs(self, token=None, ref=None):
        assembly_api = self._get_instance(token, ref)
        result = assembly_api.get_number_contigs()

        return result

    @server_method
    def get_gc_content(self, token=None, ref=None):
        assembly_api = self._get_instance(token, ref)
        result = assembly_api.get_gc_content()

        return result

    @server_method
    def get_dna_size(self, token=None, ref=None):
        assembly_api = self._get_instance(token, ref)
        result = assembly_api.get_dna_size()

        return result

    @server_method
    def get_contig_ids(self, token=None, ref=None):
        assembly_api = self._get_instance(token, ref)
        result = assembly_api.get_contig_ids()

        return result

    @server_method
    def get_contig_lengths(self, token=None, ref=None, contig_id_list=None):
        assembly_api = self._get_instance(token, ref)

        if contig_id_list is None:
            result = assembly_api.get_contig_lengths()
        else:
            result = assembly_api.get_contig_lengths(contig_id_list)

        return result

    @server_method
    def get_contig_gc_content(self, token=None, ref=None, contig_id_list=None):
        assembly_api = self._get_instance(token, ref)

        if contig_id_list is None:
            result = assembly_api.get_contig_gc_content()
        else:
            result = assembly_api.get_contig_gc_content(contig_id_list)

        return result

    @server_method
    def get_contigs(self, token=None, ref=None, contig_id_list=None):
        assembly_api = self._get_instance(token, ref)

        if contig_id_list is None:
            result = assembly_api.get_contigs()
        else:
            result = assembly_api.get_contigs(contig_id_list)

        return {x: ttypes.AssemblyContig(**result[x]) for x in result}

