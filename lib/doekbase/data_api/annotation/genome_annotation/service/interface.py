# Stdlib
import traceback

# Third-party
import zope.interface

from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# Local
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
from doekbase.data_api.annotation.genome_annotation.service import thrift_service
from doekbase.data_api.annotation.genome_annotation.service import thrift_client
from doekbase.data_api.annotation.genome_annotation.service import ttypes

import doekbase.data_api.util

_log = doekbase.data_api.util.get_logger("GenomeAnnotationService")

class GenomeAnnotationClientConnection(object):
    """
    Provides a client connection to the running GenomeAnnotation API service.
    """
    def __init__(self, url="http://localhost:9103"):
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


class GenomeAnnotationService:
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
        self.logger = doekbase.data_api.util.get_logger("GenomeAnnotationService")

    @server_method
    def get_assembly(self, token=None, ref=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_assembly(ref_only=True)

        return result

    @server_method
    def get_taxon(self, token=None, ref=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_taxon(ref_only=True)

        return result

    @server_method
    def get_feature_types(self, token=None, ref=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_feature_types()

        return result

    @server_method
    def get_feature_type_descriptions(self, token=None, ref=None, type_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_feature_type_descriptions(type_list)

        return result

    @server_method
    def get_feature_type_counts(self, token=None, ref=None, type_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_feature_type_counts(type_list)

        return result

    @server_method
    def get_feature_ids(self, token=None, ref=None,
                        type_list=None, region_list=None, function_list=None, alias_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_feature_ids(type_list=type_list, region_list=region_list,
                                        function_list=function_list, alias_list=alias_list)

        _log.info(result)

        return result

    @server_method
    def get_features(self, token=None, ref=None, feature_id_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_features(feature_id_list)

        return result

    @server_method
    def get_proteins(self, token=None, ref=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_proteins()

        return result

    @server_method
    def get_feature_aliases(self, token=None, ref=None, feature_id_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_feature_aliases(feature_id_list)

        return result

    @server_method
    def get_feature_dna(self, token=None, ref=None, feature_id_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_feature_dna(feature_id_list)

        return result

    @server_method
    def get_feature_functions(self, token=None, ref=None, feature_id_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_feature_functions(feature_id_list)

        return result

    @server_method
    def get_feature_locations(self, token=None, ref=None, feature_id_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_feature_locations(feature_id_list)

        return result

    @server_method
    def get_feature_publications(self, token=None, ref=None, feature_id_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_feature_publications(feature_id_list)

        return result

    @server_method
    def get_cds_by_gene(self, token=None, ref=None, gene_id_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_cds_by_gene(gene_id_list)

        return result

    @server_method
    def get_cds_by_mrna(self, token=None, ref=None, mrna_id_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_cds_by_mrna(mrna_id_list)

        return result

    @server_method
    def get_gene_by_cds(self, token=None, ref=None, cds_id_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_gene_by_cds(cds_id_list)

        return result

    @server_method
    def get_gene_by_mrna(self, token=None, ref=None, mrna_id_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_gene_by_mrna(mrna_id_list)

        return result

    @server_method
    def get_mrna_by_cds(self, token=None, ref=None, cds_id_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_mrna_by_cds(cds_id_list)

        return result

    @server_method
    def get_mrna_by_gene(self, token=None, ref=None, gene_id_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_mrna_by_gene(gene_id_list)

        return result
