"""
The search APIs are broken down into the different types of data stores in the
system:

* :class:`DataStore` - Data objects and their relationships
* :class:`DataModel` - Data types and their relationships
* :class:`UserActivity` - Users and usage
* :class:`MethodStore` - Method and service specifications

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
    def __init__(self, public=False):
        """Create with special flag to indicate fully 'public'
        data source (i.e. reference data).

        :param public: Is all data public?
        :type public: bool
        """
        self._refdata = public

class DataModel(SearchableData):
    """Store of data types, which together form
    a data model.
    """
    pass

class UserActivity(SearchableData):
    """Store of information about users and their activities.
    """
    pass

class MethodStore(SearchableData):
    """Store of information about "methods", which are any
    transformations of data and parameters (possibly chainable,
    so this should include workflows).
    """
    pass
