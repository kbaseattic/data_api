"""
Tests for doekbase.data_api.nav module
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/3/15'

from doekbase import data_api
from doekbase.data_api import nav

from . import shared

def setup():
    shared.setup()

class MockConn(object):
    """Mock database connection.
    """
    CANNED_OBJECTS = [
        ('Frodo', 'hobbit', {'ringbearer': True, 'hair': 'brown'}),
        ('Sam', 'hobbit', {'ringbearer': False, 'hair': 'brown'}),
        ('Merry', 'hobbit', {'ringbearer': False, 'hair': 'brown'}),
        ('Pippin', 'hobbit', {'ringbearer': False, 'hair': 'brown'}),
        ('Gimli', 'dwarf', {'ringbearer': False, 'hair': 'red'}),
        ('Legolas', 'elf', {'ringbearer': False, 'hair': 'white'}),
        ('Aragorn', 'human', {'ringbearer': False, 'hair': 'black'}),
        ('Boromir', 'human', {'ringbearer': False, 'hair': 'black'}),
        ('Gandalf', 'wizard', {'ringbearer': False, 'hair': 'silver'}),
    ]
    def __init__(self, workspace=None, **kwargs):
        self._ws = workspace
        self.client = 'fake'

    def list_objects(self):
        """Fake the actual fetching of a list of objects."""
        olist = []
        for name, type_, kwd in self.CANNED_OBJECTS:
            obj = MockNavObject(name, type_, kwd)
            olist.append(obj)
        return olist

    def get_workspace(self):
        return self._ws

    def get_object(self, objid):
        return None

class MockNavObject(dict):
    def __init__(self, name, type_, kwd):
        super(MockNavObject, self).__init__(**kwd)
        self.name = name
        self.type = type_

def test_finder():
    """Creating a Finder object"""
    conn = MockConn('myWorkspace')
    finder = nav.Finder(conn)
    assert finder is not None
    return finder

def test_list():
    """Listing workspace objects"""
    finder = test_finder()
    o1 = finder.ls()
    o2 = list(finder)
    assert o1 == o2

def expect_value_error(f, *a, **k):
    try:
        f(*a, **k)
    except ValueError:
        pass

def test_filter_args():
    """Args for filtering of listing of workspace objects"""
    finder = test_finder()
    # make sure arg. conflicts raise ValueError
    expect_value_error(finder.filter, name_re='.*', name='foobar')
    expect_value_error(finder.filter, type_='foo', type_ver='bar')
    expect_value_error(finder.filter, type_ver='foo', type_re='.*')

def test_filter():
    """Filtering of listing of workspace objects"""
    finder = test_finder()
    v = finder.filter(name='Gandalf')
    assert len(v) == 1
    assert v[0].type == 'wizard'
    v = finder.filter(type_re='w.*')
    assert len(v) == 1
    assert v[0].type == 'wizard'
    v = finder.filter(type_='hobbit')
    assert len(v) == 4
    v = finder.filter(type_='hobbit', name_re='.*r')
    assert len(v) == 2

