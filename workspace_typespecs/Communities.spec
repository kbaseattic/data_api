/*
@author Andreas Wilke, Travis Harrsion 
*/


/*
Include types from other modules

#include <KBaseFile.types>

   include KBase::Genomes;
   include KBase::Common;
   parent  KBase::Metagenome # just example

*/


module Communities {

/*
URI in form of a URL, e.g. ftp:// or http://...
*/
typedef string URI ;

/*typedef string url;
*/

typedef string Timestamp ;

/*
Data type , is controlled vocabulary. e.g. AbundanceData , Genome, Metagenome, ...
*/

typedef string DataType;
typedef string FileType;

typedef structure {
        string ID ;
        URI URL ;
} Reference ;

typedef structure {
    string name;
    DataType type;
    Timestamp created;
    string data;
} Data;

typedef structure {
    string name;
    DataType dataType;
    FileType fileType;
    Timestamp created;
    Reference ref;
} DataHandle;

typedef structure{
        string name;
        DataType type;
        Timestamp created ;
        list<Reference> members ;
} Collection;

typedef list<Reference> List ;

typedef Reference Library ;
typedef Reference Sample ; 
typedef Reference Project;
typedef DataHandle SequenceFile ;

/*
Metadata fields, for e.g metageome
@optional type
*/

    typedef structure {
        string id;
        string name;
        string type;
        mapping<string, string> data;
    } Metadata;


typedef structure {
        list<string> columns;
        list<list<float>> data;
} StatMatrix;

typedef structure {
        list<string> columns;
        list<float> data;
} StatList;

typedef structure {
        StatList summary;
        StatMatrix percents;
        StatMatrix counts;
} Drisee;

typedef structure {
        mapping<string, StatMatrix> bp_profile;
        mapping<string, StatMatrix> kmer;
        Drisee drisee;    
} StatsQC;

    typedef structure {
    	string id;
    	string generated_by;
    	Timestamp date;
    	string format;
    	URI format_url;
    	URI url;
      
    	string type;
    	string matrix_type;
    	string matrix_element_type;
    	string matrix_element_value;
       
    	tuple<int, int> shape;
    	list<string> rows;
    	list<string> columns;
    	list<list<float>> data;
	} Biom;

	typedef structure {
		Reference sequences;
		Metadata metadata;
		Reference workflow;
	} SequenceSet;

	typedef structure {
		Reference 	sequenceSet;
		Reference	Workflow;
		Metadata	parameter;
		Biom		data;
	} Profile;


typedef structure {
        mapping<string, mapping<string, list<int>>> source;
        mapping<string, list<tuple<string, int>>> ontology;
        mapping<string, list<tuple<string, int>>> taxonomy;
        mapping<string, float> sequence_stats;
        mapping<string, list<tuple<float, int>>> gc_histogram;
        mapping<string, list<tuple<float, int>>> length_histogram;
        StatsQC qc;
        list<tuple<int, float>> rarefaction;
} Statistics;


    /*
     Metagenome
    */
		
    typedef structure {
        string id;
        string job_id;        
        string name; 
        string sequence_type;
        string status;
        URI url;
        Timestamp created;        

        int mixs_compliant;
        int version;
        string pipeline_version;

        tuple<string, string> project;
        tuple<string, string> library;
        tuple<string, string> sample;

        mapping<string, string> pipeline_parameters;
        mapping<string, string> mixs;
        mapping<string, Metadata> metadata;
        
        Statistics statistics;
    } Metagenome;


/*
    @id ws Communities.Metagenome 
*/	   

typedef string metagenome_ref;

/*
        This type represents an element of a MetagenomeSet.
        Either ref or data is defined for an element, but not both.
        @optional metadata
        @optional ref
        @optional data
*/
	typedef structure {
		mapping<string, string> metadata;
		metagenome_ref ref;
		Metagenome data;
	} MetagenomeSetElement;

/*
 A type describing a set of Metagenomes, where each element of the set 
 is an embedded Metagenome object or a Metagenome object reference.
*/

typedef structure {
  string description;
  mapping<string, MetagenomeSetElement> elements;
} MetagenomeSet;




	 /*
		BiomMetagenomeEntry
		A KBase object for a profile entry in the metagenome profile object
		@optional name metadata metagenome
		#searchable BiomMetagenomeEntry.*
	*/
	
	typedef structure {
    	string id;
    	string name;
	string metagenome;
	/*
    	mapping<string, Metadata> metadata;
	*/
	mapping<string,string> metadata;
	} BiomMetagenomeEntry;

	 /*
		BiomMatrixEntry
		A KBase object for a profile entry in the metagenome profile object
		@optional name metadata metagenome
		#searchable BiomMetagenomeEntry.*
	*/
	
	typedef structure {
    	string id;
    	string name;
	string metagenome;
    	mapping<string, Metadata> metadata;
	} BiomMatrixEntry;
	
	 /*
		BiomAnnotationEntry
		A KBase object for a profile entry in the metagenome profile object
		@optional name metadata
		searchable BiomAnnotationEntry.*
	*/


	typedef structure {
    	string id;
    	string name;
    	mapping<string, list<string>> metadata;
	} BiomAnnotationEntry;






	/*
		BiomMetagenome
		A KBase object for a metagenome profile in BIOM format
		@optional url matrix_element_value metagenomes
		searchable BiomMetagenome.*
	*/


	typedef structure {
    	string id;
    	string generated_by;
	MetagenomeSet metagenomes;
    	Timestamp date;
    	string format;
    	URI format_url;
    	URI url;
       
    	string type;
    	string matrix_type;
    	string matrix_element_type;
    	string matrix_element_value;
       
    	tuple<int, int> shape;
    	list<BiomAnnotationEntry> rows;
    	list<BiomMetagenomeEntry> columns;
    	list<list<float>> data;
	} BiomMetagenome;

	/*
		BiomMatrix
		A KBase object for a metagenome profile in BIOM format
		@optional url matrix_element_value metagenomes
		searchable BiomMetagenome.*
	*/


	typedef structure {
    	string id;
    	string generated_by;
	MetagenomeSet metagenomes;
    	Timestamp date;
    	string format;
    	URI format_url;
    	URI url;
       
    	string type;
    	string matrix_type;
    	string matrix_element_type;
    	string matrix_element_value;
       
    	tuple<int, int> shape;
    	list<BiomAnnotationEntry> rows;
    	list<BiomMatrixEntry> columns;
    	list<list<float>> data;
	} BiomMatrix;
	
	typedef BiomMetagenome TaxonomicProfile;
	typedef BiomMetagenome FunctionalProfile;
	typedef BiomMatrix TaxonomicMatrix;
	typedef BiomMatrix FunctionalMatrix;
	
	typedef BiomMetagenome MetagenomeMatrix;
	typedef BiomMetagenome MetagenomeProfile;

	/* PCoA Typespec */

typedef structure {
    string id;
    string group;
    list<float> pco;
} PCoAMember;

typedef structure {
    list<float> pco;
    list<PCoAMember> data;
} PCoA;

/* Heatmap Typespec */

typedef structure {
    list<list<float>> data;
    list<string> rows;
    list<string> columns;
    list<float> colindex;
    list<float> rowindex;
    list<list<int>> coldend;
    list<list<int>> rowdend;
} Heatmap;

};

