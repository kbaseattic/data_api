KBase Data API documentation
============================

.. toctree::
   :maxdepth: 2

Semantic type system
--------------------

.. py:currentmodule:: data_api.semantics

The ``semantics`` module implements a basic description language for describing
how types relate to each other (a "type system"). The base object in this
system is a :class:`Type`:

.. autoclass:: Type

    .. automethod:: __init__(self, spec)

Types can reference each other by name (in fact, that's almost required for
this whole model to make any sense), so there needs to be a class that
can know about multiple types at once. This class is called :class:`TypeSystem`:

.. autoclass:: TypeSystem

    .. automethod:: __init__(self, spec)

You can add all your types to the `TypeSystem` class with the `add` method:

.. automethod:: TypeSystem.add(self, type_)

Then, once you have added all your types, you can get serialized schema
that combine all the types in a way that's palatable to a given format.
Right now, the only supported format is `Avro`:

.. automethod:: TypeSystem.as_avro(self, name)

There aren't any CLI tools yet, but you can see an example of this being
exercised in the `tests/test_semantics.py` unit test.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

