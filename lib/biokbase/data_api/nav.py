"""
Navigation of object containers (e.g. workspaces).

The primary class is 'Finder'::

   from biokbase.data_api import nav
   finder = nav.Finder(...) # see class docs for args and usage
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '7/30/15'

import biokbase
import os
import biokbase.workspace.client
from collections import namedtuple

## Make a simply-accessed object for object_metadata from workspace API
ObjectInfo = namedtuple('ObjectInfo',
                        'objid,name,type,save_date,version,saved_by,wsid,'
                        'workspace,chsum,size,meta')

class DBConnection(object):
    """Database connection.
    """
    DEFAULT_WS_URL = 'https://ci.kbase.us/services/ws/'
    def __init__(self, workspace=None, auth_token=None, ws_url=None):
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
        self.client = biokbase.workspace.client.Workspace(ws_url,
                                                          token=auth_token)

    def get_workspace(self):
        return str(self._ws)

    def list_objects(self):
        """List all objects in workspace.

        Return:
          list of ObjectInfo
        """
        return map(ObjectInfo._make, self.client.list_objects(self._ws_param))

class Finder(object):
    """Find objects.

    Initialize with a DBConnection object:

      f = Finder(DBConnection(workspace=1122))

    You can use indexing to look up objects by name:

      f['kb|contigset.12523']

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

    def _set_objlist(self):
        if self._force_refresh or self._objlist is None:
            self._objlist = self._client.list_objects()

    def __getitem__(self, item):
        self._set_objlist()
        if isinstance(item, int):
            return self._objlist[item]
        else:
            for o in self._objlist:
                if o.name == item:
                    return o
            raise KeyError('Object with name "{}" not found in workspace {}'.
                           format(self._ws_name))

    def list(self):
        """Get a list of metadata for all objects in the workspace.

        XXX: HANGS! Not sure why...
        """
        self._set_objlist()
        for obj in self._objlist:
            print('@@ looking at object: {}'.format(obj))
        return []