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

typedef string ObjectReference

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
 * @param created When the project was created
 * @param modified When the project was modified
 */
struct Project {
   1: required ContainerID id,
   2: optional ContainerName name
}

/**
 * A workspace container.
 *
 * @param id Unique identifier for the container
 * @param created When the workspace was created
 * @param modified When the workspace was modified
 */
 struct Workspace {
    1: requred ContainerID id,
    2: optional ContainerName name,
   10: optional TimestampMs created,
   11: optional TimestampMs modified
 }

/**
 * Metadata about an object.
 *
 * @param ref Unique object reference
 * @param type Name of object type
 * @param name Name of the object itself
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
    3: optional i64 size_min,
    4: optional i64 size_max,
    5: optional TimestampMs created_min,
    6: optional TimestampMs created_max,
    5: optional TimestampMs modified_min,
    6: optional TimestampMs modified_max
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
     create_context(1: optional ContainerName project = NONAME,
                    2: optional ContainerName workspace = NONAME)
     throws (ServiceException, AuthException)

    /**
     * Set current project within given Context.
     */
    void
    set_project(1: required Context context,
                     2: required ContainerName project)
             throws (ServiceException, AuthException)
    /**
     * Set current workspace within given Context.
     */
    void
    set_workspace(1: required Context context,
                  2: required ContainerName workspace)
    throws (ServiceException, AuthException)

    /**
     * List selected objects within current context.
     * With no parameters, this lists all objects.
     */
    list<Object>
    list_objects(1: required Context context,
                 2: optional Filter filter)
    throws (ServiceException)

    /**
     * Find objects, optionally within a given Context.
     * With no parameters, this finds all objects in all contexts.
     */
    map<Context,list<Object>>
    find_objects(1: optional Context context,
                 2: optional Filter project_filter,
                 3: optional Filter workspace_filter,
                 4: optional Filter object_filter)
    throws (ServiceException)

    /**
     * Copy object from its current context to another.
     */
     void
     copy_object(1: required ObjectReference ref,
                 2: required Context destination)
     throws (ServiceException, AuthException)

    /**
     * Move object from its current context to another.
     * Object is no longer in the source context.
     */
     void
     move_object(1: required ObjectReference ref,
                 2: required Context destination)
     throws (ServiceException, AuthException)

    /**
     * Delete object.
     */
     void
     delete_object(1: required ObjectReference ref)
     throws (ServiceException, AuthException)

}