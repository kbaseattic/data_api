.. _developer_notes:

Developer notes
================

This page provides notes on how to test and run the APIs for developers.

Unit tests can be run with a file-based Workspace library, based on the
mongomock package and implemented in the `biokbase.data_api.wsfile` module.

This mode is activated by passing a directory path instead of a
regular URL to the `--ws-url` option for nosetests. This nosetest option is
enabled by a plugin in `biokbase.data_api.tests.nose_plugin_wsurl`,
that is referred to by the "entry_points" key in the configuration in the
setup.py script. It is recommended that you also pass the `--wsfile-msgpack`
option and use the msgpack output option when creating the input data (see below).

1. Create test data

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

2. Run tests

After this is done, the command-line to nosetests would look like this::

  nosetests --ws-url=test_data  --wsfile-msgpack

The `--ws-url` option gives the path to the entire directory of files, and the `--wsfile-msgpack` means that it will load all the files ending in ".msgpack" in that directory into the file-based mongo mocking library for
the tests.