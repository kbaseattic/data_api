"""
Module for base class for Data API objects.
"""
import os
import re

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO as StringIO

import biokbase.workspace.client

REF_PATTERN = re.compile("(.+/.+(/[0-9].+)?)|(ws\.[1-9][0-9]+\.[1-9][0-9]+)")

def get_token():
    try:
        token = os.environ["KB_AUTH_TOKEN"]
    except KeyError:
        raise Exception(
            "Missing authentication token!  Set KB_AUTH_TOKEN environment variable.")

class ObjectAPI(object):
    """
    Generic Object API for basic properties and actions of a KBase Data Object.
    """

    def __init__(self, services=None, ref=None):
        if services == None or type(services) != type({}):
            raise TypeError("You must provide a service configuration dictionary! Found {0}".format(type(services)))
        elif not services.has_key("workspace_service_url"):
            raise KeyError("Expecting workspace_service_url key!")
        
        if ref == None:
            raise TypeError("Missing object reference!")
        elif type(ref) != type("") and type(ref) != type(unicode()):
            raise TypeError("Invalid reference given, expected string! Found {0}".format(type(ref)))
        elif re.match(REF_PATTERN, ref) == None:
            raise TypeError("Invalid workspace reference string! Found {0}".format(ref))
        
        self.services = services
        self.ws_client = biokbase.workspace.client.Workspace(services["workspace_service_url"], token=get_token())
        self.ref = ref
        
        info_values = self.ws_client.get_object_info_new({
            "objects": [{"ref": self.ref}],
            "includeMetadata": 0,
            "ignoreErrors": 0})[0]        
        
        self._info = {
            "object_id": info_values[0],
            "object_name": info_values[1],
            "object_reference": "{0}/{1}".format(info_values[6],info_values[0]),
            "object_reference_versioned": "{0}/{1}/{2}".format(info_values[6],info_values[0],info_values[4]),
            "type_string": info_values[2],
            "save_date": info_values[3],
            "version": info_values[4],
            "saved_by": info_values[5],
            "workspace_id": info_values[6],
            "workspace_name": info_values[7],
            "object_checksum": info_values[8],
            "object_size": info_values[9],
            "object_metadata": info_values[10]
        }
        self._id = self._info["object_id"]
        self._name = self._info["object_name"]
        self._typestring = self.ws_client.translate_to_MD5_types([self._info["type_string"]]).values()[0]
        self._version = self._info["version"]
        self._schema = None
        self._history = None
        self._provenance = None
        self._data = None

    def get_schema(self):
        """
        Retrieve the schema associated with this object.
        
        Returns:
          string"""
    
        if self._schema == None:
            self._schema = self.ws_client.get_type_info(self.get_info()["type_string"])
        
        return self._schema

    def get_typestring(self):
        """
        Retrieve the type identifier string.
        
        Returns:
          string"""
                
        return self._typestring

    def get_info(self):
        """
        Retrieve basic properties about this object.
        
        Returns:
          dict"""
            
        return self._info

    def get_history(self):
        """
        Retrieve the recorded history of this object describing how it has been modified.
        """
        
        if self._history == None:
            self._history = self.ws_client.get_object_history({"ref": self.ref})
        
        return self._history
    
    def get_provenance(self):
        """
        Retrieve the recorded provenance of this object describing how to recreate it.
        """
        
        if self._provenance == None:
            self._provenance = self.ws_client.get_object_provenance([{"ref": self.ref}])
        
        return self._provenance
    
    def get_id(self):
        """
        Retrieve the internal identifier for this object.
        
        Returns:
          string"""
    
        return self._id
    
    def get_name(self):
        """
        Retrieve the name assigned to this object.
        
        Returns:
          string"""
    
        return self._name
    
    def get_data(self):
        """
        Retrieve object data.
        
        Returns:
          dict"""
        
        if self._data == None:
            self._data = self.ws_client.get_objects([{"ref": self.ref}])[0]["data"]
        
        return self._data

    def get_data_subset(self, path_list=None):
        """
        Retrieve a subset of data from this object, given a list of paths to the data elements.
        
        Returns:
          dict"""

        return self.ws_client.get_object_subset([{"ref": self.ref, 
                        "included": path_list}])[0]["data"]
    
    def get_referrers(self):
        """
        Retrieve a dictionary that indicates by type what objects are referring to this object.
        
        Returns:
          dict"""
        
        referrers = self.ws_client.list_referencing_objects([{"ref": self.ref}])[0]
        
        object_refs_by_type = dict()        
        for x in referrers:
            typestring = self.ws_client.translate_to_MD5_types([x[2]]).values()[0]
            
            if typestring not in object_refs_by_type:
                object_refs_by_type[typestring] = list()
            
            object_refs_by_type[typestring].append(str(x[6]) + "/" + str(x[0]) + "/" + str(x[4]))
        return object_refs_by_type
    
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
