/* doesn't work: #include <publication.spec> */

module KBasePPI {

/*
This flag should work for non-String ids:
id external PubMed
*/
typedef int PubmedID;

/*
@id kb
*/
typedef string PublicationID;

typedef string Date;

/*
searchable kb_id
searchable title
@optional kb_id pubdate link title
@author JMC
*/
typedef structure {
    PubmedID pubmed_id;
    PublicationID kb_id;
    Date pubdate;
    string link;
    string title;
} Publication;

/* enum: MO, EcoCyc, IntAct, or PPI */
typedef string DatasetSource;

/* enum: 0 or 1 */
typedef int Boolean;

/* id types, temporary (tmp|x) or pre-mapped (gi|xxxxx) */
/*
@id kb
*/
typedef string GenomeID;
/*
@id ws KBaseGenomes.Genome
*/
typedef string GenomeWSID;
/*
@id kb
*/
typedef string FeatureID;
/*
@id kb
*/
typedef string ProteinID;
/*
@id kb
*/
typedef string InteractionID;
/*
@id kb
*/
typedef string InteractionDatasetID;
/*
@id kb
*/
typedef string InteractionDetectionTypeID;

/*
A method for experimentally detecting and/or annotating PPI
@optional kb_id
*/
typedef structure {
    InteractionDetectionTypeID kb_id;
    string description;
} InteractionDetectionType;

/* FeatureID and ProteinID should maybe be full Feature/Proteins, if
   we have a typespec for those.  We store both Feature and Protein
   because CS proteins are not uniquely mappable to a single Feature.
   If the ProteinID is untranslated (i.e., an external identifier for
   a protein), FeatureID does not have to be set.
@optional feature_id stoichiometry strength
*/
typedef structure {
    ProteinID protein_id;
    FeatureID feature_id;
    int rank;
    int stoichiometry;
    float strength;
} InteractionProtein;

/*
searchable kb_id;
searchable description;
searchable method.id;
searchable method.description;
searchable interaction_proteins.feature_id;
searchable publication;
@optional kb_id confidence url method publication
@author JMC
*/
typedef structure {
    InteractionID kb_id;
    float confidence;
    Boolean directional;
    string description;
    string url;
    list <InteractionProtein> interaction_proteins;
    InteractionDetectionType method;
    Publication publication;
} Interaction;

/*
This is a denormalized version of an entire PPI dataset,
in which all the relevant data are returned in a single
InteractionDataset object:
searchable kb_id;
searchable description;
searchable data_source;
searchable genomes;
searchable genomeRefs;
searchable interactions.id;
searchable interactions.description;
searchable interactions.method.id;
searchable interactions.method.description;
searchable interactions.interaction_proteins.feature_id;
searchable interactions.publication;
@optional kb_id url genomeRefs
@author JMC
*/
typedef structure {
    InteractionDatasetID kb_id;
    DatasetSource data_source;
    string description;
    string url;
    list <Interaction> interactions;
    list <GenomeID> genomes;
    list <GenomeWSID> genomeRefs;
} InteractionDataset;

};

