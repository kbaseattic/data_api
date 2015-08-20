.. lib documentation master file, created by
   sphinx-quickstart on Fri Aug  7 16:25:28 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

KBase Data API documentation
============================
The Data API provides a unified entry point to retrieve and, eventually,
store KBase data objects.


On this page
------------

.. contents::

    :depth: 1

API Reference
-------------
.. toctree::
    :maxdepth: 2

    biokbase.data_api

Using the Data API
==================

There are two primary modes of using the Data API: interactively and programmatically.
Interactively, the API can be imported into in the IPython/Jupyter notebook or
Narrative and used to explore and examine data objects.
Results will be automatically displayed as HTML and inline plots. Programmatically,
the same API can be imported into any Python code and used like a standard
library.

.. note::

    The integration of the Data API into the KBase Narrative is not quite
    done yet. For now, you need to try it out in a recent (August 2015+)
    version of the Jupyter notebook.

In both cases, the :ref:`core-api` functions are used to access the objects.
For interactive use, and some programmatic use-cases, the :ref:`highlevel-api`
will be more convenient.

.. _highlevel-api:

High-level API
--------------
This section covers how to :ref:`initialize the high-level API <highlevel-api-conf>`
to access the KBase data as an authenticated user,
then how to :ref:`use the provided functions <highlevel-api-func>`.

.. _highlevel-api-conf:

Configuration and Authorization
+++++++++++++++++++++++++++++++

.. _highlevel-api-func:

Functions
+++++++++

.. _core-api:

Core API
--------
This section covers how to initialize the high-level API to access the KBase
data as an authenticated user, then how to use the provided functions.

Configuration and Authorization
+++++++++++++++++++++++++++++++

Functions
+++++++++

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

