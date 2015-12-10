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

struct Feature_tuple {
    1: string feature_type;
    2: string feature_id;
}

struct Feature_id_filters {
    1: list<string> type_list = [];
    2: list<Region> region_list = [];
    3: list<string> function_list = [];
    4: list<string> alias_list = [];
}

struct Feature_id_mapping {
    1: map<string, list<Feature_tuple>> by_type = empty;
    2: map<string, map<string, map<string, list<Feature_tuple>>>> by_region = empty;
    3: map<string, list<Feature_tuple>> by_function = empty;
    4: map<string, list<Feature_tuple>> by_alias = empty;
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
    12: list<string> feature_notes;
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

service thrift_service {
    /**
     * Retrieve the Taxon associated with this GenomeAnnotation.
     *
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
     * Retrieve the descriptions for each Feature type in this GenomeAnnotation.
     *
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
     * Retrieve Feature ids in this GenomeAnnotation, optionally filtered by type, region, function, alias.
     *
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
    map<string, map<string, list<Feature_data>>> get_features(1:required string token,
                                           2:required ObjectReference ref,
                                           3:list<Feature_tuple> feature_tuple_list) throws (
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
                                       3:list<string> gene_id_list) throws (
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
        6:TypeException type_exception)
}
