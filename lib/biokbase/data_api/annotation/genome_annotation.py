"""
Data API for Genome Annotation entities.  This API provides methods for retrieving the
Assembly and Taxon associated with an annotation, as well as retrieving individual features.
"""

# stdlib imports
import abc
import sys
import hashlib

# 3rd party imports

# local imports
from biokbase.data_api.core import ObjectAPI

_GENOME_TYPES = ['KBaseGenomes.Genome']
_GENOME_ANNOTATION_TYPES = ['KBaseGenomesCondensedPrototypeV2.GenomeAnnotation']
TYPES = _GENOME_TYPES + _GENOME_ANNOTATION_TYPES

FEATURE_DESCRIPTIONS = {
    "CDS": "Coding Sequence",
    "PEG": "Protein Encoding Genes",
    "rna": "Ribonucliec Acid (RNA)",
    "crispr": "Clustered Regularly Interspaced Short Palindromic Repeats",
    "crs": "Clustered Regularly Interspaced Short Palindromic Repeats",
    "mrna": "Messenger RNA",
    "sRNA": "Small RNA",
    "loci": "Loci",
    "opr": "Operons",
    "pbs": "Protein Binding Site",
    "bs": "Binding Site",
    "pseudo": "PseudoGenes",
    "att": "Attenuator",
    "prm": "Promoter",
    "trm": "Terminator",
    "pp": "Prophage",
    "pi": "Pathogenicity Island",
    "rsw": "Riboswitch",
    "trnspn": "Transposon"    
}


class AbstractGenomeAnnotationAPI(ObjectAPI):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_taxon(self):
        """
        Retrieves the Taxon assigned to this Genome Annotation.
        
        Returns:
          TaxonAPI"""
        pass

    @abc.abstractmethod
    def get_assembly(self):
        """
        Retrieves the Assembly used to create this Genome Annotation.
        
        Returns:
          AssemblyAPI"""
        pass
    
    @abc.abstractmethod
    def get_feature_types(self):
        """
        Retrieves the Genome Feature type identifiers available from this Genome Annotation.
        
        Returns:
          list<str>"""
        pass

    def get_feature_type_descriptions(self, type_list=None):
        """
        Retrieves a descriptive string for each feature type identifier.
        
        Args:
          type_list: list<str>
        
        Returns:
          dict"""
        
        if type_list == None:
            return FEATURE_DESCRIPTIONS
        elif type(type_list) == type([]) and len(type_list) > 0 and \
             (type(type_list[0]) == type(u"") or type(type_list[0]) == type("")):
            return {x: FEATURE_DESCRIPTIONS[x] for x in FEATURE_DESCRIPTIONS if x in type_list}
        else:
            raise TypeError()

    @abc.abstractmethod
    def get_feature_ids(self, type_list=None, region_list=None, function_list=None, alias_list=None):
        """
        Retrieves feature ids based on filters such as feature types, regions, functional descriptions, aliases.
        
        If any argument is None, it will not be used as a filter.  
        If all arguments are None, all feature ids will be returned.
        
        Args:
          type_list: list<str>
          region_list: list<dict> e.g., [{"contig_id": str, "strand": "+"|"-"|"?", "start": int, "stop": int},...]
          function_list: list<str>
          alias_list: list<str>
        
        Returns:
          list<str>"""
        pass

    @abc.abstractmethod
    def get_feature_type_counts(self, type_list=None):
        """
        Retrieve the number of Genome Features contained in this Genome Annotation by Feature type identifier.
        
        If type_list is None, will retrieve all type counts.
        
        Args:
          type_list: list<str>
        
        Returns:
          dict<str>:<int>"""        
        pass
    
    @abc.abstractmethod
    def get_feature_locations(self, feature_id_list=None):
        """
        Retrieves the location information for Genome Features present in this Genome Annotation.
        
        If feature_id_list is None, returns all feature locations.
        
        Args:
          feature_id_list: list<str>
        
        Returns:
          dict<str>: dict
          
          {"contig_id": str,
           "strand": str,
           "start": int
           "length": int}"""                        
        pass
    
    @abc.abstractmethod
    def get_feature_dna(self, feature_id_list=None):
        """
        Retrieves the dna sequence for Genome Features present in this Genome Annotation.
        
        If feature_id_list is None, returns all feature dna.
        
        Args:
          feature_id_list: list<str>
        
        Returns:
          dict<str>: str"""
        pass

    @abc.abstractmethod
    def get_feature_functions(self, feature_id_list=None):
        """
        Retrieves the functional description for Genome Features present in this Genome Annotation.
        
        If feature_id_list is None, returns all feature functions.
        
        Args:
          feature_id_list: list<str>
        
        Returns:
          dict<str>: str"""
        pass

    @abc.abstractmethod
    def get_feature_aliases(self, feature_id_list=None):
        """
        Retrieves the aliases for Genome Features present in this Genome Annotation.
        
        If feature_id_list is None, returns all feature aliases.
        
        Args:
          feature_id_list: list<str>
        
        Returns:
          dict<str>: list<str>"""
        pass
    
    @abc.abstractmethod
    def get_feature_publications(self, feature_id_list=None):
        """
        Retrieves the publications for Genome Features present in this Genome Annotation.
        
        If feature_id_list is None, returns all feature associated publications.
        
        Args:
          feature_id_list: list<str>
        
        Returns:
          dict<str>: list<dict>"""
        pass

    @abc.abstractmethod
    def get_features(self, feature_id_list=None):
        """
        Retrieves all the available data for Genome Features present in this Genome Annotation.
        
        If feature_id_list is None, returns all feature data.
        
        Args:
          feature_id_list: list<str>
        
        Returns:
          dict<str>: dict<str>: list"""
        pass

    @abc.abstractmethod
    def get_proteins(self):
        """
        Retrieves all the available proteins for Genome Features present in this Genome Annotation.
        
        Returns:
          list<dict>"""
        pass

    @abc.abstractmethod
    def get_cds_by_mrna(self, mrna_feature_id_list=None):
        """
        """
        pass

    @abc.abstractmethod
    def get_mrna_by_cds(self, cds_feature_id_list=None): 
        """
        """
        pass

    @abc.abstractmethod
    def get_gene_by_cds(self, cds_feature_id_list=None):
        """
        """
        pass
  
    @abc.abstractmethod
    def get_gene_by_mrna(self, mrna_feature_id_list=None):
        """
        """
        pass

    @abc.abstractmethod
    def get_cds_by_gene(self, gene_feature_id_list=None):
        """
        """
        pass
    
    @abc.abstractmethod
    def get_mrna_by_gene(self, gene_feature_id_list=None):
        """
        """
        pass



class GenomeAnnotationAPI(AbstractGenomeAnnotationAPI):
    """
    Factory class for instantiating a GenomeAnnotationAPI object of the correct subtype.
    """
    
    def __init__(self, services, ref):
        super(GenomeAnnotationAPI, self).__init__(services, ref)

        generic_object = ObjectAPI(services, ref)

        is_annotation_type = generic_object._typestring.split('-')[0] in _GENOME_ANNOTATION_TYPES
        is_genome_type = generic_object._typestring.split('-')[0] in _GENOME_TYPES
    
        if not (is_annotation_type or is_genome_type):
            raise TypeError("Invalid type! Expected one of {0}, received {1}".format(TYPES, generic_object._typestring))

        if is_annotation_type:
            self.proxy = _Prototype(services, ref)
        else:
            self.proxy = _KBaseGenomes_Genome(services, ref)

    def get_taxon(self):
        return self.proxy.get_taxon()

    def get_assembly(self):
        return self.proxy.get_assembly()
    
    def get_feature_types(self):
        return self.proxy.get_feature_types()

    def get_feature_ids(self, type_list=None, region_list=None, function_list=None, alias_list=None):
        return self.proxy.get_feature_ids(type_list, region_list, function_list, alias_list)

    def get_feature_type_counts(self, type_list=None):
        return self.proxy.get_feature_type_counts(type_list)
    
    def get_cds_protein(self, cds_id_list=None):
        raise NotImplementedError

    def get_feature_locations(self, feature_id_list=None):
        return self.proxy.get_feature_locations(feature_id_list)
    
    def get_feature_dna(self, feature_id_list=None):
        return self.proxy.get_feature_dna(feature_id_list)

    def get_feature_functions(self, feature_id_list=None):
        return self.proxy.get_feature_functions(feature_id_list)

    def get_feature_aliases(self, feature_id_list=None):
        return self.proxy.get_feature_aliases(feature_id_list)
    
    def get_feature_publications(self, feature_id_list=None):
        return self.proxy.get_feature_publications(feature_id_list)

    def get_features(self, feature_id_list=None):
        return self.proxy.get_features(feature_id_list)

    def get_proteins(self):
        return self.proxy.get_proteins()

    def get_cds_by_mrna(self, mrna_feature_id_list=None):
        return self.proxy.get_cds_by_mrna(mrna_feature_id_list)

    def get_mrna_by_cds(self, cds_feature_id_list=None): 
        return self.proxy.get_mrna_by_cds(cds_feature_id_list)

    def get_gene_by_cds(self, cds_feature_id_list=None):
        return self.proxy.get_gene_by_cds(cds_feature_id_list)
  
    def get_gene_by_mrna(self, mrna_feature_id_list=None):
        return self.proxy.get_gene_by_mrna(mrna_feature_id_list)

    def get_cds_by_gene(self, gene_feature_id_list=None):
        return self.proxy.get_cds_by_gene(gene_feature_id_list)
    
    def get_mrna_by_gene(self, gene_feature_id_list=None):
        return self.proxy.get_mrna_by_gene(gene_feature_id_list)
    


class _KBaseGenomes_Genome(AbstractGenomeAnnotationAPI):
    def get_taxon(self):
        import biokbase.data_api.taxonomy.taxon
        return biokbase.data_api.taxonomy.taxon.TaxonAPI(self.services, ref=self.ref)

    def get_assembly(self):
        import biokbase.data_api.sequence.assembly
        return biokbase.data_api.sequence.assembly.AssemblyAPI(self.services, ref=self.get_data_subset(path_list=["contigset_ref"])["contigset_ref"])

    def get_feature_types(self):
        features = self.get_data_subset(path_list=["features"])["features"]
        feature_types = list()
        for x in features:
            if x["type"] not in feature_types:
                feature_types.append(x["type"])
        return feature_types

    def get_feature_ids(self, type_list=None, region_list=None, function_list=None, alias_list=None):
        """
        Retrieves feature ids based on filters such as feature types, regions, functional descriptions, aliases.
        
        Returns:
          list<str>"""
        
        if type_list == None and region_list == None and function_list == None and alias_list == None:
            # just grab everything
            features = self.get_data_subset(path_list=["features"])["features"]
            return [x['id'] for x in features]

        # once we get here we have to start pulling and filtering features
        type_ids = None
        region_ids = None
        function_ids = None
        alias_ids = None

        data = self.get_data()

        if type_list != None:
            if type(type_list) != type([]):
                raise TypeError("A list of strings indicating feature types is required.")
            elif len(type_list) == 0:
                raise TypeError("A list of strings indicating feature types is required, received an empty list.")

            type_ids = dict()            
            for x in data["features"]:
                if x["type"] not in type_ids:
                    type_ids[x["type"]] = list()
                
                type_ids[x["type"]].append(x["id"])

        if region_list != None:
            if type(region_list) != type([]):
                raise TypeError("A list of region dictionaries is required.")
            elif len(region_list) == 0:
                raise TypeError("A list of region dictionaries is required, recieved an empty list.")

            if type_list == None:
                type_list = self.get_feature_types()
    
            def is_feature_in_regions(f, regions):
                location_key = None                
                
                if f.has_key("location"):
                    location_key = "location"
                elif f.has_key("locations"):
                    location_key = "locations"
                    
                for loc in f[location_key]:
                    for r in regions:
                        if (r["contig_id"] == loc[0]) and \
                           (loc[2] == r["strand"] or r["strand"] == "?") and \
                           (loc[1] <= r["stop"] and r["start"] <= loc[1] + loc[3]):
                            return True
                return False

            region_ids = dict()
            for r in region_list:
                region_ids[r["contig_id"]] = list()
            
            for x in data["features"]:
                if is_feature_in_regions(x, region_list):
                    region_ids[x["contig_id"]].append(x["id"])

        if function_list != None:
            if type(function_list) != type([]):
                raise TypeError("A list of feature function strings is required.")
            elif len(function_list) == 0:
                raise TypeError("A list of feature function strings is required, recieved an empty list.")
            
            if type_list == None:        
                type_list = self.get_feature_types()
                        
            def is_function_in_feature(feature, function_tokens):
                if not feature.has_key('function'):
                    return False
                
                tokens = feature['function'].split()            
                
                for t in tokens:
                    if t in function_tokens:
                        return True
                
                return False
                    
            function_ids = dict()
            for function in function_list:
                function_tokens = function.split()
                function_ids[function] = [x['id'] for x in data["features"] if is_function_in_feature(x, function_tokens)]
                
        if alias_list != None:
            if type(alias_list) != type([]):
                raise TypeError("A list of feature alias strings is required.")
            elif len(alias_list) == 0:
                raise TypeError("A list of feature alias strings is required, recieved an empty list.")

            if type_list == None:
                type_list = self.get_feature_types()
            
            alias_ids = dict()            
            for alias in alias_list:
                alias_ids[alias] = list()
            
            for x in data["features"]:
                for alias in alias_list:
                    if x.has_key("aliases") and alias in x["aliases"]:
                        alias_ids[alias].append(x["id"])
        
        # collect the results and find the intersection
        intersecting_ids = dict()
        
        values_intersect = set()
        type_values = set()
        region_values = set()
        function_values = set()
        alias_values = set()
        
        # flatten the dictionaries to sets of ids
        if type_ids:
            intersecting_ids["type"] = type_ids
            for x in type_ids:
                type_values.update(type_ids[x])
        
        if region_ids:
            intersecting_ids["region"] = region_ids
            for x in region_ids:
                region_values.update(region_ids[x])
        
        if function_ids:
            intersecting_ids["function"] = function_ids
            for x in function_ids:
                function_values.update(function_ids[x])
        
        if alias_ids:    
            intersecting_ids["alias"] = alias_ids
            for x in alias_ids:
                alias_values.update(alias_ids[x])        
        
        # eliminate empty sets
        valid_sets = [x for x in [type_values, region_values, function_values, alias_values] if len(x) > 0]

        if len(valid_sets) > 1:
            # start with a union of all ids        
            for v in valid_sets:
                values_intersect.update(v)
        
            # now compute the intersection
            for v in valid_sets:
                values_intersect.intersection_update(v)
        
            intersecting_ids["intersect"] = list(values_intersect)
        
        return intersecting_ids


    def get_feature_type_counts(self, type_list=None):
        """
        Retrieves number of Genome Features from a KBaseGenomes.Genome object, filtering on Feature type.

        Returns:
          dict<str>:int"""

        if type_list == None:
            type_list = self.get_feature_types()
        
        if type(type_list) != type([]):
            raise TypeError("A list of strings indicating feature types is required.")
        elif len(type_list) == 0:
            raise TypeError("A list of strings indicating feature types is required, received an empty list.")

        features = self.get_data_subset(path_list=["features"])["features"]
        
        counts = dict()          
        
        for t in type_list:
            counts[t] = 0        
        
        for x in features:
            if x['type'] in type_list:
                counts[x['type']] += 1            
        
        return counts

    def get_feature_locations(self, feature_id_list=None):
        if feature_id_list == None:
            feature_id_list = self.get_feature_ids()
        
        if type(feature_id_list) != type([]):
            raise TypeError("A list of strings indicating feature identifiers is required.")
        elif len(feature_id_list) == 0:
            raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")        
        
        features = self.get_data_subset(path_list=["features"])["features"]
        
        if feature_id_list == None:
            feature_id_list = [x['id'] for x in features]
        
        locations = dict()            
        for x in features:
            if x['id'] in feature_id_list:
                locations[x['id']] = list()

                if x.has_key('location'):                
                    for loc in x['location']:
                        locations[x['id']].append({
                            "contig_id": loc[0],
                            "strand": loc[2],
                            "start": loc[1],
                            "length": loc[3]
                        })                            
        return locations

    def get_feature_dna(self, feature_id_list=None):
        if feature_id_list == None:
            feature_id_list = self.get_feature_ids()
        
        if type(feature_id_list) != type([]):
            raise TypeError("A list of strings indicating feature identifiers is required.")
        elif len(feature_id_list) == 0:
            raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")        
        
        features = self.get_data_subset(path_list=["features"])["features"]
        
        sequences = dict()            
        for x in features:
            if x['id'] in feature_id_list:
                if x.has_key("sequence"):
                    sequences[x['id']] = x["sequence"]
                else:
                    sequences[x['id']] = None
        return sequences

    def get_feature_functions(self, feature_id_list=None):
        if feature_id_list == None:
            feature_id_list = self.get_feature_ids()
        
        if type(feature_id_list) != type([]):
            raise TypeError("A list of strings indicating feature identifiers is required.")
        elif len(feature_id_list) == 0:
            raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")
        
        features = self.get_data_subset(path_list=["features"])["features"]
        
        functions = dict()            
        for x in features:
            if x['id'] in feature_id_list:
                if x.has_key("function"):
                    functions[x['id']] = x["function"]
                else:
                    functions[x['id']] = "Unknown"
        return functions

    def get_feature_aliases(self, feature_id_list=None):
        if feature_id_list == None:
            feature_id_list = self.get_feature_ids()
        
        if type(feature_id_list) != type([]):
            raise TypeError("A list of strings indicating feature identifiers is required.")
        elif len(feature_id_list) == 0:
            raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")        
        
        features = self.get_data_subset(path_list=["features"])["features"]
        
        aliases = dict()            
        for x in features:
            if x['id'] in feature_id_list:
                if x.has_key("aliases"):
                    aliases[x['id']] = x["aliases"]
                else:
                    aliases[x['id']] = list()
        return aliases
    
    def get_feature_publications(self, feature_id_list=None):
        if feature_id_list == None:
            feature_id_list = self.get_feature_ids()
        
        if type(feature_id_list) != type([]):
            raise TypeError("A list of strings indicating feature identifiers is required.")
        elif len(feature_id_list) == 0:
            raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")        
        
        features = self.get_data_subset(path_list=["features"])["features"]
        
        publications = dict()            
        for x in features:
            if x['id'] in feature_id_list:
                if x.has_key("publications"):
                    publications[x['id']] = x["sequence"]
                else:
                    publications[x['id']] = list()
        return publications

    def get_features(self, feature_id_list=None):
        if feature_id_list == None:
            feature_id_list = self.get_feature_ids()
                
        features = self.get_data_subset(path_list=["features"])["features"]
        
        out_features = dict()            
        for x in features:
            if x['id'] in feature_id_list:
                out_features[x['id']] = dict()
                out_features[x['id']]["feature_id"] = x['id']
                out_features[x['id']]["feature_type"] = x['type']
                out_features[x['id']]["feature_function"] = x['function']
                out_features[x['id']]["feature_locations"] = x['location']
                out_features[x['id']]["feature_md5"] = x['md5']
                
                if x.has_key('dna_sequence'):
                    out_features[x['id']]["feature_dna_sequence"] = x['dna_sequence']
                else:
                    out_features[x['id']]["feature_dna_sequence"] = None
                
                if x.has_key('dna_sequence_length'):
                    out_features[x['id']]["feature_dna_sequence_length"] = x['dna_sequence_length']
                else:
                    out_features[x['id']]["feature_dna_sequence_length"] = -1
                
                if x.has_key('publications'):
                    out_features[x['id']]["feature_publications"] = x['publications']
                else:
                    out_features[x['id']]["feature_publications"] = []
                    
                if x.has_key('aliases'):
                    out_features[x['id']]["feature_aliases"] = x['aliases']
                else:
                    out_features[x['id']]["feature_aliases"] = []
                
                out_features[x['id']]["feature_notes"] = None
                out_features[x['id']]["feature_inference"] = None
                
                if x.has_key("feature_quality_score"):
                    out_features[x['id']]["feature_quality_score"] = x['quality']
                else:
                    out_features[x['id']]["feature_quality_score"] = -1
                
                out_features[x['id']]["feature_quality_warnings"] = None
            
        return out_features

    def get_proteins(self):
        features = self.get_data()["features"]
        
        proteins = dict()
        for f in features:
            if f.has_key("protein_translation") and len(f["protein_translation"]) > 0:
                protein_id = f['id'] + ".protein"
                proteins[protein_id] = dict()
                proteins[protein_id]["protein_id"] = protein_id
                proteins[protein_id]["amino_acid_sequence"] = f["protein_translation"]
                proteins[protein_id]["function"] = None
                proteins[protein_id]["aliases"] = None
                proteins[protein_id]["md5"] = hashlib.md5(f["protein_translation"].upper()).hexdigest()

                # may need to revisit this                
                proteins[protein_id]["domain_locations"] = None
        
        return proteins                

    def get_cds_by_mrna(self, mrna_feature_id_list=None):
        if type(mrna_feature_id_list) != type([]): 
            raise TypeError("A list of strings indicating mrna feature identifiers is required.")
        elif len(mrna_feature_id_list) == 0: 
            raise TypeError("A list of strings indicating mrna feature identifiers is required, received an empty list.")
 
        return {}

    def get_mrna_by_cds(self, cds_feature_id_list=None): 
        if type(cds_feature_id_list) != type([]): 
            raise TypeError("A list of strings indicating CDS feature identifiers is required.") 
        elif len(cds_feature_id_list) == 0: 
            raise TypeError("A list of strings indicating CDS feature identifiers is required, received an empty list.") 

        return {} 

    def get_gene_by_cds(self, cds_feature_id_list=None):
        if type(cds_feature_id_list) != type([]): 
            raise TypeError("A list of strings indicating CDS feature identifiers is required.")
        elif len(cds_feature_id_list) == 0: 
            raise TypeError("A list of strings indicating CDS feature identifiers is required, received an empty list.")
 
        return {}
  
    def get_gene_by_mrna(self, mrna_feature_id_list=None):
        if type(mrna_feature_id_list) != type([]):
            raise TypeError("A list of strings indicating mrna feature identifiers is required.")
        elif len(mrna_feature_id_list) == 0:
            raise TypeError("A list of strings indicating mrna feature identifiers is required, received an empty list.")

        return {} 

    def get_cds_by_gene(self, gene_feature_id_list=None):
        if type(gene_feature_id_list) != type([]): 
            raise TypeError("A list of strings indicating gene feature identifiers is required.") 
        elif len(gene_feature_id_list) == 0: 
            raise TypeError("A list of strings indicating gene feature identifiers is required, received an empty list.") 

        return {}
    
    def get_mrna_by_gene(self, gene_feature_id_list=None):
        if type(gene_feature_id_list) != type([]):
            raise TypeError("A list of strings indicating gene feature identifiers is required.")
        elif len(gene_feature_id_list) == 0:
            raise TypeError("A list of strings indicating gene feature identifiers is required, received an empty list.")
 
        return {}



class _Prototype(AbstractGenomeAnnotationAPI):
    def _group_feature_references_by_container(self, feature_id_list=list()):
        feature_containers = dict()
    
        feature_lookup = self.get_data_subset(["feature_lookup"])["feature_lookup"]
    
        for x in feature_id_list:
            for feature_ref in feature_lookup[x]:
                if feature_ref[0] not in feature_containers:
                    feature_containers[feature_ref[0]] = list()
                
                feature_containers[feature_ref[0]].append(feature_ref[1])
        
        return feature_containers

    def get_taxon(self):
        import biokbase.data_api.taxonomy.taxon
        return biokbase.data_api.taxonomy.taxon.TaxonAPI(self.services, ref=self.get_data_subset(path_list=["taxon_ref"])["taxon_ref"])

    def get_assembly(self):
        import biokbase.data_api.sequence.assembly
        return biokbase.data_api.sequence.assembly.AssemblyAPI(self.services, ref=self.get_data_subset(path_list=["assembly_ref"])["assembly_ref"])

    def get_feature_types(self):
        return self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"].keys()

    def get_feature_ids(self, type_list=None, region_list=None, function_list=None, alias_list=None):
        """
        Retrieves feature ids based on filters such as feature types, regions, functional descriptions, aliases.
        
        Returns:
          list<str>"""
        
        if type_list == None and region_list == None and function_list == None and alias_list == None:
            # just grab everything
            feature_container_references = self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"]
            
            out_ids = list()
            for x in feature_container_references:
                feature_container = ObjectAPI(self.services, feature_container_references[x])
                out_ids.extend(feature_container.get_data()["features"].keys())
            return out_ids

        # once we get here we have to start pulling and filtering features
        type_ids = None
        region_ids = None
        function_ids = None
        alias_ids = None

        data = self.get_data()
        
        feature_container_references = data["feature_container_references"]        
        features = dict()

        if type_list != None:
            if type(type_list) != type([]):
                raise TypeError("A list of strings indicating feature types is required.")
            elif len(type_list) == 0:
                raise TypeError("A list of strings indicating feature types is required, received an empty list.")

            type_ids = dict()
            for x in type_list:
                type_ids[x] = list()
            
            for f in feature_container_references:
                if f in type_list:
                    if not features.has_key(f):
                        features[f] = ObjectAPI(self.services, feature_container_references[f]).get_data()["features"]
                    
                    type_ids[f] = features[f].keys()                    

        if region_list != None:
            if type(region_list) != type([]):
                raise TypeError("A list of region dictionaries is required.")
            elif len(region_list) == 0:
                raise TypeError("A list of region dictionaries is required, recieved an empty list.")

            if type_list == None:
                type_list = self.get_feature_types()
    
            def is_feature_in_region(f, region):
                location_key = None                
                
                if f.has_key("location"):
                    location_key = "location"
                elif f.has_key("locations"):
                    location_key = "locations"
                    
                for loc in f[location_key]:
                    if (region["contig_id"] == loc[0]) and \
                       (loc[2] == region["strand"] or region["strand"] == "?") and \
                       (loc[1] <= region["stop"] and region["start"] <= loc[1] + loc[3]):
                        return True
                return False
            
            region_ids = dict()
            for r in region_list:
                region_ids[r["contig_id"]] = list()
            
            for f in feature_container_references:
                if not features.has_key(f):
                    features[f] = ObjectAPI(self.services, feature_container_references[f]).get_data()["features"]
                
                for x in features[f]:
                    for r in region_list:
                        if is_feature_in_region(features[f][x], r):
                            region_ids[r["contig_id"]].append(features[f][x]["feature_id"])

        if function_list != None:
            if type(function_list) != type([]):
                raise TypeError("A list of feature function strings is required.")
            elif len(function_list) == 0:
                raise TypeError("A list of feature function strings is required, recieved an empty list.")
            
            if type_list == None:        
                type_list = self.get_feature_types()
            
            function_tokens = list()
            for x in function_list:
                function_tokens.extend(x.split())
            function_tokens = set(function_tokens)
            
            def is_function_in_feature(feature, function_tokens):
                if not feature.has_key('function'):
                    return False
                
                tokens = feature['function'].split()            
                
                for t in tokens:
                    if t in function_tokens:
                        return True
                
                return False
                    
            function_ids = dict()
            for function in function_list:
                function_ids[function] = list()
                function_tokens = function.split()
                
                for f in feature_container_references:
                    if not features.has_key(f):
                        features[f] = ObjectAPI(self.services, feature_container_references[f]).get_data()["features"]
                
                    for x in features[f]:
                        if is_function_in_feature(features[f][x], function_tokens):
                            function_ids[function].append(features[f][x]["feature_id"])
                
        if alias_list != None:
            if type(alias_list) != type([]):
                raise TypeError("A list of feature alias strings is required.")
            elif len(alias_list) == 0:
                raise TypeError("A list of feature alias strings is required, recieved an empty list.")

            if type_list == None:
                type_list = self.get_feature_types()
            
            feature_lookup = data["feature_lookup"]
            
            feature_containers = dict()
            
            out_ids = dict()            
            for alias in alias_list:                    
                if alias in feature_lookup:
                    ref = feature_lookup[alias][0]
                    
                    if ref not in feature_containers:
                        feature_containers[ref] = list()
                        for type_key in feature_container_references:
                            if ref in feature_container_references[type_key]:
                                out_ids[type_key] = list()
                    
                    feature_containers[ref].append(feature_lookup[alias][1])                                                
            
            for ref in feature_containers:
                for type_key in feature_container_references:
                    for alias in alias_list:
                        if alias in feature_container_references[type_key]:
                            out_ids[type_key] = feature_containers[ref]
                                        
                            if type_key in type_list:
                                out_ids[alias] = feature_containers[ref]
            alias_ids = out_ids
        
        # collect the results and find the intersection
        intersecting_ids = dict()
        
        values_intersect = set()
        type_values = set()
        region_values = set()
        function_values = set()
        alias_values = set()
        
        # flatten the dictionaries to sets of ids
        if type_ids:
            intersecting_ids["type"] = type_ids
            for x in type_ids:
                type_values.update(type_ids[x])
        
        if region_ids:
            intersecting_ids["region"] = region_ids
            for x in region_ids:
                region_values.update(region_ids[x])
        
        if function_ids:
            intersecting_ids["function"] = function_ids
            for x in function_ids:
                function_values.update(function_ids[x])
        
        if alias_ids:    
            intersecting_ids["alias"] = alias_ids
            for x in alias_ids:
                alias_values.update(alias_ids[x])        
        
        # eliminate empty sets
        valid_sets = [x for x in [type_values, region_values, function_values, alias_values] if len(x) > 0]

        if len(valid_sets) > 1:
            # start with a union of all ids        
            for v in valid_sets:
                values_intersect.update(v)
        
            # now compute the intersection
            for v in valid_sets:
                values_intersect.intersection_update(v)
        
            intersecting_ids["intersect"] = list(values_intersect)
        
        return intersecting_ids
    
    def get_feature_type_counts(self, type_list=None):
        return self.get_data_subset(path_list=["counts_map"])["counts_map"]

    def get_feature_locations(self, feature_id_list=None):
        feature_lookup = self.get_data_subset(path_list=["feature_lookup"])["feature_lookup"]

        if feature_id_list == None:
            feature_id_list = self._annotation_get_all_feature_ids()                
            
        feature_containers = self._group_feature_references_by_container(feature_id_list)
        
        locations = dict()
        for ref in feature_containers:
            features = ObjectAPI(self.services, ref).get_data_subset(path_list=["features/" + x for x in feature_id_list])["features"]
            
            for feature_id in feature_id_list:
                locations[feature_id] = list()
                for loc in features[feature_id]["locations"]:
                    locations[feature_id].append({
                        "contig_id": loc[0],
                        "strand": loc[2],
                        "start": loc[1],
                        "length": loc[3]
                    })
        
        return locations
    
    def get_feature_dna(self, feature_id_list=None):
        if feature_id_list == None:
            feature_id_list = self.get_feature_ids()
        
        if type(feature_id_list) != type([]):
            raise TypeError("A list of strings indicating feature identifiers is required.")
        elif len(feature_id_list) == 0:
            raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")        
        
        feature_lookup = self.get_data_subset(path_list=["feature_lookup"])["feature_lookup"]

        feature_containers = self._group_feature_references_by_container(feature_id_list)
        
        sequences = dict()
        for ref in feature_containers:
            features = ObjectAPI(self.services, ref).get_data_subset(path_list=["features/" + x for x in feature_id_list])["features"]
            
            for feature_id in feature_id_list:
                sequences[feature_id] = features[feature_id]["dna_sequence"]
        
        return sequences

    def get_feature_functions(self, feature_id_list=None):
        if feature_id_list == None:
            feature_id_list = self.get_feature_ids()
        
        if type(feature_id_list) != type([]):
            raise TypeError("A list of strings indicating feature identifiers is required.")
        elif len(feature_id_list) == 0:
            raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")        
        
        feature_lookup = self.get_data_subset(path_list=["feature_lookup"])["feature_lookup"]

        feature_containers = self._group_feature_references_by_container(feature_id_list)
        
        functions = dict()
        for ref in feature_containers:
            features = ObjectAPI(self.services, ref).get_data_subset(path_list=["features/" + x for x in feature_id_list])["features"]
            
            for feature_id in feature_id_list:
                if features[feature_id].has_key("function"):
                    functions[feature_id] = features[feature_id]["function"]
                else:
                    functions[feature_id] = "Unknown"
        
        return functions

    def get_feature_aliases(self, feature_id_list=None):
        if feature_id_list == None:
            feature_id_list = self.get_feature_ids()
        
        if type(feature_id_list) != type([]):
            raise TypeError("A list of strings indicating feature identifiers is required.")
        elif len(feature_id_list) == 0:
            raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")        
        
        feature_lookup = self.get_data_subset(path_list=["feature_lookup"])["feature_lookup"]

        feature_containers = self._group_feature_references_by_container(feature_id_list)
        
        aliases = dict()
        for ref in feature_containers:
            features = ObjectAPI(self.services, ref).get_data_subset(path_list=["features/" + x for x in feature_id_list])["features"]
            
            for feature_id in feature_id_list:
                if features[feature_id].has_key("aliases"):
                    aliases[feature_id] = features[feature_id]["aliases"]
                else:
                    aliases[feature_id] = list()
        
        return aliases
    
    def get_feature_publications(self, feature_id_list=None):
        if feature_id_list == None:
            feature_id_list = self.get_feature_ids()
        
        if type(feature_id_list) != type([]):
            raise TypeError("A list of strings indicating feature identifiers is required.")
        elif len(feature_id_list) == 0:
            raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")        
        
        feature_lookup = self.get_data_subset(path_list=["feature_lookup"])["feature_lookup"]

        feature_containers = self._group_feature_references_by_container(feature_id_list)
                
        publications = dict()
        for ref in feature_containers:
            features = ObjectAPI(self.services, ref).get_data_subset(path_list=["features/" + x for x in feature_id_list])["features"]
            
            for feature_id in feature_id_list:
                if features[feature_id].has_key("publications"):
                    publications[feature_id] = features[feature_id]["publications"]
                else:
                    publications[feature_id] = list()
        
        return publications

    def get_features(self, feature_id_list=None):
        if feature_id_list == None:
            feature_id_list = self.get_feature_ids()
                
        feature_lookup = self.get_data_subset(path_list=["feature_lookup"])["feature_lookup"]

        feature_containers = self._group_feature_references_by_container(feature_id_list)
        
        out_features = dict()
        for ref in feature_containers:
            features = ObjectAPI(self.services, ref).get_data_subset(path_list=["features/" + x for x in feature_containers[ref]])["features"]
            
            for x in feature_containers[ref]:
                out_features[features[x]['feature_id']] = dict()
                out_features[x]["feature_id"] = features[x]['feature_id']
                out_features[x]["feature_type"] = features[x]['type']
                out_features[x]["feature_md5"] = features[x]['md5']
                out_features[x]["feature_dna_sequence"] = features[x]['dna_sequence']
                out_features[x]["feature_dna_sequence_length"] = features[x]['dna_sequence_length']
                out_features[x]["feature_locations"] = features[x]['locations']
                
                if features[x].has_key('function'):
                    out_features[x]["feature_function"] = features[x]['function']
                else:
                    out_features[x]["feature_function"] = "Unknown"

                if features[x].has_key('publications'):
                    out_features[x]["feature_publications"] = features[x]['publications']
                else:
                    out_features[x]["feature_publications"] = []

                if features[x].has_key('aliases'):
                    out_features[x]["feature_aliases"] = features[x]['aliases']
                else:
                    out_features[x]["feature_aliases"] = []
                    
                if features[x].has_key('notes'):
                    out_features[x]["feature_notes"] = features[x]['notes']
                else:
                    out_features[x]["feature_notes"] = []

                if features[x].has_key('inference'):
                    out_features[x]["feature_inference"] = features[x]['inference']
                else:
                    out_features[x]["feature_inference"] = "Unknown"

                if features[x].has_key('quality'):
                    out_features[x]["feature_quality_score"] = features[x]['quality']
                else:
                    out_features[x]["feature_quality_score"] = []

                if features[x].has_key('quality_warnings'):
                    out_features[x]["feature_quality_warnings"] = features[x]['quality_warnings']
                else:
                    out_features[x]["feature_quality_warnings"] = []
        
        return out_features

    def get_proteins(self):
        protein_container = ObjectAPI(self.services, self.get_data()["protein_container_ref"])
        return protein_container.get_data()["proteins"]

    def get_cds_by_mrna(self, mrna_feature_id_list=None):
        if type(mrna_feature_id_list) != type([]): 
            raise TypeError("A list of strings indicating mrna feature identifiers is required.")
        elif len(mrna_feature_id_list) == 0: 
            raise TypeError("A list of strings indicating mrna feature identifiers is required, received an empty list.")

        cds = dict()
 
        data = self.get_data_subset(path_list=["feature_lookup", "feature_container_references"])
        feature_lookup = data["feature_lookup"] 
        feature_container_references = data["feature_container_references"]

        if "mrna" in feature_container_references: 
            mrna_feature_container_ref = feature_container_references["mrna"] 
        else:
            #Does not have mrna annotations in this genome
            return cds 

        mrna_features = ObjectAPI(self.services, mrna_feature_container_ref).get_data_subset(path_list=["features/" + x for x in mrna_feature_id_list])["features"]

        for mrna_feature_key in mrna_features: 
            mrna_id = mrna_features[mrna_feature_key]["feature_id"]
            
            if "mrna_properties" in mrna_features[mrna_feature_key] and \
            "associated_CDS" in mrna_features[mrna_feature_key]["mrna_properties"]:
                cds[mrna_id] = mrna_features[mrna_feature_key]["mrna_properties"]["associated_CDS"][1]
            else: 
                cds[mrna_id] = None 

        return cds 

    def get_mrna_by_cds(self, cds_feature_id_list=None): 
        if type(cds_feature_id_list) != type([]): 
            raise TypeError("A list of strings indicating CDS feature identifiers is required.") 
        elif len(cds_feature_id_list) == 0: 
            raise TypeError("A list of strings indicating CDS feature identifiers is required, received an empty list.") 
 
        mrna = dict() 
        
        data = self.get_data_subset(path_list=["feature_lookup", "feature_container_references"]) 
        feature_lookup = data["feature_lookup"] 
        feature_container_references = data["feature_container_references"] 

        if "CDS" in feature_container_references: 
            cds_feature_container_ref = feature_container_references["CDS"] 
        else: 
            #Does not have CDS annotations in this genome 
            return mrna

        cds_features = ObjectAPI(self.services, cds_feature_container_ref).get_data_subset(path_list=["features/" + x for x in cds_feature_id_list])["features"] 

        for cds_feature_key in cds_features: 
            cds_id = cds_features[cds_feature_key]["feature_id"]
            
            if "CDS_properties" in cds_features[cds_feature_key] and \
            "associated_mrna" in cds_features[cds_feature_key]["CDS_properties"]: 
                mrna[cds_id] = cds_features[cds_feature_key]["CDS_properties"]["associated_mrna"][1] 
            else: 
                mrna[cds_id] = None 

        return mrna 

    def get_gene_by_cds(self, cds_feature_id_list=None):
        if type(cds_feature_id_list) != type([]): 
            raise TypeError("A list of strings indicating CDS feature identifiers is required.")
        elif len(cds_feature_id_list) == 0: 
            raise TypeError("A list of strings indicating CDS feature identifiers is required, received an empty list.")
 
        genes = dict()
        
        data = self.get_data_subset(path_list=["feature_lookup", "feature_container_references"])
        feature_lookup = data["feature_lookup"]
        feature_container_references = data["feature_container_references"]

        if "CDS" in feature_container_references: 
            cds_feature_container_ref = feature_container_references["CDS"] 
        else:
            #Does not have CDS annotations in this genome
            return genes 

        cds_features = ObjectAPI(self.services, cds_feature_container_ref).get_data_subset(path_list=["features/" + x for x in cds_feature_id_list])["features"] 

        for cds_feature_key in cds_features:
            cds_id = cds_features[cds_feature_key]["feature_id"] 
            
            if "CDS_properties" in cds_features[cds_feature_key] and \
            "associated_mrna" in cds_features[cds_feature_key]["CDS_properties"]:
                genes[cds_id] = cds_features[cds_feature_key]["CDS_properties"]["parent_gene"][1]
            else:
                genes[cds_id] = None

        return genes
  
    def get_gene_by_mrna(self, mrna_feature_id_list=None):
        if type(mrna_feature_id_list) != type([]):
            raise TypeError("A list of strings indicating mrna feature identifiers is required.")
        elif len(mrna_feature_id_list) == 0:
            raise TypeError("A list of strings indicating mrna feature identifiers is required, received an empty list.")
 
        genes = dict() 
        
        data = self.get_data_subset(path_list=["feature_lookup", "feature_container_references"])
        feature_lookup = data["feature_lookup"] 
        feature_container_references = data["feature_container_references"]

        if "mrna" in feature_container_references:
            mrna_feature_container_ref = feature_container_references["mrna"]
        else: 
            #Does not have mrna annotations in this genome  
            return genes
        
        mrna_features = ObjectAPI(self.services, mrna_feature_container_ref).get_data_subset(path_list=["features/" + x for x in mrna_feature_id_list])["features"] 

        for mrna_feature_key in mrna_features: 
            mrna_id = mrna_features[mrna_feature_key]["feature_id"]
             
            if "mrna_properties" in mrna_features[mrna_feature_key] and \
            "parent_gene" in mrna_features[mrna_feature_key]["mrna_properties"]: 
                genes[mrna_id] =  mrna_features[mrna_feature_key]["mrna_properties"]["parent_gene"][1] 
            else:
                genes[mrna_id] = None

        return genes

    def get_cds_by_gene(self, gene_feature_id_list=None):
        if type(gene_feature_id_list) != type([]): 
            raise TypeError("A list of strings indicating gene feature identifiers is required.") 
        elif len(gene_feature_id_list) == 0: 
            raise TypeError("A list of strings indicating gene feature identifiers is required, received an empty list.") 

        cds = dict() 

        data = self.get_data_subset(path_list=["feature_lookup", "feature_container_references"]) 
        feature_lookup = data["feature_lookup"] 
        feature_container_references = data["feature_container_references"] 

        if "gene" in feature_container_references: 
            gene_feature_container_ref = feature_container_references["gene"] 
        else: 
            #Does not have gene annotations in this genome
            return cds

        gene_features = ObjectAPI(self.services, gene_feature_container_ref).get_data_subset(path_list=["features/" + x for x in gene_feature_id_list])["features"] 

        for gene_feature_key in gene_features: 
            gene_id = gene_features[gene_feature_key]["feature_id"] 
            cds[gene_id] = list()
            
            if "gene_properties" in gene_features[gene_feature_key] and \
            "children_CDS" in gene_features[gene_feature_key]["gene_properties"]: 
                for cds_tuple in gene_features[gene_feature_key]["gene_properties"]["children_CDS"]:
                    cds[gene_id].append(cds_tuple[1])
        return cds
    
    def get_mrna_by_gene(self, gene_feature_id_list=None):
        if type(gene_feature_id_list) != type([]):
            raise TypeError("A list of strings indicating gene feature identifiers is required.")
        elif len(gene_feature_id_list) == 0:
            raise TypeError("A list of strings indicating gene feature identifiers is required, received an empty list.")

        mrna = dict()
         
        data = self.get_data_subset(path_list=["feature_lookup", "feature_container_references"]) 
        feature_lookup = data["feature_lookup"] 
        feature_container_references = data["feature_container_references"] 

        if "gene" in feature_container_references:
            gene_feature_container_ref = feature_container_references["gene"]
        else: 
            #Does not have gene annotations in this genome    
            return mrna

        gene_features = ObjectAPI(self.services, gene_feature_container_ref).get_data_subset(path_list=["features/" + x for x in gene_feature_id_list])["features"]

        for gene_feature_key in gene_features:
            gene_id = gene_features[gene_feature_key]["feature_id"]
            mrna[gene_id] = list()
            
            if "gene_properties" in gene_features[gene_feature_key] and \
            "children_mrna" in gene_features[gene_feature_key]["gene_properties"]:
                for mrna_tuple in gene_features[gene_feature_key]["gene_properties"]["children_mrna"]:
                    mrna[gene_id].append(mrna_tuple[1])
        return mrna 
