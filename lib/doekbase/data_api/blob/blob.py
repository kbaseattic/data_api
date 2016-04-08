"""
Blob API
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '4/8/16'

import abc
import time

class TemporaryBlob(object):
    __metaclass__ = abc.ABCMeta

    LINE_SEP = '\n' # for .writeln()

    def __init__(self, expire_hours=24):
        self._exp_hours = expire_hours
        self._created = time.time()
        self.set_id('')

    def set_id(self, value):
        self._ref = value

    def get_expiration_time(self):
        """Get time that this blob will expire.

        Returns:
            (int) Timestamp, in #seconds since epoch. May be negative
        """
        now = time.time()
        expire = self._created + self._exp_hours * 60 * 60
        return expire - now

    @abc.abstractmethod
    def write(self, bytes):
        pass

    @abc.abstractmethod
    def writeln(self, bytes):
        pass

    @abc.abstractmethod
    def to_file(self, f):
        pass

    def __str__(self):
        return self._ref

class TemporaryBlobBuffer(TemporaryBlob):
    def __init__(self, expire_hours=0):
        TemporaryBlob.__init__(self, expire_hours=expire_hours)
        self._chunks = []

    def write(self, bytes):
        self._chunks.append(bytes)

    def writeln(self, bytes):
        self._chunks.append(bytes + self.LINE_SEP)

    def to_file(self, f):
        for chunk in self._chunks:
            f.write(chunk)

class TemporaryBlobShockNode(TemporaryBlob):
    def __init__(self, expire_hours=24):
        TemporaryBlob.__init__(self, expire_hours=expire_hours)
        ref = '1234' # XXX: Create a temporary shock node and this is the reference
        self.set_id(ref)

    def to_file(self, f):
        # XXX: Pull data from shock node and write to file
        pass

