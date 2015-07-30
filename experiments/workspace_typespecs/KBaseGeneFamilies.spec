#include <KBaseTrees.spec>

module KBaseGeneFamilies {

	typedef string domain_library_id;

	/*
		enum: CDD, SMART, Pfam, etc
	*/
	typedef string domain_source;

	/*
		date in ISO 8601 format; e.g., 2014-11-26
	*/
	typedef string date;

	/*
		enum: hmmscan-3.1b1, rpsblast-2.2.30
	*/
	typedef string program_version;

	/*
		enum: PSSM, HMM-Family, HMM-Domain, HMM-Repeat, HMM-Motif
	*/
	typedef string model_type;

	typedef string domain_accession;
	
	/*
		accession - accession of domain model (e.g., PF00244.1, or COG0001)
		cdd_id - (optional) in case of CDD it's inner id which is reported by rps-blast program
		name - name of domain model
		description - description of domain model
		length - length of profile
		model_type - domain model type
		trusted_cutoff - (optional) trusted cutoff of domain model for HMM libraries
		@optional cdd_id trusted_cutoff
	*/
	typedef structure {
		domain_accession accession;
		string cdd_id;
		string name;
		string description;
		int length;
		model_type model_type;
		float trusted_cutoff;
	} DomainModel;

	typedef structure {
		string file_name;
		string shock_id;
	} Handle;

	/* @id ws KBaseGeneFamilies.DomainLibrary */
	typedef string ws_lib_id;

	/*
		id - id of library
		source - source of library (e.g., Cog, Pfam, ...)
		source_url - ftp/http url where library can be downloaded 
		version - version of library release
		release_date - release date of library
		program - program for running domain search
		domain_prefix - prefix of domain accession defining library
		dbxref_prefix - url prefix for db-external referencing
		library_files - library files stored in Shock storage
		domains - domain information
	*/
	typedef structure {
		domain_library_id id;
		domain_source source;
		string source_url;
		string version;
		date release_date;
		program_version program;
		string domain_prefix;
		string dbxref_prefix;
		list<Handle> library_files;
		mapping<domain_accession accession, DomainModel> domains;
	} DomainLibrary;

	/* 
		@id ws KBaseGeneFamilies.DomainModelSet
	*/
	typedef string dms_ref;

	/*
		string set_name - name of model set
	*/
	typedef structure {
		string set_name;
		mapping<string domain_prefix, ws_lib_id> domain_libs;
		mapping<string domain_prefix, string dbxref_prefix> domain_prefix_to_dbxref_url;
		mapping<domain_accession domain_accession, string description> domain_accession_to_description;
	} DomainModelSet;

	/* 
		@id ws KBaseGenomes.Genome
	*/
	typedef string genome_ref;

	/* 
		@id ws KBaseGeneFamilies.DomainCluster
	typedef string domain_cluster_ref;
	*/

	typedef tuple<int start_in_feature,int stop_in_feature,float evalue,
		float bitscore, float domain_coverage> domain_place;

/*
	typedef tuple<string contig_id,string feature_id,int feature_index,
		list<domain_place>> domain_cluster_element;
*/

	/* @id ws KBaseTrees.MSA
	typedef string ws_alignment_id;
 */

	/* @id ws KBaseTrees.MSASet
	typedef string msa_set_ref;
 */

	/* @id ws KBaseTrees.Tree
	typedef string ws_tree_id;
 */

	/*
		domain_accession model - reference to domain model
		domain_cluster_ref parent_ref - optional reference to parent cluster (containing data 
			describing some common set of genomes)
		mapping<genome_ref,list<domain_cluster_element>> data - list of entrances of this domain 
			into different genomes (domain_cluster_element -> ;
			domain_place -> tuple<int start_in_feature,int stop_in_feature,float evalue,
				float bitscore,float domain_coverage>).
		ws_alignment_id msa_ref - reference to multiple alignment object where all domain 
			sequences are collected (keys in this MSA object are constructed according to this 
			pattern: <genome_ref>_<feature_id>_<start_in_feature>), field is not set in case
			clusters are stored inside DomainClusterSearchResult object, use 'msas' field of
			DomainClusterSearchResult object instead.
		@optional parent_ref
		@optional msa_ref
	typedef structure {
		domain_accession model;
		domain_cluster_ref parent_ref;
		mapping<genome_ref,list<domain_cluster_element>> data;
		ws_alignment_id msa_ref;
	} DomainCluster;
	*/

	typedef tuple<string feature_id,int feature_start,int feature_stop,int feature_dir,
		mapping<domain_accession,list<domain_place>>> annotation_element;

	typedef string contig_id;

	/* 
		@id ws KBaseGeneFamilies.DomainAlignments
	typedef string domain_alignments_ref;
	*/

	/*
		genome_ref genome_ref - reference to genome
		dms_ref used_dms_ref - domain models used for search
		mapping<contig_id, list<annotation_element>> data - 
			list of entrances of different domains into proteins of annotated genome
			(annotation_element -> typedef tuple<string feature_id,int feature_start,int feature_stop,
				int feature_dir,mapping<domain_accession,list<domain_place>>>;
			domain_place -> tuple<int start_in_feature,int stop_in_feature,float evalue,
				float bitscore,float domain_coverage>).
		mapping<contig_id, tuple<int size,int features>> contig_to_size_and_feature_count - 
			feature count and nucleotide size of every contig
		mapping<string feature_id, tuple<contig_id,int feature_index> feature_to_contig_and_index - 
			index of every feature in feature list in every contig
	*/
	typedef structure {
		genome_ref genome_ref;
		dms_ref used_dms_ref;
		mapping<contig_id, list<annotation_element>> data;
		mapping<contig_id, tuple<int size,int features>> contig_to_size_and_feature_count;
		mapping<string feature_id, tuple<contig_id,int feature_index>> feature_to_contig_and_index;
		/* domain_alignments_ref alignments_ref; */
	} DomainAnnotation;

	/*
		genome_ref genome_ref - reference to genome
		alignments - alignments of domain profile against region in feature sequence stored as 
			mapping from domain model reference to inner mapping from feature id to inner-inner 
			mapping from start position of alignment in feature sequence to aligned sequence of 
			domain occurrence (mapping<domain_accession, mapping<string feature_id,
				mapping<string start_in_feature, string alignment_with_profile>>>).
	typedef structure {
		genome_ref genome_ref;
		mapping<domain_accession,mapping<string feature_id,
			mapping<string start_in_feature,string alignment_with_profile>>> alignments; 
	} DomainAlignments;
	*/

	/* 
		@id ws KBaseGeneFamilies.DomainAnnotation
	*/
	typedef string domain_annotation_ref;

	/* 
		@id ws KBaseGeneFamilies.DomainClusterSearchResult
	typedef string dcsr_ref;
	*/

	/*
		Aggregated data for every genome.
	typedef structure {
		genome_ref genome_ref;
		string kbase_id;
		string scientific_name;
		int features;
		int features_with_domains;
		int domain_models;
		int domains;
	} GenomeStat;
	*/

	/*
		Aggregated data for every domain cluster.
	typedef structure {
		domain_accession domain_accession;
		string name;
		int genomes;
		int features;
		int domains;
	} DomainClusterStat;	
	*/

	/*
		dcsr_ref parent_ref - optional reference to parent domain clusters search results
		dms_ref used_dms_ref - domain models used for search
		mapping<genome_ref, DomainAnnotation> annotations - found domains in genomes that user 
			defined as input data for domain search
		mapping<genome_ref, DomainAlignment> alignments - alignments for found domains in genomes 
			that user defined as input data for domain search
		mapping<genome_ref, domain_annotation_ref> annotation_refs - domain annotation references 
			in case we don't want to store annotations and alignments inside result object
		mapping<domain_accession, DomainCluster> domain_clusters - clusters constructed based on 
			query_genomes plus genomes from parent object
		mapping<domain_accession, domain_cluster_ref> domain_cluster_refs - references to clusters 
			in case we don't want to store these clusters inside search result object
		mapping<domain_accession, KBaseTrees.MSA> msas - multiple alignment objects where all domain sequences 
			are collected (keys in these MSA objects are constructed according to such pattern: 
			<genome_ref>_<feature_id>_<start_in_feature>), in case this field is not set or has
			empty mapping msa_refs field should be used
		mapping<domain_accession, ws_alignment_id> msa_refs - references to multiple alignment objects 
			where all domain sequences are collected (keys in these MSA objects are constructed 
			according to such pattern: <genome_ref>_<feature_id>_<start_in_feature>)
		mapping<domain_accession, KBaseTrees.Tree> trees - trees built for MSAs stored in msas field
		mapping<domain_accession, ws_tree_id> tree_refs - trees built for MSAs stored in msa_refs field
		@optional parent_ref
		@optional used_dms_ref
		@optional annotations
		@optional alignments
		@optional annotation_refs
		@optional domain_clusters
		@optional domain_cluster_refs
		@optional msas
		@optional msa_refs
		@optional trees
		@optional tree_refs
	typedef structure {
		dcsr_ref parent_ref;
		dms_ref used_dms_ref;
		mapping<genome_ref, DomainAnnotation> annotations;
		mapping<genome_ref, DomainAlignments> alignments;
		mapping<genome_ref, domain_annotation_ref> annotation_refs;
		mapping<genome_ref, GenomeStat> genome_statistics;
		mapping<domain_accession, DomainCluster> domain_clusters;
		mapping<domain_accession, domain_cluster_ref> domain_cluster_refs;
		mapping<domain_accession, KBaseTrees.MSA> msas;
		mapping<domain_accession, ws_alignment_id> msa_refs;
		mapping<domain_accession, DomainClusterStat> domain_cluster_statistics;
		mapping<domain_accession, KBaseTrees.Tree> trees;
		mapping<domain_accession, ws_tree_id> tree_refs;
	} DomainClusterSearchResult;
	*/

	/*
		genome_ref genome - genome for domain annotation process
		dms_ref dms_ref - set of domain models that will be searched in defined genome
		string out_workspace - output workspace
		string out_result_id - id of resulting object of type DomainAnnotation
	*/
	typedef structure {
		genome_ref genome;
		dms_ref dms_ref;
		string out_workspace;
		string out_result_id;
	} SearchDomainsParams;
	
	funcdef search_domains(SearchDomainsParams params) returns (string job_id) authentication required;

	/* returns version number of service */
	funcdef version() returns (string version);

	/*
		list<domain_annotation_ref> genome_annotations - annotated genome list
		dcsr_ref clusters_for_extension - clusters already constructed for another set of genomes 
			(public ones for example)
		dms_ref dms_ref - set of domain models that were used for search in defined genomes,
			this value is stored in resulting DomainClusterSearchResult object (optional 
			field, if it's not set then one from clusters_for_extension object will be used)
		string out_workspace - output workspace
		string out_result_id - id of resulting object of type DomainSearchResult
		int is_domain_cluster_data_stored_outside - defines should domain clusters be stored 
			outside of DomainClusterSearchResult object (using domain_cluster_refs rather than 
			domain_clusters field), default value is 0
		string domain_cluster_data_id_prefix - used for domain cluster objects id generation 
			([prefix.]domain_name[.suffix])
		string domain_cluster_data_id_suffix - used for domain cluster objects id generation 
			([prefix.]domain_name[.suffix])
		@optional dms_ref
		@optional clusters_for_extension
		@optional is_domain_cluster_data_stored_outside
		@optional domain_cluster_data_id_prefix
		@optional domain_cluster_data_id_suffix
	typedef structure {
		list<domain_annotation_ref> genome_annotations;
		dcsr_ref clusters_for_extension;
		dms_ref dms_ref;
		string out_workspace;
		string out_result_id;
		int is_domain_cluster_data_stored_outside;
		string domain_cluster_data_id_prefix;
		string domain_cluster_data_id_suffix;
	} ConstructDomainClustersParams;

	funcdef construct_domain_clusters(ConstructDomainClustersParams params) returns 
		(string job_id) authentication required;
	*/

	/*
		list<genome_ref> genomes - genome list
		dcsr_ref clusters_for_extension - clusters already constructed for another set of genomes 
			(public ones for example)
		dms_ref dms_ref - set of domain models that will be searched in defined genomes (optional 
			field, you can use only clusters_for_extension or both for clusters extension
			using narrowed set of domains)
		string out_workspace - output workspace
		string out_result_id - id of resulting object of type DomainSearchResult
		int is_genome_annotation_stored_outside - defines should genome annotations be stored 
			outside of DomainClusterSearchResult object (using annotation_refs rather than 
			annotations field), default value is 0
		string genome_annotation_id_prefix - used for genome domain annotation objects id 
			generation ([prefix.]genome_name[.suffix])
		string genome_annotation_id_suffix - used for genome domain annotation objects id 
			generation ([prefix.]genome_name[.suffix])
		int is_domain_cluster_data_stored_outside - defines should domain clusters be stored 
			outside of DomainClusterSearchResult object (using domain_cluster_refs rather than 
			domain_clusters field), default value is 0
		string domain_cluster_data_id_prefix - used for domain cluster objects id generation 
			([prefix.]domain_name[.suffix])
		string domain_cluster_data_id_suffix - used for domain cluster objects id generation 
			([prefix.]domain_name[.suffix])
		@optional dms_ref
		@optional clusters_for_extension
		@optional is_genome_annotation_stored_outside
		@optional genome_annotation_id_prefix
		@optional genome_annotation_id_suffix
		@optional is_domain_cluster_data_stored_outside
		@optional domain_cluster_data_id_prefix
		@optional domain_cluster_data_id_suffix
	typedef structure {
		list<genome_ref> genomes;
		dcsr_ref clusters_for_extension;
		dms_ref dms_ref;
		string out_workspace;
		string out_result_id;
		int is_genome_annotation_stored_outside;
		string genome_annotation_id_prefix;
		string genome_annotation_id_suffix;
		int is_domain_cluster_data_stored_outside;
		string domain_cluster_data_id_prefix;
		string domain_cluster_data_id_suffix;
	} SearchDomainsAndConstructClustersParams;

	funcdef search_domains_and_construct_clusters(SearchDomainsAndConstructClustersParams params) 
		returns (string job_id) authentication required;
	*/

};


