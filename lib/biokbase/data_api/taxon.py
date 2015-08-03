from biokbase.data_api.object import ObjectAPI

class TaxonAPI(ObjectAPI):
    def __init__(self, services, ref):
        """
        Defines which types and type versions that are legal.
        """
        super(TaxonAPI, self).__init__(services, ref)
        
        self._genome_types = ['KBaseGenomes.Genome-225de07e59f4fdc5d9b8bf0bcd12c498', 
                              'KBaseGenomes.Genome-aafaaa7df90d03b33258f4fa7790dcbe', 
                              'KBaseGenomes.Genome-93da9d2c8fb7836fb473dd9c1e4ca89e', 
                              'KBaseGenomes.Genome-1e1fce431960397da77cb092d27a50cf', 
                              'KBaseGenomes.Genome-c0526fae0ce1fd8d342ec94fc4dc510a', 
                              'KBaseGenomes.Genome-c0526fae0ce1fd8d342ec94fc4dc510a', 
                              'KBaseGenomes.Genome-51b05a5c27084ae56106e60df5b66df5']
        self._taxon_types = ['KBaseGenomesCondensedPrototypeV2.Taxon-ba7d1e3c906dba5b760e22f5d3bba2a2', 
                             'KBaseGenomesCondensedPrototypeV2.Taxon-f569f539547dd1eea6a59eb9aa0b2eda']

    def get_parent(self):
        typestring = self.get_typestring()
        
        if typestring in self._taxon_types:
            return self.get_data()["parent"]
        elif typestrig in self._genome_types:
            return NotImplementedError
        
    def get_children(self, ref_list=None):
        raise NotImplementedError
    
    #use list_referencing_objects
    def get_genome_annotations(self, ref_list=None):
        raise NotImplementedError

    def get_taxonomic_lineage(self, ws_id):
        #return self.ws_client.get_object_subset([{"ref": ws_id, "included": ["taxonomy"]}])[0]["data"]["taxonomy"]
        pass
    
    def set_taxonomic_lineage(self, ws_id):
        raise NotImplementedError

    def get_scientific_name(self, ref_list=None):
        raise NotImplementedError

    def get_taxonomic_id(self, ref_list=None):
        raise NotImplementedError

    def get_domain(self, ref_list=None):
        raise NotImplementedError

    def get_aliases(self, ref_list=None):
        raise NotImplementedError

    def get_genetic_code(self, ref_list=None):
        raise NotImplementedError
