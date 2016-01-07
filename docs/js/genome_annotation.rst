.. include:: ../wsref.txt

.. _js_javascript_genome_annotation_data_api:

JavaScript Genome annotation Data API
=====================================
The Genome annotation API can be used as a client of the Python server.

.. contents::

Creating a GenomeAnnotation object
-----------------
To create a new object, instantiate :js:class:`GenomeAnnotation`
using a configuration object as the input argument.

.. code-block:: javascript

    // access reference data (no token required)
    var api_obj = GenomeAnnotation({
        ref: '1013/92/2',
        url: 'http://narrative.kbases.us',
        token: '',
        timeout: 6000
    })

Genome annotation interface
-----------------
.. js:class:: GenomeAnnotation(config)

    :param object config: Configuration object. This object has the following fields:
    * ref - The object reference for the object to be accessed in the format expected by the workspace: |wsref|.
    * url - The url for the GenomeAnnotation Service endpoint.
    * token - The KBase authorization token to be used to access the service.
    :throws ArgumentError:

.. js:function:: get_taxon()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: ObjectReference

.. js:function:: get_assembly()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: ObjectReference

.. js:function:: get_feature_types()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: list<string>

.. js:function:: get_feature_type_descriptions(feature_type_list)

    :param list<string> feature_type_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,string>

.. js:function:: get_feature_type_counts(feature_type_list)

    :param list<string> feature_type_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,i64>

.. js:function:: get_feature_ids(filters, group_type)

    :param Feature_id_filters filters:
    :param string group_type:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: Feature_id_mapping

.. js:function:: get_features(feature_id_list)

    :param list<string> feature_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,Feature_data>

.. js:function:: get_proteins()

    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,Protein_data>

.. js:function:: get_feature_locations(feature_id_list)

    :param list<string> feature_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,list<Region>>

.. js:function:: get_feature_publications(feature_id_list)

    :param list<string> feature_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,list<string>>

.. js:function:: get_feature_dna(feature_id_list)

    :param list<string> feature_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,string>

.. js:function:: get_feature_functions(feature_id_list)

    :param list<string> feature_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,string>

.. js:function:: get_feature_aliases(feature_id_list)

    :param list<string> feature_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,list<string>>

.. js:function:: get_cds_by_gene(gene_id_list)

    :param list<string> gene_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,list<string>>

.. js:function:: get_cds_by_mrna(mrna_id_list)

    :param list<string> mrna_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,string>

.. js:function:: get_gene_by_cds(cds_id_list)

    :param list<string> cds_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,string>

.. js:function:: get_gene_by_mrna(mrna_id_list)

    :param list<string> mrna_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,string>

.. js:function:: get_mrna_by_cds(gene_id_list)

    :param list<string> gene_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,string>

.. js:function:: get_mrna_by_gene(gene_id_list)

    :param list<string> gene_id_list:
    :throws ServiceException:
    :throws AuthorizationException:
    :throws AuthenticationException:
    :throws ObjectReferenceException:
    :throws AttributeException:
    :throws TypeException:
    :returns: map<string,list<string>>

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

.. js:class:: Region()

====== ========= ==========
type   attr      optional
====== ========= ==========
string contig_id Optional
string strand    Optional
i64    start     Optional
i64    length    Optional
====== ========= ==========


----

.. js:class:: Feature_id_filters()

============ ============= ==========
type         attr          optional
============ ============= ==========
list<string> type_list     Optional
list<Region> region_list   Optional
list<string> function_list Optional
list<string> alias_list    Optional
============ ============= ==========


----

.. js:class:: Feature_id_mapping()

================================================ =========== ==========
type                                             attr        optional
================================================ =========== ==========
map<string,list<string>>                         by_type     Optional
map<string,map<string,map<string,list<string>>>> by_region   Optional
map<string,list<string>>                         by_function Optional
map<string,list<string>>                         by_alias    Optional
================================================ =========== ==========


----

.. js:class:: Feature_data()

======================== =========================== ==========
type                     attr                        optional
======================== =========================== ==========
string                   feature_id                  Optional
string                   feature_type                Optional
string                   feature_function            Optional
map<string,list<string>> feature_aliases             Optional
i64                      feature_dna_sequence_length Optional
string                   feature_dna_sequence        Optional
string                   feature_md5                 Optional
list<Region>             feature_locations           Optional
list<string>             feature_publications        Optional
list<string>             feature_quality_warnings    Optional
list<string>             feature_quality_score       Optional
list<string>             feature_notes               Optional
string                   feature_inference           Optional
======================== =========================== ==========


----

.. js:class:: Protein_data()

============ =========================== ==========
type         attr                        optional
============ =========================== ==========
string       protein_id                  Optional
string       protein_amino_acid_sequence Optional
string       protein_function            Optional
list<string> protein_aliases             Optional
string       protein_md5                 Optional
list<string> protein_domain_locations    Optional
============ =========================== ==========
