/*
@author dcchivian,mhenderson
*/

module KBaseCommunities {

   typedef string URI;

/*
   typedef structure {
       GenomeSet genomes;
       FBAModelSet models;
       FBAModel community_model;

       MetagenomeSet source_material;         
       Abundance2DTableFloat abundance;
    } Community;
*/

    typedef structure {
        list<string> column_labels;       
        list<int> values;
    } Table1DInt;

    typedef structure {
        list<string> column_labels;       
        list<float> values;
    } Table1DFloat;

    typedef structure {
        list<string> column_labels;       
        list<string> values;
    } Table1DString;

    typedef structure {
        list<string> row_labels;
        list<string> column_labels;
        list<list<int>> values;
    } Table2DInt;

    typedef structure {
        list<string> row_labels;
        list<string> column_labels;
        list<list<float>> values;
    } Table2DFloat;

    typedef structure {
        list<string> row_labels;
        list<string> column_labels;
        list<list<string>> values;
    } Table2DString;

    typedef structure {
        Table2DInt abundance;
    } Abundance2DTableInt;

    typedef structure {
        Table2DFloat abundance;
    } Abundance2DTableFloat;


    /*TaxonomicProfile, FunctionalProfile*/
    typedef structure {
        Table1DInt abundance;

         string category;
         string subcategory;

         string project_name;
         string project_id;
         string sample_name;
         string sample_id;
         string metagenome_name;
         string metagenome_id;
         string sequence_type;
    } Abundance1DTableInt;

    typedef structure {
        Table1DFloat abundance;

         string category;
         string subcategory;

         string project_name;
         string project_id;
         string sample_name;
         string sample_id;
         string metagenome_name;
         string metagenome_id;
         string sequence_type;
    } Abundance1DTableFloat;

    typedef string FBAModel_ref;

    typedef structure {
        mapping<string FBAModelID, mapping<string, string>> metadata;
        mapping<string FBAModelID, string FBAModel_ref> models;
    } FBAModelSet;

    typedef structure {
        mapping<string GenomeID, mapping<string, string>> metadata;
        mapping<string GenomeID, string Genome_ref> genomes;
    } GenomeSet;

    typedef structure {
        mapping<string MetagenomeID, mapping<string, string>> metadata;
        mapping<string MetagenomeID, string Metagenome_ref> metagenomes;    
    } MetagenomeSet;

    typedef structure {
         string category;
         string subcategory;

         string project_name;
         string project_id;
         string sample_name;
         string sample_id;
         string metagenome_name;
         string metagenome_id;
         string sequence_type;

         list<tuple<int,float>> values;
    } Rarefaction;

    typedef structure {
                string first_name;
                string last_name;
                string email;
                string organization;
                string address;
    } contact_information;

    typedef string date;

/*
sample_id and sample_name are required, everything else optional
to be indexed for search: everything, except sample_url, version
need to unfold metadata properly
@optional version env_package_type feature biome material location country latitude longitude created collection_date sample_url metadata
*/
        typedef structure {
            int version;
            string sample_id;
            string sample_name;
            string env_package_type;
            string feature;
            string biome;
            string material;
            string location;
            string country;
            float latitude;
            float longitude;
            date created;
            date collection_date;

            URI sample_url;
            mapping<string,string> metadata;
        } Sample;

   /*
project_id and project_name are required, everything else optional
to be indexed for search: everything, except project_url, samples, URLs in contact info
need to unfold contact structures properly
@optional project_description created samples PI_info tech_contact funding_source ncbi_id qiime_id vamps_id greengenes_id project_url
*/
     typedef structure {
            string project_id;
            string project_name;
            string project_description;
            date created;
    
            list<string> samples;

            contact_information PI_info;
            contact_information tech_contact;

            string funding_source;
            string ncbi_id;
            string qiime_id;
            string vamps_id;
            string greengenes_id;

            URI project_url;
        } Project;   


/*
metagenome_id, metagenome_name,project,sample,sequence_type are required, everything else optional
to be indexed for search: everything, except metagenome_url, library_url, sequence_download_urls
need to store (in ws) and unfold (for solr) metadata

@optional metagenome_url library_id library_url metadata sequence_download_urls seq_method created
*/

    typedef structure {
        string metagenome_id;
        string metagenome_name;
        URI metagenome_url;
        Project project;
        Sample sample;
        string library_id;
        URI library_url;

        mapping<string, string> metadata;

        list<URI> sequence_download_urls;

        string sequence_type;
        string seq_method;
        date created;
    } Metagenome;

};


