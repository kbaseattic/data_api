.. include:: wsref.txt

.. _taxon_api:

Taxon Data API
==============

The Taxon API can be used as a library or in client/server mode.

.. contents::

.. py:currentmodule:: doekbase.data_api.taxonomy.taxon.api

Creating a Taxonomic object
--------------------------

To create a new taxon, you will create an object that implements the interface defined in :class:`doekbase.data_api.taxonomy.taxon.api.TaxonInterface`. If you are using the Python library (see :ref:`overview_diagram`), then you can instantiate the :class:`doekbase.data_api.taxonomy.taxon.api.TaxonAPI` class. This will communicate with the back-end database directly. This is the mode used when you are creating code in Python code cells in the KBase Narrative.

If instead you are using Python or another language as a client, and running the TaxonAPI within a Thrift server, you would use :class:`doekbase.data_api.taxonomy.taxon.api.TaxonClientAPI` in Python or the equivalent in the target language.

In either case you will instantiate the class with an object reference, in the format expected by the KBase workspace: |wsref|. 

Taxon object interface
----------------------

The interface used by both the client/server and local Python library APIs is shown below.

.. autoclass:: TaxonInterface
    :members:

Examples
--------

Below are example(s) in Python and, "real soon now", in JavaScript.

Python examples
+++++++++++++++

For the following examples, assume the file has the following imports
at the top of your file, Jupyter notebook, or KBase Narrative (in a code cell)::

    import os
    from doekbase.data_api.taxonomy.taxon.api import TaxonAPI

The code for all the examples is contained in the
``doekbase.data_api.tests.examples.taxon_api`` module.

.. include:: kbauth.txt

Example: Fetch and Print Taxon
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: ../lib/doekbase/data_api/tests/examples/taxon_api.py
    :linenos:
    :pyobject: fetch_and_print_taxon

