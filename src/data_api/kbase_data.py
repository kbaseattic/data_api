"""
Basic functionality.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '5/5/15'

from abc import ABCMeta, abstractmethod
from multiprocessing import Pool
from operator import itemgetter
import os
import sys
import time
import uuid

import six

class DataClient:
    """Abstract client to KBase data store.

    Implemented by subclasses for different types
    of data stores, e.g. Titan vs. local graph DB vs. Spark GraphX etc.
    """
    __metaclass__ = ABCMeta

    def __init__(self, async=False, default_timeout=30):
        """Ctor.

        :param async: Perform operations asynchronously. If true, operations
                      will return a multiprocessing.AsyncResult
        :param default_timeout: Default timeout in seconds
        """
        self._async = async
        if async:
            self._pool = Pool(processes=4)  #TODO: bigger pool size?

    @abstractmethod
    def authenticate(self, user=None, role=None, **kw):
        """Authenticate, or re-authenticate to the data store.

        Returns:
            bool: True if OK, False if not
        """
        pass

    def insert(self, obj, **kw):
        """Insert an object.

        Args:
           obj (object): Insert this object

        Returns:
            int: Number of objects actually inserted
        """
        if self._async:
            return self._pool.apply_async(self.insert_sync, (obj,), kw)
        else:
            return self.insert_sync(obj, **kw)

    @abstractmethod
    def insert_sync(self, obj):
        """Insert an object. See :meth:`insert`.
        Subclasses should override this method (not 'insert()').
        """
        pass

    def search(self, spec, **kw):
        """Search for objects.

        Returns:
           list: Iterator over objects
        """
        if self._async:
            return self._pool.apply_async(self.search_sync, (spec,), kw)
        else:
            return self.search_sync(spec, **kw)

    @abstractmethod
    def search_sync(self, spec, **kw):
        """Search for an object. See :meth:`search`.
        Subclasses should override this method (not 'search()').
        """
        pass

    def load(self, src):
        """Load data from the source into the client.
        """
        return src.load(self)

    @abstractmethod
    def load_bytes(self, f):
        pass

class MockDataClient(DataClient):
    """In-memory data client for testing.
    """
    def __init__(self):
        self.data = {}
        self.objlist = []
        super(MockDataClient, self).__init__()

    def authenticate(self, user=None, role=None, **kw):
        return True

    def insert_sync(self, obj, **kw):
        self.objlist.append((obj, kw))
        return 1

    def search_sync(self, spec, **kw):
        result = []
        if spec and spec.has_key('oid'):
            oid = spec['oid']
            result = filter(lambda o: o.oid == oid, map(itemgetter(0), self.objlist))
        return result

    def load_bytes(self, f):
        id_ = str(uuid.uuid4())
        self.data[id_] = f.read()
        return id_

############################################################

"""
Datum class hierarchy:
       +-------+
       | Datum |                                +-----------+
       +---+---+                                | (External)|
           ^                                    +-----------+
           |                                          ^
   +-------+-----+---------------+---------------+    |
   |             |               |               |    |
+--+-------+  +--+-------+  +----+--------+  +---+--+ |
| BioDatum |  | Project  |  | Narrative   |  | File +-+
+-------+--+  +----------+  +----+--------+  +------+
        |                        |
        |                        |
        v                        |
       +-------------+           |
       | (InProject) |<----------+
       +-------------+

Classes (in parentheses) are "marker" classes.
"""

class InProject(object):
    """Marker class for things that can be in a project."""
    pass

class External(object):
    """Marker class for 'external' objects."""
    pass

class Datum:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.oid = str(uuid.uuid4())
        self.provenance = Provenance()
        self.owner = None
        self.properties = {}

    def __str__(self):
        pprops = (name for name in dir(self) if not name.startswith('_'))
        return '\n'.join(['{key}: {val}'.format(key=key,
                                                val=getattr(self, key))
                          for key in sorted(pprops)])

class Project(Datum):
    def __init__(self):
        super(Project, self).__init__()
        self.sharing = []  # (role,group)*
        self.objects = set()

class BioDatum(Datum, InProject):
    def __init__(self):
        super(BioDatum, self).__init__()
        self.concept_class = None
        self.measurements = {}
        self.measurement_provenance = Provenance()

class Narrative(Datum, InProject):
    def __init__(self):
        super(Narrative, self).__init__()
        self.data = set()
        self.evidence = {}
        self.assertions = {}
        self.cells = []


class File(Datum, External):
    def __init__(self, path):
        super(External, self).__init__()
        self.properties = {'filename': path}

class Provenance(object):
    """Datum provenance.
    """
    def __init__(self):
        self.create_time = time.time()
        self.parents = set()

    def __str__(self):
        pprops = (name for name in dir(self) if not name.startswith('_'))
        return ', '.join(['{key}: {val}'.format(key=key,
                                                val=getattr(self, key))
                          for key in sorted(pprops)])

############################################################

class Source:
    """Abstract base class of a data source.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def load(self, client):
        """Convert source data and load into KBase data store. A connection
        to the data store is represented by `client`.
        """
        pass

class FastaSource(Source):
    """Implementation of Source ABC for the FASTA file format.

    Example usage::
      client = TGClient()  # e.g. TinkerGraph client
      client.authenticate( ...etc... )
      src = FastaSource("/my/great/file.fasta")
      client.load(src)
    """
    def __init__(self, input_file):
        """Initialize with a file-like input stream.
        The object needs to support `seek(0)`.

        Args:
          input_file (file): FASTA file
        """
        super(FastaSource, self).__init__()
        self._infile = input_file

    def load(self, client):
        """Finish creating the object, and load it into the
        client.

        Args:
           client (DataClient): Target client

        Returns:
            str: Unique object identifier
        """
        # XXX: read FASTA data, create ye olde objects.
        hdr = self._read_header()
        bd = BioDatum()
        bd.provenance.parents.add(File(self._infile.name))
        bd.concept_class = "Sequence" # concepts.Gene.Sequence??
        # bd.measurement_provenance = something-from-hdr
        self._infile.seek(0)
        file_id = client.load_bytes(self._infile)
        bd.measurements = {"Bytes.FASTA": file_id} # Type:<value>
        client.insert(bd)
        return bd.oid

    def _read_header(self):
        """Read and parse FASTA header.
        After this finishes, the file pointer is right after the header
        (i.e. the first byte of data)

        Returns:
           dict: What was parsed
        """
        desc = self._infile.readline()
        # TODO: parse desc to a dict of info
        return {}

############################################################


def __test(filename):
    client = MockDataClient()
    f = open(filename)
    src = FastaSource(f)
    oid = client.load(src)
    # look for it
    objects = client.search({'oid': oid})
    print("Got back objects:")
    for o in objects:
        print('--')
        print(o)
    assert len(objects) == 1
    assert objects[0].measurements['Bytes.FASTA']

if __name__ == '__main__':
    __test(sys.argv[1])