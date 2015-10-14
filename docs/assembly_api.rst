.. include:: wsref.txt

.. _assembly_api:

Assembly Data API
===================

The assembly API can be used as a library or in client/server mode.

.. contents::

.. py:currentmodule:: doekbase.data_api.assembly.genome_assembly

Creating an assembly
--------------------------

To create a new assembly, you will create an object that implements the interface defined in :class:`doekbase.data_api.sequence.assembly.api.GenomeInterface`. If you are using the
Python library (see
:ref:`overview_diagram`), then you can instantiate the :class:`doekbase.data_api.sequence.assembly.AssemblyAPI` class. This will communicate with the back-end database directly. This is the mode used when you are creating code in Python code cells in the KBase Narrative.

If instead you are using Python or another language as a client, and running the AssemblyAPI within a Thrift server, you would use :class:`doekbase.data_api.sequence.assembly.AssemblyClientAPI` in Python or the equivalent in the target language.

In either case you will instantiate the class with an object reference, in the format expected by the KBase workspace: |wsref|.


Assembly object interface
-------------------------

The interface used by both the client/server and local Python library APIs is shown below.

Interface
+++++++++

.. autoclass:: AssemblyInterface
    :members:

Examples
--------

Below are example(s) in Python and, "real soon now", in JavaScript.

Python examples
+++++++++++++++

