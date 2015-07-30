#include <KBaseSequences.spec>

module BAMBI
{

   /* 
        Workspace identifier
    */
    typedef string workspace_id;	


   /* 
        Workspace object id of sequence set
        @id ws KBaseSequences.SequenceSet        	    
    */
    typedef string ws_sequence_set_ref;


    /* 
    	A BAMBI job id obtained from UserAndJobState service 
    */
    typedef string bambi_job_id;


	/* Represents a particular site from BAMBI motif prediction 
		string source_sequence_id - ID of sequence where the site was found
		int start - position of site start 
		string left_flank - sequence of left flank
		string right_flank - sequence of right flank
		string sequence - sequence of site
		
		@optional left_flank right_flank
		
	*/
	typedef structure {
		string source_sequence_id;
		int start;
		string left_flank;
		string right_flank;
		string sequence;
	} BambiSite;

	/* Represents a particular motif found by BAMBI
		string id - KBase id of BambiMotif
		string description - string representation of a motif 
		int width - width of a motif
		int block_width - the length of the conserved part of a half of motif (motif is symmetric) 
		int gap_width - the distance between conserved blocks 
		float information_content - information content of a motif
		list<BambiSite> motif_sites - list of sites comprising a motif
		list<BambiSite> minor_sites - list additional sites found by a motif. This list is populated if search_for_minor_sites is set to 1 in BabmbiRunParameters.
	*/
	typedef structure {
		string id;
		string description;
		int width;
		int block_width;
		int gap_width;
		float information_content;
		
		list<BambiSite> motif_sites;
		list<BambiSite> minor_sites; 
		
	} BambiMotif;

	/*  Parameters of a BAMBI run. 
			
		int number_of_particles - number of samples to estimate distribution of motifs across the sequence set (parameter -P). Default: 20 * (max sequence length). 		
		int min_motif_length - minimal length of a motif (parameter -LM). Default: 18
		int max_motif_length - maximal length of a motif (parameter -UM). Default: 22
		int min_motif_block_length - minimal length of a motif block (parameter -LB). Default: 1 
		int max_motif_block_length - maximal length of a motif block (parameter -UB). Default: UM/2		
		int min_motif_gap_length - minimal length of a motif gap (parameter -LG). Default: 0
		int max_motif_gap_length - maximal length of a motif gap (parameter -UG). Default: UM - 2
		
		int initial_rho0 - initialize probability of sequence w/o motif  (parameter -r0). Default: 1 (Dirichlet pdf parameter)
		int initial_rho1 - initialize probability of sequence with motif (parameter -r1). Default: average length of input sequences

		float pa - background probability of a nucleotide A (parameter -d). Default: 0.25 
		float pc - background probability of a nucleotide C (parameter -d). Default: 0.25
		float pg - background probability of a nucleotide G (parameter -d). Default: 0.25
		float pt - background probability of a nucleotide T (parameter -d). Default: 0.25

		int number_of_runs - number of BAMBI runs to be executed (parameter -n). The output of a BAMBI run is a single,
			 the most optimal motif. Thus, if number_of_runs is larger than 1, then the "motifs" list in the BambiRunResult will have several elements,
			 one per each run. Default: 1
			 
		int search_for_minor_sites - search for additional sites using the predicted motif (parameter -s). Default: 0
	*/
	typedef structure {
		
		int number_of_particles; 
		int min_motif_length;   
		int max_motif_length;
		
		int min_motif_block_length;   
		int max_motif_block_length;  
		
		int min_motif_gap_length;
		int max_motif_gap_length;
		
		int initial_rho0; 
		int initial_rho1; 
		
		float pa; 
		float pc;
		float pg;
		float pt;		
		
		int number_of_runs;
		int search_for_minor_sites; 
	} BambiRunParameters;

	/* Represents results of a BAMBI run
		string id - KBase id of BambiRunResult
		string timestamp - timestamp for creation time of BambiRunResult
		string version - version of BAMBI
		string command_line - command line of BAMBI run 
		ws_sequence_set_ref sequence_set_ref - workspace id of a SequenceSet used for motifs search
		BabmbiRunParameters run_parameters - parametrs used to run BAMBI
		list<BambiMotif> motifs - list of predicted motifs
		string raw_output - section of BAMBI output text file
		
		@optional sequence_set_ref 
	*/
	typedef structure{
		string id;
		string timestamp;
		string version;
		string command_line;
		ws_sequence_set_ref sequence_set_ref;		
		BambiRunParameters run_parameters;
		list<BambiMotif> motifs;		
		string raw_output;
	} BambiRunResult;
	
	
	/*
		Search motifs for a given sequence set. When job is done, a reference to a BambiRunResult can be 
		obtained from UserAndJobState service using a provided job_id.
		
		workspace_id target_ws_id - target workspace id to place results to
		ws_sequence_set_ref sequenceset_ref - workspace id of the input set of sequences	
		
		BambiRunParameters params - parameters of BAMBI run
	*/	
	funcdef find_motifs(workspace_id target_ws_id, ws_sequence_set_ref sequenceset_ref, BambiRunParameters params) returns(bambi_job_id job_id) authentication required;	
	
};


