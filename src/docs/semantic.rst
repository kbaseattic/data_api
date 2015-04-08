Semantic type system
====================

.. contents::

.. py:currentmodule:: data_api.semantics

The ``semantics`` module implements a basic description language for describing
how types relate to each other (a "type system").

Type
----

The base object in this system is a :class:`Type`:

.. autoclass:: Type

    .. automethod:: __init__(self, spec)

Statement
---------

The statements that form the inter-type relationships can use, as their
predicate, the constants defined in the :class:`Statement` class:

.. autoclass:: Statement
    :members:

Type system
-----------

To parse and validate Type statements, and output a coherent joint schema,
there needs to be a class that can know about multiple types at once.
This class is called :class:`TypeSystem`:

.. autoclass:: TypeSystem

    .. automethod:: __init__(self, spec)

You can add all your types with the :meth:`TypeSystem.add` method:

.. automethod:: TypeSystem.add(self, type_)

Then, once you have added all your types, you can get serialized schema
that combine all the types in a way that's palatable to a given format.
Right now, the only supported format is `Avro <https://avro.apache.org/>`_:

.. automethod:: TypeSystem.as_avro(self, name)

Examples
--------

You can see usage examples in the ``tests/test_semantics.py`` unit test.

