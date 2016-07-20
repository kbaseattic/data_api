"""
Blob API
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '4/8/16'

# Stdlib
import abc
import requests
import time
# Local
from doekbase.data_api import exceptions

class Blob(object):
    """Abstract base class for Blobs.
    """
    __metaclass__ = abc.ABCMeta

    #: Line separator used for .writeln()
    LINE_SEP = '\n'

    def __init__(self, expire_hours=24):
        """Create a new blob, with optional expiration.

        Args:
            expire_hours (int): Time, in hours, before blob will expire and
                may be deleted by the system. Any non-positive value will
                be interpreted as infinite.
        """
        self._exp_hours = expire_hours
        self._created = time.time()
        self.set_ref('')

    def set_ref(self, value):
        """Set the (workspace) reference associated with this blob.
        """
        self._ref = value

    def get_expiration_time(self):
        """Get time that this blob will expire.

        Returns:
            (int) Timestamp, in #seconds since epoch. May be negative
        """
        if self._exp_hours <= 0:
            return 0
        now = time.time()
        expire = self._created + self._exp_hours * 60 * 60
        return expire

    @abc.abstractmethod
    def write(self, bytes):
        """Write `bytes` to the blob.

        Args:
            bytes (str): Bytes to write
        """
        pass

    @abc.abstractmethod
    def writeln(self, bytes):
        """Write `bytes` followed by a newline.

        The ``LINE_SEP`` class variable will be used to produce the newline.

        Args:
            bytes (str): Bytes to write.
        """
        pass

    @abc.abstractmethod
    def to_file(self, f):
        """Write the *contents* of this blob to the provided file-like object.

        Args:
            f (file): File-like object, with a ``write`` method
        """
        pass

    def __str__(self):
        """String representation of self

        Returns:
            (str) The reference value (see :meth:`set_ref`)
        """
        return self._ref


class BlobShockNode(Blob):
    """A blobby interface to a KBase Shock node.
    """
    BLOCKSZ = 2**20

    def __init__(self, url=None, node_id=None, auth_token=None, create=False,
                 expire_hours=0):
        """Create a 'blob' that wraps a Shock node. The node may be an existing
        node, or a new node to be created.

        Args:
            url (str): Shock service URL
            node_id (str): Shock node identifier
            auth_token (str): User authorization token
            create (bool): Create a new node, otherwise use existing
            expire_hours (int): For new node, how many hours until it
                                expires (0=infinite)
        """
        Blob.__init__(self, expire_hours=expire_hours)
        self._url = url
        self._auth_header = {'Authorization': auth_token}
        if create:
            self._ro = False
            # XXX: create new node, call .set_ref() for full URL
            raise NotImplementedError('Sorry! Creation of new Shock nodes not implemented')
        else:
            if not self._url:
                raise ValueError('"url" parameter cannot be empty if "create" flag is False')
            # use existing node
            self._ro = True
            self._node_id = node_id
            fetch_url = '{}node/{}?download_raw'.format(url, node_id)
            # If compression worked, which it doesn't, then we would change
            # "download_raw" to "download" and add this:
            #       fetch_url += '&compression=gzip'
            self.set_ref(fetch_url)

    def write(self, bytes):
        if self._ro:
            raise exceptions.ServiceError('Cannot write to existing Shock node: {}'
                                          .format(self._node_id))
        # XXX: write to node
        raise NotImplementedError('Sorry! Creating temporary shock does not work yet')

    def writeln(self, bytes):
        return self.write(bytes + self.LINE_SEP)

    def to_file(self, f):
        response = requests.get(self._ref, headers=self._auth_header, stream=True)
        for chunk in response.iter_content(decode_unicode=True, chunk_size=self.BLOCKSZ):
            f.write(chunk)


class BlobBuffer(Blob):
    """For internal use: create a 'blob' that is really just a buffer.
    """
    def __init__(self, expire_hours=0):
        Blob.__init__(self, expire_hours=expire_hours)
        self._chunks = []

    def write(self, bytes):
        self._chunks.append(bytes)

    def writeln(self, bytes):
        self._chunks.append(bytes + self.LINE_SEP)

    def to_file(self, f):
        for chunk in self._chunks:
            f.write(chunk)