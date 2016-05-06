.. include:: ../wsref.txt

.. _py_assembly_api:

Assembly Data API
===================

The Python Assembly API can be used as a library or in client/server mode.

.. py:currentmodule:: doekbase.data_api.sequence.assembly.api

Creating an AssemblyAPI object
------------------------------

To create a new AssemblyAPI object, you will create an object that implements the interface defined in :class:`doekbase.data_api.sequence.assembly.api.AssemblyInterface`. 

In either case you will instantiate the class with an object reference, in the format expected by the KBase workspace: |wsref|.

Python Library: AssemblyAPI
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are using the Python library, then you can instantiate the :class:`doekbase.data_api.sequence.assembly.api.AssemblyAPI` class. This will communicate with the back-end database directly. This is the mode used when you are creating code in Python code cells in the KBase Narrative.

.. py:class:: AssemblyAPI

    .. py:method:: __init__(services=None, token=None, ref=None)

        Construct a new AssemblyAPI object, which connects directly to the
        KBase backend stores.

        :param dict services: Dictionary with service urls, including:
            workspace_service_url for the Workspace service, e.g.
            "https://kbase.us/services/ws/".
        :param str token: KBase login token:param str ref: KBase object reference, in the format expected by the
            KBase workspace: |wsref|.
        
For example::

    import os
    from doekbase.data_api.sequence.assembly import api
    
    obj = api.AssemblyAPI(
        token=os.environ.get('KB_AUTH_TOKEN'),
        services={'workspace_service_url': 'https://kbase.us/services/ws/'},
        ref=ref)
    

Thrift Service: AssemblyClientAPI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If instead you are using Python or another language as a client, and running the AssemblyAPI within a Thrift server, you would use :class:`doekbase.data_api.sequence.assembly.api.AssemblyClientAPI` in Python or the equivalent in the target language.

.. py:class:: AssemblyClientAPI

    .. py:method:: __init__(self, url=None, token=None, ref=None)

    Construct an AssemblyClientAPI object, connected to a Thrift Assembly service
    that proxies the communication to the KBase backend stores (or its own
    cache).

    :param str url: A URL for the Thrift Assembly data API service.
    :param str token: KBase login token
    :param str ref: KBase object reference, in the format expected by the
        KBase workspace: |wsref|.

For example::

    import os
    from doekbase.data_api.sequence.assembly import api
    
    obj = api.AssemblyClientAPI(
        token=os.environ.get('KB_AUTH_TOKEN'),
        url='https://kbase.us/services/data/assembly/',
        ref=ref)

API Reference
-------------

Both the ``AssemblyAPI`` and ``AssemblyAPIClient`` implement all the following methods.

.. note:: The client methods will return object references as strings, whereas the Python library methods will instantiate the object references.

.. autoclass:: AssemblyInterface
    :members:
