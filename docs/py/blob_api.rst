.. _py_blob_api:

Blob API
==========

The Python Blob API can *only* be used as a library. And at the moment, it is really a
placeholder for a more general and powerful API that can abstract the details of the
Python blob store.

.. py:currentmodule:: doekbase.data_api.blob.blob

The abstract base `Blob` class defines the interface.

.. autoclass:: Blob
    :members: write, writeln, to_file

Other classes inherit from `Blob` and implement specific semantics.

.. autoclass:: BlobShockNode

.. autoclass:: BlobBuffer



