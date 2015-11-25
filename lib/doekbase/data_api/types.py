"""
Mapping of data store types to object classes.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '7/31/15'

# System
import re

# Third-party
from enum import  Enum # requires enum34

# Local
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.annotation.genome_annotation import GenomeAnnotationAPI
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.data_api.core import ObjectAPI

class DataStores(Enum):
    """The huge variety of data stores we have at the moment."""
    workspace = 1

## Mapping from a type name to a wrapper class, used in `get_class`
_typemap = {
    r'KBaseGenomes\.ContigSet-2\.0': AssemblyAPI,    
    r'KBaseGenomeAnnotations\.Assembly': AssemblyAPI,
    r'KBaseGenomeAnnotations\.GenomeAnnotation': GenomeAnnotationAPI,
    r'KBaseGenomes\.Genome-.*': GenomeAnnotationAPI,
    r'KBaseGenomeAnnotations\.Taxon': TaxonAPI
}

def get_re(d, key, default_value):
    """Get key from dict, but treat keys *in* dict as regular
     expressions.

     Args:
       d: Dictionary to search
       key: String key
       default_value: A default value, any type

     Returns:
       matching value or `default_value` if not found
    """
    for dkey, dval in d.items():
        if re.match(dkey, key):
            return dval
    return default_value

def get_object_class(type_name, store=DataStores.workspace):
    """Get the appropriate object class for a given type name.

    Args:
      type_name - string name of type
      store - type of data store (currently only 'workspace')

    Returns:
      appropriate subclass of Data (possibly just the base class)
    """
    clazz = None
    if store == DataStores.workspace:
        clazz = get_re(_typemap, type_name, ObjectAPI)
    return clazz