# Use the namespace "simple" for all languages
namespace * simple

# CONSTANTS
const string VERSION = "0.0.1"

# TYPES
typedef string ObjectReference

# EXCEPTIONS
exception ServiceException {
    1: string message;
    2: string stacktrace;
    3: string method;
    4: map<string,string> inputs;
}

# METHODS
service thrift_service {

    /**
     * Retrieve property from SimpleType.
     */
    string get_property(1:string token, 2:ObjectReference ref) throws (1:ServiceException failure),

    /**
     * Retrieve count of something from SimpleType.
     */
    i64 get_count(1:string token, 2:ObjectReference ref) throws (1:ServiceException failure)
}