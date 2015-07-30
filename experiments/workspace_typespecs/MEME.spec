#include <KBaseSequences.spec>

/* 
	Module MEME version 1.0
	This module provides a set of methods for work with regulatory motifs. These methods integrate capabilities of three MEME Suite tools into KBase:
	- MEME is a tool for finding ungapped motifs in unaligned DNA sequences
	- TOMTOM is a tool for comparison of an input DNA motif to the elements of a database of known motifs
	- MAST is a tool for searching biological sequence databases for occurrences of known motifs
	
	Data types summary
	MemeRunParameters data type keeps input parameters for MEME run.
	TomtomRunParameters data type keeps input parameters for TOMTOM run.
	MastRunParameters data type keeps input parameters for MAST run.
	MemeSite data type represents a particular site from MEME motif description.
	MemeMotif data type represents DNA sequence motif predicted by MEME.
	MemeRunResult data type represents result of a single MEME run and contains parameters of the search and list of identified motifs.
	MemePSPM data type represents a position-specific letter-probability matrix for use with TOMTOM and MAST.
	MemePSPMCollection data type contains collection of matrices for use with TOMTOM and MAST.
	TomtomHit represents a results of comparison of two matrices by TOMTOM.
	TomtomRunResult represents result of a single TOMTOM run.
	MastHit represents a particular MAST hit.
	MastRunResult represents results of a single MAST run.

	Methods summary
	find_motifs_with_meme - runs MEME for a set of nucleotide sequences provided as SequenceSet object and returns MemeRunResult object
	find_motifs_with_meme_from_ws - runs MEME for a set of nucleotide sequences provided as workspace ID of the SequenceSet and returns kbase ID of MemeRunResult object saved in workspace
	find_motifs_with_meme_job_from_ws - runs MEME for a set of nucleotide sequences provided as workspace ID of the SequenceSet and returns job ID 
	compare_motifs_with_tomtom - runs TOMTOM for MemePSPM as query vs. MemePSPMCollection as target and returns TomtomRunResult (list of motif pairs)
	(removed)compare_motifs_with_tomtom_from_ws - runs TOMTOM for MemePSPM as query vs. MemePSPMCollection as target provided as workspace IDs and returns kbase ID of the TomtomRunResult saved in workspace
	(removed)compare_motifs_with_tomtom_job_from_ws - runs TOMTOM for MemePSPM as query vs. MemePSPMCollection as target provided as workspace IDs and returns job ID
	compare_motifs_with_tomtom_by_collection - runs TOMTOM for two collection of PSPMs and returns TomtomRunResult (list of motif pairs)
	compare_motifs_with_tomtom_by_collection_from_ws - runs TOMTOM for two collection of PSPMs provided as workspace IDs and returns kbase ID of the TomtomRunResult saved in workspace
	compare_motifs_with_tomtom_job_by_collection_from_ws - runs TOMTOM for two collection of PSPMs provided as workspace IDs and returns job ID
	find_sites_with_mast - runs MAST for MemePSPM vs. SequenceSet and returns MastRunResult (list of MAST hits)
	(removed)find_sites_with_mast_from_ws - runs MAST for MemePSPM stored in workspace vs. SequenceSet stored in workspace and returns kbase ID of MastRunResult (list of MAST hits) saved in workspace
	(removed)find_sites_with_mast_job_from_ws - runs MAST for MemePSPM stored in workspace vs. SequenceSet stored in workspace and returns job ID
	find_sites_with_mast_by_collection - runs MAST for MemePSPMCollection vs. SequenceSet and returns MastRunResult (list of MAST hits)
	find_sites_with_mast_by_collection_from_ws - runs MAST for MemePSPMCollection stored in workspace vs. SequenceSet stored in workspace and returns kbase ID of MastRunResult (list of MAST hits) saved in workspace
	find_sites_with_mast_job_by_collection_from_ws - runs MAST for MemePSPMCollection stored in workspace vs. SequenceSet stored in workspace and returns kbase ID of MastRunResult (list of MAST hits) saved in workspace
	get_pspm_collection_from_meme_result - converts MemeRunResult into MemePSPMCollection
	get_pspm_collection_from_meme_result_from_ws - converts MemeRunResult into MemePSPMCollection and writes the result to workspace
	get_pspm_collection_from_meme_result_job_from_ws - returns ID of job object that contains ID of MemePSPMCollection converted from MemeRunResult
	
*/

module MEME
{
	/* Represents WS KBaseSequences.SequenceSet identifier
		@id ws KBaseSequences.SequenceSet
	*/
	typedef string sequence_set_ref;

	/* Represents WS MemeRunResult identifier
		@id ws MEME.MemeRunResult
	*/
	typedef string meme_run_result_ref;

	/* Represents WS MemePSPMCollection identifier
		@id ws MEME.MemePSPMCollection
	*/
	typedef string meme_pspm_collection_ref;

	/* Represents a particular site from MEME motif description 
		string source_sequence_id - ID of sequence where the site was found
		int start - position of site start 
		float pvalue - site P-value
		string left_flank - sequence of left flank
		string sequence - sequence of site
		string right_flank - sequence of right flank
		
		@optional start pvalue left_flank right_flank

	*/
	typedef structure {
		string source_sequence_id;
		int start;
		float pvalue;
		string left_flank;
		string right_flank;
		string sequence;
	} MemeSite;

	/* Represents a particular motif found by MEME
		string id - KBase ID of MemeMotif
		string description - name of motif or number of motif in collection or anything else
		int width - width of motif
		int sites - number of sites
		float llr - log likelihood ratio of motif
		float evalue - E-value of motif
		string raw_output - part of MEME output file with data about this motif
		list<MemeSite> sites - list of sites
		
		@optional description width llr evalue raw_output

	*/
	typedef structure {
		string id;
		string description;
		int width;
		float llr;
		float evalue;
		string raw_output;
		list<MemeSite> sites;
	} MemeMotif;

	/* Contains parameters of a MEME run
		string mod - distribution of motifs, acceptable values are "oops", "zoops", "anr"
		int nmotifs - maximum number of motifs to find
		int minw - minumum motif width
		int maxw - maximum motif width
		int nsites - number of sites for each motif
		int minsites - minimum number of sites for each motif
		int maxsites - maximum number of sites for each motif
		int pal - force palindromes, acceptable values are 0 and 1
		int revcomp - allow sites on + or - DNA strands, acceptable values are 0 and 1
		sequence_set_ref source_ref - WS reference to source SequenceSet object
		string source_id - id of source SequenceSet object
		
		@optional nmotifs minw maxw nsites minsites maxsites pal revcomp source_ref source_id

	*/
	typedef structure {
		string mod;
		int nmotifs;
		int minw;
		int maxw;
		int nsites;
		int minsites;
		int maxsites;
		int pal;
		int revcomp;
		sequence_set_ref source_ref;
		string source_id;
	} MemeRunParameters;

	/* Represents results of a single MEME run
		string id - KBase ID of MemeRunResult
		string source_ref - WS reference to source SequenceSet object
		string source_id - id of source SequenceSet object
		string timestamp - timestamp for creation time of collection
		string version - version of MEME like "MEME version 4.9.0 (Release date: Wed Oct  3 11:07:26 EST 2012)"
		string input_file_name - name of input file, DATAFILE field of MEME output
		string alphabet - ALPHABET field of MEME output (like "ACGT")
		string training_set - strings from TRAINING SET section, except DATAFILE and ALPHABET fields
		string command_line - command line of MEME run 
		string mod - value of mod parameter of MEME run
		int nmotifs - value of nmotifs parameter of MEME run
		string evt - value of evt parameter of MEME run
		string object_function - value of object function parameter of MEME run
		int minw - value of minw parameter of MEME run
		int maxw - value of maxw parameter of MEME run
		float minic - value of minic parameter of MEME run
		int wg - value of wg parameter of MEME run
		int ws - value of wc parameter of MEME run
		string endgaps - value of endgaps parameter of MEME run
		int minsites - value of minsites parameter of MEME run
		int maxsites - value of maxsites parameter of MEME run
		float wnsites - value of wnsites parameter of MEME run
		int prob - value of prob parameter of MEME run
		string spmap - value of spmsp parameter of MEME run
		float spfuzz - value of spfuzz parameter of MEME run
		string substring - value of substring parameter of MEME run
		string branching - value of branching parameter of MEME run
		string wbranch - value of wbranch parameter of MEME run
		string prior - value of prior parameter of MEME run
		float b - value of b parameter of MEME run
		int maxiter - value of maxiter parameter of MEME run
		float distance - value of distance parameter of MEME run
		int n - value of n parameter of MEME run
		int n_cap - value of N parameter of MEME run
		string strands - value of strands parameter of MEME run
		int seed - value of seed parameter of MEME run
		int seqfrac - value of seqfrac parameter of MEME run
		string letter_freq - letter frequencies in dataset
		string bg_freq - background letter frequencies
		list<MemeMotif> motifs - A list of all motifs in a collection
		string raw_output - section of MEME output text file (all before motif data)
		MemeRunParameters params
		
		@optional source_ref source_id timestamp meme_version input_file_name alphabet training_set command_line mod nmotifs evt object_function minw maxw minic wg ws endgaps minsites maxsites wnsites prob spmap spfuzz substring branching wbranch prior b maxiter distance n n_cap strands seed seqfrac letter_freq bg_freq motifs raw_output

	*/
	typedef structure{
		string id;
		string source_ref;
		string source_id;
		string timestamp;
		string meme_version;
		string input_file_name;
		string alphabet;
		list<string> training_set;
		string command_line;
		string mod;
		int nmotifs;
		string evt;
		string object_function;
		int minw;
		int maxw;
		float minic;
		int wg;
		int ws;
		string endgaps;
		int minsites;
		int maxsites;
		float wnsites;
		int prob;
		string spmap;
		string spfuzz;
		string substring;
		string branching;
		string wbranch;
		string prior;
		float b;
		int maxiter;
		float distance;
		int n;
		int n_cap;
		string strands;
		int seed;
		int seqfrac;
		string letter_freq;
		string bg_freq;
		list<MemeMotif> motifs;
		string raw_output;
		MemeRunParameters params;
	} MemeRunResult;
	
	/* Represents a position-specific probability matrix fot MEME motif
		string id - KBase ID of the matrix object
		string source_id - KBase ID of source object
		string description - description of motif
		string alphabet - ALPHABET field of MEME output ("ACGT" for nucleotide motifs)
		int width - width of motif
		int nsites - number of sites
		float evalue - E-value of motif
		list<list<float>> matrix - The letter probability matrix is a table of probabilities where the rows are positions in the motif and the columns are letters in the alphabet. The columns are ordered alphabetically so for DNA the first column is A, the second is C, the third is G and the last is T.
		
		@optional source_id description width nsites evalue

	*/
	typedef structure {
		string id;
		string source_id;
		string description;
		string alphabet;
		int width;
		int nsites;
		float evalue;
		list<list<float>> matrix;
	} MemePSPM;

	/* Represents collection of MemePSPMs
		string id - KBase ID of MotifPSPMMeme
		meme_run_result_ref source_ref - WS reference of source object
		string timestamp - timestamp for creation time of collection
		string description - user's description of the collection
		string alphabet - ALPHABET field of MEME output ("ACGT" for nucleotide motifs)
		list<MemeMotif> pspms - A list of all MemePSPMs in a collection
		
		@optional source_ref timestamp description
	*/
	typedef structure{
		string id;
		meme_run_result_ref source_ref;
		string timestamp;
		string description;
		string alphabet;
		list<MemePSPM> pspms;
	} MemePSPMCollection;

	/* Contains parameters of a TOMTOM run
		meme_pspm_collection_ref query_ref - query motifs for TOMTOM run
		meme_pspm_collection_ref target_ref - target motifs for TOMTOM run
		string pspm_id - KBase ID of a MemePSPM from the query collection that will be used. When empty string provided, all motifs in the query collection will be used
		float thresh - thresh parameter of TOMTOM run, must be smaller than or equal to 1.0 unless evalueTomtom == 1
		int evalue - evalue parameter of TOMTOM run (accepable values are "0" and "1")
		string dist - value of dist parameter of TOMTOM run (accepable values are "allr", "ed", "kullback", "pearson", "sandelin")
		int internal - internal parameter of TOMTOM run (accepable values are "0" and "1")
		int min_overlap - value of min-overlap parameter of TOMTOM run. In case a query motif is smaller than minOverlapTomtom specified, then the motif's width is used as the minimum overlap for that query.
		
		@optional query_ref target_ref pspm_id thresh evalue dist internal min_overlap
	*/
	typedef structure {
		meme_pspm_collection_ref query_ref;
		meme_pspm_collection_ref target_ref;
		string pspm_id;
		float thresh;
		int evalue;
		string dist;
		int internal;
		int min_overlap;
	} TomtomRunParameters;

	/*	Represents a particluar TOMTOM hit
		string query_pspm_id - id of query MemePSPM
		string target_pspm_id - id of target MemePSPM
		int optimal_offset - Optimal offset: the offset between the query and the target motif
		float pvalue - p-value
		float evalue - E-value
		float qvalue - q-value
		int overlap - Overlap: the number of positions of overlap between the two motifs.
		string query_consensus - Query consensus sequence.
		string target_consensus - Target consensus sequence.
		string strand - Orientation: Orientation of target motif with respect to query motif.
		
		@optional optimal_offset pvalue evalue qvalue overlap query_consensus target_consensus strand
	*/
	typedef structure{
		string query_pspm_id;
		string target_pspm_id;
		int optimal_offset;
		float pvalue;
		float evalue;
		float qvalue;
		int overlap;
		string query_consensus;
		string target_consensus;
		string strand;
	} TomtomHit;
	
	/* Represents result of a single TOMTOM run
		string id - KBase ID of TomtomRunResult
		string timestamp - timestamp for creation time of TomtomRunResult
		TomtomRunParameters params - run parameters
		list<TomtomHit> hits - A list of all hits found by TOMTOM
		
		@optional timestamp hits
	*/
	typedef structure{
		string id;
		string timestamp;
		TomtomRunParameters params;
		list<TomtomHit> hits;
	} TomtomRunResult;

	/* Contains parameters of a MAST run
		meme_pspm_collection_ref query_ref - query motifs for MAST run
		sequence_set_ref target_ref - target sequences for MAST run
		string pspm_id - KBase ID of a MemePSPM from the query collection that will be used. When empty string provided, all motifs in the query collection will be used
		float mt - value of mt parameter for MAST run
		
		@optional query_ref target_ref pspm_id mt 
	*/
	typedef structure {
		meme_pspm_collection_ref query_ref;
		sequence_set_ref target_ref;
		string pspm_id;
		float mt;
	} MastRunParameters;

	/*	Represents a particluar MAST hit
		string seq_id - name of sequence
		string strand - strand ("+" or "-")
		string pspm_id - id of MemePSPM
		int hit_start - start position of hit
		int hit_end - end position of hit
		float score - hit score
		float hitPvalue - hit p-value
		
		@optional strand hit_start hit_end score hit_pvalue
	*/
	typedef structure{
		string seq_id;
		string pspm_id;
		string strand;
		int hit_start;
		int hit_end;
		float score;
		float hit_pvalue;
	} MastHit;
	
	/* Represents result of a single MAST run
		string id - KBase ID of MastRunResult
		string timestamp - timestamp for creation time of MastRunResult
		MastRunParameters params - run parameters
		list<MastHit> hits - A list of all hits found by MAST
		
		@optional timestamp hits
	*/
	typedef structure{
		string id;
		string timestamp;
		MastRunParameters params;
		list<MastHit> hits;
	} MastRunResult;

	/*
		Returns results of a single MEME run
		MEME will be run with -dna -text parameters
		SequenceSet sequenceSet - input set of sequences
		MemeRunParameters params - parameters of MEME run
	*/
	funcdef find_motifs_with_meme(KBaseSequences.SequenceSet sequenceSet, MemeRunParameters params) returns(MemeRunResult meme_run_result);

	/*
		Returns kbase id of MemeRunResult object that contains results of a single MEME run
		MEME will be run with -dna -text parameters
		string ws_name - workspace id to save run result
		MemeRunParameters params - parameters of MEME run
	*/
	funcdef find_motifs_with_meme_from_ws(string ws_name, MemeRunParameters params) returns(string output_id) authentication required;

	/*
		Returns id of job object that contains id of a single MEME run result
		MEME will be run with -dna -text parameters
		string ws_name - workspace id to save run result
		MemeRunParameters params - parameters of MEME run
	*/
	funcdef find_motifs_with_meme_job_from_ws(string ws_name, MemeRunParameters params) returns(string job_id) authentication required;

	/*
		Returns TomtomRunResult with results of a single TOMTOM run
		TOMTOM will be run with -text parameter
		MemePSPM query - query motifs for TOMTOM run
		MemePSPMCollection target - target motifs for TOMTOM run
		TomtomRunParameters params - parameters of TOMTOM run
	*/
	funcdef compare_motifs_with_tomtom(MemePSPM query, MemePSPMCollection target, TomtomRunParameters params) returns(TomtomRunResult tomtom_run_result);
	
	/*
		Returns kbase ID of TomtomRunResult with results of a single TOMTOM run
		string ws_name - workspace id 
		TOMTOM will be run with -text parameter
		TomtomRunParameters params - parameters of TOMTOM run
	
	funcdef compare_motifs_with_tomtom_from_ws(string ws_name, TomtomRunParameters params) returns(string output_id) authentication required;
	*/

	/*
		Returns ID of job object that contains id of a single TOMTOM run result
		string ws_id - workspace id 
		TOMTOM will be run with -text parameter
		string query_id - kbase id of query MemePSPM for TOMTOM run
		string target_id - kbase id of MemePSPMCollection with target motifs for TOMTOM run
		TomtomRunParameters params - parameters of TOMTOM run
	
	funcdef compare_motifs_with_tomtom_job_from_ws(string ws_name, TomtomRunParameters params) returns(string job_id) authentication required;
	*/

	/*
		Returns TomtomRunResult with results of a single TOMTOM run
		TOMTOM will be run with -text parameter
		MemePSPMCollection query - query motifs for TOMTOM run
		MemePSPMCollection target - target motifs for TOMTOM run
		TomtomRunParameters params - parameters of TOMTOM run
	*/
	funcdef compare_motifs_with_tomtom_by_collection (MemePSPMCollection query, MemePSPMCollection target, TomtomRunParameters params) returns(TomtomRunResult tomtom_run_result);
	
	/*
		Returns kbase ID of TomtomRunResult with results of a single TOMTOM run
		string ws_name - workspace id 
		TOMTOM will be run with -text parameter
		TomtomRunParameters params - parameters of TOMTOM run
	*/
	funcdef compare_motifs_with_tomtom_by_collection_from_ws(string ws_name, TomtomRunParameters params) returns(string output_id) authentication required;

	/*
		Returns ID of job object that contains ID of results of a single TOMTOM run
		string ws_name - workspace id 
		TOMTOM will be run with -text parameter
		TomtomRunParameters params - parameters of TOMTOM run
	*/
	funcdef compare_motifs_with_tomtom_job_by_collection_from_ws(string ws_name, TomtomRunParameters params) returns(string job_id) authentication required;

	/*
		Returns MastRunResult containing list of MAST hits
		MAST will be run with -hit_list parameter
		MemePSPM query - query PSPM for MAST run
		SequenceSet target - target sequences for MAST run
		MastRunParameters params - parameters of MAST run
	*/
	funcdef find_sites_with_mast(MemePSPM query, KBaseSequences.SequenceSet target, MastRunParameters params) returns(MastRunResult mast_run_result);

	/*
		Returns kbase ID of MastRunResult containing list of MAST hits
		MAST will be run with -hit_list parameter
		string ws_name - workspace id
		MastRunParameters params - parameters of MAST run
	funcdef find_sites_with_mast_from_ws(string ws_name, MastRunParameters params) returns(string output_id) authentication required;
	*/

	/*
		Returns ID of job object that contains ID of MastRunResult
		MAST will be run with -hit_list parameter
		string ws_name - workspace id 
		MastRunParameters params - parameters of MAST run
	funcdef find_sites_with_mast_job_from_ws(string ws_id, MastRunParameters params) returns(string job_id) authentication required;
	*/

	/*
		Returns MastRunResult containing list of MAST hits
		MAST will be run with -hit_list parameter
		MemePSPMCollection query - query motifs for MAST run
		SequenceSet target - target sequences for MAST run
		MastRunParameters params - parameters of MAST run
	*/
	funcdef find_sites_with_mast_by_collection (MemePSPMCollection query, KBaseSequences.SequenceSet target, MastRunParameters params) returns(MastRunResult mast_run_result);

	/*
		Returns kbase ID of MastRunResult containing list of MAST hits
		MAST will be run with -hit_list parameter
		string ws_name - workspace id 
		MastRunParameters params - parameters of MAST run
	*/
	funcdef find_sites_with_mast_by_collection_from_ws(string ws_name, MastRunParameters params) returns(string output_id) authentication required;

	/*
		Returns ID of job object that contains ID of MastRunResult
		MAST will be run with -hit_list parameter
		string ws_name - workspace id 
		MastRunParameters params - parameters of MAST run
	*/
	funcdef find_sites_with_mast_job_by_collection_from_ws(string ws_name, MastRunParameters params) returns(string job_id) authentication required;

	/*
		Converts MemeRunResult into MemePSPMCollection 
		MemeRunResult meme_run_result - source MemeRunResult
	*/
	funcdef get_pspm_collection_from_meme_result (MemeRunResult meme_run_result) returns(MemePSPMCollection meme_pspm_collection);

	/*
		Converts MemeRunResult into MemePSPMCollection and writes the result to workspace
		string ws_name - workspace id
		string input_id - KBase ID of source MemeRunResult
	*/
	funcdef get_pspm_collection_from_meme_result_from_ws (string ws_name, string input_id) returns(string output_id) authentication required;

	/*
		Returns ID of job object that contains ID of MemePSPMCollection converted from MemeRunResult
		string ws_name - workspace id
		string meme_run_result_id - KBase ID of source MemeRunResult
	*/
	funcdef get_pspm_collection_from_meme_result_job_from_ws (string ws_name, meme_run_result_ref input_id) returns(string job_id) authentication required;

};


