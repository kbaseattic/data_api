namespace py genome_annotation
namespace js genome_annotation
namespace perl DOEKBase.DataAPI.annotation.genome_annotation

/*
TODO - Automatically populate version from setup.py.
*/

const string VERSION = "{{version}}"

typedef string ObjectReference

exception ServiceException {
    1: required string message;
    2: optional string stacktrace;
    3: optional map<string,string> inputs;
}

exception AuthorizationException {
    1: required string message;
    2: optional string stacktrace;
}

exception AuthenticationException {
    1: required string message;
    2: optional string stacktrace;
}

exception ObjectReferenceException {
    1: required string message;
    2: optional string stacktrace;
}

exception AttributeException {
    1: required string message;
    2: optional string stacktrace;
}

exception TypeException {
    1: required string message;
    2: optional string stacktrace;
    3: optional list<string> valid_types;
}

struct Region {
    1: string contig_id;
    2: string strand;
    3: i64 start;
    4: i64 length;
}

struct Feature_id_filters {
    1: list<string> type_list = [];
    2: list<Region> region_list = [];
    3: list<string> function_list = [];
    4: list<string> alias_list = [];
}

struct Feature_id_mapping {
    1: map<string, list<string>> by_type = {};
    2: map<string, map<string, map<string, list<string>>>> by_region = {};
    3: map<string, list<string>> by_function ={};
    4: map<string, list<string>> by_alias = {};
}

struct Feature_data {
    1: string feature_id;
    2: string feature_type;
    3: string feature_function;
    4: map<string, list<string>> feature_aliases;
    5: i64 feature_dna_sequence_length;
    6: string feature_dna_sequence;
    7: string feature_md5;
    8: list<Region> feature_locations;
    9: list<string> feature_publications;
    10: list<string> feature_quality_warnings;
    11: list<string> feature_quality_score;
    12: string feature_notes;
    13: string feature_inference;
}

struct Protein_data {
    1: string protein_id;
    2: string protein_amino_acid_sequence;
    3: string protein_function;
    4: list<string> protein_aliases;
    5: string protein_md5;
    6: list<string> protein_domain_locations;
}

struct Exon_data {
    1: Region exon_location;
    2: string exon_dna_sequence;
    3: i64 exon_ordinal;
}

struct UTR_data {
    1: list<Region> utr_locations;
    2: string utr_dna_sequence;
}


service thrift_service {
    /**
     * Retrieve the Taxon associated with this GenomeAnnotation.
     *
     * @return Reference to TaxonAPI object
     */
    ObjectReference get_taxon(1:required string token,
                              2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the Assembly associated with this GenomeAnnotation.
     *
     * @return reference to AssemblyAPI object
     */
    ObjectReference get_assembly(1:required string token,
                                 2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the list of Feature types in this GenomeAnnotation.
     *
     * @return List of feature type identifiers (strings)
     */
    list<string> get_feature_types(1:required string token,
                                   2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the descriptions for each Feature type in
     * this GenomeAnnotation.
     *
     * @param feature_type_list List of Feature types. If this list is empty or None, then the whole mapping will be returned.
     * @return Name and description for each requested Feature Type
     */
    map<string,string> get_feature_type_descriptions(1:required string token,
                                                     2:required ObjectReference ref,
                                                     3:list<string> feature_type_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the count of each Feature type in this GenomeAnnotation.
     *
     * @param feature_type_list  List of Feature Types. If empty, will retrieve counts for all Feature Types.
     */
    map<string,i64> get_feature_type_counts(1:required string token,
                                            2:required ObjectReference ref,
                                            3:list<string> feature_type_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve Feature IDs in this GenomeAnnotation, optionally filtered by type, region, function, alias.
     *
     * @param filters Dictionary of filters that can be applied to contents. If this is empty or missing, all Feature IDs will be returned.
     * @param group_type How to group results, which is a single string matching one of the values for the ``filters`` parameter.
     * @return Result with values for requested `group_type` filled in under a key named for that group_type, which will be 'by_' plus the first token of the filter name, e.g. 'by_alias' for group_type 'alias_list'.
     */
    Feature_id_mapping get_feature_ids(1:required string token,
                                       2:required ObjectReference ref,
                                       3:Feature_id_filters filters,
                                       4:string group_type) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve Feature data available in this GenomeAnnotation.
     *
     */
    map<string, Feature_data> get_features(1:required string token,
                                           2:required ObjectReference ref,
                                           3:list<string> feature_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve Protein data available in this GenomeAnnotation.
     *
     */
    map<string, Protein_data> get_proteins(1:required string token,
                                           2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve Feature locations in this GenomeAnnotation.
     *
     */
    map<string, list<Region>> get_feature_locations(1:required string token,
                                                    2:required ObjectReference ref,
                                                    3:list<string> feature_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve Feature publications in this GenomeAnnotation.
     *
     */
    map<string,list<string>> get_feature_publications(1:required string token,
                                                      2:required ObjectReference ref,
                                                      3:list<string> feature_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve Feature DNA sequences in this GenomeAnnotation.
     *
     */
    map<string,string> get_feature_dna(1:required string token,
                                       2:required ObjectReference ref,
                                       3:list<string> feature_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve Feature functions in this GenomeAnnotation.
     *
     */
    map<string,string> get_feature_functions(1:required string token,
                                             2:required ObjectReference ref,
                                             3:list<string> feature_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve Feature aliases in this GenomeAnnotation.
     *
     */
    map<string,list<string>> get_feature_aliases(1:required string token,
                                                 2:required ObjectReference ref,
                                                 3:list<string> feature_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the CDS id for each Gene id in this GenomeAnnotation.
     *
     */
    map<string,list<string>> get_cds_by_gene(1:required string token,
                                             2:required ObjectReference ref,
                                             3:list<string> gene_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the CDS id for each mRNA id in this GenomeAnnotation.
     *
     */
    map<string,string> get_cds_by_mrna(1:required string token,
                                       2:required ObjectReference ref,
                                       3:list<string> mrna_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the Gene id for each CDS id in this GenomeAnnotation.
     *
     */
    map<string,string> get_gene_by_cds(1:required string token,
                                       2:required ObjectReference ref,
                                       3:list<string> cds_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the Gene id for each mRNA id in this GenomeAnnotation.
     *
     */
    map<string,string> get_gene_by_mrna(1:required string token,
                                        2:required ObjectReference ref,
                                        3:list<string> mrna_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the mRNA id for each CDS id in this GenomeAnnotation.
     *
     */
    map<string,string> get_mrna_by_cds(1:required string token,
                                       2:required ObjectReference ref,
                                       3:list<string> cds_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the mRNA id for each Gene id in this GenomeAnnotation.
     *
     */
    map<string, list<string>> get_mrna_by_gene(1:required string token,
                                               2:required ObjectReference ref,
                                               3:list<string> gene_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve Exon information for each mRNA id in this GenomeAnnotation.
     *
     */
    map<string, list<Exon_data>> get_mrna_exons(1:required string token,
                                                2:required ObjectReference ref,
                                                3:list<string> mrna_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve UTR information for each mRNA id in this GenomeAnnotation.
     *
     */
    map<string, map<string, UTR_data>> get_mrna_utrs(1:required string token,
                                                     2:required ObjectReference ref,
                                                     3:list<string> mrna_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception)

}
