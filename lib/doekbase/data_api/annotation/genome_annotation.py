"""
Data API for Genome Annotation entities.  This API provides methods for retrieving the
Assembly and Taxon associated with an annotation, as well as retrieving individual features.
"""

# stdlib imports
import abc
import hashlib

# 3rd party imports

# local imports
from doekbase.data_api.core import ObjectAPI

_GENOME_TYPES = ['KBaseGenomes.Genome']
_GENOME_ANNOTATION_TYPES = ['KBaseGenomesCondensedPrototypeV2.GenomeAnnotation']
TYPES = _GENOME_TYPES + _GENOME_ANNOTATION_TYPES

#: Mapping of feature type codes to descriptions
#: of their meaning. The keys of this mapping give possible values for
#: functions taking feature type identifiers, e.g.
#: :meth:`GenomeInterface.get_feature_types`.
FEATURE_DESCRIPTIONS = {
    "CDS": "Coding Sequence",
    "PEG": "Protein Encoding Genes",
    "rna": "Ribonucliec Acid (RNA)",
    "crispr": "Clustered Regularly Interspaced Short Palindromic Repeats",
    "crs": "Clustered Regularly Interspaced Short Palindromic Repeats",
    "mRNA": "Messenger RNA",
    "sRNA": "Small RNA",
    "loci": "Loci or Gene (Genbank)",
    "locus": "Locus or Gene (Genbank)",
    "gene": "Gene",
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


class GenomeInterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_taxon(self):
        """Retrieves the Taxon assigned to this Genome Annotation.
        
        Returns:
          TaxonAPI: Taxon object
        """
        pass

    @abc.abstractmethod
    def get_assembly(self):
        """Retrieves the Assembly used to create this Genome Annotation.
        
        Returns:
          AssemblyAPI: Assembly object
        """
        pass
    
    @abc.abstractmethod
    def get_feature_types(self):
        """Retrieves the Genome Feature type identifiers available from this
        Genome Annotation.
        
        Returns:
          list<str>: List of feature type identifiers.
        """
        pass

    def get_feature_type_descriptions(self, type_list=None):
        """Retrieves a descriptive string for each feature type identifier.
        
        Args:
          type_list (list<str>): List of feature types. The known values for
            these are enumerated in the module's  :data:`FEATURE_DESCRIPTIONS`.
            If this list is empty or None, then the whole mapping will be
            returned.
        
        Returns:
          dict: Key/value pairs for each requested feature description.
        """
        
        if not type_list:
            result = FEATURE_DESCRIPTIONS
        else:
            result = {}
            for key in type_list:
                if not isinstance(key, basestring):
                    raise TypeError("key '{}' is type '{}', but type 'str' "
                                    "expected".format(key, type(key)))
            result[key] = FEATURE_DESCRIPTIONS[key]
        return result

    @abc.abstractmethod
    def get_feature_ids(self, type_list=None, region_list=None,
                        function_list=None, alias_list=None):
        """Retrieves feature ids based on filters such as feature types,
        regions, functional descriptions, aliases.
        
        If any argument is None, it will not be used as a filter.  
        If all arguments are None, all feature ids will be returned.
        
        Args:
          type_list (list<str>): List of feature types. Each should match a
            value in :data:`FEATURE_DESCRIPTIONS`.
          region_list (list<dict>): List of region objects, e.g.:
            [{"contig_id": str, "strand": "+"|"-"|"?", "start": int, "stop": int},...]
          function_list (list<str>): List of functions
          alias_list (list<str>): List of feature aliases
        
        Returns:
          dict<str,list<dict or str>>: Mapping of each retrieved feature ID
             to its corresponding value.
        """
        pass  # TODO: add examples in docs for function_list and alias_list

    @abc.abstractmethod
    def get_feature_type_counts(self, type_list=None):
        """Retrieve the number of Genome Features, grouped by
        feature type identifier.
        
        Args:
          type_list (list<str>): List of feature types. Each should match a
            value in :data:`FEATURE_DESCRIPTIONS`. If None,
            or empty, will retrieve all type counts.

        Returns:
          dict: Map of string feature types to integer counts.
        """
        pass
    
    @abc.abstractmethod
    def get_feature_locations(self, feature_id_list=None):
        """Retrieves the location information for given genome features.
        
        Args:
          feature_id_list (list<str>): List of features to retrieve.
            If None, returns all feature functions.
        
        Returns:
          dict: Mapping from feature IDs to location information for each.
          The location information has the following key/value pairs:

          contig_id : str
              The identifier for this contig
          strand : str
              The strand for the contig ????
          start : int
              The start position for the contig
          length : int
              The length of the contig
        """
        pass
    
    @abc.abstractmethod
    def get_feature_dna(self, feature_id_list=None):
        """Retrieves the DNA sequence for genome features.
        
        If `feature_id_list` is None, returns all feature dna.
        
        Args:
          feature_id_list (list<str>): List of features.
        
        Returns:
          dict<str,str>: Mapping of feature IDs to their values.
        """
        pass

    @abc.abstractmethod
    def get_feature_functions(self, feature_id_list=None):
        """
        Retrieves the functional description for given features.


        Args:
          feature_id_list (list<str>): List of features to retrieve.
            If None, returns all feature functions.

        
        Returns:
          dict<str,str>: Mapping from feature IDs to their functions.

        """
        pass

    @abc.abstractmethod
    def get_feature_aliases(self, feature_id_list=None):
        """Retrieves the aliases for genome features.

        Args:
          feature_id_list (list<str>): List of features to retrieve.
            If None, returns all feature functions.
        
        Returns:
          dict<str>: list<str>"""
        pass
    
    @abc.abstractmethod
    def get_feature_publications(self, feature_id_list=None):
        """Retrieves the publications for genome features.

        Args:
          feature_id_list (list<str>): List of features to retrieve.
            If None, returns all feature functions.
        
        Returns:
          dict<str>: list<dict>"""
        pass

    @abc.abstractmethod
    def get_features(self, feature_id_list=None):
        """Retrieves all the available data for Genome Features.

        Args:
          feature_id_list (list<str>): List of features to retrieve.
            If None, returns all feature functions.
        
        Returns:
          dict<str,dict<str,list>>: Mapping from feature IDs to dicts
            of available data.
        """
        pass

    @abc.abstractmethod
    def get_proteins(self):
        """Retrieves all the available proteins for genome features.

        Returns:
          list<dict>"""
        pass

    @abc.abstractmethod
    def get_cds_by_mrna(self, mrna_feature_id_list=None):
        """Retrieves coding sequences (cds) for given mRNA feature IDs.

        Args:
           mrna_feature_id_list (list<str>): List of features to retrieve.
             If None, returns all values.
        Returns:
          ????
        """
        pass

    @abc.abstractmethod
    def get_mrna_by_cds(self, cds_feature_id_list=None):
        """Retrieves mRNA for given coding sequences (cds) feature IDs.

        Args:
           cds_feature_id_list (list<str>): List of features to retrieve.
             If None, returns all values.
        Returns:
          ????
        """
        pass

    @abc.abstractmethod
    def get_gene_by_cds(self, cds_feature_id_list=None):
        """Retrieves Genes for given coding sequence (cds)  feature IDs.

        Args:
           cds_feature_id_list (list<str>): List of features to retrieve.
             If None, returns all values.
        Returns:
          ????
        """
        pass
  
    @abc.abstractmethod
    def get_gene_by_mrna(self, mrna_feature_id_list=None):
        """Retrieves Genes for given mRNA feature IDs.

        Args:
           mrna_feature_id_list (list<str>): List of features to retrieve.
             If None, returns all values.
        Returns:
          ????
        """
        pass

    @abc.abstractmethod
    def get_cds_by_gene(self, gene_feature_id_list=None):
        """Retrieves coding sequences (cds) for given Gene feature IDs.

        Args:
           gene_feature_id_list (list<str>): List of features to retrieve.
             If None, returns all values.
        Returns:
          ????
        """
        pass
    
    @abc.abstractmethod
    def get_mrna_by_gene(self, gene_feature_id_list=None):
        """Retrieves mRNA for given Gene feature IDs.

        Args:
           gene_feature_id_list (list<str>): List of features to retrieve.
             If None, returns all values.
        Returns:
          ????
        """
        pass



class GenomeAnnotationAPI(ObjectAPI, GenomeInterface):
    """
    Factory class for instantiating a GenomeAnnotationAPI object of the correct subtype.
    """
    
    def __init__(self, services, token, ref):
        super(GenomeAnnotationAPI, self).__init__(services, token, ref)

        generic_object = ObjectAPI(services, token, ref)

        is_annotation_type = generic_object._typestring.split('-')[0] in _GENOME_ANNOTATION_TYPES
        is_genome_type = generic_object._typestring.split('-')[0] in _GENOME_TYPES
    
        if not (is_annotation_type or is_genome_type):
            raise TypeError("Invalid type! Expected one of {0}, received {1}".format(TYPES, generic_object._typestring))

        if is_annotation_type:
            self.proxy = _Prototype(services, token, ref)
        else:
            self.proxy = _KBaseGenomes_Genome(services, token, ref)

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
    


class _KBaseGenomes_Genome(ObjectAPI, GenomeInterface):
    def __init__(self, services, token, ref):
        super(_KBaseGenomes_Genome, self).__init__(services, token, ref)

    def get_taxon(self):
        from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
        return TaxonAPI(self.services, token=self._token, ref=self.ref)

    def get_assembly(self):
        from doekbase.data_api.sequence.assembly import AssemblyAPI
        return AssemblyAPI(self.services, self._token, ref=self.get_data_subset(path_list=["contigset_ref"])["contigset_ref"])

    def get_feature_types(self):
        feature_types = list()
        data = self.get_data()
        features = data["features"]

        for x in features:
            if x["type"] not in feature_types:
                feature_types.append(x["type"])

        return feature_types

    def get_feature_ids(self, type_list=None, region_list=None, function_list=None, alias_list=None):
        """
        Retrieves feature ids based on filters such as feature types, regions, functional descriptions, aliases.
        
        Returns:
          list<str>"""
        
        if type_list is None and region_list is None and function_list is None and alias_list is None:
            # just grab everything
            features = self.get_data_subset(path_list=["features"])["features"]
            feature_ids = dict()
            feature_ids["type"] = dict()
            for x in features:
                if x["type"] not in feature_ids["type"]:
                    feature_ids["type"][x["type"]] = list()

                feature_ids["type"][x["type"]].append(x['id'])

            return feature_ids

        # once we get here we have to start pulling and filtering features
        type_ids = None
        region_ids = None
        function_ids = None
        alias_ids = None

        data = self.get_data()

        if type_list is not None:
            if not isinstance(type_list, list):
                raise TypeError("A list of strings indicating feature types is required.")
            elif len(type_list) == 0:
                raise TypeError("A list of strings indicating feature types is required, received an empty list.")

            type_ids = dict()            
            for x in data["features"]:
                if x["type"] not in type_ids:
                    type_ids[x["type"]] = list()
                
                type_ids[x["type"]].append(x["id"])

        if region_list is not None:
            if not isinstance(region_list, list):
                raise TypeError("A list of region dictionaries is required.")
            elif len(region_list) == 0:
                raise TypeError("A list of region dictionaries is required, recieved an empty list.")

            if type_list is None:
                type_list = self.get_feature_types()
    
            def is_feature_in_regions(f, regions):
                location_key = None                
                
                if "location" in f:
                    location_key = "location"
                elif "locations" in f:
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

        if function_list is not None:
            if not isinstance(function_list, list):
                raise TypeError("A list of feature function strings is required.")
            elif len(function_list) == 0:
                raise TypeError("A list of feature function strings is required, recieved an empty list.")
            
            if type_list is None:        
                type_list = self.get_feature_types()
                        
            def is_function_in_feature(feature, function_tokens):
                if "function" not in feature:
                    return False
                
                tokens = feature["function"].split()
                
                for t in tokens:
                    if t in function_tokens:
                        return True
                
                return False
                    
            function_ids = dict()
            for function in function_list:
                function_tokens = function.split()
                function_ids[function] = [x['id'] for x in data["features"] if is_function_in_feature(x, function_tokens)]
                
        if alias_list is not None:
            if not isinstance(alias_list, list):
                raise TypeError("A list of feature alias strings is required.")
            elif len(alias_list) == 0:
                raise TypeError("A list of feature alias strings is required, recieved an empty list.")

            if type_list is None:
                type_list = self.get_feature_types()
            
            alias_ids = dict()            
            for alias in alias_list:
                alias_ids[alias] = list()
            
            for x in data["features"]:
                for alias in alias_list:
                    if "aliases" in x and alias in x["aliases"]:
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
        counts = dict()
        data = self.get_data()
        features = data["features"]

        if type_list is None:
            for x in features:
                if x["type"] not in counts:
                    counts[x["type"]] = 0

                counts[x["type"]] += 1
        else:
            try:
                assert len(type_list) > 0

                for t in type_list:
                    counts[t] = 0
            except TypeError:
                raise TypeError("A list of strings indicating feature types is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating feature types is required, received an empty list.")

            for x in features:
                if x["type"] in type_list:
                    counts[x["type"]] += 1
        
        return counts

    def get_feature_locations(self, feature_id_list=None):
        locations = dict()
        data = self.get_data()
        features = data["features"]

        if feature_id_list is None:
            for x in features:
                locations[x['id']] = list()
                if 'location' in x:
                    for loc in x['location']:
                        locations[x['id']].append({
                            "contig_id": loc[0],
                            "strand": loc[2],
                            "start": loc[1],
                            "length": loc[3]
                        })
        else:
            try:
                feature_refs = ["features/" + x for x in feature_id_list]
                assert len(feature_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")

            for x in features:
                if x['id'] in feature_id_list:
                    locations[x['id']] = list()

                    if 'location' in x:
                        for loc in x['location']:
                            locations[x['id']].append({
                                "contig_id": loc[0],
                                "strand": loc[2],
                                "start": loc[1],
                                "length": loc[3]
                            })

        return locations

    def get_feature_dna(self, feature_id_list=None):
        sequences = dict()
        data = self.get_data()
        features = data["features"]

        if feature_id_list is None:
            for x in features:
                if "sequence" in x:
                    sequences[x['id']] = x["sequence"]
                else:
                    sequences[x['id']] = None
        else:
            try:
                feature_refs = ["features/" + x for x in feature_id_list]
                assert len(feature_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")

            for x in features:
                if x['id'] in feature_id_list:
                    if "sequence" in x:
                        sequences[x['id']] = x["sequence"]
                    else:
                        sequences[x['id']] = None

        return sequences

    def get_feature_functions(self, feature_id_list=None):
        functions = dict()
        data = self.get_data()
        features = data["features"]

        if feature_id_list is None:
            for x in features:
                if "function" in x:
                    functions[x['id']] = x["function"]
                else:
                    functions[x['id']] = "Unknown"
        else:
            try:
                feature_refs = ["features/" + x for x in feature_id_list]
                assert len(feature_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")

            for x in features:
                if x['id'] in feature_id_list:
                    if "function" in x:
                        functions[x['id']] = x["function"]
                    else:
                        functions[x['id']] = "Unknown"

        return functions

    def get_feature_aliases(self, feature_id_list=None):
        aliases = dict()
        data = self.get_data()
        features = data["features"]

        if feature_id_list is None:
            for x in features:
                if "aliases" in x:
                    aliases[x['id']] = x["aliases"]
                else:
                    aliases[x['id']] = list()
        else:
            try:
                feature_refs = ["features/" + x for x in feature_id_list]
                assert len(feature_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")

            for x in features:
                if x['id'] in feature_id_list:
                    if "aliases" in x:
                        aliases[x['id']] = x["aliases"]
                    else:
                        aliases[x['id']] = list()

        return aliases
    
    def get_feature_publications(self, feature_id_list=None):
        publications = dict()
        data = self.get_data()
        features = data["features"]

        if feature_id_list is None:
            for x in features:
                if "publications" in x:
                    publications[x['id']] = x["publications"]
                else:
                    publications[x['id']] = list()
        else:
            try:
                feature_refs = ["features/" + x for x in feature_id_list]
                assert len(feature_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")

            for x in features:
                if x['id'] in feature_id_list:
                    if "publications" in x:
                        publications[x['id']] = x["publications"]
                    else:
                        publications[x['id']] = list()

        return publications

    def get_features(self, feature_id_list=None):
        out_features = dict()
        data = self.get_data()
        features = data["features"]

        def fill_out_feature(x):
            f = dict()
            f["feature_id"] = x['id']
            f["feature_type"] = x['type']
            f["feature_function"] = x['function']
            f["feature_locations"] = x['location']


            if 'dna_sequence' in x:
                f["feature_dna_sequence"] = x['dna_sequence']

                if 'md5' in x:
                    f["feature_md5"] = x['md5']
                else:
                    f["feature_md5"] = hashlib.md5(x["dna_sequence"].upper()).hexdigest()
            else:
                f["feature_dna_sequence"] = None
                f["feature_md5"] = None

            if 'dna_sequence_length' in x:
                f["feature_dna_sequence_length"] = x['dna_sequence_length']
            else:
                f["feature_dna_sequence_length"] = -1

            if 'publications' in x:
                f["feature_publications"] = x['publications']
            else:
                f["feature_publications"] = []

            if 'aliases' in x:
                f["feature_aliases"] = x['aliases']
            else:
                f["feature_aliases"] = []

            f["feature_notes"] = None
            f["feature_inference"] = None

            if "feature_quality_score" in x:
                f["feature_quality_score"] = x['quality']
            else:
                f["feature_quality_score"] = -1

            f["feature_quality_warnings"] = None

            return f

        if feature_id_list is None:
            for x in features:
                out_features[x['id']] = fill_out_feature(x)
        else:
            try:
                feature_refs = ["features/" + x for x in feature_id_list]
                assert len(feature_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")

            for x in features:
                if x['id'] in feature_id_list:
                    out_features[x['id']] = fill_out_feature(x)

        return out_features

    def get_proteins(self):
        proteins = dict()
        data = self.get_data()
        features = data["features"]
        
        for f in features:
            if "protein_translation" in f and len(f["protein_translation"]) > 0:
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
        try:
            feature_refs = ["features/" + x for x in mrna_feature_id_list]
            assert len(feature_refs) > 0
        except TypeError:
            raise TypeError("A list of strings indicating mrna feature identifiers is required.")
        except AssertionError:
            raise TypeError("A list of strings indicating mrna feature identifiers is required, received an empty list.")
 
        return {}

    def get_mrna_by_cds(self, cds_feature_id_list=None): 
        try:
            feature_refs = ["features/" + x for x in cds_feature_id_list]
            assert len(feature_refs) > 0
        except TypeError:
            raise TypeError("A list of strings indicating CDS feature identifiers is required.")
        except AssertionError:
            raise TypeError("A list of strings indicating CDS feature identifiers is required, received an empty list.") 

        return {} 

    def get_gene_by_cds(self, cds_feature_id_list=None):
        try:
            feature_refs = ["features/" + x for x in cds_feature_id_list]
            assert len(feature_refs) > 0
        except TypeError:
            raise TypeError("A list of strings indicating CDS feature identifiers is required.")
        except AssertionError:
            raise TypeError("A list of strings indicating CDS feature identifiers is required, received an empty list.")
 
        return {}
  
    def get_gene_by_mrna(self, mrna_feature_id_list=None):
        try:
            feature_refs = ["features/" + x for x in mrna_feature_id_list]
            assert len(feature_refs) > 0
        except TypeError:
            raise TypeError("A list of strings indicating mrna feature identifiers is required.")
        except AssertionError:
            raise TypeError("A list of strings indicating mrna feature identifiers is required, received an empty list.")

        return {} 

    def get_cds_by_gene(self, gene_feature_id_list=None):
        try:
            feature_refs = ["features/" + x for x in gene_feature_id_list]
            assert len(feature_refs) > 0
        except TypeError:
            raise TypeError("A list of strings indicating gene feature identifiers is required.")
        except AssertionError:
            raise TypeError("A list of strings indicating gene feature identifiers is required, received an empty list.") 

        return {}
    
    def get_mrna_by_gene(self, gene_feature_id_list=None):
        try:
            feature_refs = ["features/" + x for x in gene_feature_id_list]
            assert len(feature_refs) > 0
        except TypeError:
            raise TypeError("A list of strings indicating gene feature identifiers is required.")
        except AssertionError:
            raise TypeError("A list of strings indicating gene feature identifiers is required, received an empty list.")
 
        return {}



class _Prototype(ObjectAPI, GenomeInterface):
    def __init__(self, services, token, ref):
        super(_Prototype, self).__init__(services, token, ref)

    def _get_feature_containers(self, feature_id_list=None):
        if feature_id_list is None:
            feature_containers = self.get_data_subset(["feature_container_references"])["feature_container_references"].values()
        else:
            feature_lookup = self.get_data_subset(path_list=["feature_lookup"])["feature_lookup"]
            feature_containers = dict()

            try:
                assert len(feature_id_list) > 0

                for x in feature_id_list:
                    for feature_ref in feature_lookup[x]:
                        if feature_ref[0] not in feature_containers:
                            feature_containers[feature_ref[0]] = list()

                        feature_containers[feature_ref[0]].append(feature_ref[1])
            except TypeError:
                raise TypeError("A list of strings indicating feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")

        return feature_containers

    def get_taxon(self):
        from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
        return TaxonAPI(self.services, token=self._token, ref=self.get_data_subset(path_list=["taxon_ref"])["taxon_ref"])

    def get_assembly(self):
        from doekbase.data_api.sequence.assembly import AssemblyAPI
        return AssemblyAPI(self.services, token=self._token, ref=self.get_data_subset(path_list=["assembly_ref"])["assembly_ref"])

    def get_feature_types(self):
        return self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"].keys()

    def get_feature_ids(self, type_list=None, region_list=None, function_list=None, alias_list=None):
        """
        Retrieves feature ids based on filters such as feature types, regions, functional descriptions, aliases.
        
        Returns:
          dict<str>:dict<str>:list<str>"""
        
        if type_list is None and region_list is None and function_list is None and alias_list is None:
            # just grab everything
            feature_container_references = self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"]
            
            out_ids = {"type": {}}
            for x in feature_container_references:
                feature_container = ObjectAPI(self.services, self._token, feature_container_references[x])
                container_data = feature_container.get_data()
                out_ids[x] = container_data["features"].keys()
            return out_ids

        # once we get here we have to start pulling and filtering features
        type_ids = None
        region_ids = None
        function_ids = None
        alias_ids = None

        data = self.get_data()
        
        feature_container_references = data["feature_container_references"]        
        features = dict()

        if type_list is not None:
            if not isinstance(type_list, list):
                raise TypeError("A list of strings indicating feature types is required.")
            elif len(type_list) == 0:
                raise TypeError("A list of strings indicating feature types is required, received an empty list.")

            type_ids = dict()
            for x in type_list:
                type_ids[x] = list()
            
            for f in feature_container_references:
                if f in type_list:
                    if f not in features:
                        features[f] = ObjectAPI(self.services, self._token, feature_container_references[f]).get_data()["features"]
                    
                    type_ids[f] = features[f].keys()                    

        if region_list is not None:
            if not isinstance(region_list, list):
                raise TypeError("A list of region dictionaries is required.")
            elif len(region_list) == 0:
                raise TypeError("A list of region dictionaries is required, recieved an empty list.")

            def is_feature_in_region(f, region):
                location_key = None                
                
                if "location" in f:
                    location_key = "location"
                elif "locations" in f:
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
                if f not in features:
                    features[f] = ObjectAPI(self.services, self._token, feature_container_references[f]).get_data()["features"]
                
                for x in features[f]:
                    for r in region_list:
                        if is_feature_in_region(features[f][x], r):
                            region_ids[r["contig_id"]].append(features[f][x]["feature_id"])

        if function_list is not None:
            if not isinstance(function_list, list):
                raise TypeError("A list of feature function strings is required.")
            elif len(function_list) == 0:
                raise TypeError("A list of feature function strings is required, recieved an empty list.")

            function_tokens = list()
            for x in function_list:
                function_tokens.extend(x.split())
            function_tokens = set(function_tokens)
            
            def is_function_in_feature(feature, function_tokens):
                if 'function' not in feature:
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
                    if f not in features:
                        features[f] = ObjectAPI(self.services, self._token, feature_container_references[f]).get_data()["features"]
                
                    for x in features[f]:
                        if is_function_in_feature(features[f][x], function_tokens):
                            function_ids[function].append(features[f][x]["feature_id"])
                
        if alias_list is not None:
            if not isinstance(alias_list, list):
                raise TypeError("A list of feature alias strings is required.")
            elif len(alias_list) == 0:
                raise TypeError("A list of feature alias strings is required, received an empty list.")

            if type_list is None:
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

    def _get_feature_data(self, data=None, feature_id_list=None):
        out = dict()
        feature_containers = self._get_feature_containers(feature_id_list)

        if feature_id_list is not None:
            try:
                feature_refs = ["features/" + x for x in feature_id_list]
                assert len(feature_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating feature " +
                                "identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating feature " +
                                "identifiers is required, " +
                                "received an empty list.")

        for ref in feature_containers:
            if feature_id_list is None:
                features = ObjectAPI(self.services, self._token, ref).get_data()["features"]
                working_list = features
            else:
                container = ObjectAPI(self.services, self._token, ref)
                features = container.get_data_subset(path_list=feature_refs)["features"]
                working_list = feature_id_list

            if data == "aliases":
                for feature_id in working_list:
                    if "aliases" in features[feature_id]:
                        out[feature_id] = features[feature_id]["aliases"]
                    else:
                        out[feature_id] = list()
            elif data == "locations":
                for feature_id in working_list:
                    out[feature_id] = list()
                    for loc in features[feature_id]["locations"]:
                        out[feature_id].append({
                            "contig_id": loc[0],
                            "strand": loc[2],
                            "start": loc[1],
                            "length": loc[3]
                    })
            elif data == "dna":
                for feature_id in working_list:
                    out[feature_id] = features[feature_id]["dna_sequence"]
            elif data == "publications":
                for feature_id in working_list:
                    if "publications" in features[feature_id]:
                        out[feature_id] = features[feature_id]["publications"]
                    else:
                        out[feature_id] = list()
            elif data == "functions":
                for feature_id in working_list:
                    if "function" in features[feature_id]:
                        out[feature_id] = features[feature_id]["function"]
                    else:
                        out[feature_id] = "Unknown"

        return out

    def get_feature_locations(self, feature_id_list=None):
        return self._get_feature_data("locations", feature_id_list)

    def get_feature_dna(self, feature_id_list=None):
        return self._get_feature_data("dna", feature_id_list)

    def get_feature_functions(self, feature_id_list=None):
        return self._get_feature_data("functions", feature_id_list)

    def get_feature_aliases(self, feature_id_list=None):
        return self._get_feature_data("aliases", feature_id_list)

    def get_feature_publications(self, feature_id_list=None):
        return self._get_feature_data("publications", feature_id_list)

    def get_features(self, feature_id_list=None):
        out_features = dict()
        feature_containers = self._get_feature_containers(feature_id_list)

        for ref in feature_containers:
            container = ObjectAPI(self.services, self._token, ref)
            if feature_id_list is None:
                features = container.get_data()["features"]
                working_list = features
            else:
                features = container.get_data_subset(
                    path_list=["features/" + x for x in feature_containers[ref]])["features"]
                working_list = feature_containers[ref]
            
            for x in working_list:
                out_features[features[x]['feature_id']] = dict()
                out_features[x]["feature_id"] = features[x]['feature_id']
                out_features[x]["feature_type"] = features[x]['type']
                out_features[x]["feature_md5"] = features[x]['md5']
                out_features[x]["feature_dna_sequence"] = features[x]['dna_sequence']
                out_features[x]["feature_dna_sequence_length"] = features[x]['dna_sequence_length']
                out_features[x]["feature_locations"] = features[x]['locations']
                
                if 'function' in features[x]:
                    out_features[x]["feature_function"] = features[x]['function']
                else:
                    out_features[x]["feature_function"] = "Unknown"

                if 'publications' in features[x]:
                    out_features[x]["feature_publications"] = features[x]['publications']
                else:
                    out_features[x]["feature_publications"] = []

                if 'aliases' in features[x]:
                    out_features[x]["feature_aliases"] = features[x]['aliases']
                else:
                    out_features[x]["feature_aliases"] = []
                    
                if 'notes' in features[x]:
                    out_features[x]["feature_notes"] = features[x]['notes']
                else:
                    out_features[x]["feature_notes"] = []

                if 'inference' in features[x]:
                    out_features[x]["feature_inference"] = features[x]['inference']
                else:
                    out_features[x]["feature_inference"] = "Unknown"

                if 'quality' in features[x]:
                    out_features[x]["feature_quality_score"] = features[x]['quality']
                else:
                    out_features[x]["feature_quality_score"] = []

                if 'quality_warnings' in features[x]:
                    out_features[x]["feature_quality_warnings"] = features[x]['quality_warnings']
                else:
                    out_features[x]["feature_quality_warnings"] = []
        
        return out_features

    def get_proteins(self):
        protein_container = ObjectAPI(self.services, self._token, self.get_data()["protein_container_ref"])
        return protein_container.get_data()["proteins"]

    def _get_by_mrna(self, feature_type=None, mrna_feature_id_list=None):
        out = dict()

        feature_container_references = self.get_data_subset(
            path_list=["feature_container_references"])["feature_container_references"]

        if "mRNA" in feature_container_references:
            try:
                mrna_refs = ["features/" + x for x in mrna_feature_id_list]
                assert len(mrna_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating feature " +
                                "identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating feature " +
                                "identifiers is required, " +
                                "received an empty list.")

            mrna_feature_container_ref = feature_container_references["mRNA"]
            mrna_feature_container = ObjectAPI(self.services,
                                               self._token,
                                               mrna_feature_container_ref)
            mrna_features = mrna_feature_container.get_data_subset(path_list=mrna_refs)["features"]

            for mrna_feature_key in mrna_features:
                mrna_id = mrna_features[mrna_feature_key]["feature_id"]

                if feature_type == "cds" and "mRNA_properties" in mrna_features[mrna_feature_key] and \
                "associated_CDS" in mrna_features[mrna_feature_key]["mRNA_properties"]:
                    out[mrna_id] = mrna_features[mrna_feature_key]["mRNA_properties"]["associated_CDS"][1]
                elif feature_type == "gene" and "mRNA_properties" in mrna_features[mrna_feature_key] and \
                "parent_gene" in mrna_features[mrna_feature_key]["mRNA_properties"]:
                    out[mrna_id] =  mrna_features[mrna_feature_key]["mRNA_properties"]["parent_gene"][1]
                else:
                    out[mrna_id] = None

        return out

    def get_cds_by_mrna(self, mrna_feature_id_list=None):
        return self._get_by_mrna("cds", mrna_feature_id_list)

    def get_gene_by_mrna(self, mrna_feature_id_list=None):
        return self._get_by_mrna("gene", mrna_feature_id_list)

    def _get_by_cds(self, feature_type=None, cds_feature_id_list=None):
        out = dict()

        feature_container_references = self.get_data_subset(
            path_list=["feature_container_references"])["feature_container_references"]

        if "CDS" in feature_container_references:
            try:
                cds_refs = ["features/" + x for x in cds_feature_id_list]
                assert len(cds_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating feature " +
                                "identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating feature " +
                                "identifiers is required, " +
                                "received an empty list.")

            cds_feature_container_ref = feature_container_references["CDS"]
            cds_feature_container = ObjectAPI(self.services,
                                              self._token,
                                              cds_feature_container_ref)
            cds_features = cds_feature_container.get_data_subset(path_list=cds_refs)["features"]

            for cds_feature_key in cds_features:
                cds_id = cds_features[cds_feature_key]["feature_id"]

                if feature_type == "mrna" and "CDS_properties" in cds_features[cds_feature_key] and \
                "associated_mRNA" in cds_features[cds_feature_key]["CDS_properties"]:
                    out[cds_id] = cds_features[cds_feature_key]["CDS_properties"]["associated_mRNA"][1]
                elif feature_type == "gene" and "CDS_properties" in cds_features[cds_feature_key] and \
                "associated_mRNA" in cds_features[cds_feature_key]["CDS_properties"]:
                    out[cds_id] = cds_features[cds_feature_key]["CDS_properties"]["parent_gene"][1]
                else:
                    out[cds_id] = None

        return out

    def get_mrna_by_cds(self, cds_feature_id_list=None):
        return self._get_by_cds("mrna", cds_feature_id_list)

    def get_gene_by_cds(self, cds_feature_id_list=None):
        return self._get_by_cds("gene", cds_feature_id_list)

    def _get_by_gene(self, feature_type=None, gene_feature_id_list=None):
        out = dict()

        feature_container_references = self.get_data_subset(
            path_list=["feature_container_references"])["feature_container_references"]

        if "gene" in feature_container_references:
            try:
                gene_refs = ["features/" + x for x in gene_feature_id_list]
                assert len(gene_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating feature " +
                                "identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating feature " +
                                "identifiers is required, " +
                                "received an empty list.")

            gene_feature_container = ObjectAPI(self.services,
                                               self._token,
                                               feature_container_references["gene"])
            gene_features = gene_feature_container.get_data_subset(path_list=gene_refs)["features"]

            for gene_feature_key in gene_features:
                gene_id = gene_features[gene_feature_key]["feature_id"]
                out[gene_id] = list()

                if feature_type == "cds" and "gene_properties" in gene_features[gene_feature_key] and \
                "children_CDS" in gene_features[gene_feature_key]["gene_properties"]:
                    for cds_tuple in gene_features[gene_feature_key]["gene_properties"]["children_CDS"]:
                        out[gene_id].append(cds_tuple[1])
                elif feature_type == "mrna" and "gene_properties" in gene_features[gene_feature_key] and \
                "children_mRNA" in gene_features[gene_feature_key]["gene_properties"]:
                    for mrna_tuple in gene_features[gene_feature_key]["gene_properties"]["children_mRNA"]:
                        out[gene_id].append(mrna_tuple[1])

        return out

    def get_cds_by_gene(self, gene_feature_id_list=None):
        return self._get_by_gene("cds", gene_feature_id_list)

    def get_mrna_by_gene(self, gene_feature_id_list=None):
        return self._get_by_gene("mrna", gene_feature_id_list)