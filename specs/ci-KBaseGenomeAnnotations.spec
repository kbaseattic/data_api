module KBaseGenomeAnnotations{ 

/*
Reference to a taxon object 
    @id ws KBaseGenomeAnnotations.Taxon
*/
typedef string taxon_ref;

/*
Reference to a taxon object 
    @id ws KBaseGenomeAnnotations.TaxonSet
*/
typedef string taxon_set_ref;

/*
The Taxon object holds the data associated with a taxon.  This taxon could be a leaf or branch in the taxonomic tree.

We lost reference_genome_annotation_id 

@optional aliases genetic_code scientific_lineage parent_taxon_ref kingdom rank embl_code inherited_div_flag inherited_GC_flag mitochondrial_genetic_code inherited_MGC_flag GenBank_hidden_flag hidden_subtree_flag division_id comments

*/
typedef structure {
  int taxonomy_id;
  string scientific_name;
  string scientific_lineage;
  string rank;
  string kingdom;
  string domain;
  list<string> aliases;
  int genetic_code;
  taxon_ref parent_taxon_ref;
  string embl_code;
  int inherited_div_flag;
  int inherited_GC_flag;
  int mitochondrial_genetic_code;
  int inherited_MGC_flag;
  int GenBank_hidden_flag;
  int hidden_subtree_flag;
  int division_id;
  string comments;
} Taxon;


/*
The TaxonLookup holds first three letters of the scientific names as top level key.  Value is a mapping of scientific name or taxon aliases as the key, and the value is the taxonomy id.  This is populated by the names.dmp file from NCBI.

*/
typedef structure {
  mapping<string scientific_name_abbreviation, mapping<string scientific_name_alias, string taxonomy_id>> taxon_lookup;
} TaxonLookup;


/*
The TaxonSet object holds references to 1 or more taxons.  It can be used generically to hold multiple taxons.
However the main usage will be to hold a list of children taxons.

taxon_ref is a WS object reference.

@optional name description notes

*/

typedef structure {
  string taxon_set_id;
  string name;
  string description;
  string notes;
  mapping<string taxonomy_id, taxon_ref taxon_ref> taxons;
} TaxonSet;


/*
Reference to a taxon object 
    @id ws KBaseGenomeAnnotations.GenomeAnnotation
*/
typedef string genome_annotation_ref;


/*
The GenomeAnnotationSet object holds references to 1 or more GenomeAnnotations.  It can be used generically to hold multiple GenomeAnnotations.

genome_annotation_ref is a WS object reference.

@optional name description notes

*/

typedef structure {
  string genome_annotation_set_id;
  string name;
  string description;
  string notes;
  mapping<string genome_annotation_id, genome_annotation_ref genome_annotation_ref> genome_annotations;
} GenomeAnnotationSet;


/*
The Contig is an individual contiguous sequence.
This is the result of an assembly, it can be complete (ex: full chromosome or circular DNA), it can also be partial
due to the limitations of the assembly itself.

is_complete - is an indication of complete chromosome, plasmid, etc.

is_circular - True, False and Unknown are viable values, could make an int(bool). If field not present viewed as unknown.

@optional name description is_complete 
*/
typedef structure {
  string contig_id;
  int length;
  string md5;
  string name;
  string description;
  int is_complete; 
  string is_circular; 
  int start_position;
  int num_bytes;
  float gc_content;
} contig;


/* 
Reference to a handle to the Reads file on shock
    @id handle
*/
typedef string reads_handle_ref;

/* 
Reference to a handle to the Assembly Fasta file on shock
    @id handle
*/
typedef string fasta_handle_ref;



/*
The Assembly object contains the information about an Assembly of Reads. The sequence data for this would be stored within a shock node.
The assembly itself is a collection of Contig subobjects.

Type is a controlled vocabulary.  Example Finished, Draft.

reads_handle_ref and fasta_handle_ref are handle service references to shock.

assembly_stats assembly_stats; - should be in there, but needs to be flushed out by Fang Fang

@optional name external_source external_source_id external_source_origination_date reads_handle_ref notes taxon_ref

*/
typedef structure {
  string assembly_id;
  string name;
  string md5;
  string external_source;
  string external_source_id;
  string external_source_origination_date;
  float gc_content;
  string type;
  reads_handle_ref reads_handle_ref; 
  fasta_handle_ref fasta_handle_ref; 
  mapping<string contig_id, contig> contigs;
  int dna_size;
  int num_contigs;
  string notes;
  taxon_ref taxon_ref;
} Assembly;

/*
Reference to an assembly object 
    @id ws KBaseGenomeAnnotations.Assembly
*/
typedef string assembly_ref;

/*
The AnnotationQuality is an object that has details about the quality of and completeness of the annotation

@optional data_quality_warnings metadata_completeness_warnings
*/
typedef structure {
  float metadata_completeness; 
  list<string> metadata_completeness_warnings;
  float data_quality; 
  list<string> data_quality_warnings; 
  int feature_types_present; 
  int evidence_supported; 
} AnnotationQuality;


/* 
Reference to a generic workspace object.  Used in evidence. 
    @id ws  
*/ 
typedef string generic_ws_reference;



/*
Evidence is information that supports some other bit of information or assertion

Generic WS reference, not to a specific typed object.  A workspace reference.

Evidence type - structural or functional?

@optional description supporting_objects
*/
typedef structure {
  string evidence_id;
  string description;
  string evidence_type; 
  list<generic_ws_reference> supporting_objects;
} evidence;


/*
EvidenceContainer is a set of evidences.  Technically it could be any list of evidences, but typically it would be set of evidences to support the annotation of a genome.

May want publications in here?

@optional name description notes
*/
typedef structure {
  string evidence_container_id;
  string name;
  string description;
  string notes;
  mapping<string evidence_id, evidence evidence> evidences;
} EvidenceContainer;

/*
Annotation pipeline specific : Seed_role_element

@optional variant_code role
*/
typedef structure {
    string role;
    string subsystem;
    string variant_code;
} seed_role;

/*
Annotation pipeline specific : Seed_roles
*/ 
typedef structure {
    mapping<string feature_id, list<seed_role> roles> feature_roles;
} SeedRoles;

/* 
Reference to a SeedRoles object
    @id ws KBaseGenomeAnnotations.SeedRoles
*/ 
typedef string seed_roles_ref; 


/*
Protein

Included function, but technically a protein may have different functions in different organisms or environments 
Note the following:
mapping<string domain, <list<list<tuple<int coordinate_start, int coordinate_stop>>>>>; 
The outer list is for multiple of the same domain in the same protein.
The inner list is to accommodate domains that are non-continuous sequence.

What about the following?
INTERACTIONS? ACTIVE SITE? ALLOSTERIC SITE? Folding pattern?

@optional function domain_locations
*/
typedef structure {
  string protein_id;
  mapping<string domain, list<list<tuple<int coordinate_start, int coordinate_stop>>> locations> domain_locations; 
  string amino_acid_sequence;
  string function;
  mapping<string alias, list<string> sources> aliases;
  string md5;
} protein;


/*
The protein container has multiple proteins in it 

@optional name description notes
*/
typedef structure {
  string protein_container_id;
  string name;
  string description;
  string notes;
  mapping<string protein_id, protein protein> proteins;
} ProteinContainer;

/*
Reference to an EvidenceContainer object 
    @id ws KBaseGenomeAnnotations.EvidenceContainer
*/
typedef string evidence_container_ref;

/*
Reference to an ProteinContainer object 
    @id ws KBaseGenomeAnnotations.ProteinContainer
*/
typedef string protein_container_ref;


/*
  @optional EC_Number associated_mRNA parent_gene codes_for_protein_ref
  
  NOTE THAT associated_mRNA feature type is there so you go up to the GenomeAnnotation object and pull its mRNA info from the feature_containers_map
  Same thing for the parent gene.
  This design choice was made because of the chicken and egg scenario between CDS, mRNA and Gene
*/
typedef structure {
  tuple<protein_container_ref protein_container_ref, string protein_id> codes_for_protein_ref;
  string EC_Number;
  tuple<string feature_type, string feature_id> associated_mRNA;
  tuple<string feature_type, string feature_id> parent_gene;
} CDS_properties;

/*
  @optional associated_CDS parent_gene
  
  NOTE THAT associated_CDS feature type is there so you go up to the GenomeAnnotation object and pull its CDS info from the feature_containers_map
  Same thing for the parent gene.
  This design choice was made because of the chicken and egg scenario between CDS, mRNA and Gene
*/
typedef structure {
  tuple<string feature_type, string feature_id> associated_CDS;
  tuple<string feature_type, string feature_id> parent_gene;
} mRNA_properties;

/*
  @optional children_CDS children_mRNA
  
  NOTE THAT Children * feature type is there so you go up to the GenomeAnnotation object and pull its mRNA info from the feature_containers_map
  Same thing for the parent gene.
  This design choice was made because of the chicken and egg scenario between CDS, mRNA and Gene
*/
typedef structure {
  list<tuple<string feature_type, string feature_id>> children_CDS;
  list<tuple<string feature_type, string feature_id>> children_mRNA;
} gene_properties;

/*
Structure for a publication (from ER API)
also want to capture authors, journal name (not in ER)
*/
typedef tuple<int, string, string, string, string, string, string> publication;

/*
Key is the key from the file
Value is the value of the file.  
This is a catch all for keys that do not directly map to an object field.  
Downside, no API methods will know the keys and how tooperate on them.
*/
typedef mapping<string key, string value> additional_properties_map;
 
/*
Feature is a individual feature of the Genome annotation (Ex: a CDS, a promoter, etc)
It has specific subobjects for particular feature types. (ex: CDS, mRNA, gene, operon, pathway) 
This is expandable in the future to include more specific properties for more types.
 
For quality_warnings do we want severity (warnings, errors)?

Do all features have coordinates? Shuffleons do and do not Genbank has a mobile_element_type feature type.
Do we want to try and capture motifs. Orthologs? Orthologs get a little tricky in terms of multiple annotations for the same genome and taxonomy.

evidence_container_ref is a workspace reference.  The list of strings is ids into EvidenceContainer mapping.
 
@optional function aliases publications notes inference feature_quality evidences 
@optional CDS_properties mRNA_properties gene_properties additional_properties trans_splicing
*/
typedef structure {
  string feature_id;
  list<tuple<string contig_id, int start, string strand, int length>> locations;
  string type;
  string function;
  string md5;
  string dna_sequence;
  int dna_sequence_length;
  list<publication> publications;
  mapping<string alias, list<string> sources> aliases;
  string notes;
  string inference; 
  float feature_quality; 
  list<string> quality_warnings; 
  tuple<evidence_container_ref evidence_container_ref, list<string>> evidences ;
  CDS_properties CDS_properties;
  mRNA_properties mRNA_properties;
  gene_properties gene_properties;
  additional_properties_map additional_properties;
  int trans_splicing;
} feature;


/*
A feature_conatainer is a set a features.  Typically this would be used to group annotations of the same type that are associated with the same genome annotation.
Technically it can support a bunch of features of different types from different genome_annotations.

The feature type is a controlled vocabulary perhaps derived from http://www.insdc.org/files/feature_table.html#7.2
type would be controlled vocabulary - Ex: CDS, etc.

Note this structure allows for flexible sets.  
So type may not be required or a "mixed" type may need to be introduced into the controlled vocabulary.(assuming mixed for now)
However it is a requirement that all the features within the container must be referencing the same assembly.

@optional name description notes

*/
typedef structure {
  string feature_container_id;
  string type; 
  string name;
  string description;
  string notes;
  assembly_ref assembly_ref;
  mapping<string feature_id, feature feature> features;
} FeatureContainer;

/*
Reference to an FeatureContainer object 
    @id ws KBaseGenomeAnnotations.FeatureContainer
*/
typedef string feature_container_ref;

/*
feature_container_ref is a versioned workspace reference
The feature type is a controlled vocabulary perhaps derived from http://www.insdc.org/files/feature_table.html#7.2
*/
typedef mapping<string feature_type, feature_container_ref feature_container_ref> feature_containers_map;



/*
The type is either a feature type or "protein". 
This is designed for fast count lookup of all the types instead of having to drill down into the containers
*/
typedef mapping<string type, int count> counts_map;
  
/*
Feature lookup is way to look up a feature within a GenomeAnnotation.
Able to lookup by id or alias
 
note feature key could be id or alias. Allows for fast lookup of any feature by id or alias.  

feature_container_ref is a WS reference

*/
typedef mapping<string feature_key, list<tuple<feature_container_ref feature_container_ref, string feature_id>> lookups> feature_lookup;

/*
Reference to an Annotation quality object 
    @id ws KBaseGenomeAnnotations.AnnotationQuality
*/
typedef string annotation_quality_ref;

/* 
Reference to a handle to the Genbank file on shock
    @id handle 
*/ 
typedef string genbank_handle_ref;


/*
The key is alias source.
This is designed for fast count lookup of all the allias sources instead of having to drill down into the containers
*/
typedef mapping<string type, int count> alias_source_counts_map;

/*
The key is interfeature relationship.
This is designed for fast count lookup of all the interfeature relationships. instead of having to drill down into the containers
*/
typedef mapping<string type, int count> interfeature_relationship_counts_map;

/*
The GenomeAnnotation is the core central object. It is the annotation of a given organism and assembly.

location and environment information (perhaps separate fields for latitude, longitude, altitude)(perhaps we need a MixS object)

quality_score could be in genome_annotation_quality_detail instead

methodology - Not sure if needed? example would be rast

type -refers to representative, reference, user, etc

taxon_ref is a versioned workspace reference
annotation_quality_ref is a versioned workspace reference
evidence_container_ref would be a versioned workspace reference 
protein_container_ref would be a versioned workspace reference
assembly_ref would be a versioned workspace reference

genbank_handle_ref are handle service references to shock.

@optional external_source external_source_id external_source_origination_date notes environmental_comments quality_score 
@optional annotation_quality_ref publications evidence_container_ref methodology seed_roles_ref genbank_handle_ref 
@optional alias_source_counts_map interfeature_relationship_counts_map
*/
 
typedef structure {
  string genome_annotation_id;
  string external_source;
  string external_source_id;
  string external_source_origination_date;
  string notes;
  string environmental_comments; 
  taxon_ref taxon_ref;
  assembly_ref assembly_ref;
  int reference_annotation;
  float quality_score; 
  annotation_quality_ref annotation_quality_ref; 
  list<publication> publications;
  feature_containers_map feature_container_references;
  protein_container_ref protein_container_ref;
  evidence_container_ref evidence_container_ref;
  feature_lookup feature_lookup;
  string methodology; 
  counts_map counts_map;
  seed_roles_ref seed_roles_ref;
  string type;
  genbank_handle_ref genbank_handle_ref;
  alias_source_counts_map alias_source_counts_map;  
  interfeature_relationship_counts_map interfeature_relationship_counts_map;
} GenomeAnnotation; 

};
