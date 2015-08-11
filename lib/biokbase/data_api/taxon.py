"""
Data API for Taxon entities.  This API provides methods for traversing
taxonomic parent/child relationships, and accessing information such as
NCBI taxonomic id, scientific name, scientific lineage, etc.
"""

from biokbase.data_api.object import ObjectAPI
from biokbase.data_api.genome_annotation import GenomeAnnotationAPI

_GENOME_TYPES = ['KBaseGenomes.Genome']
_TAXON_TYPES = ['KBaseGenomesCondensedPrototypeV2.Taxon']
TYPES = _GENOME_TYPES + _TAXON_TYPES

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

        self._is_genome_type = self._typestring.split('-')[0] in _GENOME_TYPES
        self._is_taxon_type = self._typestring.split('-')[0] in _TAXON_TYPES
        
        if not (self._is_genome_type or self._is_taxon_type):
            raise TypeError("Invalid type! Expected one of {0}, received {1}".format(TYPES, self._typestring))
    
    def get_parent(self):
        """
        Retrieve parent Taxon of this Taxon as a TaxonAPI object.
        If this is accessing a Genome object, returns None.
        
        Returns:
          TaxonAPI"""
        
        if self._is_taxon_type:
            try:
                parent_ref = self.get_data()["parent_taxon_ref"]
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
                if x.split('-')[0] in _TAXON_TYPES:
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
            print referrers
            
            annotations = list()
            for object_type in referrers:
                if object_type.split('-')[0] in biokbase.data_api.genome_annotation.TYPES:
                    for x in referrers[object_type]:
                        annotations.append(GenomeAnnotationAPI(self.services, ref=x))
            
            if len(annotations) == 0:
                return None
            else:
                return annotations
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

    def get_kingdom(self):
        """
        Retrieve the kingdom associated with this Taxonomic Unit.
        
        Returns:
          str"""
        
        if self._is_genome_type:
            return None
        elif self._is_taxon_type:
            data = self.get_data()
            
            if data.has_key("kingdom"):
                return self.get_data()["kingdom"]
            else:
                return None

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
            data = self.get_data()
            if "aliases" in data:
                return self.get_data()["aliases"]
            else:
                return list()

    def get_genetic_code(self):
        """
        Retrieve the genetic code for this Taxonomic Unit.
        
        Returns:
          int"""
        
        if self._is_genome_type:
            return self.get_data_subset(["genetic_code"])["genetic_code"]
        elif self._is_taxon_type:
            return self.get_data()["genetic_code"]
