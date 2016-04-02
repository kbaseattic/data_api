.. include:: ../wsref.txt

.. _py_taxon_api:

Taxon Data API
==============

The Python Taxon API can be used as a library or in client/server mode.

.. py:currentmodule:: doekbase.data_api.taxonomy.taxon.api

Creating a TaxonAPI object
---------------------------

To create a new TaxonAPI object, you will create an object that implements the interface defined in :class:`doekbase.data_api.taxonomy.taxon.api.TaxonInterface`. This class can implement a library or a Thrift client. In either case you will instantiate the class with an object reference. The interfaces used by both classes are shown below.

Python Library: TaxonAPI
^^^^^^^^^^^^^^^^^^^^^^^^

If you are using the Python library, then you can instantiate the :class:`doekbase.data_api.taxonomy.taxon.api.TaxonAPI` class. This will communicate with the back-end database directly. This is the mode used when you are creating code in Python code cells in the KBase Narrative.

.. py:class:: TaxonAPI

    .. py:method:: __init__(services=None, token=None, ref=None)

    Construct a new TaxonAPI object, which connects directly to the
    KBase backend stores.

    :param dict services: Dictionary with service urls, including:
        workspace_service_url for the Workspace service, e.g.
        "https://kbase.us/services/ws/".
    :param str token: KBase login token
    :param str ref: KBase object reference, in the format expected by the
        KBase workspace: |wsref|.

For example::

    import os
    from doekbase.data_api.taxonomy.taxon import api
    
    obj = api.TaxonAPI(
        token=os.environ.get('KB_AUTH_TOKEN'),
        services={'workspace_service_url': 'https://kbase.us/services/ws/'},
        ref=ref)
    

Thrift Service: TaxonClientAPI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If instead you are using Python or another language as a client, and running the TaxonAPI within a Thrift server, you would use :class:`doekbase.data_api.taxonomy.taxon.api.TaxonClientAPI` in Python or the equivalent in the target language.

.. py:class:: TaxonClientAPI

    .. py:method:: __init__(self, url=None, token=None, ref=None)

    Construct a TaxonClientAPI object, connected to a Thrift Taxon service
    that proxies the communication to the KBase backend stores (or its own
    cache).

    :param str url: A URL in the format `host:port` for the Thrift Taxon
        service.
    :param str token: KBase login token
    :param str ref: KBase object reference, in the format expected by the
        KBase workspace: |wsref|.

For example::

    import os
    from doekbase.data_api.taxonomy.taxon import api
    
    obj = api.TaxonClientAPI(
        token=os.environ.get('KB_AUTH_TOKEN'),
        url='https://kbase.us/services/data/taxon/',
        ref=ref)

API Reference
-------------

Both the ``TaxonAPI`` and ``TaxonAPIClient`` implement all the following methods.

.. note:: The client methods will return object references as strings, whereas the Python library methods will instantiate the object references.

.. autoclass:: TaxonInterface
    :members:
