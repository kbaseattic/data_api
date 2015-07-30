/* 
	Module KBaseNetworks version 2.0
	This module provides access to various types of network-related datasets across all domains of  in a unified format.

	Networks are composed of Nodes and Edges. Nodes represent entities from the datasets (e.g., genes, proteins,
	biclusters, subystems, etc.), and edges represent relationships (e.g., protein-protein interactions,
	gene-subsystem membership, etc.). Networks can contain Nodes and Edges from multiple datasets.

	All methods in this module can be classified into two types: 
	i. getting general information about datasets and network types currently available via Networks API
	   For example: all_DatasetSources(), allnetwork_types(), datasetSource2Datasets()
	ii. building various types of Network objects
	   For example: buildFirstNeighborNetwork(), buildInternalNetwork()
*/

module KBaseNetworks 
{


    /* A boolean. 0 = false, other = true. */
    typedef string boolean;

	/* The name of a dataset that can be accessed as a source for creating a network */
	typedef string dataset_source_ref;
	
	/* Type of network that can be created from a dataset */
	typedef string network_type;
	
	/* Type of node in a network */
	typedef string node_type;
	
	/* Type of edge in a network */
	typedef string edge_type;
	
	/* NCBI taxonomy id */	
	typedef string taxon;
	

	

	
	/* Provides detailed information about the source of a dataset.
		string id - A unique  identifier of a dataset source
		string name - A name of a dataset source
    	    	dataset_source_ref reference - Reference to a dataset source
    	    	string description - General description of a dataset source
    	    	string resourceURL - URL of the public web resource hosting the data represented by this dataset source
		
	*/	
  	typedef structure {
		string id;
    		string name;
		dataset_source_ref reference;    
		string description;
		string resource_url;
  	} DatasetSource;  
  
  
  	/* Represents a particular dataset.
		string id - A unique  identifier of a dataset 
    	    	string name - The name of a dataset
    	    	string description - Description of a dataset
    	    	network_type networkType - Type of network that can be generated from a given dataset
		dataset_source_ref sourceReference - Reference to a dataset source
		list<taxon> taxons - A list of NCBI taxonomy ids of all organisms for which genomic features (genes, proteins, etc) are used in a given dataset 
    	    	mapping<string,string> properties - Other properties  		  		
  	*/
 	typedef structure {
	    string id;
    	string name;
		string description;
		network_type network_type;
		dataset_source_ref source_ref;
		list<taxon> taxons;
		mapping<string,string> properties;
  	} Dataset;
  

	/* Represents a node in a network.
	   	string id - A unique  identifier of a node 
		string name - String representation of a node. It should be a concise but informative representation that is easy for a person to read.
    	    	string entity_id - The identifier of a  entity represented by a given node 
		node_type type - The type of a node
    	    	mapping<string,string> properties - Other properties of a node
    	    	mapping<string,string> user_annotations - User annotations of a node		
	*/  
  	typedef structure {
   		string id;  
		string name;
		string entity_id;
		node_type type;
		mapping<string,string> properties;
		mapping<string,string> user_annotations;
  	} Node;
  
  	/* Represents an edge in a network.
	   	string id - A unique  identifier of an edge 
    	    	string name - String representation of an edge. It should be a concise but informative representation that is easy for a person to read.
    	    	string node_id1 - Identifier of the first node (source node, if the edge is directed) connected by a given edge 
    	    	string node_id2 - Identifier of the second node (target node, if the edge is directed) connected by a given edge
    	    	boolean	directed - Specify whether the edge is directed or not. 1 if it is directed, 0 if it is not directed
    	    	float confidence - Value from 0 to 1 representing a probability that the interaction represented by a given edge is a true interaction
    	    	float strength - Value from 0 to 1 representing a strength of an interaction represented by a given edge
    	    	string dataset_id - The identifier of a dataset that provided an interaction represented by a given edge
		mapping<string,string> properties - Other edge properties
    	    	mapping<string,string> user_annotations - User annotations of an edge    	    		
  	*/
  	typedef structure {
	    	string id;  
    		string name;
		string node_id1;
		string node_id2;
		boolean	directed;
		float confidence;
		float strength;
		string dataset_id;
		mapping<string,string> properties;
		mapping<string,string> user_annotations;  
  	} Edge;
  

	/* Represents a network
	        string id - A unique  identifier of a network 
    	    	string name - String representation of a network. It should be a concise but informative representation that is easy for a person to read.
		list<Edge> edges - A list of all edges in a network
		list<Node> nodes - A list of all nodes in a network
		list<Dataset> datasets - A list of all datasets used to build a network
		mapping<string,string> properties - Other properties of a network
		mapping<string,string> user_annotations - User annotations of a network  
	*/  
  	typedef structure {    
		string id;
		string name;
		list<Edge> edges;
		list<Node> nodes;
		list<Dataset> datasets;
		mapping<string,string> properties;
		mapping<string,string> user_annotations;  
  	} Network;
  


	/* Represents a single entity-entity interaction
		string id - id of interaction
       	string entity1_id - entity1 identifier
       	string entity2_id - entity2 identifier
		string type	  - type of interaction
		float strength	  - strength of interaction
		float confidence  - confidence of interaction

		mapping<string,float> scores - various types of scores. 
			Known score types: 

				GENE_DISTANCE - distance between genes on a chromosome 
				CONSERVATION_SCORE - conservation, ranging from 0 (not conserved) to 1 (100% conserved)
				GO_SCORE - Smallest shared GO category, as a fraction of the genome, or missing if one of the genes is not characterized
				STRING_SCORE - STRING score
				COG_SIM	- whether the genes share (1) a COG category or not (0)
				EXPR_SIM - correlation of expression patterns
				SAME_OPERON - whether the pair is predicted to lie (1) in the same operon or not (0)
				SAME_OPERON_PROB - estimated probability that the pair is in the same operon. Values near 1 or 0 are confident predictions of being in the same operon or not, while values near 0.5 are low-confidence predictions.



       	@optional id type strength confidence scores
   	*/
   	typedef structure{
		string id;
       	string entity1_id;
       	string entity2_id;
		string type;
		float strength;
		float confidence;
		mapping<string,float> scores;

   	} Interaction;



   	/* Represents a set of interactions
	    	string id - interaction set identifier
    		string name - interaction set name
		string type - interaction set type. If specified, all interactions are expected to be of the same type.
\		string description - interaction set description
		DatasetSource source - source
		list<taxon> taxons - taxons
	      list<Interaction> interactions - list of interactions

       	@optional description type taxons
   	*/
   	typedef structure{
	    	string id;
    		string name;
		string description;
		string type;
		DatasetSource source;
		list<taxon> taxons;
	      list<Interaction> interactions;
   	} InteractionSet;



 	/* 
	   Returns a list of all datasets that can be used to create a network 
	*/
	funcdef all_datasets() returns(list<Dataset> datasets);
    
   	/* 
	   Returns a list of all dataset sources available in  via Networks API 
	*/  
	funcdef all_dataset_sources() returns(list<DatasetSource> datasetSources);
	
 	/* 
	   Returns a list of all types of networks that can be created 
	*/	
	funcdef all_network_types() returns(list<network_type> networkTypes);

   	/* 
	   Returns a list of all datasets from a given dataset source   		
	   	   dataset_source_ref datasetSourceRef - A reference to a dataset source   		   		
   	*/
  	funcdef dataset_source2datasets(dataset_source_ref source_ref) returns(list<Dataset> datasets);
  	
  	/*
	   Returns a list of all datasets that can be used to build a network for a particular genome represented by NCBI taxonomy id. 
  		taxon taxon - NCBI taxonomy id
  	*/
  	funcdef taxon2datasets(taxon taxid) returns(list<Dataset> datasets);
  	
  	/*
	   Returns a list of all datasets that can be used to build a network of a given type.
  	   	network_type networkType - The type of network
  	
  	*/
  	funcdef network_type2datasets(network_type net_type) returns(list<Dataset> datasets);
  	
	/*
	   Returns a list of all datasets that have at least one interaction for a given  entity
		
	*/  	
  	funcdef entity2datasets(string entity_id) returns(list<Dataset> datasets);

  
	/*
	   Returns a "first-neighbor" network constructed based on a given list of datasets. A first-neighbor network contains 
	   "source" nodes and all other nodes that have at least one interaction with the "source" nodes. 
	   Only interactions of given types are considered.    
  	   	list<string> dataset_ids - List of dataset identifiers to be used for building a network
  		list<string> entity_ids - List of entity identifiers to be used as source nodes
  	   	list<edge_type> edge_types - List of possible edge types to be considered for building a network
	*/    
  	funcdef build_first_neighbor_network(list<string> dataset_ids, list<string> entity_ids, list<edge_type> edge_types) returns(Network network);
  	
	/*
	   Returns a "first-neighbor" network constructed basing on a given list of datasets. First-neighbor network contains 
	   "source" nodes and all other nodes that have at least one interaction with the "source" nodes. 
	   Only interactions of given types are considered. Additional cutOff parameter allows setting a threshold
	   on the strength of edges to be considered.   
  	   	list<string> dataset_ids - List of dataset identifiers to be used for building a network
  		list<string> entity_ids - List of entity identifiers to be used as source nodes
  	   	list<edge_type> edge_types - List of possible edge types to be considered for building a network
  	   	float cutOff - The threshold on the strength of edges to be considered for building a network
  	   			
	*/  	  	
  	funcdef build_first_neighbor_network_limted_by_strength(list<string> dataset_ids, list<string> entity_ids, list<edge_type> edge_types, float cutOff) returns(Network network);
  	
  	
	/*
	   Returns an "internal" network constructed based on a given list of datasets. 
	   Internal network contains only the nodes defined by the gene_ids parameter, 
	   and edges representing interactions between these nodes.  Only interactions of given types are considered.    
  	   	list<string> dataset_ids - List of dataset identifiers to be used for building a network
  		list<string> gene_ids - Identifiers of genes of interest for building a network 	
  	   	list<edge_type> edge_types - List of possible edge types to be considered for building a network
  	   			
	*/    	
  	funcdef build_internal_network(list<string> dataset_ids, list<string> gene_ids, list<edge_type> edge_types) returns(Network network);
  	
  	
	/*
	   Returns an "internal" network constructed based on a given list of datasets. 
	   Internal network contains the only nodes defined by the gene_ids parameter, 
	   and edges representing interactions between these nodes.  Only interactions of given types are considered. 
	   Additional cutOff parameter allows to set a threshold on the strength of edges to be considered.     
  	   	list<string> dataset_ids - List of dataset identifiers to be used for building a network
  		list<string> gene_ids - Identifiers of genes of interest for building a network 	
  	   	list<edge_type> edge_types - List of possible edge types to be considered for building a network
 	   	float cutOff - The threshold on the strength of edges to be considered for building a network
  	   			
	*/     	
  	funcdef build_internal_network_limited_by_strength(list<string> dataset_ids, list<string> gene_ids, list<edge_type> edge_types, float cutOff) returns(Network network);

};

