namespace * taxon

const string VERSION = "0.0.1"

typedef string ObjectReference

exception ServiceException {
    1: string message;
    2: string stacktrace;
    3: string method;
    4: map<string,string> inputs;
}

service thrift_service {

    /**
     * Retrieve parent Taxon.
     *
     */
    ObjectReference get_parent(1:string token, 2:ObjectReference ref) throws (1:ServiceException failure),

    /**
     * Retrieve children Taxon.
     *
     */
    list<ObjectReference> get_children(1:string token, 2:ObjectReference ref) throws (1:ServiceException failure),

    /**
     * Retrieve associated GenomeAnnotation objects.
     *
     */
    list<ObjectReference> get_genome_annotations(1:string token, 2:ObjectReference ref) throws (1:ServiceException failure),

    /**
     * Retrieve the scientific lineage.
     *
     */
    string get_scientific_lineage(1:string token, 2:ObjectReference ref) throws (1:ServiceException failure),

    /**
     * Retrieve the scientific name.
     *
     */
    string get_scientific_name(1:string token, 2:ObjectReference ref) throws (1:ServiceException failure),

    /**
     * Retrieve the taxonomic id.
     *
     */
    i32 get_taxonomic_id(1:string token, 2:ObjectReference ref) throws (1:ServiceException failure),

    /**
     * Retrieve the kingdom.
     *
     */
    string get_kingdom(1:string token, 2:ObjectReference ref) throws (1:ServiceException failure),

    /**
     * Retrieve the domain.
     *
     */
    string get_domain(1:string token, 2:ObjectReference ref) throws (1:ServiceException failure),

    /**
     * Retrieve the genetic code.
     *
     */
    byte get_genetic_code(1:string token, 2:ObjectReference ref) throws (1:ServiceException failure),

    /**
     * Retrieve the aliases.
     *
     */
    list<string> get_aliases(1:string token, 2:ObjectReference ref) throws (1:ServiceException failure)
}
