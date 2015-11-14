.. include:: wsref.txt

.. _taxon_api:

Taxon Data API
==============

The Taxon API can be used as a library or in client/server mode.

.. contents::

.. py:currentmodule:: doekbase.data_api.taxonomy.taxon.api

Creating a Taxonomic object
---------------------------

To create a new Taxon object, you will create an object that implements the interface defined in :class:`doekbase.data_api.taxonomy.taxon.api.TaxonInterface`. This class can implement a library or a Thrift client. In either case you will instantiate the class with an object reference. The interfaces used by both classes are shown below.

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

Common API methods
^^^^^^^^^^^^^^^^^^

Both the `TaxonAPI` and `TaxonAPIClient` implement all the following methods.

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

