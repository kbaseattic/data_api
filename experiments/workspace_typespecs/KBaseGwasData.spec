
module KBaseGwasData {


  /*
       Specification for the VariationFastq Metadata
  */

  /*
      reference genome id for mapping the fastq file
  */

  typedef string genome_id;

  /*
     Object for the Variation Metadata
     @optional read_count base_count assay library platform source  	
  */
  typedef structure {
	string domain;
	string paired;
	genome_id ref_genome;
	string platform;
	string read_count;
	string base_count;
	string assay;
	string library;
	string source_id;
	string source;
   	string title;
	string sample_id;
        string ext_source_date;
   }VariationSampleMetaData;

  /*
    Complete List of Variation MetaData
  */
  typedef list<VariationSampleMetaData> VariationSamplesMetaData;
 
  /*
       A reference to Variation fastq  object on shock
         
  */
 
  typedef string shock_url;

   /*   
       A reference to Variation fastq  object on shock
           
  */
	
  typedef string shock_id;
   
  
  /*   
       A reference to Variation fastq  object

  */
  typedef structure{
	shock_id shock_id;
	shock_url shock_url;
	}shock_ref;
 
  /*
      Variation fastq  object

  */

  typedef structure {
	string name;
	string type;
	string created;
	shock_ref  shock_ref;
	VariationSampleMetaData metadata;  
  }VariationSample;

   /*
       list of VariationSamples
   */

  typedef list<VariationSample> VariationSamplesSet;
 
/*
      Variation vcf  object

*/

  typedef structure {
        string name;
        string type;
        string created;
        shock_ref  shock_ref;
        VariationSampleMetaData metadata;
  }VariantCall;

   /*
       list of VCF objects
   */

  typedef list<VariantCall> VariantCallSet;







  /*  
       A reference to GWAS population object
            @id ws  KBaseGwasData.GwasPopulation
  */
    
   typedef string GwasPopulation_obj_id;


  /*  
       A reference to GWAS population variation object
            @id ws  KBaseGwasData.GwasPopulationVariation
  */
    
   typedef string GwasPopulationVariation_obj_id;


  /*  
       A reference to GWAS population trait object
            @id ws  KBaseGwasData.GwasPopulationTrait
  */
    
   typedef string GwasPopulationTrait_obj_id;



  /*  
       A reference to GWAS population kinship object
            @id ws  KBaseGwasData.GwasPopulationStructure
  */
    
   typedef string GwasPopulationStructure_obj_id;


  /*  
       A reference to GWAS population kinship object
            @id ws  KBaseGwasData.GwasPopulationKinship
  */
    
   typedef string GwasPopulationKinship_obj_id;

  /*  
       A reference to GWAS top/significant variations object
            @id ws  KBaseGwasData.GwasTopVariations
  */
    
   typedef string GwasTopVariations_obj_id;

  /*  
       A reference to GWAS top/significant genelist object
            @id ws  KBaseGwasData.GwasGeneList
  */
    
   typedef string GwasGeneList_obj_id;

  /*  
       A reference to kbase genome id in central store
            @id kb 
  */
    
   typedef string kbase_genome_id;

  /*  
       A reference to kbase genome id in central store
            @id kb 
  */
    
   typedef string kbase_gene_id;

  /*  
       A reference to kbase contig id in central store
            @id kb 
  */
    
   typedef string kbase_contig_id;





       


  /* Genome details 


      This is not an independent object in itself. 
      But it is a structure that is repeatedly used in all objects

      kbase_genome_name - eg. Arabidopsis thaliana Tair 9
      kbase_genome_id - eg. kb|g.3899 
      source_genome_name - Athaliana.TAIR10
      source - TAIR / KBASE / PHYTOZOME / ENSEMBLE 

  */


   typedef structure {
       string kbase_genome_name;
       string kbase_genome_id;
       string source_genome_name;
       string source;
    } genome_details;






   /* Observation Unit details- Details for each ecotype / germplasm in a GwasPopulation object.

       This is not an independent object in itself. It is used in gwas population

       source_id -  ecotype or germplasm id
       latitude - latitude from where ecotype was obtained
       longitude - longitude from where ecotype was obtained
       nativenames - native name of the ecotype
       region - state
       country - country
       comment - comment
       kbase_obs_unit_id - kbase registered id  of observation unit

   */


   typedef structure {
      string source_id;
      string latitude;
      string longitude;
      string nativenames; 
      string comment;
      string region; 
      string country; 
      string kbase_obs_unit_id; 
   } observation_unit_details;



   /* GwasPopulation object stores metadata for each ecotype/germplasm in the population

      genome - details of genome
      GwasPopulation_description - A brief description of  the population
      observation_unit_details - list of observation_unit_details 
      originator - Lab or PI
      pubmed_id - Pubmed id related to the population
      comment - comment
     Search indexing: Index everything

   */

   typedef structure {
      genome_details genome;
      string GwasPopulation_description; 
      string originator; 
      string pubmed_id; 
      string comment; 
      list  <observation_unit_details> observation_unit_details; 
   } GwasPopulation;






   /* shock_property for large datasets that need not be indexed eg. variation but needed for gwas analysis or landing pages are kept in shock.

     shock_url - shock ip address along with port eg. http://140.221.84.236:8000
     shock_id - shock id of the data

   */

   typedef structure {
      string shock_url; 
      string shock_id;
   } shock_property;


/*
      @optional emmax_format_hapmap_shock_id tassel_format_hapmap_shock_id 

      vcf_shock_id - vcf_shock_id
      emmax_format_hapmap_shock_id - emmax_hapmap_shock_id
      tassel_format_hapmap_shock_id - tassel_hapmap_shock_id
 
*/

   typedef structure {
      string shock_url;
      string vcf_shock_id; 
      string emmax_format_hapmap_shock_id;
      string tassel_format_hapmap_shock_id;
   } filetypes;







  /* Details of nucleotide variation in the population


     @optional  parent_variation_obj_id minor_allele_frequency 

      GwasPopulation_obj_id - object id of the GwasPopulation
      filetypes - filetype for the vcf file eg. VCF, HAPMAP, PLINK
      comment - Placeholder for comments
      assay - The assay method for genotyping or identifying SNPs
      originator - PI / LAB
      genome - genome_details 
      variation_file - shock property of variation file
      string GwasPopulationVariation_obj_id - parent object id: VCF-FILTERING use case
      minor_allele_frequency - minor allele frequency filtering

     Search indexing: Donot index --> variation_file

  */ 
 
   typedef structure {

      GwasPopulation_obj_id  GwasPopulation_obj_id; 
      string comment; 
      string assay; 
      string originator;
      genome_details genome;
      filetypes files;
      string pubmed_id;
      string minor_allele_frequency; 
      GwasPopulationVariation_obj_id parent_variation_obj_id;
      list <tuple <string obs, string kbase_obs_unit>>  obs_units;

   } GwasPopulationVariation;





   /* GwasPopulationTrait object contains trait details for one trait in a population 

      genome - genome_details
      GwasPopulation_obj_id - object id of the population
      originator - PI, lab or institution doing phenotype analysis
      trait_ontology_id -  trait ontology of trait
      trait_name - short trait name
      unit_of_measure - unit of measurement of trait eg. MEAN, COUNT, NUMDAYS
      protocol - a brief protocol describing trait measurement
      comment - Comments or any other information related to the trait
      trait_measurements - list of values for each ecotype for a trait;


     Search indexing: Donot index --> trait_measurements

   */

   typedef structure{
      genome_details genome;
      GwasPopulation_obj_id GwasPopulation_obj_id; 
      string originator; 
      string trait_ontology_id; 
      string trait_name; 
      string unit_of_measure; 
      string protocol; 
      list <tuple <string ecotype_id, string measurement>> trait_measurements;
      string comment; 
   } GwasPopulationTrait;


/*

       kinship_matrix_shock_id - shock id of kinship matrix data; 
*/

   typedef structure {
      string shock_url;
      string kinship_matrix_shock_id; 
   } kinship_data;






   /* GwasPopulationKinship has population kinship matrix

      genome - genome details
      GwasPopulationVariation_obj_id - object id of the population
      kinship_data is the shock reference of data for the kinship matrix

   */



   typedef structure {
      kinship_data kinship;
      genome_details genome;
      GwasPopulationVariation_obj_id GwasPopulationVariation_obj_id;
      GwasPopulation_obj_id GwasPopulation_obj_id;
      string comment; 
   } GwasPopulationKinship;


       
   /*  Details of significant variations

       id - id of contig
       position - base position of snp
       pvalue - pvalue of association in GWAS analysis 
       minus_log_pvalue - kept for consistency with widgets



   */
   typedef structure {

      string id;
      int position;
      float minus_log_pvalue;
      float pvalue;
   } variation_details;


   /* Details of contigs


   */

   typedef structure {
      string id;
      string name;
      int len;
      string kbase_contig_id;
  } contig_details;




   /* List of significant snps and pvalues obtained after gwas analysis

    
      source - kbase analysis/public data
      protocol - a brief protocol describing trait measurement
      originator - lab or pi
      trait_ontology_id -  trait ontology of trait
      genome - genome details
      GwasPopulation_obj_id - object id of population
      GwasPopulationVariation_obj_id - object id of the population variation data.
      trait_name - short trait name
      GwasPopulationTrait_obj_id - object id of trait data
      pvaluecutoff - pvalue cut off for snps
      GwasPopulationStructure_obj_id - object id of population structure data. optional
      GwasPopulationKinship_obj_id - object id of population kinship data. optional

      unit_of_measure: measurement units;
     Search indexing: Donot index --> variations, contigs 
     @optional unit_of_measure GwasPopulationStructure_obj_id

   */


   typedef structure {

      string source; 
      string protocol; 
      GwasPopulationTrait_obj_id GwasPopulationTrait_obj_id; 
      string num_population;
      string unit_of_measure;
      string assay;
      string trait_ontology_id; 
      genome_details genome;
      string trait_name; 
      string originator; 
      GwasPopulationVariation_obj_id GwasPopulationVariation_obj_id;
      GwasPopulation_obj_id GwasPopulation_obj_id;
      list <contig_details> contigs; 
      list <tuple < int id, int position, float minus_log_pvalue, string snpid>> variations;
      string comment;
      GwasPopulationStructure_obj_id GwasPopulationStructure_obj_id; 
      GwasPopulationKinship_obj_id GwasPopulationKinship_obj_id; 
      float pvaluecutoff;
   } GwasTopVariations; 



   /* Gwasgenelist has the list of genes obtained on the basis of significant snp list

      GwasPopulationVariation_obj_id - object id of the population variation data.
      GwasPopulationTrait_obj_id - object id of trait data
      pvaluecutoff - pvalue cut off for snps
      distance_cutoff - distance from the snp

      
     Search indexing:  Get all data from GwasPopulationVariation_obj_id: ignore -- variations and contigs
   */

   typedef structure {

      string GwasTopVariations_obj_id;
      float pvaluecutoff;
      int distance_cutoff;
      list <tuple < string kbase_contig_id, string source_gene_id, string kbase_gene_id, int position, string genedescription, float pvalue, string source_contig_id , int gene_begin, int gene_end >> genes_snp_list;
      list <tuple <string kbase_contig_id, string source_gene_id, string kbase_gene_id, string genedescription, string source_contig_id>> genes;
   } GwasGeneList;











	

    /* Population Unit */
    typedef structure {
        string populationId;
    } populationUnit;
     
    /* Trait Unit */
    typedef structure {
       string traitId;
    } traitUnit;
     
    /* TopVariation Unit */
    typedef structure {
        string topvariationId;
    } topVariationUnit;
     
    /* genelist Unit */
    typedef structure {
        string genelistId;
    } genelistUnit;

    typedef structure {
        string variationId;
    } variationUnit;

    typedef structure {
        string kinshipId;
    } kinshipUnit;
 
     
    /* Population - Trait tuble */
    typedef structure {
        string populationId;
        list <traitUnit> traits;
    } populationTraitUnit;

    /* Population - variation tuple */
    typedef structure {
        string populationId;
        list <variationUnit> variations;
    } populationVariationUnit;

  typedef structure {
        string variationId;
        list <kinshipUnit> kinships;
    } variationKinshipUnit;




    /* Trait - TopVariation Unit */
    typedef structure {
        string traitId;
        list <topVariationUnit> topvariations;
    } traitTopvariationUnit;
 

     
    /* TopVariation -Genelist Unit */
    typedef structure {
        string topvariationId;
        list <genelistUnit> genelists;
    } topvariationGenelistUnit;


    typedef structure {
      string obj_id;
      string obj_name;
    } idnameUnit;
     
     
    typedef structure {
        list <populationUnit> gwasPopulations;
        list <populationVariationUnit> population_and_variation;
        list <variationKinshipUnit> variation_and_kinship;
        list <populationTraitUnit> population_and_trait;
        list <traitTopvariationUnit> trait_and_topvariation;
        list <topvariationGenelistUnit> topvariation_and_genelist;
        list <idnameUnit> idname;
    } GwasPopulationSummary;
     






};

