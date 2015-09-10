"""
Workspace DB following PEP-249
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/16/15'

import os
from doekbase.data_api import db
from doekbase.workspace.client import Workspace

DEFAULT_WS_URL = 'https://ci.kbase.us/services/ws/'
DEFAULT_SHOCK_URL = 'https://ci.kbase.us/services/shock-api/'

def connect(ws_url=DEFAULT_WS_URL, shock_url=DEFAULT_SHOCK_URL):
    conn = WorkspaceConnection(ws_url, shock_url)
    return conn

def get_token():
    try:
        token = os.environ["KB_AUTH_TOKEN"]
    except KeyError:
        raise Exception(
            "Missing authentication token!"
            "Set KB_AUTH_TOKEN environment variable.")
    return token

class WorkspaceConnection(db.BaseConnection):
    """Database connection to the KBase 'Workspace', the
    main KBase data store.
    """
    def __init__(self, url, shock_url, token=None):
        self.token = token or get_token()
        self.ws_client = Workspace(
            url, token=self.token)
        super(WorkspaceConnection, self).__init__()

    def close(self):
        self.ws_client = None

    def commit(self):
        pass

    def rollback(self):
        pass

    def cursor(self):
        return self.ws_client