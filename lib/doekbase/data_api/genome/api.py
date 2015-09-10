"""
Simple example client.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/13/15'

# Imports

# Stdlib
import abc
import sys
# Third-party
import spec_pb2 as pb
# Local
from doekbase.data_api.util import get_logger
from doekbase.data_api.util import log_start, log_end

# Logging

_log = get_logger('genome.api')

# Constants

NAMESPACE = 'GenomeAnnotation'  # for the registry

# Classes and functions

class GenomeAnnotationAPI:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def get_info(self, ref):
        pass

    @abc.abstractmethod
    def get_taxon(self, ref):
        pass

