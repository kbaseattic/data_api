# Stdlib
import logging

# Third-party
import zope.interface

# Local
from doekbase.data_api import service_core
from doekbase.data_api.service_core import server_method
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
from doekbase.data_api.annotation.genome_annotation.service import thrift_service
from doekbase.data_api.annotation.genome_annotation.service import thrift_client
from doekbase.data_api.annotation.genome_annotation.service import ttypes


_log = logging.getLogger('.'.join([__name__, 'service']))

class GenomeAnnotationClientConnection(service_core.BaseClientConnection):
    """Provides a client connection to the running GenomeAnnotation API service.
    """
    def __init__(self, url="http://localhost:9103"):
        service_core.BaseClientConnection.__init__(self, thrift_client, url)


class GenomeAnnotationService(service_core.BaseService):
    zope.interface.implements(thrift_service.Iface)

    def __init__(self, services=None):
        service_core.BaseService.__init__(self, _log, ttypes,
                                          GenomeAnnotationAPI, services=services)

    @server_method
    def get_assembly(self, token=None, ref=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_assembly(ref_only=True)

        return result

    @server_method
    def get_taxon(self, token=None, ref=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_taxon(ref_only=True)
        return result

    @server_method
    def get_feature_types(self, token=None, ref=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_feature_types()
        return result

    @server_method
    def get_feature_type_descriptions(self, token=None, ref=None, type_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_feature_type_descriptions(type_list)
        return result

    @server_method
    def get_feature_type_counts(self, token=None, ref=None, type_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_feature_type_counts(type_list)
        return result

    @server_method
    def get_feature_ids(self, token=None, ref=None, filters=None, group_by=None):
        ga_api = self._get_instance(token, ref)

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
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_features(feature_id_list)

        output = dict()
        for k,v in result.items():
            output[k] = ttypes.Feature_data(**v)
            output[k].feature_locations = [ttypes.Region(**r)
                                           for r in v["feature_locations"]]

        return output

    @server_method
    def get_proteins(self, token=None, ref=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_proteins()
        output = {x: ttypes.Protein_data(**result[x]) for x in result}

        return output

    @server_method
    def get_feature_aliases(self, token=None, ref=None, feature_id_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_feature_aliases(feature_id_list)

        return result

    @server_method
    def get_feature_dna(self, token=None, ref=None, feature_id_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_feature_dna(feature_id_list)

        return result

    @server_method
    def get_feature_functions(self, token=None, ref=None, feature_id_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_feature_functions(feature_id_list)

        return result

    @server_method
    def get_feature_locations(self, token=None, ref=None, feature_id_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_feature_locations(feature_id_list)
        output = {x: [ttypes.Region(**z) for z in result[x]] for x in result}

        return output

    @server_method
    def get_feature_publications(self, token=None, ref=None, feature_id_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_feature_publications(feature_id_list)

        return result

    @server_method
    def get_cds_by_gene(self, token=None, ref=None, gene_id_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_cds_by_gene(gene_id_list)

        return result

    @server_method
    def get_cds_by_mrna(self, token=None, ref=None, mrna_id_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_cds_by_mrna(mrna_id_list)

        return result

    @server_method
    def get_gene_by_cds(self, token=None, ref=None, cds_id_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_gene_by_cds(cds_id_list)

        return result

    @server_method
    def get_gene_by_mrna(self, token=None, ref=None, mrna_id_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_gene_by_mrna(mrna_id_list)

        return result

    @server_method
    def get_mrna_by_cds(self, token=None, ref=None, cds_id_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_mrna_by_cds(cds_id_list)

        return result

    @server_method
    def get_mrna_by_gene(self, token=None, ref=None, gene_id_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_mrna_by_gene(gene_id_list)

        return result

    @server_method
    def get_mrna_exons(self, token=None, ref=None, mrna_id_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_mrna_exons(mrna_id_list)
        output = {}
        for mrna_id in result:
            output[mrna_id] = [
                ttypes.Exon_data(exon_location=ttypes.Region(**x["exon_location"]),
                                 exon_dna_sequence=x["exon_dna_sequence"],
                                 exon_ordinal=x["exon_ordinal"])\
                for x in result[mrna_id]
            ]

        return output

    @server_method
    def get_mrna_utrs(self, token=None, ref=None, mrna_id_list=None):
        ga_api = self._get_instance(token, ref)
        result = ga_api.get_mrna_utrs(mrna_id_list)
        output = {}
        for mrna_id in result:
            output[mrna_id] = {}
            for utr_id in result[mrna_id]:
                regions = result[mrna_id][utr_id]["utr_locations"]
                output[mrna_id][utr_id] = ttypes.UTR_data(
                    utr_locations=[ttypes.Region(**x) for x in regions],
                    utr_dna_sequence=result[mrna_id][utr_id]["utr_dna_sequence"])

        return output
