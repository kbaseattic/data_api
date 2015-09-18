"""
Test workspace mocking.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/3/15'

# Imports

# stdlib
import json
import os
import tempfile
# third-party
# local
from doekbase.data_api import wsfile

record_template = '''{{
        "ref": "{ref}",
        "type": "{type}",
        "name": "{name}",
        "links": [ {links} ],
        "data": {data},
        "metadata": {{ }}
}}'''


def foo_datum(n):
    d = {'index': n, 'value': n * 2.0,
        'muppets': {
            'colors': {
                'kermit': 'green',
                'animal': 'orange'
            },
            'actors': {
                'kermit': 'Jim Henson',
                'animal': 'Frank Oz',
            }
        }}
    return json.dumps(d)

TEST_DATA = [
    {'ref': '10/1', 'type': 'Foo',
     'name': 'first', 'data': foo_datum(1),
     'links': []},
    {'ref': '10/2', 'type': 'Foo',
     'name': 'second', 'data': foo_datum(2),
     'links': ','.join(['"{}"'.format(r) for r in ['10/1']])},
]

_mock = None
_tempdir = None

def setup():
    global _mock, _tempdir

    print("Setting up mock DB")
    _tempdir = tempfile.mkdtemp()
    filenames = []
    for datum in TEST_DATA:
        filename = datum['ref'].replace('/', '_')
        #print('@@ filename={} ref={}'.format(filename, datum['ref']))
        path = os.path.join(_tempdir, filename) + '.json'
        ofile = open(path, 'w')
        record_buf = record_template.format(**datum)
        ofile.write(record_buf)
        ofile.close()
        filenames.append(filename)

    # note: run nosetests with '-s' to see this
    #print("@@ input data:")
    #print(infile.getvalue())

    wsfile.WorkspaceFile.use_msgpack = False
    _mock = wsfile.WorkspaceFile(_tempdir)
    for filename in filenames:
        _mock.load(filename)

def teardown():
    # remove temporary files and directory
    for filename in os.listdir(_tempdir):
        path = os.path.join(_tempdir, filename)
        os.unlink(path)
    os.rmdir(_tempdir)

def test_get_object_history():
    # just make sure it doesn't crash.
    _mock.get_object_history({'ref': '10/1'})


def test_get_object_info_new():
    r = _mock.get_object_info_new({'objects': [{'ref': '10/1'}]})
    assert len(r) == 1
    obj = r[0]
    #print("@@ get_oin-obj: {}".format(obj))
    assert obj[1] == 'first'
    assert obj[2] == 'Foo'


def test_get_object_provenance():
    # just make sure it doesn't crash.
    _mock.get_object_provenance([{'ref': '10/1'}])


def test_get_object_subset():
    actors_1 = {'ref': '10/1', 'included': ['muppets/actors']}
    r = _mock.get_object_subset([actors_1])
    assert len(r) == 1
    obj = r[0]['data']
    #print("@@ get_os-obj: {}".format(obj))
    assert 'muppets' in obj
    assert 'actors' in obj['muppets']
    assert obj['muppets']['actors']['kermit'] == 'Jim Henson'
    assert 'colors' not in obj['muppets']

    # try again, this time with 2
    actors_2 = {'ref': '10/2', 'included': ['muppets/actors']}
    r = _mock.get_object_subset([actors_1, actors_2])
    assert len(r) == 2
    for obj in r:
        d = obj['data']
        assert 'muppets' in d
        assert 'actors' in d['muppets']
        assert 'colors' not in d['muppets']

    # retrieve a top level property
    r = _mock.get_object_subset([{'ref': '10/2', 'included': ['value']}])
    assert len(r) == 1
    for obj in r:
        d = obj['data']
        assert 'value' in d
        assert isinstance(d['value'], float)

    # retrieve two children of the same parent
    r = _mock.get_object_subset([{'ref': '10/2', 'included': ['muppets/actors', 'muppets/colors']}])
    assert len(r) == 1
    for obj in r:
        d = obj['data']
        assert 'muppets' in d
        assert 'actors' in d['muppets']
        assert 'colors' in d['muppets']



def test_get_objects():
    r = _mock.get_objects([{'ref': '10/1'}, {'ref': '10/2'}])
    assert len(r) == 2
    for obj in r:
        assert 'data' in obj
        assert 'object_info' in obj


def test_get_type_info():
    r = _mock.get_type_info('Foo')
    assert 'type_string' in r
    assert r['type_string'] == 'Foo'


def test_list_referencing_objects():
    r = _mock.list_referencing_objects([{'ref': '10/1'}, {'ref': '10/2'}])
    assert len(r) == 2
    # second is refrring to first
    assert len(r[0]) == 1
    assert r[0][0][1] == 'second'
    # nobody is referring to second
    assert len(r[1]) == 0
