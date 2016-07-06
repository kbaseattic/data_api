"""
Tests for the thrift_include module
"""
import logging
import os
import shutil
import tempfile
from doekbase.data_api.tests import shared
from doekbase.data_api import exceptions
from doekbase.data_api import thrift_include

_log = None

def setup():
    global _log
    shared.setup()
    _log = logging.getLogger('nose.test_thrift_include')

input_files = {
    'A':"""File A
#%include B
  #%include C
Some stuff here

#%include D
goodbye""",
    'B': "Hello from File B",
    'C': "Hello from File C",
    'D': """Hello from File D..
Here is file E:
#%include E
More of file D.
""",
    'E': "Hello from File E"
}

expected_output = """File A
#%include B
{B}
#%endinclude B
#%include C
{C}
#%endinclude C
Some stuff here

#%include D
Hello from File D..
Here is file E:
{E}
More of file D.
#%endinclude D
goodbye""".format(**input_files)

class TemporaryDirectory(object):
    def __init__(self):
        self._d = None
    def __enter__(self):
        self._d = tempfile.mkdtemp()
        return self._d
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._d is not None:
            shutil.rmtree(self._d)
        self._d = None

def _test_include(in_place=None):
    with TemporaryDirectory() as tmpdirname:
        _log.info("Temporary directory: {}".format(tmpdirname))
        # create input files
        for filename, contents in input_files.items():
            f = open(os.path.join(tmpdirname, filename), 'w')
            f.write(contents)
            f.close()

        # preprocess the root input file
        if in_place:
            a = open(os.path.join(tmpdirname, 'A'), 'r+')
            a_write = a
        else:
            a = open(os.path.join(tmpdirname, 'A'), 'r')
            a_write = open(os.path.join(tmpdirname, 'Aw'), 'w')
        pp = thrift_include.ThriftPP(read_file=a, write_file=a_write, include_paths=[tmpdirname])
        changed = pp.process()
        assert changed
        a.close()
        if a is not a_write:
            a_write.close()

        # check the content
        a = open(os.path.join(tmpdirname, a_write.name), 'r')
        got_lines = a.readlines()
        _log.debug("Got {:d}:\n{}".format(len(got_lines), ''.join(got_lines)))

        expected_lines = expected_output.split('\n')
        _log.debug("Expected {:d}:\n{}".format(len(expected_lines), '\n'.join(expected_lines)))
        assert len(got_lines) == len(expected_lines)

        for got, expected in zip(got_lines, expected_lines):
            assert got.strip() == expected.strip()

def test_include_in_place():
    _test_include(in_place=True)

def test_include_copy():
    _test_include(in_place=False)