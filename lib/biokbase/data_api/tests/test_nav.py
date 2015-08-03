"""
Tests for biokbase.data_api.nav module
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/3/15'

import unittest
from biokbase.data_api import nav

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

class NavTests(unittest.TestCase):
    def setUp(self):
        conn = MockConn('myWorkspace')
        self.finder = nav.Finder(conn)

    def testLs(self):
        self.failUnless(False)  # Fail

def main():
    unittest.main()

if __name__ == '__main__':
    main()
