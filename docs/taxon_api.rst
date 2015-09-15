.. include:: wsref.txt

Taxon Data API
==============

The API can be used as a library or in client/server mode.

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
    :members: get_parent, get_children, get_scientific_name, get_taxonomic_id, get_kingdom, get_domain, get_aliases
