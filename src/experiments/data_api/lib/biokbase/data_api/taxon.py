import biokbase.data_api.object.ObjectAPI as ObjectAPI

class TaxonAPI(ObjectAPI):
    def get_parent(self):
        raise NotImplementedError
        
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
