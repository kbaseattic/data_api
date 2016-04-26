namespace py assembly
namespace js assembly
namespace perl DOEKBase.DataAPI.sequence.assembly

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

/**
 * Derived statistical information about an assembly.
 */
struct AssemblyStats {
    /** Total number of contiguous sequences. */
    1: i64 num_contigs;
    /** Total length of all dna sequences. */
    2: i64 dna_size;
    /** Proportion of guanine (G) and cytosine (C) content. */
    3: double gc_content;
}

/**
 * Metadata about the external source of this Assembly.
 */
struct AssemblyExternalSourceInfo {
    /** Name of the external source */
    1: string external_source;
    /** Identifier of external source */
    2: string external_source_id;
    /** Origination date of external source */
    3: string external_source_origination_date;
}

struct AssemblyContig {
    /** Contig ID */
    1: string contig_id;
    /** Actual contents of the sequence for this contig */
    2: string sequence;
    /** Length of the contig */
    3: i64 length;
    /** GC proportion for the contig */
    4: double gc_content;
    /** Hex-digest of MD5 hash of the contig's contents */
    5: string md5;
    /** Name of the contig */
    6: string name;
    /** Description of the contig */
    7: string description;
    /** True if this contig is complete, False otherwise */
    8: bool is_complete;
    /** True if this contig is circular, False otherwise */
    9: bool is_circular;
}


service thrift_service {
    /**
     * Retrieve Assembly ID.
     */
    string get_assembly_id(1:required string token,
                           2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve associated GenomeAnnotation objects.
     *
     * @return List of GenomeAnnotation object references
     *
     */
    list<ObjectReference> get_genome_annotations(1:required string token,
                                                 2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the external source information for this Assembly.
     *
     * @return Metadata about the external source
     */
    AssemblyExternalSourceInfo get_external_source_info(1:required string token,
                                                        2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the derived statistical information about this Assembly.
     *
     */
    AssemblyStats get_stats(1:required string token,
                            2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the number of contigs for this Assembly.
     *
     * @return Total number of contiguous sequences.
     */
    i64 get_number_contigs(1:required string token,
                           2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the total GC content for this Assembly.
     *
     * @return Proportion of GC content, between 0 and 1.
     */
    double get_gc_content(1:required string token,
                          2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the total DNA size for this Assembly.
     *
     * @return Total DNA size
     */
    i64 get_dna_size(1:required string token,
                     2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the contig identifiers for this Assembly.
     *
     * @return List of contig IDs.
     */
    list<string> get_contig_ids(1:required string token,
                                2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the lengths of the contigs in this Assembly.
     *
     * @return Mapping of contig ID to contig length.
     */
    map<string, i64> get_contig_lengths(1:required string token,
                                        2:required ObjectReference ref,
                                        3:list<string> contig_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the gc content for contigs in this Assembly.
     *
     * @return Mapping of contig IDs to GC content proportion.
     */
    map<string, double> get_contig_gc_content(1:required string token,
                                              2:required ObjectReference ref,
                                              3:list<string> contig_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve all the data for the contigs in this Assembly.
     *
     * @return Mapping of contig ID to details for that contig.
     */
    map<string, AssemblyContig> get_contigs(1:required string token,
                                            2:required ObjectReference ref,
                                            3:list<string> contig_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Get reference to FASTA data
     */
    ObjectReference to_fasta(1:required string token,
                             2:required ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception)

}
