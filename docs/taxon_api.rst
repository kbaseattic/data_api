.. include:: wsref.txt

Taxon Data API
==============

The API can be used as a library or in client/server mode.

.. contents::

.. py:currentmodule:: doekbase.data_api.taxonomy.taxon.api

Getting a Taxonomic object
--------------------------

To get a taxon, create an instance of the `TaxonAPI` class.
 
.. autoclass:: TaxonAPI
    :noindex:

    .. automethod:: __init__

For the client, use instead `TaxonClientAPI`:

.. autoclass:: TaxonClientAPI
    :noindex:

    .. automethod:: __init__
    

In both cases the object reference is in the format expected by the
KBase workspace: |wsref|. 

Basic operations
----------------

The basic operations are documented in the parent class to both library and client/server, ``TaxonInterface``.

.. autoclass:: TaxonInterface
    :noindex:
    :members: get_parent, get_children, get_scientific_name, get_taxonomic_id, get_kingdom, get_domain, get_aliases, get_genetic_code

Examples
++++++++

For the following examples, assume the file has the following imports
at the top::

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

Advanced operations
-------------------

The advanced operations are (also) documented in the parent class to both library and client/server, ``TaxonInterface``.

.. autoclass:: TaxonInterface
    :noindex:
    :members: get_scientific_lineage, get_genome_annotations

