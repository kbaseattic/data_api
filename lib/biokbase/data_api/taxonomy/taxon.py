"""
Data API for Taxon entities.  This API provides methods for traversing
taxonomic parent/child relationships, and accessing information such as
NCBI taxonomic id, scientific name, scientific lineage, etc.
"""

# stdlib
import abc

# 3rd party

# local
from biokbase.data_api.core import ObjectAPI
from biokbase.data_api.annotation.genome_annotation import GenomeAnnotationAPI

_GENOME_TYPES = ['KBaseGenomes.Genome']
_TAXON_TYPES = ['KBaseGenomesCondensedPrototypeV2.Taxon']
TYPES = _GENOME_TYPES + _TAXON_TYPES


class AbstractTaxonAPI(ObjectAPI):
    """
    Represents a Taxonomic Unit, e.g., species.
    Built to support KBaseGenomesCondensedPrototypeV2.Taxon and KBaseGenomes.Genome.
    """    

    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def get_parent(self):
        """
        Retrieve parent Taxon of this Taxon as a TaxonAPI object.
        If this is accessing a Genome object, returns None.
        
        Returns:
          TaxonAPI"""
        pass
        
    @abc.abstractmethod
    def get_children(self):
        """
        Retrieve the children Taxon of this Taxon as TaxonAPI objects.
        If this is accessing a Genome object, returns None.
        
        Returns:
          list<TaxonAPI>"""
        pass
        
    @abc.abstractmethod
    def get_genome_annotations(self):
        """
        Retrieve the GenomeAnnotations that refer to this Taxon.
        If this is accessing a Genome object, returns None.
        
        Returns:
          list<GenomeAnnotationAPI>"""
        pass

    @abc.abstractmethod
    def get_scientific_lineage(self):
        """
        Retrieve the scientific lineage of this Taxon.
        
        Returns:
          str
        
          e.g., "Top unit;Middle unit;Lowest unit" """
        pass
    
    @abc.abstractmethod
    def get_scientific_name(self):
        """
        Retrieve the scientific name of this Taxon.
        
        Returns:
          str
            
          e.g., Escherichia Coli K12 str. MG1655"""
        pass

    @abc.abstractmethod
    def get_taxonomic_id(self):
        """
        Retrieve the NCBI taxonomic id of this Taxon.
        The KBaseGenomes.Genome type's closest representative is source_id.
        
        Unknown == -1
        
        Returns:
          int"""
        pass

    @abc.abstractmethod
    def get_kingdom(self):
        """
        Retrieve the kingdom associated with this Taxonomic Unit.
        
        Returns:
          str"""
        pass

    @abc.abstractmethod
    def get_domain(self):
        """
        Retrieve the domain associated with this Taxonomic Unit.
        
        Returns:
          str"""
        pass

    @abc.abstractmethod
    def get_aliases(self):
        """
        Retrieve the aliases for this Taxonomic Unit.
        
        Returns:
          list<str>"""        
        pass

    @abc.abstractmethod
    def get_genetic_code(self):
        """
        Retrieve the genetic code for this Taxonomic Unit.
        
        Returns:
          int"""
        pass


class TaxonAPI(AbstractTaxonAPI):
    def __init__(self, services, ref):
        """
        Defines which types and type versions that are legal.
        """
        
        super(TaxonAPI, self).__init__(services, ref)

        is_genome_type = self._typestring.split('-')[0] in _GENOME_TYPES
        is_taxon_type = self._typestring.split('-')[0] in _TAXON_TYPES
        
        if not (is_genome_type or is_taxon_type):
            raise TypeError("Invalid type! Expected one of {0}, received {1}".format(TYPES, self._typestring))
        
        if is_taxon_type:
            self.proxy = _Prototype(services, ref)
        else:
            self.proxy = _KBaseGenomes_Genome(services, ref)
    
    def get_parent(self):
        return self.proxy.get_parent()
        
    def get_children(self):
        return self.proxy.get_children()
        
    def get_genome_annotations(self):
        return self.proxy.get_genome_annotations()

    def get_scientific_lineage(self):
        return self.proxy.get_scientific_lineage()
    
    def get_scientific_name(self):
        return self.proxy.get_scientific_name()

    def get_taxonomic_id(self):
        return self.proxy.get_taxonomic_id()

    def get_kingdom(self):
        return self.proxy.get_kingdom()

    def get_domain(self):
        return self.proxy.get_domain()

    def get_aliases(self):
        return self.proxy.get_aliases()

    def get_genetic_code(self):
        return self.proxy.get_genetic_code()


class _KBaseGenomes_Genome(AbstractTaxonAPI):
    def get_parent(self):
        return None
        
    def get_children(self):
        return list()
        
    def get_genome_annotations(self):
        return list()

    def get_scientific_lineage(self):
        return self.get_data_subset(["taxonomy"])["taxonomy"]
    
    def get_scientific_name(self):
        return self.get_data_subset(["scientific_name"])["scientific_name"]

    def get_taxonomic_id(self):
        try:
            return int(self.get_data_subset(["source_id"])["source_id"])
        except:
            return -1

    def get_kingdom(self):
        return None

    def get_domain(self):
        return self.get_data_subset(["domain"])["domain"]

    def get_aliases(self):
        return list()

    def get_genetic_code(self):
        return self.get_data_subset(["genetic_code"])["genetic_code"]
            
            
class _Prototype(AbstractTaxonAPI):
    def get_parent(self):
        try:
            parent_ref = self.get_data()["parent_taxon_ref"]
        except KeyError:
            return None
        
        return _Prototype(self.services, ref=parent_ref)
        
    def get_children(self):
        referrers = self.get_referrers()
        children = list()
        
        for x in referrers:
            if x.split('-')[0] in _TAXON_TYPES:
                children.extend([TaxonAPI(self.services, ref=y) for y in referrers[x]])
        
        if len(children) == 0:
            return None
        else:
            return children
        
    def get_genome_annotations(self):
        import biokbase.data_api.annotation.genome_annotation            
        
        referrers = self.get_referrers()
        
        annotations = list()
        for object_type in referrers:
            if object_type.split('-')[0] in biokbase.data_api.annotation.genome_annotation.TYPES:
                for x in referrers[object_type]:
                    annotations.append(biokbase.data_api.annotation.genome_annotation.GenomeAnnotationAPI(self.services, ref=x))
        
        return annotations

    def get_scientific_lineage(self):
        return self.get_data()["scientific_lineage"]
    
    def get_scientific_name(self):
        return self.get_data()["scientific_name"]

    def get_taxonomic_id(self):
        return self.get_data()["taxonomy_id"]

    def get_kingdom(self):
        data = self.get_data()
        
        if data.has_key("kingdom"):
            return self.get_data()["kingdom"]
        else:
            return None

    def get_domain(self):
        return self.get_data()["domain"]

    def get_aliases(self):
        data = self.get_data()
        
        if "aliases" in data:
            return self.get_data()["aliases"]
        else:
            return list()

    def get_genetic_code(self):
        return self.get_data()["genetic_code"]