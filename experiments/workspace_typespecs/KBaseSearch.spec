#include <KBaseGenomes.spec>

/*
@author kkeller,mhenderson,shinjae
*/


module KBaseSearch {    
    /*
    	Reference to a ContigSet object containing the contigs for this genome in the workspace
		@id ws KBaseSearch.ContigSet
	*/
    typedef string contigset_ref;
    /*
		Reference to a ProteinSet object containing the proteins for this genome in the workspace
		@id ws KBaseSearch.ProteinSet
	*/
    typedef string proteinset_ref;
    /*
		Reference to a Feature object in the workspace
		@id ws KBaseSearch.Feature
	*/
    typedef string search_feature_ref;
    /*
		Reference to a FeatureSet object in the workspace
		@id ws KBaseSearch.SearchFeatureSet
	*/
    typedef string search_featureset_ref;
    /*
		Reference to a TranscriptSet object containing the transcripts for this genome in the workspace
		@id ws KBaseSearch.TranscriptSet
	*/
    typedef string transcriptset_ref;
    /*
		Reference to a source_id
		@id external SEED GenBank MicrobesOnline
	*/
    typedef string source_id;
    /*
		KBase genome ID
		@id kb
	*/
    typedef string genome_id;
    /*
		Genome feature ID
		@id external
	*/
    typedef string feature_id;
    /*
		Reference to an individual contig in a ContigSet object
		@id subws KBaseSearch.ContigSet.contigs.[].id
	*/
    typedef string contig_ref;
    /*
		ContigSet contig ID
		@id external
	*/
    typedef string contig_id;
    /*
		KBase contig set ID
		@id kb
	*/
    typedef string contigset_id;
    /*
		Reference to a source_id
		@id external
	*/
    typedef string source_id;
    /*
		Reference to a reads file in shock
		@id shock
	*/
    typedef string reads_ref;
    /*
		Reference to a fasta file in shock
		@id shock
	*/
    typedef string fasta_ref;

    /* Type spec for a "Contig" subobject in the "ContigSet" object

		contig_id id - ID of contig in contigset
		string md5 - unique hash of contig sequence
		string sequence - sequence of the contig
		string description - Description of the contig (e.g. everything after the ID in a FASTA file)

		@optional length name description
		@searchable ws_subset id md5
	*/
	typedef structure {
		contig_id id;
		int length;
		string md5;
		string sequence;
		string name;
		string description;
    } Contig;

	/* Type spec for the "ContigSet" object

		contigset_id id - unique kbase ID of the contig set
		string name - name of the contig set
		string type - type of the contig set (values are: Organism,Environment,Collection)
		source_id source_id - source ID of the contig set
		string source - source of the contig set
		list<Contig> contigs - list of contigs in the contig set
		reads_ref reads_ref - reference to the shocknode with the rawreads from which contigs were assembled
		fasta_ref fasta_ref - reference to fasta file from which contig set were read

		@optional name md5 source_id source type reads_ref fasta_ref
        @searchable ws_subset contigs.*.(id,md5) md5 id name source_id source type
	*/
	typedef structure {
		contigset_id id;
		string name;
		string md5;
		source_id source_id;
		string source;
		string type;
		reads_ref reads_ref;
		fasta_ref fasta_ref;
		mapping<contig_id, Contig> contigs;
    } ContigSet;

	/*
		Type of a genome feature with possible values peg, rna
	*/
    typedef string feature_type;
    /* A region of DNA is maintained as a tuple of four components:

		the contig
		the beginning position (from 1)
		the strand
		the length

	   We often speak of "a region".  By "location", we mean a sequence
	   of regions from the same genome (perhaps from distinct contigs).
    */
    typedef tuple<string contig_id, int begin, string strand,int length, int ordinal> region_of_dna;
    /*
		a "location" refers to a list of regions of DNA on contigs
    */
    typedef list<region_of_dna> location;
    /*
		a notation by a curator of the genome object
    */
    typedef tuple<string comment, string annotator, int annotation_time> annotation;

    /*
	Structure for a publication (from ER API)
	also want to capture authors, journal name (not in ER)

    */
    typedef tuple<int id, string source_db, string article_title, string link, string pubdate, string authors, string journal_name> publication;

    /*
	Structure for subsystem data (from CDMI API)

    */
    typedef tuple<string subsystem, string variant, string role> subsystem_data;

    /*
	Structure for regulon data (from CDMI API)

    */
    typedef tuple<string regulon_id, list<feature_id> regulon_set, list<feature_id> tfs> regulon_data;

    /*
	Structure for an atomic regulon (from CDMI API)

    */
    typedef tuple<string atomic_regulon_id, int atomic_regulon_size> atomic_regulon;

    /*
	Structure for co-occurring fids (from CDMI API)

    */
    typedef tuple<feature_id scored_fid, float score> co_occurring_fid;

    /*
	Structure for coexpressed fids (from CDMI API)

    */
    typedef tuple<feature_id scored_fid, float score> coexpressed_fid;




    /*
	Structure for a protein family
		@optional query_begin query_end subject_begin subject_end score evalue subject_description release_version
    */
    typedef structure {
		string id;
		string subject_db;
		string release_version;
		string subject_description;
		int query_begin;
		int query_end;
		int subject_begin;
		int subject_end;
		float score;
		float evalue;
    } ProteinFamily;


    typedef string source_db;
    typedef string alias;

    /*
    	Structure for a single feature of a Genome
	Should genome_id contain the genome_id in the Genome object,
	the workspace id of the Genome object, a genomeref,
	something else?
	
		@optional function md5 feature_source_id protein_translation protein_families subsystems roles feature_publications subsystems subsystem_data aliases annotations regulon_data atomic_regulons coexpressed_fids co_occurring_fids dna_sequence protein_translation_length dna_sequence_length
		@searchable ws_subset feature_id feature_type function aliases md5
    */
    typedef structure {
		feature_id feature_id;
		genome_id genome_id;
		location location;
		feature_type feature_type;
		string function;
		string md5;
		string feature_source_id;
		string protein_translation;
		string dna_sequence;
		int protein_translation_length;
		int dna_sequence_length;
		list<string> roles;
		list<publication> feature_publications;
		list<string> subsystems;
		list<ProteinFamily> protein_families;
		mapping<source_db,list<alias> > aliases;
		list<annotation> annotations;
		list<subsystem_data> subsystem_data;
		list<regulon_data> regulon_data;
		list<atomic_regulon> atomic_regulons;
		list<coexpressed_fid> coexpressed_fids;
		list<co_occurring_fid> co_occurring_fids;
    } Feature;

    /*
        Type definition for an IndividualFeature
        IndividualFeatures can either be a  Feature structure
        (contained in the data field) or a reference to a
        Feature object (contained in the ref field)
        (Technically it could be both; not sure how to handle that yet)

        @optional data ref
    */
    typedef structure {
        Feature data;
        search_feature_ref ref;
    } IndividualFeature;

	/* Type spec for the "FeatureSet" object

		should not need searchable attribute for a ref
		#searchable ws_subset features.*.(feature_id,genome_id,function,md5)
	*/
    typedef structure {
        mapping<feature_id, IndividualFeature> features;
    } SearchFeatureSet;

    /*
    	Genome object holds much of the data relevant for a genome in KBase
	Genome publications should be papers about the genome, not
	papers about certain features of the genome (which go into the
	Feature object)
	Should the Genome object have a list of feature ids? (in
	addition to having a list of feature_refs)
	Should the Genome object contain a list of contig_ids too?

    	@optional md5 taxonomy gc_content complete dna_size num_contigs contig_lengths genome_source genome_source_id domain genome_publications contigset_ref proteinset_ref transcriptset_ref featureset_ref
    	@searchable ws_subset num_contigs genome_source_id genome_source genetic_code genome_id scientific_name domain taxonomy contigset_ref proteinset_ref transcriptset_ref featureset_ref
    */
    typedef structure {
		genome_id genome_id;
		string scientific_name;
		string domain;
		int genetic_code;
		int dna_size;
		int num_contigs;
		mapping<contig_id, int> contig_lengths;
		string genome_source;
		source_id genome_source_id;
		string md5;
		string taxonomy;
		float gc_content;
		int complete;
		list<publication> genome_publications;

		search_featureset_ref featureset_ref;
		contigset_ref contigset_ref;
		proteinset_ref proteinset_ref;
		transcriptset_ref transcriptset_ref;
    } Genome;



	/*
	    @id ws KBaseGenomes.Genome
	*/
	typedef string genome_ref;

	/*
        This type represents an element of a GenomeSet.
        Either ref or data is defined for an element, but not both.
        @optional metadata
        @optional ref
        @optional data
	*/
	typedef structure {
		mapping<string, string> metadata;
		genome_ref ref;
		KBaseGenomes.Genome data;
	} GenomeSetElement;

	/*
	    A type describing a set of Genomes, where each element of the set 
	    is an embedded Genome object or a Genome object reference.
	*/
	typedef structure {
		string description;
		mapping<string, GenomeSetElement> elements;
	} GenomeSet;


	/*
	    @id ws KBaseGenomes.Feature
	*/
	typedef string feature_ref;

	/*
        This type represents an element of a GenomeSet.
        Either ref or data is defined for an element, but not both.
        @optional metadata
        @optional ref
        @optional data
	*/
	typedef structure {
		mapping<string, string> metadata;
		feature_ref ref;
		KBaseGenomes.Feature data;
	} FeatureSetElement;

	/*
	    A type describing a set of Genomes, where each element of the set 
	    is an embedded Genome object or a Genome object reference.
	*/
	typedef structure {
		string description;
		mapping<string, FeatureSetElement> elements;
	} FeatureSet;



	/*
		A gene_id is a string (usually kb.g.NNNN.CCC.NNNN, but can be free-form)
	*/
	typedef string gene_id;

    /*
        An evidence code is a string (in the future, from a controlled vocabulary)
    */
    typedef string evidence_code;

	/*
        A gene list is a list of gene_ids
	*/
	typedef list<gene_id> gene_list;

	/*
		Structure for Ontology object

		@optional evidence_codes
	*/
	typedef structure {
        string ontology_id;
        string ontology_type;
        string ontology_domain;
        string ontology_description;
        list<evidence_code> evidence_codes;
        mapping<genome_id,gene_list> gene_list;
    } Ontology;


    typedef structure {
        string cmd_name;
        mapping<string, string> cmd_args;
        string cmd_description;
        int max_runtime;
        mapping<string, string> opt_args;
    } CommandConfig;

    typedef structure {
        mapping<string, mapping<string, CommandConfig>> config_map;
    } Type2CommandConfig;

};




