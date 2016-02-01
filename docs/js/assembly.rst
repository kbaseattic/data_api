.. include:: ../wsref.txt

.. _js_javascript_assembly_data_api:

JavaScript Assembly Data API
============================
The Assembly API can be used as a client of the Python server.

.. contents::

Creating an Assembly object
---------------------------
To create a new object, instantiate :js:class:`Assembly`
using a configuration object as the input argument.

.. code-block:: javascript

    // access reference data (no token required)
    var api_obj = Assembly({
        ref: '1013/92/2',
        url: 'http://narrative.kbases.us',
        token: '',
        timeout: 6000
    })

Assembly interface
------------------
.. js:class:: Assembly(config)

    :param object config: Configuration object. This object has the following
    fields:
        * ref - The object reference for the object to be accessed in the format expected by the workspace: |wsref|.
        * url - The url for the GenomeAnnotation Service endpoint.
        * token - The KBase authorization token to be used to access the service.

    :throws ArgumentError:

.. js:function:: get_assembly_id()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: string

.. js:function:: get_genome_annotations()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: list<ObjectReference>

.. js:function:: get_external_source_info()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns:  :js:class:`AssemblyExternalSourceInfo` 

.. js:function:: get_stats()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns:  :js:class:`AssemblyStats` 

.. js:function:: get_number_contigs()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: i64

.. js:function:: get_gc_content()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: double

.. js:function:: get_dna_size()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: i64

.. js:function:: get_contig_ids()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: list<string>

.. js:function:: get_contig_lengths(contig_id_list)

    :param list<string> contig_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,i64>

.. js:function:: get_contig_gc_content(contig_id_list)

    :param list<string> contig_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,double>

.. js:function:: get_contigs(contig_id_list)

    :param list<string> contig_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string, :js:class:`AssemblyContig` >

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


----

.. js:class:: AssemblyStats()

====== =========== ==========
type   attr        optional
====== =========== ==========
i64    num_contigs Optional
i64    dna_size    Optional
double gc_content  Optional
====== =========== ==========


----

.. js:class:: AssemblyExternalSourceInfo()

====== ================================ ==========
type   attr                             optional
====== ================================ ==========
string external_source                  Optional
string external_source_id               Optional
string external_source_origination_date Optional
====== ================================ ==========


----

.. js:class:: AssemblyContig()

====== =========== ==========
type   attr        optional
====== =========== ==========
string contig_id   Optional
string sequence    Optional
i64    length      Optional
double gc_content  Optional
string md5         Optional
string name        Optional
string description Optional
bool   is_complete Optional
bool   is_circular Optional
====== =========== ==========
