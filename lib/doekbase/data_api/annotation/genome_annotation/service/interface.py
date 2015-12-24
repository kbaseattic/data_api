# Stdlib
import logging
import time
import traceback

# Third-party
import zope.interface

from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# Local
from doekbase.data_api import exceptions
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
from doekbase.data_api.annotation.genome_annotation.service import thrift_service
from doekbase.data_api.annotation.genome_annotation.service import thrift_client
from doekbase.data_api.annotation.genome_annotation.service import ttypes

import doekbase.data_api.util


_log = logging.getLogger('.'.join([__name__, 'service']))

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
            error = None
            _log.debug('method={meth} state=begin token={tok} ref={ref} args={'
                       'args} kwargs={kw}'
                       .format(meth=func.__name__, tok=token, ref=ref,
                               args=args, kw=kwargs))
            t0 = time.time()
            try:
                return func(self, token, ref, *args, **kwargs)
            except AttributeError, e:
                error = e
                raise ttypes.AttributeException(e.message, traceback.print_exc())
            except exceptions.AuthenticationError, e:
                error = e
                raise ttypes.AuthenticationException(e.message, traceback.print_exc())
            except exceptions.AuthorizationError, e:
                error = e
                raise ttypes.AuthorizationException(e.message, traceback.print_exc())
            except exceptions.TypeError, e:
                error = e
                raise ttypes.TypeException(e.message, traceback.print_exc())
            except Exception, e:
                error = e
                raise ttypes.ServiceException(e.message, traceback.print_exc(), {"ref": str(ref)})
            finally:
                if error is None:
                    _log.debug('method={meth} state=end token={tok} ref={ref} '
                               'args={args} kwargs={kw} dur={t:.3f}'
                               .format(meth=func.__name__, tok=token, ref=ref,
                                       args=args, kw=kwargs, t=time.time() - t0))
                else:
                    _log.error('method={meth} state=error token={tok} '
                               'ref={ref} args={args} kwargs={kw}'
                               'error_message="{m}" dur={t:.3f}'
                               .format(meth=func.__name__, tok=token, ref=ref,
                                       args=args, kw=kwargs, m=error.message,
                                       t=time.time() - t0))

        return wrapper

    def __init__(self, services=None):
        _log.debug('method=__init__ state=begin services={s}'
                  .format(s=services))
        try:
            if services is None or not isinstance(services, dict):
                raise TypeError("You must provide a service configuration " +
                                "dictionary! Found {0}".format(type(services)))
            elif not services.has_key("workspace_service_url"):
                raise KeyError("Expecting workspace_service_url key!")
        except Exception as e:
            _log.error('method=__init__ state=error services={s}'
                       'error_message="{m}"'
                      .format(s=services, m=e.message))
            raise
        self.services = services
        _log.debug('method=__init__ state=end services={s} '
                   .format(s=services))

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
    def get_feature_ids(self, token=None, ref=None, filters=None, group_by=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)

        converted_filters = dict()
        if filters is not None:
            if len(filters.type_list) > 0:
                converted_filters["type_list"] = filters.type_list

            if len(filters.region_list) > 0:
                converted_filters["region_list"] = [{"contig_id": x.contig_id,
                                                     "strand": x.strand,
                                                     "start": x.start,
                                                     "length": x.length}
                                                    for x in filters.region_list]
            if len(filters.function_list) > 0:
                converted_filters["function_list"] = filters.function_list

            if len(filters.alias_list) > 0:
                converted_filters["alias_list"] = filters.alias_list

        if group_by is None:
            group_by = "type"

        result = ga_api.get_feature_ids(filters=converted_filters, group_by=group_by)

        if "by_type" in result:
            output = ttypes.Feature_id_mapping(by_type=result["by_type"])
        elif "by_region" in result:
            output = ttypes.Feature_id_mapping(by_region=result["by_region"])
        elif "by_function" in result:
            output = ttypes.Feature_id_mapping(by_function=result["by_function"])
        elif "by_alias" in result:
            output = ttypes.Feature_id_mapping(by_alias=result["by_alias"])
        else:
            raise ttypes.TypeException("Unrecognized output {}".format(result.keys()))

        return output

    @server_method
    def get_features(self, token=None, ref=None, feature_id_list=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_features(feature_id_list)

        output = dict()
        for k,v in result.items():
            output[k] = ttypes.Feature_data(**v)
            output[k].feature_locations = [ttypes.Region(contig_id=r[0],
                                                         strand=r[2],
                                                         start=r[1],
                                                         length=r[3])
                                           for r in v["feature_locations"]]

        return output

    @server_method
    def get_proteins(self, token=None, ref=None):
        ga_api = GenomeAnnotationAPI(self.services, token, ref)
        result = ga_api.get_proteins()
        output = {x: ttypes.Protein_data(**result[x]) for x in result}

        return output

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
        output = {x: [ttypes.Region(**z) for z in result[x]] for x in result}

        return output

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
