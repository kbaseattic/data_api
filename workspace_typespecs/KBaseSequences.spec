module KBaseSequences
{
	/* Represents a particular sequence from sequence set
		string sequence_id - identifier of a sequence
		string description - description of a sequence
		string sequence - nucleotide sequence 
	*/
	typedef structure{
		string sequence_id;
		string description;
		string sequence;
	} Sequence;
	
	/* Represents set of sequences
		string sequence_set_id - identifier of sequence set
		string description - description of a sequence set
		list<Sequence> sequences - list of sequences 
	*/
	typedef structure{
		string sequence_set_id;
		string description;
		list<Sequence> sequences;
	} SequenceSet;
};

