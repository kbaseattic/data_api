"""
Tests for biokbase.data_api.nav module
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/3/15'

import unittest
from biokbase.data_api import nav

from . import shared

def setup():
    shared.setup()

class MockConn(nav.DBConnection):
    """Mock database connection.
    """
    def __init__(self, workspace=None, **kwargs):
        self._ws = workspace
        self.client = 'fake'

    def list_objects(self):
        return []

    def get_object(self, objid):
        return None

@unittest.skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_list():
    """Test the 'ls' functions."""
    conn = MockConn('myWorkspace')
    finder = nav.Finder(conn)
