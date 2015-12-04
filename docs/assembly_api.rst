.. include:: wsref.txt

.. _assembly_api:

Assembly Data API
===================

The assembly API can be used as a library or in client/server mode.

.. contents::

.. py:currentmodule:: doekbase.data_api.sequence.assembly.api

Creating an Assembly object
----------------------------

To create a new Assembly object, you will create an object that implements the interface defined in :class:`doekbase.data_api.sequence.assembly.api.AssemblyInterface`. This class can implement a library or a Thrift client. 
In either case you will instantiate the class with an object reference. The interfaces used by both classes are shown below.

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
    :param str token: KBase login token
    :param str ref: KBase object reference, in the format expected by the
        KBase workspace: |wsref|.

Thrift Service: AssemblyClientAPI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If instead you are using Python or another language as a client, and running the AssemblyAPI within a Thrift server, you would use :class:`doekbase.data_api.sequence.assembly.api.AssemblyClientAPI` in Python or the equivalent in the target language.

.. py:class:: AssemblyClientAPI

    .. py:method:: __init__(self, url=None, token=None, ref=None)

    Construct an AssemblyClientAPI object, connected to a Thrift Assembly service
    that proxies the communication to the KBase backend stores (or its own
    cache).

    :param str url: A URL in the format `host:port` for the Thrift Assembly
        data API service.
    :param str token: KBase login token
    :param str ref: KBase object reference, in the format expected by the
        KBase workspace: |wsref|.

Common API methods
^^^^^^^^^^^^^^^^^^

Both the `AssemblyAPI` and `AssemblyAPIClient` implement all the following methods.

.. autoclass:: AssemblyInterface
    :members:

Examples
--------

Below are example(s) in Python and, "real soon now", in JavaScript.

