import requests
import sys
import json
import datetime
import re
import tempfile
import shutil
import string

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO as StringIO

from biokbase.data_api import _get_token as get_token
import biokbase.workspace.client

REF_PATTERN = re.compile(".+/.+(/.+)?")

class ObjectAPI(object):
    """
    Generic Object API for basic properties and actions of a KBase Data Object.
    """

    def __init__(self, services=None, ref=None):
        if services == None or type(services) != type({}):
            raise TypeError("You must provide a service configuration dictionary! Found {0}".format(type(services)))
        elif not services.has_key("workspace_service_url"):
            raise KeyError("Expecting workspace_service_url key!")
        
        if ref == None or type(ref) != type("") or re.match(REF_PATTERN, ref) == None:
            raise TypeError("Invalid workspace reference string! Found {0}".format(ref))
        
        self.services = services
        self.ws_client = biokbase.workspace.client.Workspace(services["workspace_service_url"], token=get_token())
        self.ref = ref
        
        self._typestring = None
        self._info = None
        self._id = None
        self._name = None

    def get_schema(self):
        """
        Retrieve the schema associated with this object.
        
        Returns:
            string
        """
    
        return self.ws_client.get_type_info(self.get_info()[2])

    def get_typestring(self):
        """
        Retrieve the type identifier string.
        
        Returns:
            string
        """
        
        if self._typestring == None:
            self._typestring = self.ws_client.translate_to_MD5_types([self.get_info()[2]]).values()[0]
        
        return self._typestring

    def get_info(self):
        """
        Retrieve basic properties about this object.
        
        Returns:
            dict
        """
    
        if self._info == None:
            self._info = self.ws_client.get_object_info_new({
                "objects": [{"ref": self.ref}],
                "includeMetadata": 0,
                "ignoreErrors": 0})[0]
        
        return self._info

    def get_history(self):
        """
        Retrieve the recorded history of this object describing how it has been modified.
        """
    
        return self.ws_client.get_object_history({"ref": self.ref})
    
    def get_provenance(self):
        """
        Retrieve the recorded provenance of this object describing how to recreate it.
        """
    
        return self.ws_client.get_object_provenance([{"ref": self.ref}])
    
    def get_id(self):
        """
        Retrieve the internal identifier for this object.
        
        Returns:
            string
        """
    
        if self._id == None:
            self._id = self.ws_client.get_object_info_new({
                "objects": [{"ref": self.ref}],
                "includeMetadata": 0,
                "ignoreErrors": 0})[0][0]
        
        return self._id
    
    def get_name(self):
        """
        Retrieve the name assigned to this object.
        
        Returns:
            string
        """
    
        if self._name == None:
            self._name = self.ws_client.get_object_info_new({
                "objects": [{"ref": self.ref}],
                "includeMetadata": 0,
                "ignoreErrors": 0})[0][1]
        
        return self._name
    
    def get_stats(self):
        """
        Retrieve any derived statistical information known about this object.
        """
    
        return self.get_info()

    def get_data(self):
        """
        Retrieve object data.
        
        Returns:
            dict
        """
        
        return self.ws_client.get_objects([{"ref": self.ref}])[0]["data"]

    def get_data_subset(self, path_list=None):
        """
        Retrieve a subset of data from this object, given a list of paths to the data elements.
        
        Returns:
            dict
        """
    
        return self.ws_client.get_object_subset([{"ref": self.ref, 
                        "included": path_list}])[0]["data"]
    
    def copy(self, to_ws=None):
        """
        Performs a naive object copy to a target workspace.  A naive object copy is a simple
        copy that only generates a copy object of this entity, but any referencing entities
        are not included or considered.  More specific object copies should be implemented by
        specific types that understand their copy semantics for children and other referencing
        or referenced objects.
        
        Args:
            to_ws : the target workspace to copy the object to, which the user must have permission
            to write to.        
        """
    
        name = self.get_name()
        
        try:
            return self.ws_client.copy_object({"from": {"ref": self.ref}, "to": {"workspace": to_ws, "name": name}})
        except Exception, e:
            return {"error": e.message}
