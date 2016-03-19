.. JavaScript documentation master file

KBase JavaScript Data API documentation
========================================

.. toctree::

    Assembly API <clients/js/assembly>
    Genome Annotation API <clients/js/genome_annotation>
    Taxon API <clients/js/taxon>

The Data API provides a unified entry point to retrieve and, eventually,
store KBase data objects. This page describes the JavaScript client API.
All APIs use the Thrift protocol to communicate between the client and server.

Packaging with Require
----------------------
The JavaScript client API wraps the Thrift auto-generated API. It is packaged
so that it can be easily included in other JavaScript projects with ``require``.

Asynchronous API with Promises
------------------------------
Because it is meant to be used in interactive widgets and web pages, the
API has also been implemented using an asynchronous ``promise`` interface:
every call returns a promise object immediately, and the caller can decide
when and how to wait for the result. The API uses the "bluebird" promises
library; for more information see `this tutorial page <http://bluebirdjs.com/docs/why-promises.html>`_ and `the bluebird code on github <https://github.com/petkaantonov/bluebird/>`_.
