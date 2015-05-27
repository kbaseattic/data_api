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

"""
WIP
"""
from .semantics import Type

class Node(object):
    def __init__(self, type_=None):
        """
        :type type_: Type
        """
        self._type = type_

    def get(self, subset=()):
        """Projection operator."""
        return [getattr(self, name) for name in subset]

    def find_related(self, node_type=None, edge_type=None,
                     node_filter=None, edge_filter=None, max_depth=0):
        """Find all related nodes of type `node_type` that are related
        by edges of type `edge_type`. Filter nodes and edges according to
        values in `node_filter` and `edge_filter`.
        Look `max_depth` nodes away from the origin, with values <= 0
        meaning no limit.

        :return: List of Node
        """
        pass

    