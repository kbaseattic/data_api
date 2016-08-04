namespace py genome_annotation
namespace js genome_annotation
namespace perl DOEKBase.DataAPI.annotation.genome_annotation

/*
TODO - Automatically populate version from setup.py.
*/

const string VERSION = "{{version}}"

typedef string ObjectReference

exception ServiceException {
    /** Readable message desribing the error condition. */
    1: required string message;
    /** Program stack trace */
    2: optional string stacktrace;
    /** Optional mapping */
    3: optional map<string,string> inputs;
}

exception AuthorizationException {
    /** Readable message desribing the error condition. */
    1: required string message;
    /** Program stack trace */
    2: optional string stacktrace;
}

exception AuthenticationException {
    /** Readable message desribing the error condition. */
    1: required string message;
    /** Program stack trace */
    2: optional string stacktrace;
}

exception ObjectReferenceException {
    /** Readable message desribing the error condition. */
    1: required string message;
    /** Program stack trace */
    2: optional string stacktrace;
}

exception AttributeException {
    /** Readable message desribing the error condition. */
    1: required string message;
    /** Program stack trace */
    2: optional string stacktrace;
}

exception TypeException {
    /** Readable message desribing the error condition. */
    1: required string message;
    /** Program stack trace */
    2: optional string stacktrace;
    /** List of types that would have been acceptable. */
    3: optional list<string> valid_types;
}

struct Region {
    /** The identifier for the contig to which this region corresponds. */
    1: string contig_id;
    /** Either a "+" or a "-", for the strand on which the region is located. */
    2: string strand;
    /** Starting position for this region. */
    3: i64 start;
    /** Distance from the start position that bounds the end of the region. */
    4: i64 length;
}

/**
 * Filters passed to :meth:`get_feature_ids`
 */
struct Feature_id_filters {
    /**
     * List of Feature type strings.
     */
    1: list<string> type_list = [];
    /**
     * List of region specs.
     * For example::
     *     [{"contig_id": str, "strand": "+"|"-",
     *       "start": int, "length": int},...]
     *
     * The Feature sequence begin and end are calculated as follows:
     *   - [start, start) for "+" strand
     *   - (start - length, start] for "-" strand
     */
    2: list<Region> region_list = [];
    /**
     * List of function strings.
     */
    3: list<string> function_list = [];
    /**
     *  List of alias strings.
     */
    4: list<string> alias_list = [];
}

struct Feature_id_mapping {
    /** Mapping of Feature type string to a list of Feature IDs */
    1: map<string, list<string>> by_type = {};
    /**
     * Mapping of contig ID, strand "+" or "-", and range "start--end" to
     * a list of Feature IDs. For example::
     *    {'contig1': {'+': {'123--456': ['feature1', 'feature2'] }}}
     */
    2: map<string, map<string, map<string, list<string>>>> by_region = {};
    /** Mapping of function string to a list of Feature IDs */
    3: map<string, list<string>> by_function ={};
    /** Mapping of alias string to a list of Feature IDs */
    4: map<string, list<string>> by_alias = {};
}

struct Feature_data {
    /** Identifier for this feature */
    1: string feature_id;
    /** The Feature type e.g., "mRNA", "CDS", "gene", ... */
    2: string feature_type;
    /** The functional annotation description */
    3: string feature_function;
    /** Dictionary of Alias string to List of source string identifiers */
    4: map<string, list<string>> feature_aliases;
    /** Integer representing the length of the DNA sequence for convenience */
    5: i64 feature_dna_sequence_length;
    /** String containing the DNA sequence of the Feature */
    6: string feature_dna_sequence;
    /** String containing the MD5 of the sequence, calculated from the uppercase string */
    7: string feature_md5;
    /**
     * List of dictionaries::
     *     { "contig_id": str,
     *       "start": int,
     *       "strand": str,
     *       "length": int  }
     *
     * List of Feature regions, where the Feature bounds are
     * calculated as follows:
     *
     * - For "+" strand, [start, start + length)
     * - For "-" strand, (start - length, start]
    */
    8: list<Region> feature_locations;
    /**
     * List of any known publications related to this Feature
     */
    9: list<string> feature_publications;
    /**
     * List of strings indicating known data quality issues.
     * Note: not used for Genome type, but is used for
     * GenomeAnnotation
     */
    10: list<string> feature_quality_warnings;
    /**
     * Quality value with unknown algorithm for Genomes,
     * not calculated yet for GenomeAnnotations.
     */
    11: list<string> feature_quality_score;
    /** Notes recorded about this Feature */
    12: string feature_notes;
    /** Inference information */
    13: string feature_inference;
}

struct Protein_data {
    /** Protein identifier, which is feature ID plus ".protein" */
    1: string protein_id;
    /** Amino acid sequence for this protein */
    2: string protein_amino_acid_sequence;
    /** Function of protein */
    3: string protein_function;
    /** List of aliases for the protein */
    4: list<string> protein_aliases;
    /** MD5 hash of the protein translation (uppercase) */
    5: string protein_md5;
    6: list<string> protein_domain_locations;
}

struct Exon_data {
    /** Location of the exon in the contig. */
    1: Region exon_location;
    /** DNA Sequence string. */
    2: string exon_dna_sequence;
    /** The position of the exon, ordered 5' to 3'. */
    3: i64 exon_ordinal;
}

struct UTR_data {
    /** Locations of this UTR */
    1: list<Region> utr_locations;
    /** DNA sequence string for this UTR */
    2: string utr_dna_sequence;
}

struct Summary_data {
    /** Scientific name of the organism. */
    1: string scientific_name;
    /** NCBI taxonomic id of the organism. */
    2: i64 taxonomy_id;
    /** Taxonomic kingdom of the organism. */
    3: string kingdom;
    /** Scientific lineage of the organism. */
    4: list<string> scientific_lineage;
    /** Scientific name of the organism. */
    5: byte genetic_code;
    /** Aliases for the organism associated with this GenomeAnnotation. */
    6: list<string> organism_aliases;
    /** Source organization for the Assembly. */
    7: string assembly_source;
    /** Identifier for the Assembly used by the source organization. */
    8: string assembly_source_id;
    /** Date of origin the source indicates for the Assembly. */
    9: string assembly_source_date;
    /** GC content for the entire Assembly. */
    10: double gc_content;
    /** Total DNA size for the Assembly. */
    11: i64 dna_size;
    /** Number of contigs in the Assembly. */
    12: i64 num_contigs;
    /** Contig identifier strings for the Assembly. */
    13: list<string> contig_ids;
    /** Name of the external source. */
    14: string external_source;
    /** Date of origin the external source indicates for this GenomeAnnotation. */
    15: string external_source_date;
    /** Release version for this GenomeAnnotation data. */
    16: string release;
    /** Name of the file used to generate this GenomeAnnotation. */
    17: string original_source_filename;
    /** Number of features of each type. */
    18: map<string, i64> feature_type_counts;
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
     * @return Reference to AssemblyAPI object
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
     * Retrieve the list of Feature types.
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
     * @param feature_type_list List of Feature types. If this list
     *  is empty or None,
     *  the whole mapping will be returned.
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
     * Retrieve the count of each Feature type.
     *
     * @param feature_type_list  List of Feature Types. If empty,
     *   this will retrieve  counts for all Feature Types.
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
     * Retrieve Feature IDs, optionally filtered by type, region, function, alias.
     *
     * @param filters Dictionary of filters that can be applied to contents.
     *   If this is empty or missing, all Feature IDs will be returned.
     * @param group_type How to group results, which is a single string matching one
     *   of the values for the ``filters`` parameter.
     * @return Grouped mapping of features.
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
     * Retrieve Feature data.
     *
     * @param feature_id_list List of Features to retrieve.
     *   If None, returns all Feature data.
     * @return Mapping from Feature IDs to dicts of available data.
     */
    map<string, Feature_data> get_features(1:required string token,
                                           2:required ObjectReference ref,
                                           3:list<string> feature_id_list,
                                           4:bool exclude_sequence) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve Protein data.
     *
     * @return Mapping from protein ID to data about the protein.
     */
    map<string, Protein_data> get_proteins(1:required string token,
                                           2:required ObjectReference ref,
                                           3:list<string> cds_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve Feature locations.
     *
     * @param feature_id_list List of Feature IDs for which to retrieve locations.
     *     If empty, returns data for all features.
     * @return Mapping from Feature IDs to location information for each.
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
     * Retrieve Feature publications.
     *
     * @param feature_id_list List of Feature IDs for which to retrieve publications.
     *     If empty, returns data for all features.
     * @return Mapping from Feature IDs to publication info for each.
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
     * Retrieve Feature DNA sequences.
     *
     * @param feature_id_list List of Feature IDs for which to retrieve sequences.
     *     If empty, returns data for all features.
     * @return Mapping of Feature IDs to their DNA sequence.
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
     * Retrieve Feature functions.
     *
     * @param feature_id_list List of Feature IDs for which to retrieve functions.
     *     If empty, returns data for all features.
     * @return Mapping of Feature IDs to their functions.
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
     * Retrieve Feature aliases.
     *
     * @param feature_id_list List of Feature IDS for which to retrieve aliases.
     *     If empty, returns data for all features.
     * @return Mapping of Feature IDs to a list of aliases.
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
     * Retrieves coding sequence Features (cds) for given gene Feature IDs.
     *
     * @param feature_id_list List of gene Feature IDS for which to retrieve CDS.
     *     If empty, returns data for all features.
     * @return Mapping of gene Feature IDs to a list of CDS Feature IDs.
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
     * Retrieves coding sequence (cds) Feature IDs for given mRNA Feature IDs.
     *
     * @param feature_id_list List of mRNA Feature IDS for which to retrieve CDS.
     *     If empty, returns data for all features.
     * @return Mapping of mRNA Feature IDs to a list of CDS Feature IDs.
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
     * Retrieves gene Feature IDs for given coding sequence (cds) Feature IDs.
     *
     * @param feature_id_list List of cds Feature IDS for which to retrieve gene IDs.
     *     If empty, returns all cds/gene mappings.
     * @return Mapping of cds Feature IDs to gene Feature IDs.
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
     * Retrieves gene Feature IDs for given mRNA Feature IDs.
     *
     * @param feature_id_list List of mRNA Feature IDS for which to retrieve gene IDs.
     *     If empty, returns all mRNA/gene mappings.
     * @return Mapping of mRNA Feature IDs to gene Feature IDs.
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
     * Retrieves mRNA Features for given coding sequences (cds) Feature IDs.
     *
     * @param feature_id_list List of cds Feature IDS for which to retrieve mRNA IDs.
     *     If empty, returns all cds/mRNA mappings.
     * @return Mapping of cds Feature IDs to mRNA Feature IDs.
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
     * Retrieve the mRNA IDs for given gene IDs.
     *
     * @param feature_id_list List of gene Feature IDS for which to retrieve mRNA IDs.
     *     If empty, returns all gene/mRNA mappings.
     * @return Mapping of gene Feature IDs to a list of mRNA Feature IDs.
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
     * Retrieve Exon information for each mRNA ID.
     *
     * @param feature_id_list List of mRNA Feature IDS for which to retrieve exons.
     *     If empty, returns data for all exons.
     * @return Mapping of mRNA Feature IDs to a list of exons (:js:data:`Exon_data`).
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
     * Retrieve UTR information for each mRNA Feature ID.
     *
     *  UTRs are calculated between mRNA features and corresponding CDS features.
     *  The return value for each mRNA can contain either:
     *     - no UTRs found (empty dict)
     *     -  5' UTR only
     *     -  3' UTR only
     *     -  5' and 3' UTRs
     *
     *  Note: The Genome data type does not contain interfeature
     *  relationship information. Calling this method for Genome objects
     *  will raise a :js:throws:`exc.TypeException`.
     *
     * @param feature_id_list List of mRNA Feature IDS for which to retrieve UTRs.
     * If empty, returns data for all UTRs.
     * @return Mapping of mRNA Feature IDs to a mapping that contains
     * both 5' and 3' UTRs::
     *     { "5'UTR": :js:data:`UTR_data`, "3'UTR": :js:data:`UTR_data` }
     */
    map<string, map<string, UTR_data>> get_mrna_utrs(1:required string token,
                                                     2:required ObjectReference ref,
                                                     3:list<string> mrna_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve a summary representation of this GenomeAnnotation.
     *
     * @return summary data
     */
    Summary_data get_summary(1:required string token,
                             2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve a summary representation of this GenomeAnnotation.
     *
     * @return summary data
     */
    bool save_summary(1:required string token,
                      2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception)
}
