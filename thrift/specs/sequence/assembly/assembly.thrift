namespace * assembly

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

struct AssemblyStats {
    1: i64 num_contigs;
    2: i64 dna_size;
    3: double gc_content;
}

struct AssemblyExternalSourceInfo {
    1: string external_source;
    2: string external_source_id;
    3: string external_source_origination_date;
}

struct AssemblyContig {
    1: string contig_id;
    2: string sequence;
    3: i64 length;
    4: double gc_content;
    5: string md5;
    6: string name;
    7: string description;
    8: bool is_complete;
    9: bool is_circular;
}


service thrift_service {
    /**
     * Retrieve Assembly identifier string.
     *
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
     * Retrieve the Assembly stats.
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
     */
    map<string, i64> get_contig_gc_content(1:required string token,
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
     */
    map<string, AssemblyContig> get_contigs(1:required string token,
                                            2:required ObjectReference ref,
                                            3:list<string> contig_id_list) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception)
}
