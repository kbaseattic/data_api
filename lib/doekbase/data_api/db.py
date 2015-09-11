"""
PEP-249 style database API for KBase databases
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/12/15'

from abc import ABCMeta, abstractmethod

# Globals
apilevel = '1.0'
threadsafety = 0
paramstyle = 'pyformat'  # Not used

# Exceptions
class StandardError(Exception):
    pass
class Warning(StandardError):
    pass
class Error(StandardError):
    pass
class InterfaceError(StandardError):
    pass
class DatabaseError(StandardError):
    pass
class DataError(DatabaseError):
    pass
class OperationalError(DatabaseError):
    pass
class IntegrityError(DatabaseError):
    pass
class InternalError(DatabaseError):
    pass
class ProgrammingError(DatabaseError):
    pass
class NotSupportedError(DatabaseError):
    pass

# Base types

class BaseConnection:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def cursor(self):
        pass
