"""
Mapping of data store types to object classes.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '7/31/15'

from enum import  Enum # requires enum34
from biokbase.data_api.assembly import AssemblyAPI
from biokbase.data_api.genome_annotation import GenomeAnnotationAPI
from biokbase.data_api.taxon import TaxonAPI
from biokbase.data_api.object import ObjectAPI

class DataStores(Enum):
    """The huge variety of data stores we have at the moment."""
    workspace = 1

## Mapping from a type name to a wrapper class, used in `get_class`
_typemap = {
    'KBaseGenomes.ContigSet-2.0': AssemblyAPI,
    'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation': GenomeAnnotationAPI,
    'KBaseGenomesCondensedPrototypeV2.Taxon': TaxonAPI
}

def get_object_class(type_name, store=DataStores.workspace):
    """Get the appropriate object class for a given type name.

    Args:
      type_name - string name of type
      store - type of data store (currently only 'workspace')

    Returns:
      appropriate subclass of ObjectAPI (possibly just the base class)
    """
    clazz = None
    if store == DataStores.workspace:
        clazz = _typemap.get(type_name, ObjectAPI)
    return clazz