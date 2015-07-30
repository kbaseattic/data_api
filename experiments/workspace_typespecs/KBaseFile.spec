#include <KBaseCommon.spec>
/* A module containing specifications for various file types stored in Shock
    with references in the workspace.
*/
module KBaseFile {

    typedef int bool;
    
    /* A handle id from the Handle Service for a shock node.
      @id handle
    */
    typedef string handle_id;

    /* A handle for a file stored in Shock.
      hid - the id of the handle in the Handle Service that references this
         shock node
      id - the id for the shock node
      url - the url of the shock server
      type - the type of the handle. This should always be ‘shock’.
      file_name - the name of the file
      remote_md5 - the md5 digest of the file.
      remote_sha1 - the sha1 digest of the file.
    
      @optional file_name remote_md5 remote_sha1
    */
    typedef structure {
      handle_id hid;
      string file_name;
      string id;
      string url;
      string type;
      string remote_md5;
      string remote_sha1;
    } Handle;

    /* A reference to a file stored in Shock.
      file - the location of and information about a file stored in Shock
      encoding - the encoding of the file (e.g. UTF8)
      type - the file type (e.g. XML, FASTA, GFF)
      size - the file size in bytes.
      description - a description of the file

      @optional description
      @metadata ws encoding
      @metadata ws description
      @metadata ws size
      @metadata ws type
    */
    typedef structure {
      Handle file;
      string encoding;
      string type;
      int size;
      string description;
    } FileRef;

    /* A library of paired end reads. If data is interleaved lib2 will be null
        or absent.
      lib1 - the left reads
      lib2 - the right reads
      strain - information about the genetic source
      source - information about the source of this data
      insert_size_mean - the mean size of the genetic fragments
      insert_size_std_dev - the standard deviation of the size of the genetic
          fragments
      interleaved - whether the left and right reads are interleaved in a
          single file
      read_orientation_outward - the orientation of the reads. If false or
          absent, the read directions face each other. Otherwise, the
          sequencing occurs in in an outward direction from the primer pairs.
      sequencing_tech - the technology used to sequence the genetic information
      read_count - the number of reads in the this dataset
      read_size - the total size of the reads, in bases
      gc_content - the GC content of the reads.
      single_genome - true or missing if the reads are from a single genome.
          False if the reads are from a metagenome.

      @optional lib2
      @optional insert_size_mean insert_size_std_dev interleaved
      @optional read_orientation_outward gc_content source strain
      @optional read_size read_count single_genome
      @metadata ws strain.genus
      @metadata ws strain.species
      @metadata ws strain.strain
      @metadata ws strain.ncbi_taxid
      @metadata ws source.source
      @metadata ws source.source_id
      @metadata ws source.project_id
      @metadata ws read_count
      @metadata ws read_size
      @metadata ws gc_content
      @metadata ws sequencing_tech
      @metadata ws single_genome
    */
    typedef structure {
      FileRef lib1;
      FileRef lib2;
      KBaseCommon.StrainInfo strain;
      KBaseCommon.SourceInfo source;
    
      float insert_size_mean;
      float insert_size_std_dev;
      bool interleaved;
      bool read_orientation_outward;
      bool single_genome;
     
      string sequencing_tech;
      int read_count;
      int read_size;
      float gc_content;
    } PairedEndLibrary;

    /*  A library of single end reads.
      lib - the reads
      strain - information about the genetic source
      source - information about the source of this data
      sequencing_tech - the technology used to sequence the genetic information
      read_count - the number of reads in the this dataset
      read_size - the total size of the reads, in bases
      gc_content - the GC content of the reads.
      single_genome - true or missing if the reads are from a single genome.
          False if the reads are from a metagenome.

      @optional gc_content source strain read_count read_size single_genome
      @metadata ws strain.genus
      @metadata ws strain.species
      @metadata ws strain.strain
      @metadata ws strain.ncbi_taxid
      @metadata ws source.source
      @metadata ws source.source_id
      @metadata ws source.project_id
      @metadata ws read_count
      @metadata ws read_size
      @metadata ws gc_content
      @metadata ws sequencing_tech
      @metadata ws single_genome
    */
    typedef structure {
      FileRef lib;
      KBaseCommon.StrainInfo strain;
      KBaseCommon.SourceInfo source;

      bool single_genome;
      string sequencing_tech;
      int read_count;
      int read_size;
      float gc_content;
    } SingleEndLibrary;

    /* A workspace id for a paired end library.
      @id ws KBaseFile.PairedEndLibrary
    */
    typedef string pairedlib_id;
    
    /* A workspace id for a single end library.
      @id ws KBaseFile.SingleEndLibrary
    */
    typedef string singlelib_id;
    
    /* An assembly of reads.
      Note it is *strongly* encouraged that the read libraries are included,
      but the fields are optional because for some data sources there is
      currently no way to map the assembly to the source reads.
    
      assembly_file - the assembly
      strain - information about the genetic source
      source - information about the source of this data
      size - the total estimated size of the genome, in bases
      gc_content - the overall GC content of the assembly
      contigs - the number of contigs in the assembly
      pairedlibs - references to the paired end libraries used to construct
          this assembly
      singlelibs - references to the single end libraries used to construct
          this assembly
      assembler - the assembler program used to create the assembly file
      assembler_version - the version of the assembler
      assembler_parameters - the parameters provided to the assembler
      scaffold_gap_pct - the percentage of bases in scaffolds that are gap
          characters
      scaffold_N50 - the N50 value for the scaffolds
      scaffold_L50 - the L50 value for the scaffolds
      contig_N50 - the N50 value for the contigs
      contig_L50 - the L50 value for the contigs

      @optional gc_content source
      @optional pairedlibs singlelibs
      @optional assembler assembler_version assembler_parameters
      @optional scaffold_gap_pct
      @optional scaffold_N50 scaffold_L50 contig_N50 contig_L50
      
      @metadata ws strain.genus
      @metadata ws strain.species
      @metadata ws strain.strain
      @metadata ws strain.ncbi_taxid
      @metadata ws source.source
      @metadata ws source.source_id
      @metadata ws source.project_id
      @metadata ws size
      @metadata ws contigs
      @metadata ws gc_content
    */
    typedef structure {
      FileRef assembly_file;
      KBaseCommon.StrainInfo strain;
      KBaseCommon.SourceInfo source;

      int size;
      int gc_content;
      int contigs;

      string assembler;
      string assembler_version;
      string assembler_parameters;

      float scaffold_gap_pct;
      int scaffold_N50;
      int scaffold_L50;
      int contig_N50;
      int contig_L50;

      list<pairedlib_id> pairedlibs;
      list<singlelib_id> singlelibs;
    } AssemblyFile;

    /* A workspace id for an assembly file.
      @id ws KBaseFile.AssemblyFile
    */
    typedef string assembly_id;

    /* A type for a DNA feature.

      CDS - A coding sequence of DNA, e.g. a protein encoding gene
      locus - a gene with potentially many mRNAs and CDSs
      mRNA - messenger RNA
      tRNA - transfer RNA
      sRNA - small RNA
      siRNA - small interfering RNA
      promoter - a promoter for a gene
      operon - an operon
      bind - a binding site
      pbind - a binding site for a protein
      operator - an operator site for a promoter
      atten - an attenuator
      term - a terminator
      CRISPR - a CRISPR
      pseudo - a pseudogene
      proph - a prophage
      ribosw - a riboswitch
      transp - a transposon
      pathis - a pathogenicity island
    */
    typedef string dna_feature_type;

    /* A file containing annotation data.
      Note it is *strongly* recommended to include the assembly id, but the
      field is optional since for some data sources the mapping is not
      maintained.

      annotation_file - the annotation file
      strain - information about the genetic source
      source - information about the source of this data
      features_by_type - the count of features by the type of the feature
      assembly_id - a reference to the assembly used to construct this
          annotation.

      @optional source
      @optional assembly
      @optional features_by_type
      @metadata ws strain.genus
      @metadata ws strain.species
      @metadata ws strain.strain
      @metadata ws strain.ncbi_taxid
      @metadata ws source.source
      @metadata ws source.source_id
      @metadata ws source.project_id
    */
    typedef structure {
      FileRef annotation_file;
      KBaseCommon.StrainInfo strain;
      KBaseCommon.SourceInfo source;

      mapping<dna_feature_type, int> features_by_type;

      assembly_id assembly;
    } AnnotationFile;
};


