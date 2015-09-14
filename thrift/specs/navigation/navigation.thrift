namespace * navigation

const string VERSION = "0.1.0"

/*
 * Exceptions
 * ----------
 */

exception ServiceException {
    1: string message,
    2: string stacktrace,
    3: string method,
    4: map<string,string> inputs
}

exception AuthException {
    1: required string message,
    2: optional string stacktrace
}

/*
 * Data structures
 * ---------------
 */

/**
 * Version of an object.
 * May either be a number, as in Subversion,
 * or a string which would accommodate a hash, as in Git.
 *
 * @param seqno Numeric version
 * @param hash String version
 */
union ObjectVersion {
   1: i32 seqno,
   2: string hash
}

/** Object reference.
 * @param id Unique object identifier
 * @param version Object version
 */
struct ObjectReference {
    1: required string id,
    2: optional ObjectVersion version
}

/** Globally unique identifier. */
typedef string ContainerID

/** Scope-unique name. */
typedef string ContainerName

/** Null value for ContainerID. */
const ContainerID NOWHERE = ''

/** Null value for ContainerName. */
const ContainerName NONAME = ''

/** Date/time.
 * This is defined as the number of
 * _milliseconds_ since the UNIX epoch (1/1/1970).
 */
typedef i64 TimestampMs

/** A string search expression. */
typedef string SearchExpr

/**
 * Current state.
 * @param project The current project.
 * @param workspace The current workspace.
 */
struct Context {
  1: required Project project,
  2: required Workspace workspace
}

/**
 * A project container.
 *
 * @param id Unique identifier for the container
 * @param name Human-readable name for container (may not be unique)
 * @param created When the project was created
 * @param modified When the project was modified
 */
struct Project {
   1: required ContainerID id,
   2: optional ContainerName name,
   10: optional TimestampMs created,
   11: optional TimestampMs modified
}

/**
 * A workspace container.
 *
 * @param id Unique identifier for the container
 * @param name Human-readable name for container (may not be unique)
 * @param created When the workspace was created
 * @param modified When the workspace was modified
 */
 struct Workspace {
    1: required ContainerID id,
    2: optional ContainerName name,
   10: optional TimestampMs created,
   11: optional TimestampMs modified
 }

/**
 * Metadata about an object.
 *
 * @param ref Unique object reference
 * @param type Name of object type
 * @param name Human-readable name of the object (may not be unique)
 * @param created When the object was created
 * @param modified When the object was modified
 * @param size Size of serialized uncompressed object, in bytes
 */
struct Object {
    1: required ObjectReference ref,
    2: required string type,
    3: optional string name,
   10: optional TimestampMs created,
   11: optional TimestampMs modified,
   12: optional i64 size
}

/**
 * Filter for selecting objects.
 */
struct Filter {
    1: optional SearchExpr name,
    2: optional SearchExpr type,
    3: optional VersionExpr version,
    10: optional TimestampMs created_min,
    11: optional TimestampMs created_max,
    12: optional TimestampMs modified_min,
    13: optional TimestampMs modified_max,
    14: optional i64 size_min,
    15: optional i64 size_max,
}

/**
 * Expression to find version(s) of an object,
 * based either on a numeric sequence or
 * on match with a string ("hash").
 */
struct VersionExpr {
  1: optional ObjectVersion min_seqno,
  2: optional ObjectVersion max_seqno,
  3: string hash
}

/*
 * Service methods
 * ---------------
 */

service thrift_service {

    /**
     * Create and return a new Context.
     *
     * @param project Optional starting project, default is NONAME.
     * @param workspace Optional starting workspace, default is NONAME.
     * @return new Context
     * @throws ServiceException for permissions errors, etc.
     */
     Context
     create_context(1: ContainerName project = NONAME,
                    2: ContainerName workspace = NONAME)
      throws (1: ServiceException serr, 2: AuthException aerr)

    /**
     * Set current project within given Context.
     */
    void
    set_project(1: Context context,
                2: ContainerName project)
             throws (1: ServiceException serr, 2:AuthException aerr)
    /**
     * Set current workspace within given Context.
     */
    void
    set_workspace(1: Context context,
                  2: ContainerName workspace)
    throws (1: ServiceException serr, 2: AuthException aerr)

    /**
     * List selected objects within current context.
     * With no parameters, this lists all objects.
     */
    list<Object>
    list_objects(1: Context context,
                 2: Filter filter)
    throws (1: ServiceException serr)

    /**
     * Find objects, optionally within a given Context.
     * With no parameters, this finds all objects in all contexts.
     */
    map<Context,list<Object>>
    find_objects(1: Context context,
                 2: Filter project_filter,
                 3: Filter workspace_filter,
                 4: Filter object_filter)
    throws (1: ServiceException serr)

    /**
     * Copy object from its current context to another.
     */
     void
     copy_object(1: required ObjectReference ref,
                 2: required Context destination)
     throws (1: ServiceException serr, 2: AuthException aerr)

    /**
     * Move object from its current context to another.
     * Object is no longer in the source context.
     */
     void
     move_object(1: required ObjectReference ref,
                 2: required Context destination)
     throws (1: ServiceException serr, 2: AuthException aerr)

    /**
     * Delete object.
     */
     void
     delete_object(1: required ObjectReference ref)
     throws (1: ServiceException serr, 2: AuthException aerr)

}