"""
Module for base class for Data API objects.
"""

# Imports

# Stdlib
from collections import namedtuple
import logging
import os
import re
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO as StringIO
# Local
from doekbase.data_api.util import get_logger, log_start, log_end
from doekbase.workspace.client import Workspace
from doekbase.data_api.wsfile import WorkspaceFile
from doekbase.data_api import cache
from doekbase.data_api.util import PerfCollector, collect_performance

# Logging

_log = get_logger('doekbase.data_api.core')

# Globals
REF_PATTERN = re.compile("(.+/.+(/[0-9].+)?)|(ws\.[1-9][0-9]+\.[1-9][0-9]+)")

g_ws_url = "https://ci.kbase.us/services/ws/"
g_shock_url = "https://ci.kbase.us/services/shock-api/"
g_handle_url = "https://ci.kbase.us/services/handle_service/"
g_use_msgpack = True

g_stats = PerfCollector('ObjectAPI')

def fix_docs(cls):
    for name, func in vars(cls).items():
        if func is not None and func.__doc__ is None:
            for parent in cls.__bases__:
                if hasattr(parent, name):
                    parfunc = getattr(parent, name)
                    if parfunc and hasattr(parfunc, '__doc__'):
                        func.__doc__ = parfunc.__doc__
                        break
    return cls

#: Name positional parts of WorkspaceInfo tuple
WorkspaceInfo = namedtuple('WorkspaceInfo', [
    'id',               # ws_id (int)
    'workspace',        # ws_name
    'owner',            # username
    'moddate',          # timestamp
    'object',           # int
    'user_permission',  # permission
    'globalread',       # permission
    'lockstat',         # lock_status
    'metadata'          # usermeta
])

def get_token():
    try:
        token = os.environ["KB_AUTH_TOKEN"]
    except KeyError:
        raise Exception(
            "Missing authentication token!  Set KB_AUTH_TOKEN environment variable.")

class ObjectAPI(object):
    """
    Generic Object API for basic properties and actions
    of a KBase Data Object.
    
    In general, users will not instantiate this object directly, but instead
    they will create a biology-specific object like `TaxonAPI` or
    `GenomeAnnotationAPI`. However, methods in this class may be used to get
    basic shared properties like provenance or metadata.
    
    If you find yourself using some form of :meth:`get_data` or :meth:`get_data_subset` frequently, 
    you should consider wrapping those calls in a higher-level method that is
    specific to the kind of data you want. 
    """
    def __init__(self, services=None, token=None, ref=None):
        """Create new object.
 
        Args:
          services (dict): Service configuration dictionary. Required keys:
              * workspace_service_url: URL for Workspace, such as `https://ci.kbase.us/services/ws/`
          ref (str): Object reference, which can be the name of the object
             (although this is not unique), or a numeric identifier in the
             format `A/B[/C]` where A is the number of the workspace, B is the
             number identifying the object, and C is the "version" number of
             the object.
        """
        if services is None or type(services) != type({}):
            raise TypeError("You must provide a service configuration dictionary! Found {0}".format(type(services)))
        elif not services.has_key("workspace_service_url"):
            raise KeyError("Expecting workspace_service_url key!")
        
        if ref is None:
            raise TypeError("Missing object reference!")
        elif type(ref) != type("") and type(ref) != type(unicode()):
            raise TypeError("Invalid reference given, expected string! "
                            "Found {0}".format(type(ref)))
        elif re.match(REF_PATTERN, ref) is None:
            raise TypeError("Invalid workspace reference string! Found {0}"
                            .format(ref))

        self.services = services
        self.ref = ref
        self._token = None

        ws_url = services["workspace_service_url"]
        local_workspace = False
        if '://' in ws_url: # assume a real Workspace server
            if token is None or len(token.strip()) == 0:
                self._token = get_token()
            else:
                self._token = token

            _log.debug('Connect to Workspace service at {}'.format(ws_url))
            self.ws_client = Workspace(ws_url, token=self._token)
        else:
            _log.debug('Load from Workspace file at {}'.format(ws_url))
            local_workspace = True
            self.ws_client = self._init_ws_from_files(ws_url)

        info_values = self.ws_client.get_object_info_new({
            "objects": [{"ref": self.ref}],
            "includeMetadata": 0,
            "ignoreErrors": 0})
        if not info_values:
            raise ValueError("Cannot find object: {}".format(self.ref))
        oi = info_values[0]

        self._info = {
            "object_id": oi[0],
            "object_name": oi[1],
            "object_reference": "{0}/{1}".format(oi[6],oi[0]),
            "object_reference_versioned": "{0}/{1}/{2}".format(oi[6],oi[0],oi[4]),
            "type_string": oi[2],
            "save_date": oi[3],
            "version": oi[4],
            "saved_by": oi[5],
            "workspace_id": oi[6],
            "workspace_name": oi[7],
            "object_checksum": oi[8],
            "object_size": oi[9],
            "object_metadata": oi[10]
        }
        self._id = self._info["object_id"]
        self._name = self._info["object_name"]
        self._typestring = self.ws_client.translate_to_MD5_types(
            [self._info["type_string"]]).values()[0]
        self._version = str(self._info["version"])
        self._schema = None
        self._history = None
        self._provenance = None
        self._data = None
        # Init stats
        self._stats = g_stats
        # Init the caching object. Pass in whether the object is
        # publically available (which can determine whether it is cached)
        if local_workspace:
            global_read = True  # Local file-workspace objects are public
        else:
            wsinfo = self.ws_client.get_workspace_info({
                'id': self._info['workspace_id']})
            wsinfo_obj = WorkspaceInfo(*wsinfo)
            global_read = (wsinfo_obj.globalread == 'r')
        self._cache = cache.ObjectCache(
            self._info["object_reference_versioned"],
            is_public=global_read)

        # TODO always use a versioned reference to the data object
        #self.ref = self._info["object_reference_versioned"]

    @property
    def stats(self):
        return self._stats

    @property
    def cache_stats(self):
        return self._cache.stats

    def _init_ws_from_files(self, path):
        ext = '.msgpack'
        extlen = len(ext)
        WorkspaceFile.use_msgpack = True
        client = WorkspaceFile(path)
        num_loaded = 0
        for name in os.listdir(path):
            if name.endswith(ext):
                ref = name[:-extlen]
                t0 = log_start(_log, 'load', level=logging.DEBUG,
                               kvp={'ref': ref})
                client.load(ref)
                log_end(_log, t0, 'client.load', level=logging.DEBUG,
                        kvp={'ref': ref})
            num_loaded += 1
        if num_loaded == 0:
            raise ValueError('No files with extension "{e}" found in path {p}'
                             .format(e=ext, p=path))
        return client

    @collect_performance(g_stats)
    def get_schema(self):
        """
        Retrieve the schema associated with this object.
        
        Returns:
          string"""
    
        if self._schema is None:
            self._schema = self.ws_client.get_type_info(self.get_info()["type_string"])
        
        return self._schema

    @collect_performance(g_stats)
    def get_typestring(self):
        """
        Retrieve the type identifier string.
        
        Returns:
          string"""
                
        return self._typestring

    @collect_performance(g_stats)
    def get_info(self):
        """Retrieve basic properties about this object.
        
        Returns:
          dict
            object_id
            object_name
            object_reference
            object_reference_versioned
            type_string
            save_date
            version
            saved_by
            workspace_id
            workspace_name
            object_checksum
            object_size
            object_metadata"""

        return self._info

    @collect_performance(g_stats)
    def get_history(self):
        """
        Retrieve the recorded history of this object describing how it has been modified.

        Returns:
          list<dict>
            object_id
            object_name
            object_reference
            object_reference_versioned
            type_string
            save_date
            version
            saved_by
            workspace_id
            workspace_name
            object_checksum
            object_size
            object_metadata
        """
        
        if self._history == None:
            history_list = self.ws_client.get_object_history({"ref": self.ref})

            self._history = list()

            for object_info in history_list:
                self._history.append({
                    "object_id": object_info[0],
                    "object_name": object_info[1],
                    "object_reference": "{0}/{1}".format(object_info[6],object_info[0]),
                    "object_reference_versioned": "{0}/{1}/{2}".format(object_info[6],
                                                                       object_info[0],
                                                                       object_info[4]),
                    "type_string": object_info[2],
                    "save_date": object_info[3],
                    "version": object_info[4],
                    "saved_by": object_info[5],
                    "workspace_id": object_info[6],
                    "workspace_name": object_info[7],
                    "object_checksum": object_info[8],
                    "object_size": object_info[9],
                    "object_metadata": object_info[10]})

        return self._history

    @collect_performance(g_stats)
    def get_provenance(self):
        """
        Retrieve the recorded provenance of this object describing how to recreate it.

        Returns:
          list<dict>
            time
            service_name
            service_version
            service_method
            method_parameters
            script_name
            script_version
            script_command_line
            input_object_references
            validated_object_references
            intermediate_input_ids
            intermediate_output_ids
            external_data
            description
        """

        if self._provenance is None:
            result = self.ws_client.get_object_provenance([{"ref": self.ref}])

            if len(result) > 0:
                provenance_list = result[0]["provenance"]
            else:
                provenance_list = list()

            self._provenance = list()

            copy_keys = {"time": "time",
                         "service": "service_name",
                         "service_ver": "service_version",
                         "method": "service_method",
                         "method_params": "method_parameters",
                         "script": "script_name",
                         "script_ver": "script_version",
                         "script_command_line": "script_command_line",
                         "input_ws_objects": "input_object_references",
                         "resolved_ws_objects": "validated_object_references",
                         "intermediate_incoming": "intermediate_input_ids",
                         "intermediate_outgoing": "intermediate_output_ids",
                         "external_data": "external_data",
                         "description": "description"}

            for object_provenance in provenance_list:
                action = dict()

                for k in copy_keys:
                    if k in object_provenance:
                        if isinstance(object_provenance[k], list) and len(object_provenance[k]) == 0:
                            continue

                        action[copy_keys[k]] = object_provenance[k]

                self._provenance.append(action)

        return self._provenance

    @collect_performance(g_stats)
    def get_id(self):
        """
        Retrieve the internal identifier for this object.
        
        Returns:
          string"""
    
        return self._id

    @collect_performance(g_stats)
    def get_version(self):
        """
        Retrieve the version identifier for this object.

        Returns:
          string"""

        return self._version

    @collect_performance(g_stats)
    def get_name(self):
        """
        Retrieve the name assigned to this object.
        
        Returns:
          string"""
    
        return self._name

    @collect_performance(g_stats)
    def get_data(self):
        """Retrieve object data.
        
        Returns:
          dict (contents according to object type)"""
        
        return self._cache.get_data(self._get_data_ws)

    def _get_data_ws(self):
        return self.ws_client.get_objects([{"ref": self.ref}])[0]["data"]

    @collect_performance(g_stats)
    def get_data_subset(self, path_list=None):
        """Retrieve a subset of data from this object, given a list of paths
        to the data elements.

        Args:
          path_list (list): List of paths, each a string of node names
                            separated by forward slashes, e.g.
                            ['a/bee/sea', 'd/ee/eph/gee']
        Returns:
          dict (contents according to object type and data requested)"""

        return self._cache.get_data_subset(self._get_data_subset_ws,
                                           path_list=path_list)

    def _get_data_subset_ws(self, path_list=None):
        return self.ws_client.get_object_subset([{"ref": self.ref, 
                        "included": path_list}])[0]["data"]

    @collect_performance(g_stats)
    def get_referrers(self, most_recent=True):
        """Retrieve a dictionary that indicates by type what objects are
        referring to this object.

        Args:
          most_recent: True or False, defaults to True indicating that results
              should be restricted to the latest version of any referencing object.
              If this parameter is False, results will contain all versions of any
              referencing objects.

        Returns:
          dict typestring -> object_reference"""

        referrers = self.ws_client.list_referencing_objects([{"ref": self.ref}])[0]

        # sort all object references in descending order by time
        referrers = sorted(referrers, cmp=lambda a,b: a[3] > b[3])
        
        object_refs_by_type = {}

        # keep track of which objects we have seen so far, the first instance will be the latest
        # so only keep that reference
        found_objects = {}
        for x in referrers:
            typestring = self.ws_client.translate_to_MD5_types([x[2]]).values()[0]

            if typestring not in object_refs_by_type:
                object_refs_by_type[typestring] = []

            unversioned_ref = str(x[6]) + "/" + str(x[0])
            if most_recent and unversioned_ref in found_objects:
                continue

            # Mark an entry for a new object
            found_objects[unversioned_ref] = None
            object_refs_by_type[typestring].append(str(x[6]) + "/" + str(x[0]) + "/" + str(x[4]))

        return object_refs_by_type

    @collect_performance(g_stats)
    def copy(self, to_ws=None):
        """
        Performs a naive object copy to a target workspace.  A naive object copy is a simple
        copy that only generates a copy object of this entity, but any referencing entities
        are not included or considered.  More specific object copies should be implemented by
        specific types that understand their copy semantics for children and other referencing
        or referenced objects.
        
        Args:
          to_ws : the target workspace to copy the object to, which the user must have permission
          to write to."""
    
        name = self.get_name()
        
        try:
            return self.ws_client.copy_object({"from": {"ref": self.ref}, "to": {"workspace": to_ws, "name": name}})
        except Exception, e:
            return {"error": e.message}

    def __eq__(self, other):
        """Test equality by underlying KBase object ID.
        """
        #print("@@ obj. eq called")
        return self._id == other._id

