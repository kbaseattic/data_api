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

    .. automethod:: __init__

For the client, use instead `TaxonClientAPI`:

.. autoclass:: TaxonClientAPI

    .. automethod:: __init__
    

In both cases the object reference is in the format expected by the
KBase workspace: |wsref|. 

Basic operations
----------------

The basic operations are documented in the parent class to both library and client/server, ``TaxonInterface``.

.. autoclass:: TaxonInterface
    :members: get_parent, get_children, get_scientific_name, get_taxonomic_id, get_kingdom, get_domain, get_aliases, get_genetic_code

Example 1: Fetch and print taxon name
+++++++++++++++++++++++++++++++++++++

.. code-block:: python
    :linenos:

        from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
        taxon = TaxonAPI(token=os.environ.get('KB_AUTH_TOKEN', ref='1019/4'))
        print('Got taxon "{} ({})".format(taxon.get_scientific_name(),
                                           taxon.get_taxonomic_id()))

In line 1, we import the module and the API class that we intend to use (the library version). In line 2, the API is initialized and the target object is given as the main parameter. After this step, the methods of the instance can be used to fetch and show taxonomic information (lines 3-4).

Advanced operations
-------------------

The advanced operations are (also) documented in the parent class to both library and client/server, ``TaxonInterface``.

.. autoclass:: TaxonInterface
    :members: get_scientific_lineage, get_genome_annotations

