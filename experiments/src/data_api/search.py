"""
The search APIs are broken down into the different types of data stores in the
system:

* :class:`DataStore` - Data objects and their relationships
* :class:`DataModel` - Data types and their relationships

Each data store is represented with a separate subclass
of the parent "SearchableData".
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '4/8/15'

class SearchableData(object):
    """Base functionality for any searchable data source.
    """
    pass

class DataStore(SearchableData):
    """Store of data objects.
    """
    def __init__(self):
        """Main data store.
        """

class DataModel(SearchableData):
    """Store of data types, which together form a data model (type system).
    """
    pass

