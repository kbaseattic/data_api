"""
Navigation of object containers (e.g. workspaces).

The primary class is 'Finder'::

   from doekbase.data_api import nav
   finder = nav.Finder(...) # see class docs for args and usage
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '7/30/15'

# System
from collections import namedtuple
import glob
import os
import re

# Local
import doekbase
import doekbase.workspace.client

# the types module is being removed:
#from doekbase.data_api.types import get_object_class

def get_object_class(type_pattern):
    # XXX: This should return the class for a given type pattern
    return None

def add_dicts(a, b):
    """Add two dictionaries together and return a third."""
    c = a.copy()
    c.update(b)
    return c

## Make a simply-accessed object for object_metadata from workspace API
_ObjectInfo = namedtuple('_ObjectInfo',
                        'objid,name,type,save_date,version,saved_by,wsid,'
                        'workspace,chsum,size,meta')

class ObjectInfo(_ObjectInfo):
    """Metadata about one object."""
    def set_conn(self, conn):
        self._conn = conn
        return self  # for chaining

    @property
    def data(self):
        """Get full, raw, data from its metadata."""
        return self._conn.get_object(self.objid)

    @property
    def object(self):
        """Get wrapped KBase data object from the metadata."""
        clazz = get_object_class(self.type)
        if clazz is None:
            raise RuntimeError('Internal error: Cannot get any class '
                               'for type "{}"'.format(self.name))
        kwparams = self._conn.get_objectapi_params(self.objid)
        return clazz(**kwparams)

class DBConnection(object):
    """Database connection."""
    DEFAULT_WS_URL = 'https://ci.kbase.us/services/ws/'
    DEFAULT_SHOCK_URL = 'https://ci.kbase.us/services/shock-api/'
    def __init__(self, workspace=None, auth_token=None, ws_url=None, shock_url=None):
        if workspace is None:
            raise ValueError("Workspace id, e.g. 1003, required")
        try:
            self._ws = int(workspace)
            self._ws_param = {'ids': [self._ws]}
        except ValueError:
            raise ValueError("Workspace id must be an integer")
        if auth_token is None:
            try:
                varname = 'KB_AUTH_TOKEN'
                auth_token = os.environ[varname]
            except IndexError:
                raise ValueError('Unable to authorize. No '
                                 'value given for auth_token and '
                                 'environment variable {} not found'.
                                 format(varname))
        if ws_url is None:
            ws_url = self.DEFAULT_WS_URL
            
        if shock_url is None:
            shock_url = self.DEFAULT_SHOCK_URL
        
        self._ws_url = ws_url        
        self._shock_url = shock_url
        self.client = doekbase.workspace.client.Workspace(ws_url,
                                                          token=auth_token)

    def get_objectapi_params(self, objid):
        """Get back the params that the Data ctor wants, as
        a dictionary with the correct keyword arguments set.
        """
        return dict(services={'workspace_service_url': self._ws_url, 
                              'shock_service_url': self._shock_url},
                    ref='{}/{}'.format(self._ws, objid))

    def get_workspace(self):
        return str(self._ws)

    def list_objects(self):
        """List all objects in workspace.

        Return:
          list of ObjectInfo
        """
        objlist = self.client.list_objects(self._ws_param)
        return [ObjectInfo._make(o).set_conn(self) for o in objlist]

    def get_object(self, objid):
        """Get an object in the workspace.

        TODO: Make this work!!
        """
        oid = {'wsid': self._ws, 'objid': objid}
        params = [oid]
        obj = self.client.get_objects(params)
        return obj

class Finder(object):
    """Find objects.

    Initialize with a DBConnection object:

      f = Finder(DBConnection(workspace=1122))

    You can use indexing to look up objects by name:

      f['kb|contigset.12523']

    The name can contain Unix glob characters (e.g. "*"):

      f['Rhodobacter*']

    You can also look up objects by position

      f[0]

    You can look up an object by arbitrary attributes by
    passing a dict-like object (anything with an 'items' method) as the index

       f[dict(type='KBaseGenomes.ContigSet-2.0')]

    Use list() to see all objects:

      print(list(f))
    """
    def __init__(self, conn, cache=True):
        """Ctor.

        Args:
          conn - DBConnection object
          cache - If True (the default), cache objects and don't
                  contact the server again. If False, contact the
                  server every time.
        """
        if not hasattr(conn, 'client'):
            raise ValueError('Input "conn" parameter does not look like '
                             'a DBConnection object; no "client" attribute '
                             'found')
        self._client = conn
        self._objlist = None
        self._force_refresh = not cache
        self._ws_name = conn.get_workspace()
        self._globmatch = glob.fnmatch.fnmatchcase

    def _set_objlist(self):
        if self._force_refresh or self._objlist is None:
            self._objlist = self._client.list_objects()

    def ls(self):
        """List objects in the current container namespace.

        Returns:
          list of objects, each in the same form returned by the indexing
          operations.
        """
        return list(self)

    def filter(self, objid=None, name=None, name_re=None, type_=None,
               type_re=None, type_ver=None, **kw):
        """Return a filtered subset of the contained objects.

        Args:
            objid (int): Object identifier
            name (str): Exact match name
            name_re (str): Regular expression match name
            type_ (str): Exact match type
            type_re (str): Regular expression match type
            type_ver (tuple): Match on string type and str version comparator
            kw (dict): Names and values, matched as exact strings. If the
                       name is not in the record, it is ignored.
        """
        if name_re is not None and name is not None:
            raise ValueError('keywords "name_re" and "name" cannot both be given')
        if sum(map(bool, (type_re, type_, type_ver))) > 1:
            raise ValueError(
                'keywords "type_re", "type", and "type_ver" are exclusive')
        result = []
        for o in list(self):
            if objid is not None:
                if o.objid != objid:
                    continue
            if name_re is not None:
                if not re.match(name_re, o.name):
                    continue
            elif name is not None:
                if name != o.name:
                    continue
            if type_re is not None:
                if not re.match(type_re, o.type):
                    continue
            elif type_ is not None:
                if type_ != o.type:
                    continue
            kwmatch = True
            for k, v in kw:
                if k in o:
                    if o[k] != v:
                        kwmatch = False
                        break
            if not kwmatch:
                continue
            result.append(o)
        return result

    def __getitem__(self, item):
        """Indexing."""
        self._set_objlist()
        if isinstance(item, int):
            return self._objlist[item]
        elif hasattr(item, 'items'): # dict-like
            for o in self._objlist:
                matched = True
                for k, v in item.items():
                    if getattr(o, k, None) != v:
                        matched = False
                        break
                if matched:
                    return o
            raise KeyError('Object with attributes ({}) not found '
                           'in workspace {}'.
                           format(item, self._ws_name))
        else:
            for o in self._objlist:
                if o.name == item:
                    return o
                elif self._globmatch(o.name, item):
                    return o
            raise KeyError('Object with name "{}" not found in workspace {}'.
                           format(item, self._ws_name))
