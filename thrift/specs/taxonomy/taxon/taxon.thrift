namespace * taxon

/*
TODO - Automatically populate version from setup.py.
*/

const string VERSION = "{{version}}"

typedef string ObjectReference

struct ObjectInfo {
    1: i64 object_id;
    2: string object_name;
    3: string object_reference;
    4: string object_reference_versioned;
    5: string type_string;
    6: string save_date;
    7: i64 version;
    8: string saved_by;
    9: i64 workspace_id;
    10: string workspace_name;
    11: string object_checksum;
    12: i64 object_size;
    13: map<string,string> object_metadata;
}

typedef list<ObjectInfo> ObjectHistory

struct ExternalDataUnit {
    1: string resource_name;
    2: string resource_url;
    3: string resource_version;
    4: string resource_release_date;
    5: string data_url;
    6: string data_id;
    7: string description;
}

struct ObjectProvenanceAction {
    1: string time;
    2: string service_name;
    3: string service_version;
    4: string service_method;
    5: list<binary> method_parameters;
    6: string script_name;
    7: string script_version;
    8: string script_command_line;
    9: list<string> input_object_references;
    10: list<string> validated_object_references;
    11: list<string> intermediate_input_ids;
    12: list<string> intermediate_output_ids;
    13: list<ExternalDataUnit> external_data;
    14: string description;
}

typedef list<ObjectProvenanceAction> ObjectProvenance

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


service thrift_service {

    /**
     * Retrieve object info.
     *
     */
    ObjectInfo get_info(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve object history.
     *
     */
    ObjectHistory get_history(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve object provenance.
     *
     */
    ObjectProvenance get_provenance(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve object identifier.
     *
     */
    i64 get_id(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve object name.
     *
     */
    string get_name(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve object version.
     *
     */
    string get_version(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve parent Taxon.
     *
     */
    ObjectReference get_parent(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve children Taxon.
     *
     */
    list<ObjectReference> get_children(1:string token, 2:ObjectReference ref) throws (
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
    list<ObjectReference> get_genome_annotations(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the scientific lineage.
     *
     */
    list<string> get_scientific_lineage(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the scientific name.
     *
     */
    string get_scientific_name(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the taxonomic id.
     *
     */
    i32 get_taxonomic_id(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the kingdom.
     *
     */
    string get_kingdom(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the domain.
     *
     */
    string get_domain(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the genetic code.
     *
     */
    i32 get_genetic_code(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception),

    /**
     * Retrieve the aliases.
     *
     */
    list<string> get_aliases(1:string token, 2:ObjectReference ref) throws (
        1:ServiceException generic_exception,
        2:AuthorizationException authorization_exception,
        3:AuthenticationException authentication_exception,
        4:ObjectReferenceException reference_exception,
        5:AttributeException attribute_exception,
        6:TypeException type_exception)
}
