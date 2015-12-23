.. include:: ../wsref.txt

.. _js_javascript_taxon_data_api:

JavaScript Taxon Data API
=========================
The Taxon API can be used as a client of the Python server.

.. contents::

Creating a Taxon object
-----
To create a new object, instantiate :js:class:`Taxon`
using a configuration object as the input argument.

.. code-block:: javascript

    // access reference data (no token required)
    var api_obj = Taxon({
        ref: '1013/92/2',
        url: 'http://narrative.kbases.us',
        token: '',
        timeout: 6000
    })

Taxon interface
-----------------
.. js:class:: Taxon(config)

    :param object config: Configuration object. This object has the following fields:
    * ref - The object reference for the object to be accessed in the format expected by the workspace: |wsref|.
    * url - The url for the GenomeAnnotation Service endpoint.
    * token - The KBase authorization token to be used to access the service.
    :throws ArgumentError:

.. js:function:: get_info()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: ObjectInfo

.. js:function:: get_history()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: ObjectHistory

.. js:function:: get_provenance()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: ObjectProvenance

.. js:function:: get_id()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: i64

.. js:function:: get_name()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: string

.. js:function:: get_version()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: string

.. js:function:: get_parent()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: ObjectReference

.. js:function:: get_children()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: list<ObjectReference>

.. js:function:: get_genome_annotations()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: list<ObjectReference>

.. js:function:: get_scientific_lineage()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: list<string>

.. js:function:: get_scientific_name()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: string

.. js:function:: get_taxonomic_id()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: i32

.. js:function:: get_kingdom()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: string

.. js:function:: get_domain()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: string

.. js:function:: get_genetic_code()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: i32

.. js:function:: get_aliases()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: list<string>

----

.. js:class:: ObjectInfo()

================== ========================== ==========
type               attr                       optional
================== ========================== ==========
i64                object_id                  Optional
string             object_name                Optional
string             object_reference           Optional
string             object_reference_versioned Optional
string             type_string                Optional
string             save_date                  Optional
i64                version                    Optional
string             saved_by                   Optional
i64                workspace_id               Optional
string             workspace_name             Optional
string             object_checksum            Optional
i64                object_size                Optional
map<string,string> object_metadata            Optional
================== ========================== ==========


----

.. js:class:: ExternalDataUnit()

====== ===================== ==========
type   attr                  optional
====== ===================== ==========
string resource_name         Optional
string resource_url          Optional
string resource_version      Optional
string resource_release_date Optional
string data_url              Optional
string data_id               Optional
string description           Optional
====== ===================== ==========


----

.. js:class:: ObjectProvenanceAction()

====================== =========================== ==========
type                   attr                        optional
====================== =========================== ==========
string                 time                        Optional
string                 service_name                Optional
string                 service_version             Optional
string                 service_method              Optional
list<binary>           method_parameters           Optional
string                 script_name                 Optional
string                 script_version              Optional
string                 script_command_line         Optional
list<string>           input_object_references     Optional
list<string>           validated_object_references Optional
list<string>           intermediate_input_ids      Optional
list<string>           intermediate_output_ids     Optional
list<ExternalDataUnit> external_data               Optional
string                 description                 Optional
====================== =========================== ==========


----

.. js:class:: ServiceException()

================== ========== ==========
type               attr       optional
================== ========== ==========
string             message    Required
string             stacktrace Optional
map<string,string> inputs     Optional
================== ========== ==========


----

.. js:class:: AuthorizationException()

====== ========== ==========
type   attr       optional
====== ========== ==========
string message    Required
string stacktrace Optional
====== ========== ==========


----

.. js:class:: AuthenticationException()

====== ========== ==========
type   attr       optional
====== ========== ==========
string message    Required
string stacktrace Optional
====== ========== ==========


----

.. js:class:: ObjectReferenceException()

====== ========== ==========
type   attr       optional
====== ========== ==========
string message    Required
string stacktrace Optional
====== ========== ==========


----

.. js:class:: AttributeException()

====== ========== ==========
type   attr       optional
====== ========== ==========
string message    Required
string stacktrace Optional
====== ========== ==========


----

.. js:class:: TypeException()

============ =========== ==========
type         attr        optional
============ =========== ==========
string       message     Required
string       stacktrace  Optional
list<string> valid_types Optional
============ =========== ==========
