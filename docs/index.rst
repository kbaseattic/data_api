.. lib documentation master file, created by
   sphinx-quickstart on Fri Aug  7 16:25:28 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
    :maxdepth: 4

    create_api
    API Reference <modules>

KBase Data API documentation
============================
The Data API provides a unified entry point to retrieve and, eventually,
store KBase data objects. A simplified view of how the Data API relates to other
components of KBase is below::

    +------------------------------+
    |Services/Narrative code cells |
    +------------------------------+
        |                    ^
        v                    |
    *******************************
    ||     Data API library      ||
    *******************************
        ^                    |
        |                    v
    +-----------------------------+
    |     Workspace/Datastores    |
    +-----------------------------+
    

Using the Data API
==================

There are two primary modes of using the Data API: interactively and programmatically.
Interactively, the API can be imported into in the IPython/Jupyter notebook or
Narrative and used to explore and examine data objects.
Results will be automatically displayed as HTML and inline plots. Programmatically,
the same API can be imported into any Python code and used like a standard
library.

.. note:: 
  The integration of the Data API into the KBase Narrative is not quite done yet. 
  For now, you need to try it out in a recent (August 2015+) version of the Jupyter notebook.

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

Developer notes
===============

Running tests
-------------
Unit tests can be run with a file-based Workspace library, based on the
mongomock package and implemented in the `biokbase.data_api.wsfile` module.

This mode is activated by passing a directory path instead of a
regular URL to the `--ws-url` option for nosetests. This nosetest option is
enabled by a plugin in `biokbase.data_api.tests.nose_plugin_wsurl`,
that is referred to by the "entry_points" key in the configuration in the
setup.py script. It is recommended that you also pass the `--wsfile-msgpack`
option and use the msgpack output option when creating the input data (see below).

Step 1: Create test data
++++++++++++++++++++++++

To create the test data for the file-based workspace, you need to dump some existing workspace objects into a directory. This is done with the `dump_wsfile` script in the bin/ directory (also installed by setup.py in the package bin path). An example invocation of this script is::

    dump_wsfile --url ci  --file test_data/test-objects.txt --msgpack --dir test_data -vv

This would dump all object IDs found in the file `test_data/test-objects.txt`
into the directory `test_data`, using the CI (continuous integration) workspace
server, formatting them using `MessagePack <http://msgpack.org/>`_.

An `objects.txt` file simply lists full object IDs, i.e. "<workspace>/<object>[/<version>]", one per line. Lines starting with
"#" and blank lines are ignored. For example::

    # Genome
    PrototypeReferenceGenomes/kb|g.3899
    # Features
    PrototypeReferenceGenomes/kb|g.3899_feature_container_gene
    PrototypeReferenceGenomes/kb|g.3899_feature_container_CDS
    PrototypeReferenceGenomes/kb|g.3899_feature_container_mRNA
    # Taxon
    993/674615/1

Step 2: Run tests
+++++++++++++++++
After this is done, the command-line to nosetests would look like this::

  nosetests --ws-url=test_data  --wsfile-msgpack

The `--ws-url` option gives the path to the entire directory of files, and the `--wsfile-msgpack` means that it will load all the files ending in ".msgpack" in that directory into the file-based mongo mocking library for
the tests.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

