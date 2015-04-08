Search API
==========

.. automodule:: data_api.search

It is an open question whether there is anything in the base
:class:`SearchableData` class,
i.e., whether there is a common set of search methods or a common
language in which queries can be expressed. One option is to go the
relational route, and allow a subset of SQL to be used as a common
search language in every API (regardless of underlying implementation,
which *could* be something besides a relational store, although that
would clearly imply some extra effort on our part).

.. py:currentmodule:: data_api.search

.. autoclass:: SearchableData

.. autoclass:: DataStore
    :members:
    :special-members:

.. autoclass:: DataModel

.. autoclass:: UserActivity

.. autoclass:: MethodStore