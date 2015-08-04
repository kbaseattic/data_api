from biokbase.data_api.object import ObjectAPI

class TaxonAPI(ObjectAPI):
    """
    Represents a Taxonomic Unit, e.g., species.
    Built to support KBaseGenomesCondensedPrototypeV2.Taxon and KBaseGenomes.Genome.
    """    
    
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

        self._is_genome_type = self._typestring in self._genome_types
        self._is_taxon_type = self._typestring in self._taxon_types
        
        if not (self._is_genome_type or self._is_taxon_type):
            raise TypeError("Invalid type! Expected KBaseGenomes.Genome or KBaseGenomesCondensedPrototypeV2.Taxon, received {0}".format(self._typestring))
    
    def get_parent(self):
        """
        Retrieve parent Taxon of this Taxon as a TaxonAPI object.
        If this is accessing a Genome object, returns None.
        
        Returns:
          TaxonAPI"""
        
        if self._is_taxon_type:
            try:
                parent_data = self.get_data()
                print parent_data
                parent_ref = self.get_data()["parent_taxon_ref"]
                print parent_ref
            except KeyError:
                return None
            
            return TaxonAPI(self.services, ref=parent_ref)
        elif self._is_genome_type:
            return None
        
    def get_children(self):
        """
        Retrieve the children Taxon of this Taxon as TaxonAPI objects.
        If this is accessing a Genome object, returns None.
        
        Returns:
          list<TaxonAPI>"""
        
        if self._is_taxon_type:
            referrers = self.get_referrers()
            children = list()
            
            for x in referrers:
                if x in self._taxon_types:
                    children.extend([TaxonAPI(self.services, ref=y) for y in referrers[x]])
            
            if len(children) == 0:
                return None
            else:
                return children
        elif self._is_genome_type:
            return None
        
    def get_genome_annotations(self):
        """
        Retrieve the GenomeAnnotations that refer to this Taxon.
        If this is accessing a Genome object, returns None.
        
        Returns:
          list<GenomeAnnotationAPI>"""
        
        if self._is_taxon_type:
            import biokbase.data_api.genome_annotation            
            
            referrers = self.get_referrers()
            annotations = [biokbase.data_api.genome_annotation.GenomeAPI(self.services, ref=referrers[x]) \
                           for x in referrers if x.startswith("KBaseGenomesCondensedPrototypeV2.GenomeAnnotation")]
            
            if len(annotations) == 0:
                return None
        elif self._is_genome_type:
            return None

    def get_scientific_lineage(self):
        """
        Retrieve the scientific lineage of this Taxon.
        
        Returns:
          str
        
          e.g., "Top unit;Middle unit;Lowest unit" """
        
        if self._is_genome_type:
            return self.get_data_subset(["taxonomy"])["taxonomy"]
        elif self._is_taxon_type:
            return self.get_data()["scientific_lineage"]
    
    def get_scientific_name(self):
        """
        Retrieve the scientific name of this Taxon.
        
        Returns:
          str
            
          e.g., Escherichia Coli K12 str. MG1655"""
        
        if self._is_genome_type:
            return self.get_data_subset(["scientific_name"])["scientific_name"]
        elif self._is_taxon_type:
            return self.get_data()["scientific_name"]

    def get_taxonomic_id(self):
        """
        Retrieve the NCBI taxonomic id of this Taxon.
        The KBaseGenomes.Genome type's closest representative is source_id.
        
        Unknown == -1
        
        Returns:
          int"""
        
        if self._is_genome_type:
            try:
                return int(self.get_data_subset(["source_id"])["source_id"])
            except:
                return -1
        elif self._is_taxon_type:
            return self.get_data()["taxonomy_id"]

    def get_domain(self):
        """
        Retrieve the domain associated with this Taxonomic Unit.
        
        Returns:
          str"""
        
        if self._is_genome_type:
            return self.get_data_subset(["domain"])["domain"]
        elif self._is_taxon_type:
            return self.get_data()["domain"]

    def get_aliases(self):
        """
        Retrieve the aliases for this Taxonomic Unit.
        
        Returns:
          list<str>"""        
        
        if self._is_genome_type:
            return list()
        elif self._is_taxon_type:
            return self.get_data()["aliases"]

    def get_genetic_code(self):
        """
        Retrieve the genetic code for this Taxonomic Unit.
        
        Returns:
          int"""
        
        if self._is_genome_type:
            return self.get_data_subset(["genetic_code"])["genetic_code"]
        elif self._is_taxon_type:
            return self.get_data()["genetic_code"]
