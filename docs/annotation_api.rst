.. include:: wsref.txt

.. _annotation_api:

Annotation Data API
===================

The Annotation API can be used as a library or in client/server mode.

.. contents::

.. py:currentmodule:: doekbase.data_api.annotation.genome_annotation

Creating an Annotation
----------------------

To create a new taxon, you will create an object that implements the interface defined in :class:`doekbase.data_api.annnotation.genome_annotation.api.GenomeInterface`.

* From the KBase Narrative (or within any Python program), instantiate the :class:`doekbase.data_api.annotation.genome_annotation.GenomeAnnotationAPI` class. This will communicate with the back-end database directly::

    my_ann = GenomeAnnotationAPI(
        token=os.environ.get('KB_AUTH_TOKEN'),      # Authorization token
        services={'workspace_service_url': ws_url}, # Workspace Service to contact, 
                                                    #   e.g., ws_url='https://kbase.us/services/ws/'
        ref=ref)                                    # Object reference (see below)
    

* If, instead, you are using Python or another language as a client, and running the GenomeAnnotationAPI within a Thrift server, you would use :class:`doekbase.data_api.annotation.genome_annotation.GenomeAnnotationClientAPI` in Python or the equivalent in the target language.

In either case you will instantiate the class with an object reference, in the format expected by the KBase workspace: |wsref|.


Genome annotation object interface
----------------------------------

The interface used by both the client/server and local Python library APIs is shown below.

Feature description codes
+++++++++++++++++++++++++

.. autodata:: FEATURE_DESCRIPTIONS
    :annotation:

Interface
+++++++++

.. autoclass:: GenomeInterface
    :members:

Examples
--------

Below are example(s) in Python and, "real soon now", in JavaScript.

Python examples
+++++++++++++++

Example: Write proteins as a FASTA file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../lib/doekbase/data_api/tests/examples/genome_annotation_api.py
    :linenos:
    :pyobject: proteins_to_fasta

