"""
Data API for Genome Annotation entities.  This API provides methods for retrieving the
Assembly and Taxon associated with an annotation, as well as retrieving individual features.
"""

# stdlib imports
import abc
import hashlib

# 3rd party imports
import blist

# local imports
from doekbase.data_api.core import ObjectAPI
from doekbase.data_api.util import get_logger, logged
from doekbase.data_api import exceptions
import doekbase.data_api.annotation.genome_annotation.service.ttypes as ttypes

_GENOME_TYPES = ['KBaseGenomes.Genome']
_GENOME_ANNOTATION_TYPES = ['KBaseGenomeAnnotations.GenomeAnnotation']
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

_log = get_logger("GenomeAnnotationAPI")


class GenomeAnnotationInterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_taxon(self, ref_only=False):
        """Retrieves the Taxon assigned to this Genome Annotation.
        
        Returns:
          TaxonAPI: Taxon object
        """
        pass

    @abc.abstractmethod
    def get_assembly(self, ref_only=False):
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
    def get_feature_ids(self, filters=None, group_by="type"):
        """Retrieves feature ids based on filters such as feature types,
        regions, functional descriptions, aliases.
        
        If no filters are applied, all feature ids will be returned.
        Only the group_by selected will be included in the results.
        
        Retrieves feature ids based on filters such as feature types, regions, functional descriptions, aliases.

        Args:
          filters: Optional dictionary of filters that can be applied to object contents.
                   Recognized filter keys:
                       "type_list" - List of feature type strings.
                                     Should be findable in :data:`FEATURE_DESCRIPTIONS`.
                       "region_list" - List of region specs.
                                       e.g.,[{"contig_id": str, "strand": "+"|"-"|"?", "start": int, "length": int},...]
                       "function_list" - List of function strings to match.
                       "alias_ist" - List of alias strings to match.

          group_by: Specify the grouping of feature ids returned.
                    Recognized values are one of ["type","region","function","alias"]
                    Defaults to "type".

        Returns:
          {"by_type": dict<str feature_type, list<str feature_id>>,
           "by_region": dict<str contig_id, dict<str strand, dict<string range, list<string feature_id>>>>,
           "by_function": dict<str function, list<str feature_id>>,
           "by_alias": dict<str alias, list<str feature_id>>}"""

        pass  # TODO: add examples in docs for function_list and alias_list

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
    def get_cds_by_mrna(self, mrna_feature_id_list=None):
        """Retrieves coding sequences (cds) for given mRNA feature IDs.

        Args:
           mrna_feature_id_list (list<str>): List of mrna feature ids to map to cds feature ids.
             If None, returns all mappings between mrna feature ids and cds feature ids.
        Returns:
          dict<str>: str
        """
        pass

    @abc.abstractmethod
    def get_mrna_by_cds(self, cds_feature_id_list=None):
        """Retrieves mRNA for given coding sequences (cds) feature IDs.

        Args:
           cds_feature_id_list (list<str>): List of cds feature ids to map to mrna feature ids.
             If None, returns all mappings between cds feature ids and mrna feature ids
        Returns:
          dict<str>: str
        """
        pass

    @abc.abstractmethod
    def get_gene_by_cds(self, cds_feature_id_list=None):
        """Retrieves Genes for given coding sequence (cds)  feature IDs.

        Args:
           cds_feature_id_list (list<str>): List of features to retrieve.
             If None, returns all values.
        Returns:
          dict<str>: str
        """
        pass
  
    @abc.abstractmethod
    def get_gene_by_mrna(self, mrna_feature_id_list=None):
        """Retrieves Genes for given mRNA feature IDs.

        Args:
           mrna_feature_id_list (list<str>): List of gene feature ids to map to mrna feature ids.
             If None, returns all values.
        Returns:
          dict<str>: str
        """
        pass

    @abc.abstractmethod
    def get_cds_by_gene(self, gene_feature_id_list=None):
        """Retrieves coding sequences (cds) for given Gene feature IDs.

        Args:
           gene_feature_id_list (list<str>): List of features to retrieve.
             If None, returns all values.
        Returns:
          dict<str>: list<str>
        """
        pass
    
    @abc.abstractmethod
    def get_mrna_by_gene(self, gene_feature_id_list=None):
        """Retrieves mRNA for given Gene feature IDs.

        Args:
           gene_feature_id_list (list<str>): List of mrna feature ids to map to gene feature ids.
             If None, returns all values.
        Returns:
          dict<str>: list<str>
        """
        pass



class GenomeAnnotationAPI(ObjectAPI, GenomeAnnotationInterface):
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
            self.proxy = _GenomeAnnotation(services, token, ref)
        else:
            self.proxy = _KBaseGenomes_Genome(services, token, ref)

    def get_taxon(self, ref_only=False):
        return self.proxy.get_taxon(ref_only)

    def get_assembly(self, ref_only=False):
        return self.proxy.get_assembly(ref_only)
    
    def get_feature_types(self):
        return self.proxy.get_feature_types()

    def get_feature_ids(self, filters=None, group_by="type"):
        return self.proxy.get_feature_ids(filters, group_by)

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
    

class _KBaseGenomes_Genome(ObjectAPI, GenomeAnnotationInterface):
    def __init__(self, services, token, ref):
        super(_KBaseGenomes_Genome, self).__init__(services, token, ref)
        self._data_features_blist = None  # see self._get_features()

    def get_taxon(self, ref_only=False):
        from doekbase.data_api.taxonomy.taxon.api import TaxonAPI

        if ref_only:
            return self.ref
        else:
            return TaxonAPI(self.services, token=self._token, ref=self.ref)

    def get_assembly(self, ref_only=False):
        from doekbase.data_api.sequence.assembly.api import AssemblyAPI

        contigset_ref = self.get_data_subset(path_list=["contigset_ref"])["contigset_ref"]

        if ref_only:
            return contigset_ref
        else:
            return AssemblyAPI(self.services, self._token, ref=contigset_ref)

    def get_feature_types(self):
        feature_types = list()
        features = self._get_features()

        for x in features:
            if "type" in x and x["type"] not in feature_types:
                feature_types.append(x["type"])

        return feature_types

    def get_feature_ids(self, filters=None, group_by="type"):
        # no choice but to pull all features
        features = self._get_features()

        _log.debug('get_feature_ids.start num_features={:d}'.format(len(
            features)))

        # now process all filters and reduce the data
        if filters is None:
            filters = dict()

        if "type_list" in filters and filters["type_list"] is not None:
            if not isinstance(filters["type_list"], list):
                raise TypeError("A list of strings indicating feature types is required.")
            elif len(filters["type_list"]) == 0:
                raise TypeError("A list of strings indicating feature types is required, received an empty list.")

            remove_features = list()
            for i in xrange(len(features)):
                if features[i]["type"] not in filters["type_list"]:
                    remove_features.append(i)
            if len(remove_features) > 0:
                for i in reversed(remove_features):
                    del features[i]

        if "region_list" in filters and filters["region_list"] is not None:
            if not isinstance(filters["region_list"], list):
                raise TypeError("A list of region dictionaries is required.")
            elif len(filters["region_list"]) == 0:
                raise TypeError("A list of region dictionaries is required, received an empty list.")

            def is_feature_in_regions(f, regions):
                if "location" not in f:
                    return False

                for loc in f["location"]:
                    for r in regions:
                        if r["contig_id"] == loc[0] and \
                           (loc[2] == r["strand"] or r["strand"] == "?"):

                            if loc[2] == "+" and \
                               max(loc[1], r["start"]) <= min(loc[1]+loc[3], r["start"] + r["length"]):
                                return True
                            elif loc[2] == "-" and \
                               max(loc[1]+loc[3], r["start"]) <= min(loc[1], r["start"]):
                                return True
                return False

            remove_features = list()
            for i in xrange(len(features)):
                if not is_feature_in_regions(features[i], filters["region_list"]):
                    remove_features.append(i)
            if len(remove_features) > 0:
                for i in reversed(remove_features):
                    del features[i]

        if "function_list" in filters and filters["function_list"] is not None:
            if not isinstance(filters["function_list"], list):
                raise TypeError("A list of feature function strings is required.")
            elif len(filters["function_list"]) == 0:
                raise TypeError("A list of feature function strings is required, received an empty list.")

            remove_features = list()
            for i in xrange(len(features)):
                if "function" not in features[i]:
                    remove_features.append(i)
                else:
                    found = False
                    for f in filters["function_list"]:
                        if features[i]["function"].find(f) >= 0:
                            found = True
                            break

                    if not found:
                        remove_features.append(i)
            if len(remove_features) > 0:
                for i in reversed(remove_features):
                    del features[i]

        if "alias_list" in filters and filters["alias_list"] is not None:
            if not isinstance(filters["alias_list"], list):
                raise TypeError("A list of feature alias strings is required.")
            elif len(filters["alias_list"]) == 0:
                raise TypeError("A list of feature alias strings is required, received an empty list.")

            remove_features = list()
            for i in xrange(len(features)):
                if "aliases" not in features[i]:
                    remove_features.append(i)
                else:
                    found = False
                    for alias in filters["alias_list"]:
                        if alias in features[i]["aliases"]:
                            found = True

                    if not found:
                        remove_features.append(i)
            if len(remove_features) > 0:
                for i in reversed(remove_features):
                    del features[i]

        # now that filtering has been completed, attempt to group the data as requested
        results = dict()

        if group_by == "type":
            results["by_type"] = dict()
            for x in features:
                if x["type"] not in results["by_type"]:
                    results["by_type"][x["type"]] = list()

                results["by_type"][x["type"]].append(x["id"])
        elif group_by == "region":
            results["by_region"] = dict()
            for x in features:
                for r in x["location"]:
                    contig_id = r[0]
                    strand = r[2]
                    start = r[1]
                    length = r[3]
                    range = "{}-{}".format(start,start+length)

                    if contig_id not in results["by_region"]:
                        results["by_region"][contig_id] = dict()

                    if strand not in results["by_region"][contig_id]:
                        results["by_region"][contig_id][strand] = dict()

                    if range not in results["by_region"][contig_id][strand]:
                        results["by_region"][contig_id][strand][range] = list()

                    results["by_region"][contig_id][strand][range].append(x["id"])
        elif group_by == "function":
            results["by_function"] = dict()
            for x in features:
                if x["function"] not in results["by_function"]:
                    results["by_function"][x["function"]] = list()

                results["by_function"][x["function"]].append(x["id"])
        elif group_by == "alias":
            results["by_alias"] = dict()
            for x in features:
                for alias in x["aliases"]:
                    if alias not in results["by_alias"]:
                        results["by_alias"][alias] = list()

                    results["by_alias"][alias].append(x["id"])

        _log.debug('get_feature_ids.end num_features={:d}'.format(len(
            features)))

        return results


    def get_feature_type_counts(self, type_list=None):
        """
        Retrieves number of Genome Features from a KBaseGenomes.Genome object, filtering on Feature type.

        Returns:
          dict<str>:int"""
        counts = dict()
        features = self.get_data()["features"]

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
        features = self._get_features()

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
        features = self._get_features()

        if feature_id_list is None:
            for x in features:
                if "sequence" in x:
                    sequences[x['id']] = x["sequence"]
                else:
                    sequences[x['id']] = ""
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
                        sequences[x['id']] = ""

        return sequences

    def get_feature_functions(self, feature_id_list=None):
        functions = dict()
        features = self._get_features()

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
        features = self._get_features()

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
        features = self._get_features()

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
        features = self._get_features()

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
                f["feature_dna_sequence"] = ""
                f["feature_md5"] = ""

            if 'dna_sequence_length' in x:
                f["feature_dna_sequence_length"] = x['dna_sequence_length']
            else:
                f["feature_dna_sequence_length"] = -1

            if 'publications' in x:
                f["feature_publications"] = x['publications']
            else:
                f["feature_publications"] = []

            if 'aliases' in x:
                f["feature_aliases"] = {k: list() for k in x['aliases']}
            else:
                f["feature_aliases"] = {}

            f["feature_notes"] = []
            f["feature_inference"] = ""

            if "feature_quality_score" in x:
                f["feature_quality_score"] = str(x['quality'])
            else:
                f["feature_quality_score"] = ""

            f["feature_quality_warnings"] = []

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
        features = self._get_features()
        
        for f in features:
            if "protein_translation" in f and len(f["protein_translation"]) > 0:
                protein_id = f['id'] + ".protein"
                proteins[protein_id] = dict()
                proteins[protein_id]["protein_id"] = protein_id
                proteins[protein_id]["protein_amino_acid_sequence"] = f["protein_translation"]
                proteins[protein_id]["protein_function"] = None
                proteins[protein_id]["protein_aliases"] = None
                proteins[protein_id]["protein_md5"] = hashlib.md5(f["protein_translation"].upper()).hexdigest()

                # may need to revisit this                
                proteins[protein_id]["protein_domain_locations"] = None
        
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

    def _get_features(self):
        """Get a *copy* of the features.
        The original list of features should not be modified anywhere.
        """
        # create/cache a 'blist' version of the features so copying will be cheap
        if self._data_features_blist is None:
            self._data_features_blist = blist.blist(self.get_data()['features'])
        # return a copy of the underlying list
        return self._data_features_blist[:]


class _GenomeAnnotation(ObjectAPI, GenomeAnnotationInterface):
    def __init__(self, services, token, ref):
        super(_GenomeAnnotation, self).__init__(services, token, ref)

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

    def get_taxon(self, ref_only=False):
        from doekbase.data_api.taxonomy.taxon.api import TaxonAPI

        taxon_ref = self.get_data_subset(path_list=["taxon_ref"])["taxon_ref"]

        if ref_only:
            return taxon_ref
        else:
            return TaxonAPI(self.services, token=self._token, ref=taxon_ref)

    def get_assembly(self, ref_only=False):
        from doekbase.data_api.sequence.assembly.api import AssemblyAPI

        assembly_ref = self.get_data_subset(path_list=["assembly_ref"])["assembly_ref"]

        if ref_only:
            return assembly_ref
        else:
            return AssemblyAPI(self.services, token=self._token, ref=assembly_ref)

    def get_feature_types(self):
        return self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"].keys()

    def get_feature_ids(self, filters=None, group_by="type"):
        if filters is None:
            filters = dict()

        data = self.get_data()

        feature_container_references = data["feature_container_references"]
        features = dict()

        # process all filters
        if "type_list" in filters and filters["type_list"] is not None:
            if not isinstance(filters["type_list"], list):
                raise TypeError("A list of strings indicating feature types is required.")
            elif len(filters["type_list"]) == 0:
                raise TypeError("A list of strings indicating feature types is required, received an empty list.")

            # only pull data for features that are in the type_list
            for f in feature_container_references:
                if f in filters["type_list"]:
                    container_data = ObjectAPI(self.services, self._token, feature_container_references[f]).get_data()["features"]
                    features.update(container_data)
        else:
            # pull down all features
            for f in feature_container_references:
                container_data = ObjectAPI(self.services, self._token, feature_container_references[f]).get_data()["features"]
                features.update(container_data)

        if "region_list" in filters and filters["region_list"] is not None:
            if not isinstance(filters["region_list"], list):
                raise TypeError("A list of region dictionaries is required.")
            elif len(filters["region_list"]) == 0:
                raise TypeError("A list of region dictionaries is required, received an empty list.")

            def is_feature_in_regions(f, regions):
                for loc in f["locations"]:
                    for r in regions:
                        if r["contig_id"] == loc[0] and \
                           (loc[2] == r["strand"] or r["strand"] == "?"):

                            if loc[2] == "+" and \
                               max(loc[1], r["start"]) <= min(loc[1]+loc[3], r["start"] + r["length"]):
                                return True
                            elif loc[2] == "-" and \
                               max(loc[1]+loc[3], r["start"]) <= min(loc[1], r["start"]):
                                return True
                return False

            remove_features = list()

            for f in features:
                if not is_feature_in_regions(features[f], filters["region_list"]):
                    remove_features.append(f)

            for f in remove_features:
                del features[f]

        if "function_list" in filters and filters["function_list"] is not None:
            if not isinstance(filters["function_list"], list):
                raise TypeError("A list of feature function strings is required.")
            elif len(filters["function_list"]) == 0:
                raise TypeError("A list of feature function strings is required, received an empty list.")

            remove_features = list()

            for f in features:
                if "function" not in features[f]:
                    remove_features.append(f)
                else:
                    found = False
                    for func in filters["function_list"]:
                        if features[f]["function"].find(func) >= 0:
                            found = True

                    if not found:
                        remove_features.append(f)

            for f in remove_features:
                del features[f]

        if "alias_list" in filters and filters["alias_list"] is not None:
            if not isinstance(filters["alias_list"], list):
                raise TypeError("A list of feature alias strings is required.")
            elif len(filters["alias_list"]) == 0:
                raise TypeError("A list of feature alias strings is required, received an empty list.")

            remove_features = list()

            for f in features:
                if "aliases" not in features[f]:
                    remove_features.append(f)
                else:
                    found = False
                    for alias in filters["alias_list"]:
                        if alias in features[f]["aliases"]:
                            found = True

                    if not found:
                        remove_features.append(f)

            for f in remove_features:
                del features[f]

        # now that filtering has been completed, attempt to group the data as requested
        results = dict()

        if group_by == "type":
            results["by_type"] = dict()
            for x in features:
                if features[x]["type"] not in results["by_type"]:
                    results["by_type"][features[x]["type"]] = list()

                results["by_type"][features[x]["type"]].append(features[x]["feature_id"])
        elif group_by == "region":
            results["by_region"] = dict()
            for x in features:
                for r in features[x]["locations"]:
                    contig_id = r[0]
                    strand = r[2]
                    start = r[1]
                    length = r[3]
                    range = "{}-{}".format(start,start+length)

                    if contig_id not in results["by_region"]:
                        results["by_region"][contig_id] = dict()

                    if strand not in results["by_region"][contig_id]:
                        results["by_region"][contig_id][strand] = dict()

                    if range not in results["by_region"][contig_id][strand]:
                        results["by_region"][contig_id][strand][range] = list()

                    results["by_region"][contig_id][strand][range].append(features[x]["feature_id"])
        elif group_by == "function":
            results["by_function"] = dict()
            for x in features:
                if features[x]["function"] not in results["by_function"]:
                    results["by_function"][features[x]["function"]] = list()

                results["by_function"][features[x]["function"]].append(features[x]["feature_id"])
        elif group_by == "alias":
            results["by_alias"] = dict()
            for x in features:
                if "aliases" in features[x]:
                    for alias in features[x]["aliases"]:
                        if alias not in results["by_alias"]:
                            results["by_alias"][alias] = list()

                        results["by_alias"][alias].append(features[x]["feature_id"])

        return results

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
            # Get list of feature IDs
            if feature_id_list is None:
                features = ObjectAPI(self.services, self._token, ref).get_data()["features"]
                working_list = features
            else:
                container = ObjectAPI(self.services, self._token, ref)
                features = container.get_data_subset(path_list=feature_refs)["features"]
                working_list = feature_id_list
            # Pull out either aliases or locations from each feature
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

        def fill_out_feature(x):
            f = dict()
            f["feature_id"] = x['feature_id']
            f["feature_type"] = x['type']
            f["feature_md5"] = x['md5']
            f["feature_dna_sequence"] = x['dna_sequence']
            f["feature_dna_sequence_length"] = x['dna_sequence_length']
            f["feature_locations"] = x['locations']

            if 'function' in x:
                f["feature_function"] = x['function']
            else:
                f["feature_function"] = "Unknown"

            if 'publications' in x:
                f["feature_publications"] = x['publications']
            else:
                f["feature_publications"] = []

            if 'aliases' in x:
                f["feature_aliases"] = x['aliases']
            else:
                f["feature_aliases"] = {}

            if 'notes' in x:
                f["feature_notes"] = x['notes']
            else:
                f["feature_notes"] = []

            if 'inference' in x:
                f["feature_inference"] = x['inference']
            else:
                f["feature_inference"] = "Unknown"

            if 'quality' in x:
                f["feature_quality_score"] = x['quality']
            else:
                f["feature_quality_score"] = []

            if 'quality_warnings' in x:
                f["feature_quality_warnings"] = x['quality_warnings']
            else:
                f["feature_quality_warnings"] = []

            return f


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
                out_features[x] = fill_out_feature(features[x])

        return out_features

    def get_proteins(self):
        protein_container = ObjectAPI(self.services, self._token, self.get_data()["protein_container_ref"])
        result = protein_container.get_data()["proteins"]

        output = dict()
        for x in result:
            output[x] = dict()
            for k in result[x]:
                if k.startswith("protein_"):
                    output[x][k] = result[x][k]
                else:
                    output[x]["protein_" + k] = result[x][k]
        return output

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


_ga_log = get_logger('GenomeAnnotationClientAPI')

class GenomeAnnotationClientAPI(GenomeAnnotationInterface):

    def client_method(func):
        def wrapper(self, *args, **kwargs):
            if not self.transport.isOpen():
                self.transport.open()

            try:
                return func(self, *args, **kwargs)
            except ttypes.AttributeException, e:
                raise AttributeError(e.message)
            except ttypes.AuthenticationException, e:
                raise exceptions.AuthenticationError(e.message)
            except ttypes.AuthorizationException, e:
                raise exceptions.AuthorizationError(e.message)
            except ttypes.TypeException, e:
                raise exceptions.TypeError(e.message)
            except ttypes.ServiceException, e:
                raise exceptions.ServiceError(e.message)
            except Exception, e:
                raise
            finally:
                self.transport.close()
        return wrapper

    @logged(_ga_log, log_name='init')
    def __init__(self, url=None, token=None, ref=None):
        from doekbase.data_api.annotation.genome_annotation.service.interface import GenomeAnnotationClientConnection

        #TODO add exception handling and better error messages here
        self.url = url
        self.transport, self.client = GenomeAnnotationClientConnection(url).get_client()
        self.ref = ref
        self._token = token

    @logged(_ga_log)
    @client_method
    def get_taxon(self, ref_only=False):
        return self.client.get_taxon(self._token, self.ref)

    @logged(_ga_log)
    @client_method
    def get_assembly(self, ref_only=False):
        return self.client.get_assembly(self._token, self.ref)

    @logged(_ga_log)
    @client_method
    def get_feature_types(self):
        return self.client.get_feature_types(self._token, self.ref)
    
    @logged(_ga_log)
    @client_method
    def get_feature_type_descriptions(self, type_list=None):
        return self.client.get_feature_type_descriptions(self._token, self.ref, type_list)

    @logged(_ga_log)
    @client_method
    def get_feature_type_counts(self, type_list=None):
        return self.client.get_feature_type_counts(self._token, self.ref, type_list)

    @logged(_ga_log)
    @client_method
    def get_feature_ids(self, filters=None, group_by="type"):
        converted_filters = ttypes.Feature_id_filters()
        if filters is not None:
            if "type_list" in filters:
                type_list = filters["type_list"]
            else:
                type_list = list()

            if "region_list" in filters:
                region_list = [ttypes.Region(**x) for x in filters["region_list"]]
            else:
                region_list = list()

            if "function_list" in filters:
                function_list = filters["function_list"]
            else:
                function_list = list()

            if "alias_list" in filters:
                alias_list = filters["alias_list"]
            else:
                alias_list = list()

            converted_filters = ttypes.Feature_id_filters(type_list=type_list,
                                                          region_list=region_list,
                                                          function_list=function_list,
                                                          alias_list=alias_list)

        result = self.client.get_feature_ids(self._token, self.ref, converted_filters, group_by)

        group_key = "by_{}".format(group_by)

        return {group_key: result.__dict__[group_key]}

    @logged(_ga_log)
    @client_method
    def get_features(self, feature_id_list=None):
        result = self.client.get_features(self._token, self.ref, feature_id_list)

        output = dict()
        for x in result:
            output[x] = dict()

            for k in result[x].__dict__:
                output[x][k] = result[x].__dict__[k]

        return output

    @logged(_ga_log)
    @client_method
    def get_proteins(self):
        result = self.client.get_proteins(self._token, self.ref)

        output = dict()
        for x in result:
            output[x] = dict()

            for k in result[x].__dict__:
                output[x][k] = result[x].__dict__[k]

        return output

    @logged(_ga_log)
    @client_method
    def get_feature_locations(self, feature_id_list=None):
        result = self.client.get_feature_locations(self._token, self.ref, feature_id_list)

        output = dict()
        for x in result:
            output[x] = list()

            for region in result[x]:
                output[x].append({k: region.__dict__[k] for k in region.__dict__})

        return output

    @logged(_ga_log)
    @client_method
    def get_feature_dna(self, feature_id_list=None):
        return self.client.get_feature_dna(self._token, self.ref, feature_id_list)

    @logged(_ga_log)
    @client_method
    def get_feature_functions(self, feature_id_list=None):
        return self.client.get_feature_functions(self._token, self.ref, feature_id_list)

    @logged(_ga_log)
    @client_method
    def get_feature_aliases(self, feature_id_list=None):
        return self.client.get_feature_aliases(self._token, self.ref, feature_id_list)

    @logged(_ga_log)
    @client_method
    def get_feature_publications(self, feature_id_list=None):
        return self.client.get_feature_publications(self._token, self.ref, feature_id_list)

    @logged(_ga_log)
    @client_method
    def get_cds_by_mrna(self, mrna_feature_id_list=None):
        return self.client.get_cds_by_mrna(self._token, self.ref, mrna_feature_id_list)

    @logged(_ga_log)
    @client_method
    def get_mrna_by_cds(self, cds_feature_id_list=None):
        return self.client.get_mrna_by_cds(self._token, self.ref, cds_feature_id_list)

    @logged(_ga_log)
    @client_method
    def get_gene_by_cds(self, cds_feature_id_list=None):
        return self.client.get_gene_by_cds(self._token, self.ref, cds_feature_id_list)

    @logged(_ga_log)
    @client_method
    def get_gene_by_mrna(self, mrna_feature_id_list=None):
        return self.client.get_gene_by_mrna(self._token, self.ref, mrna_feature_id_list)

    @logged(_ga_log)
    @client_method
    def get_cds_by_gene(self, gene_feature_id_list=None):
        return self.client.get_cds_by_gene(self._token, self.ref, gene_feature_id_list)

    @logged(_ga_log)
    @client_method
    def get_mrna_by_gene(self, gene_feature_id_list=None):
        return self.client.get_mrna_by_gene(self._token, self.ref, gene_feature_id_list)
