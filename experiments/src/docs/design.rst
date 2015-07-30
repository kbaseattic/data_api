Design notes
============

This is a record of results of various discussions. The idea is that the most
recent "conclusions" are presented, but sometimes there have been
different ideas over time and they are not resolved. Nothing here represents a final design decision. However, decisions are being made as necessary in order to drive the prototyping efforts and avoid paralysis.

Notes from specific discussions will reference an abbreviation as defined below:

* ``DM_0408`` - Dan Gunter & Matt Henderson, April 8 2015

.. _sample_queries:

Sample queries
^^^^^^^^^^^^^^

Try to model the requirements of the system by listing the `top 20 queries <http://research.microsoft.com/en-us/collaboration/fourthparadigm/4th_paradigm_book_part1_szalay.pdf>`_. We're not to 20 yet, but here's a start:

* for this model, show me associated genomes
* how many genomes have at least one gene that produces this protein
* show me what connects to this model
* what can I do with a model
* what can I do with a matrix of values


Object mutability
^^^^^^^^^^^^^^^^^

``DM_0408``

Current w.s. makes objects immutable. This has some benefits. You can go back
to earlier versions of the object, and references to an object can
retain their integrity. However as we start to think about the possibility of search across the user data (not something that is enabled at any deep level right now), we quickly hit the problem that you don't actually want to search every old object. So you may want to consider making objects mutable, with a log of the deltas to allow rewinding. On the other hand, this solution doesn't address the issue of not changing data to which there is a reference.

Here is a diagram::

                        +---------+
                        |         |
    +-----------+       +      +--v-----+
    |           +---->Modify   | deltas |
    | original  |        +     +--+-----+
    +-----+-----+        |        |
          ^              |        |
          |              |        v
          |              |      viewable
          +--------------+      (narrative landing
                save            pages)


Services
^^^^^^^^

``DM_0408``

Science services may want to consume more low-level objects, like tables, matrices and arrays. Rather than letting services go outside the KBase type system, one idea is to think of two level of science services:

* Services, which always consume KBase types (and have KBase provenance etc.)
* Functions, which can consume lower-level types (see Generic Types, below). These can still be understood by the system, have provenance, and be plugged together by the service in whatever way the service sees fit. Functions might be programs that already exist, which consume files or operate on matrices.

Generic types
^^^^^^^^^^^^^

``DM_0408``

KBase needs a set of "generic types" to represent data arrangements that combine, concatenate, munge, or subset existing KBase conceptual types. These belong in a separate branch of the type hierarchy, and can be treated differently by the system in some ways -- e.g., not downloadable or uploadable directly by any defined methods of KBase.

Generic types needed:

* table - e.g. coefficients
* matrix
* dictionary
* list
* set

Datastores in the system
^^^^^^^^^^^^^^^^^^^^^^^^

``DM_0408``

Some original ideas along this line were to break the datastores into 4 pieces: main datastore, data model, user info and activity, and the services/method store. But after talking through some `sample queries`_, it seemed clear that a lot of things need to co-exist in order for the relationships between them to be navigated. Thus, the new list of datastores is more like:

* Datastore: scientific data, operations (scientific methods), users (who is working on what, who owns what), annotations
* Data models: Type relationships
* Service API registry: discovery for core KBase official APIs as well as community or contributed APIs


