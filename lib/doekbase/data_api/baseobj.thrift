/*
 * Base object types and methods in Thrift
 *
 * Author: Dan Gunter <dkgunter@lbl.gov>
 * Date: 8/25/15
 *
*/

namespace * baseobj

const string VERSION = "0.0.1"

# Types
# -----

/**
 * Object reference.
 */
typedef string ObjectReference

/**
 * Default metadata for an object.
 */
struct Metadata {
    1: string object_id
    2: string object_name
    3: ObjectReference object_reference
    4: string object_reference_versioned
    5: string type_string
    6: string save_date
    7: string version
    8: string saved_by
    9: i64 workspace_id
    10: string workspace_name
    11: string object_checksum
    12: i64 object_size
    13: string object_metadata
}

/**
 * Object history.
 */
struct History {
    1: list<string> events
}

/**
 * List of object references.
 */
typedef list<ObjectReference> ObjectReferenceList

/**
 * Mapping of types to referrers.
 */
typedef map<string,ObjectReferenceList> Referrers

/**
 * Object provenance.
 */
struct Provenance {
    1: string where_i_came_from
}

/**
 * Untyped object data
 */
typedef binary RawData

/**
 * Authorization info
 */
struct AuthInfo {
    1: string token
}

# Methods
# -------

service thrift_service {

    /**
     * Initialize.
     */
    void init(1: AuthInfo auth),

    /**
     * Get basic object information.
     *
     * @param ref. Object to retrieve. This sets the object
     *             reference for subsequent operations.
     */
    Metadata get_info(1: ObjectReference ref),

    /**
     * Retrieve the schema associated with an object.
     */
    string get_schema(),

    /**
     * Retrieve the history.
     */
    History get_history(),

    /**
     * Retrieve the provenance.
     */
    Provenance get_provenance(),

    /**
      * Retrieve the list of referrers.
      */
    Referrers get_referrers(),

   /**
    * Retrieve the object data.
    */
    RawData get_data(),

   /**
    * Retrieve a subset of the object data.
    *
    * @param path_list. List of pths to the data elements.
    */
    RawData get_data_subset(1: list<string> path_list)

}
