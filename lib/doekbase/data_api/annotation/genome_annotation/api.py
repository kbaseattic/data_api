"""
Data API for Genome Annotation entities.  This API provides methods for retrieving the
Assembly and Taxon associated with an annotation, as well as retrieving individual Features.
"""

# stdlib imports
import abc
import hashlib

# 3rd party imports
#import blist

# local imports
from doekbase.data_api.core import ObjectAPI, fix_docs
from doekbase.data_api.util import get_logger, logged
from doekbase.data_api import exceptions
import doekbase.data_api.annotation.genome_annotation.service.ttypes as ttypes

_GENOME_TYPES = ['KBaseGenomes.Genome']
_GENOME_ANNOTATION_TYPES = ['KBaseGenomeAnnotations.GenomeAnnotation']
TYPES = _GENOME_TYPES + _GENOME_ANNOTATION_TYPES

#: Mapping of Feature type codes to descriptions
#: of their meaning. The keys of this mapping give possible values for
#: functions taking Feature type identifiers, e.g.
#: :meth:`GenomeInterface.get_feature_types`.
FEATURE_DESCRIPTIONS = {
    "CDS": "Coding Sequence",
    "PEG": "Protein Encoding Genes",
    "rna": "Ribonucliec Acid (RNA)",
    "crispr": "Clustered Regularly Interspaced Short Palindromic Repeats",
    "crs": "Clustered Regularly Interspaced Short Palindromic Repeats",
    "mRNA": "Messenger RNA",
    "sRNA": "Small RNA",
    "loci": "Loci or Genes (Genbank)",
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

    # filters and groups for get_feature_ids()
    _valid_filters = ["type_list", "region_list", "function_list", "alias_list"]
    _valid_groups = ["type", "region", "function", "alias"]

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
          list<str>: List of Feature type identifiers.
        """
        pass

    def get_feature_type_descriptions(self, type_list=None):
        """Retrieves a descriptive string for each Feature type identifier.
        
        Args:
          type_list (list<str>): List of Feature types. The known values for
            these are enumerated in the module's  :data:`FEATURE_DESCRIPTIONS`.
            If this list is empty or None, then the whole mapping will be
            returned.
        
        Returns:
          dict: Key/value pairs for each requested Feature description.
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
        """Retrieve the numbers of genome Features, grouped by
        Feature type identifier.

        Args:
          type_list (list<str>): List of Feature types. Each should match a
            value in :data:`FEATURE_DESCRIPTIONS`. If None,
            or empty, will retrieve all type counts.

        Returns:
          dict: Map of string Feature types to integer counts.
        """
        pass

    @abc.abstractmethod
    def get_feature_ids(self, filters=None, group_by="type"):
        """Retrieve Feature ids based on filters such as Feature types,
        regions, functional descriptions, aliases.

        If no value is given for ``filters``, all Feature ids will be returned.
        Only the group_by selected will be included in the results.

        Args:
            filters (dict): Optional dictionary of filters that can be applied to
              contents. Recognized filter keys are:

            - `type_list`: List of Feature type strings. Possible values in
              `FEATURE_DESCRIPTIONS`.

            - `region_list`: List of region specs. e.g.,
              ``[{"contig_id": str, "strand": "+"|"-", "start": int, "length": int},...]``

                The Feature sequence begin and end are calculated as follows:
                  [start, start + length) for "+" strand
                  (start - length, start] for "-" strand

            - `function_list`: List of function strings to match.

            - `alias_list`: List of alias strings to match.

            group_by (str): Specify the grouping of Feature ids returned.
                Possible values are the same as the filter keys.

        Returns:
            (dict) Result with values for requested grouping filled in under a
            key named for that grouping::

                {"by_type": dict<str feature_type, list<str feature_id>>,
                 "by_region": dict<str contig_id, dict<str strand, dict<string range, list<string feature_id>>>>,
                 "by_function": dict<str function, list<str feature_id>>,
                 "by_alias": dict<str alias, list<str feature_id>>}
        """

        pass  # TODO: add examples in docs for function_list and alias_list

    @abc.abstractmethod
    def get_features(self, feature_id_list=None):
        """Retrieves all the available data for a genomes' Features.

        Args:

          feature_id_list (list<str>): List of Features to retrieve.
              If None, returns all Feature data.

        Returns:
          dict: Mapping from Feature IDs to dicts of available data.
          The Feature data has the following key/value pairs:

          - feature_id: str
              Identifier for this Feature

          - feature_type: str
              The Feature type e.g., mRNA, CDS, gene

          - feature_function: str
              The functional annotation description

          - feature_locations: list<{"contig_id": str, "start": int, "strand": str, "length": int}>
              List of Feature regions, where the Feature bounds are calculated as follows:
                  For "+" strand, [start, start + length)
                  For "-" strand, (start - length, start]

          - feature_dna_sequence: str
              String containing the DNA sequence of the Feature

          - feature_dna_sequence_length: int
              Integer representing the length of the DNA sequence for convenience

          - feature_md5: str
              String containing the MD5 of the sequence, calculated from the uppercase string

          - feature_publications: list<int, str, str, str, str, str, str>
              List of any known publications related to this Feature

          - feature_aliases: dict<str, list<string>>
              Dictionary of Alias string to List of source string identifiers

          - feature_notes: str
              Notes recorded about this Feature

          - feature_inference: str
              Inference information

          - feature_quality_score: int
              Quality value with unknown algorithm for Genomes,
              not calculated yet for GenomeAnnotations

          - feature_quality_warnings: list<str>
              List of strings indicating known data quality issues.
              Note - not used for Genome type, but is used for GenomeAnnotation
        """
        pass

    @abc.abstractmethod
    def get_proteins(self):
        """Retrieves all the available proteins for a genome.

        Returns:
          list<dict>"""
        pass

    @abc.abstractmethod
    def get_feature_locations(self, feature_id_list=None):
        """Retrieves the location information for given genome Features.
        
        Args:

          feature_id_list (list<str>): List of Features to retrieve.
            If None, returns all Feature locations.

            The Feature sequence begin and end are calculated as follows:
                [start, start + length) for "+" strand
                (start - length, start] for "-" strand

        Returns:
          dict: Mapping from Feature IDs to location information for each.
          The location information has the following key/value pairs:

          - contig_id : str
              The identifier for the contig this region corresponds to

          - strand : str
              Whether this region is located on the '+' or '-' strand

          - start : int
              The starting position for this region

          - length : int
              The distance from the start position that defines the end boundary for the region.
        """
        pass
    
    @abc.abstractmethod
    def get_feature_dna(self, feature_id_list=None):
        """Retrieves the DNA sequences for genome Features.
        
        If `feature_id_list` is None, returns DNA sequences for all features.
        
        Args:
          feature_id_list (list<str>): List of Features to retrieve data for.
        
        Returns:

          dict<str,str>: Mapping of Feature IDs to their DNA sequence.
        """
        pass

    @abc.abstractmethod
    def get_feature_functions(self, feature_id_list=None):
        """
        Retrieves the functional description for given Features.

        Args:
          feature_id_list (list<str>): List of Features to retrieve data for.
            If None, returns all Feature functions.

        
        Returns:
          dict<str,str>: Mapping from Feature IDs to their functions.

        """
        pass

    @abc.abstractmethod
    def get_feature_aliases(self, feature_id_list=None):
        """Retrieves the aliases for genome features.

        Args:
          feature_id_list (list<str>): List of Features to retrieve data for.
            If None, returns all Feature aliases.
        
        Returns:
          dict<str>: list<str>"""
        pass
    
    @abc.abstractmethod
    def get_feature_publications(self, feature_id_list=None):
        """Retrieves the publications for genome Features.

        Args:
          feature_id_list (list<str>): List of Features to retrieve data for.
            If None, returns all Feature publications.
        
        Returns:
          dict<str>: list<dict>"""
        pass

    @abc.abstractmethod
    def get_mrna_utrs(self, mrna_feature_id_list=None):
        """Retrieves the untranslated regions (UTRs) for mRNA features.

        UTRs are calculated between mRNA features and corresponding CDS features.
        The return value for each mRNA can contain either:
            no UTRs found (empty dict)
            5' UTR only
            3' UTR only
            5' and 3' UTRs

        Note - The Genome data type does not contain interfeature relationship information
        and will raise a TypeError exception when this method is called.

        Args:
          mrna_feature_id_list (list<str>): List of mRNA Feature ids to retrieve UTRs from.
        Returns:
          dict<str mrna_feature_id>: {"5'UTR": UTR_data, "3'UTR": UTR_data}

          Where UTR_data is a dictionary with the following key/value pairs:
              - utr_locations: list<Feature Region>
                  Feature Region is a dict with these key/value pairs:
                      contig_id: str
                      start: int
                      strand: str
                      length: int
              - utr_dna_sequence: str
                  DNA sequence string for this UTR
          """
        pass

    @abc.abstractmethod
    def get_mrna_exons(self, mrna_feature_id_list=None):
        """Retrieves the exon DNA sequence within mRNA features.

        Exon_data = {
            "exon_location": A Feature region {"contig_id": str, "start": int, "strand": str, "length": int}
        }

        Args:
          mrna_feature_id_list (list<str>): List of mRNA Feature ids to retrieve exons for.
        Returns:
          Dictionary mapping from mRNA Feature id string to a list of exon dictionary entries.
          Each exon dictionary has the following key/value pairs:
              exon_location: {"contig_id": str, "start": int, "strand": str, "length": int}
                  Feature region for the exon boundaries:
                      For "+" strand, [start, start + length)
                      For "-" strand, (start - length, start]
              exon_dna_sequence: str
                  DNA Sequence string for this exon
              exon_ordinal: int
                  The position of the exon, ordered 5' to 3'.
        """
        pass

    @abc.abstractmethod
    def get_cds_by_mrna(self, mrna_feature_id_list=None):
        """Retrieves coding sequence Features (cds) for given mRNA Feature IDs.

        Args:
           mrna_feature_id_list (list<str>): List of mRNA Feature ids to map to cds Features.
             If None, returns all mappings between mRNA Feature ids and cds Feature ids.
        Returns:
          dict<str>: str
        """
        pass

    @abc.abstractmethod
    def get_mrna_by_cds(self, cds_feature_id_list=None):
        """Retrieves mRNA Features for given coding sequences (cds) Feature IDs.

        Args:
           cds_feature_id_list (list<str>): List of cds Feature ids to map to mRNA Features.
             If None, returns all mappings between cds Feature ids and mRNA Feature ids
        Returns:
          dict<str>: str
        """
        pass

    @abc.abstractmethod
    def get_gene_by_cds(self, cds_feature_id_list=None):
        """Retrieves gene Features for given coding sequence (cds) Feature IDs.

        Args:
           cds_feature_id_list (list<str>): List of cds Feature ids to map to gene Features.
             If None, returns all mappings between cds Feature ids and gene Features.
        Returns:
          dict<str>: str
        """
        pass
  
    @abc.abstractmethod
    def get_gene_by_mrna(self, mrna_feature_id_list=None):
        """Retrieves gene Features for given mRNA Feature IDs.

        Args:
           mrna_feature_id_list (list<str>): List of mRNA Feature ids to map to gene Feature ids.
             If None, returns all mappings between mRNA Feature ids and gene Feature ids.
        Returns:
          dict<str>: str
        """
        pass

    @abc.abstractmethod
    def get_cds_by_gene(self, gene_feature_id_list=None):
        """Retrieves coding sequence Features (cds) for given gene Feature IDs.

        Args:
           gene_feature_id_list (list<str>): List of gene Feature ids to map to cds Feature ids.
             If None, returns all mappings between gene Feature ids and cds Feature ids.
        Returns:
          dict<str>: list<str>
        """
        pass
    
    @abc.abstractmethod
    def get_mrna_by_gene(self, gene_feature_id_list=None):
        """Retrieves mRNA for given gene Feature IDs.

        Args:
           gene_feature_id_list (list<str>): List of gene Feature ids to map to mRNA Feature ids.
             If None, returns all mappings between gene Feature ids and mRNA Feature ids.
        Returns:
          dict<str>: list<str>
        """
        pass


@fix_docs
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

    def get_mrna_utrs(self, mrna_feature_id_list=None):
        return self.proxy.get_mrna_utrs(mrna_feature_id_list)

    def get_mrna_exons(self, mrna_feature_id_list=None):
        return self.proxy.get_mrna_exons(mrna_feature_id_list)

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
    

@fix_docs
class _KBaseGenomes_Genome(ObjectAPI, GenomeAnnotationInterface):
    def __init__(self, services, token, ref):
        super(_KBaseGenomes_Genome, self).__init__(services, token, ref)

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
        feature_types = []
        features = self.get_data()['features']

        for x in features:
            if "type" in x and x["type"] not in feature_types:
                feature_types.append(x["type"])

        return feature_types

    def get_feature_ids(self, filters=None, group_by="type"):
        if filters is None:
            filters = {}

        for k in filters:
            if k not in self._valid_filters:
                raise KeyError("Invalid filter key {}, valid filters are {}".format(k, self._valid_filters))

        if group_by not in self._valid_groups:
            raise ValueError("Invalid group_by {}, valid group_by values are {}".format(group_by, self._valid_groups))

        # no choice but to pull all features
        features = self.get_data()['features']

        # now process all filters and reduce the data
        remove_features = set()

        if "type_list" in filters and filters["type_list"] is not None:
            if not isinstance(filters["type_list"], list):
                raise TypeError("A list of strings indicating Feature types is required.")
            elif len(filters["type_list"]) == 0:
                raise TypeError("A list of strings indicating Feature types is required, received an empty list.")

            for i in xrange(len(features)):
                if features[i]["type"] not in filters["type_list"]:
                    remove_features.add(i)

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
                        if r["contig_id"] == loc[0] and loc[2] == r["strand"]:
                            if loc[2] == "+" and \
                               max(loc[1], r["start"]) <= min(loc[1]+loc[3], r["start"] + r["length"]):
                                return True
                            elif loc[2] == "-" and \
                               max(loc[1] - loc[3], r["start"] - r["length"]) <= min(loc[1], r["start"]):
                                return True
                return False

            for i in xrange(len(features)):
                if not is_feature_in_regions(features[i], filters["region_list"]):
                    remove_features.add(i)

        if "function_list" in filters and filters["function_list"] is not None:
            if not isinstance(filters["function_list"], list):
                raise TypeError("A list of Feature function strings is required.")
            elif len(filters["function_list"]) == 0:
                raise TypeError("A list of Feature function strings is required, received an empty list.")

            for i in xrange(len(features)):
                if "function" not in features[i]:
                    remove_features.add(i)
                else:
                    found = False
                    for f in filters["function_list"]:
                        if features[i]["function"].find(f) >= 0:
                            found = True
                            break

                    if not found:
                        remove_features.add(i)

        if "alias_list" in filters and filters["alias_list"] is not None:
            if not isinstance(filters["alias_list"], list):
                raise TypeError("A list of Feature alias strings is required.")
            elif len(filters["alias_list"]) == 0:
                raise TypeError("A list of Feature alias strings is required, received an empty list.")

            for i in xrange(len(features)):
                if "aliases" not in features[i]:
                    remove_features.add(i)
                else:
                    found = False
                    for alias in filters["alias_list"]:
                        if alias in features[i]["aliases"]:
                            found = True

                    if not found:
                        remove_features.add(i)

        keep_features = [i for i in xrange(len(features)) if i not in remove_features]

        # now that filtering has been completed, attempt to group the data as requested
        results = {}

        if group_by == "type":
            results["by_type"] = {}
            for i in keep_features:
                if features[i]["type"] not in results["by_type"]:
                    results["by_type"][features[i]["type"]] = []

                results["by_type"][features[i]["type"]].append(features[i]["id"])
        elif group_by == "region":
            results["by_region"] = {}
            for i in keep_features:
                for r in features[i]["location"]:
                    contig_id = r[0]
                    strand = r[2]
                    start = r[1]
                    length = r[3]
                    range = "{}-{}".format(start,start+length)

                    if contig_id not in results["by_region"]:
                        results["by_region"][contig_id] = {}

                    if strand not in results["by_region"][contig_id]:
                        results["by_region"][contig_id][strand] = {}

                    if range not in results["by_region"][contig_id][strand]:
                        results["by_region"][contig_id][strand][range] = []

                    results["by_region"][contig_id][strand][range].append(features[i]["id"])
        elif group_by == "function":
            results["by_function"] = {}
            for i in keep_features:
                if features[i]["function"] not in results["by_function"]:
                    results["by_function"][features[i]["function"]] = []

                results["by_function"][features[i]["function"]].append(features[i]["id"])
        elif group_by == "alias":
            results["by_alias"] = {}
            for i in keep_features:
                for alias in features[i]["aliases"]:
                    if alias not in results["by_alias"]:
                        results["by_alias"][alias] = []

                    results["by_alias"][alias].append(features[i]["id"])

        return results

    def get_feature_type_counts(self, type_list=None):
        """
        Retrieves the number of genome Features from a KBaseGenomes.Genome object, filtering on Feature type.

        Returns:
          dict<str>:int"""
        counts = {}
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
                raise TypeError("A list of strings indicating Feature types is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating Feature types is required, received an empty list.")

            for x in features:
                if x["type"] in type_list:
                    counts[x["type"]] += 1
        
        return counts

    def get_feature_locations(self, feature_id_list=None):
        locations = {}
        features = self.get_data()['features']

        if feature_id_list is None:
            for x in features:
                locations[x['id']] = []
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
                raise TypeError("A list of strings indicating Feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating Feature identifiers is required, received an empty list.")

            for x in features:
                if x['id'] in feature_id_list:
                    locations[x['id']] = []

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
        sequences = {}
        features = self.get_data()['features']

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
                raise TypeError("A list of strings indicating Feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating Feature identifiers is required, received an empty list.")

            for x in features:
                if x['id'] in feature_id_list:
                    if "sequence" in x:
                        sequences[x['id']] = x["sequence"]
                    else:
                        sequences[x['id']] = ""

        return sequences

    def get_feature_functions(self, feature_id_list=None):
        functions = {}
        features = self.get_data()['features']

        if feature_id_list is None:
            for x in features:
                if "function" in x:
                    functions[x['id']] = x["function"]
                else:
                    functions[x['id']] = ""
        else:
            try:
                feature_refs = ["features/" + x for x in feature_id_list]
                assert len(feature_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating Feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating Feature identifiers is required, received an empty list.")

            for x in features:
                if x['id'] in feature_id_list:
                    if "function" in x:
                        functions[x['id']] = x["function"]
                    else:
                        functions[x['id']] = ""

        return functions

    def get_feature_aliases(self, feature_id_list=None):
        aliases = {}
        features = self.get_data()['features']

        if feature_id_list is None:
            for x in features:
                if "aliases" in x:
                    aliases[x['id']] = x["aliases"]
                else:
                    aliases[x['id']] = []
        else:
            try:
                feature_refs = ["features/" + x for x in feature_id_list]
                assert len(feature_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating Feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating Feature identifiers is required, received an empty list.")

            for x in features:
                if x['id'] in feature_id_list:
                    if "aliases" in x:
                        aliases[x['id']] = x["aliases"]
                    else:
                        aliases[x['id']] = []

        return aliases
    
    def get_feature_publications(self, feature_id_list=None):
        publications = {}
        features = self.get_data()['features']

        if feature_id_list is None:
            for x in features:
                if "publications" in x:
                    publications[x['id']] = x["publications"]
                else:
                    publications[x['id']] = []
        else:
            try:
                feature_refs = ["features/" + x for x in feature_id_list]
                assert len(feature_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating Feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating Feature identifiers is required, received an empty list.")

            for x in features:
                if x['id'] in feature_id_list:
                    if "publications" in x:
                        publications[x['id']] = x["publications"]
                    else:
                        publications[x['id']] = []

        return publications

    def get_features(self, feature_id_list=None):
        out_features = {}
        features = self.get_data()['features']

        def fill_out_feature(x):
            f = {}
            f["feature_id"] = x['id']
            f["feature_type"] = x['type']
            f["feature_function"] = x.get('function', '')

            if "location" in x:
                f["feature_locations"] = [{"contig_id": loc[0],
                                           "start": loc[1],
                                           "strand": loc[2],
                                           "length": loc[3]} for loc in x['location']]
            else:
                f["feature_locations"] = []

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

            #if 'publications' in x:
            #    f["feature_publications"] = x['publications']
            #else:
            #    f["feature_publications"] = []
            f["feature_publications"] = []

            if 'aliases' in x:
                f["feature_aliases"] = {k: [] for k in x['aliases']}
            else:
                f["feature_aliases"] = {}

            f["feature_notes"] = ""
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
                raise TypeError("A list of strings indicating Feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating Feature identifiers is required, received an empty list.")

            for x in features:
                if x['id'] in feature_id_list:
                    out_features[x['id']] = fill_out_feature(x)

        return out_features

    def get_proteins(self):
        proteins = {}
        features = self.get_data()['features']
        
        for f in features:
            if "protein_translation" in f and len(f["protein_translation"]) > 0:
                protein_id = f['id'] + ".protein"
                proteins[protein_id] = {}
                proteins[protein_id]["protein_id"] = protein_id
                proteins[protein_id]["protein_amino_acid_sequence"] = f["protein_translation"]
                proteins[protein_id]["protein_function"] = None
                proteins[protein_id]["protein_aliases"] = None
                proteins[protein_id]["protein_md5"] = hashlib.md5(f["protein_translation"].upper()).hexdigest()

                # may need to revisit this                
                proteins[protein_id]["protein_domain_locations"] = None
        
        return proteins                

    def get_mrna_utrs(self, mrna_feature_id_list=None):
        raise TypeError("The Genome type does not contain relationships between features." +
                        "  This method cannot return valid results for this data type.")

    def get_mrna_exons(self, mrna_feature_id_list=None):
        data = self.get_data()

        exons = {}

        if mrna_feature_id_list is None:
            mrna_feature_id_list = []

        mrna_list_length = len(mrna_feature_id_list)

        for feature_data in data["features"]:
            if feature_data["type"] != "mRNA":
                continue

            if mrna_list_length > 0 and feature_data["id"] not in mrna_feature_id_list:
                continue

            if "dna_sequence" not in feature_data or "location" not in feature_data:
                continue

            feature_exons = []
            offset = 0
            for i in xrange(len(feature_data["location"])):
                exon_location = feature_data["location"][i]

                feature_exons.append({
                    "exon_location": {"contig_id": exon_location[0],
                                      "start": exon_location[1],
                                      "strand": exon_location[2],
                                      "length": exon_location[3]},
                    "exon_dna_sequence": feature_data["dna_sequence"][offset:offset + exon_location[3]],
                    "exon_ordinal": i
                })

                offset += exon_location[3]

            exons[feature_data["id"]] = feature_exons

        return exons

    def get_cds_by_mrna(self, mrna_feature_id_list=None):
        raise TypeError("The Genome type does not contain relationships between features." +
                        "  This method cannot return valid results for this data type.")

    def get_mrna_by_cds(self, cds_feature_id_list=None):
        raise TypeError("The Genome type does not contain relationships between features." +
                        "  This method cannot return valid results for this data type.")

    def get_gene_by_cds(self, cds_feature_id_list=None):
        raise TypeError("The Genome type does not contain relationships between features." +
                        "  This method cannot return valid results for this data type.")
  
    def get_gene_by_mrna(self, mrna_feature_id_list=None):
        raise TypeError("The Genome type does not contain relationships between features." +
                        "  This method cannot return valid results for this data type.")

    def get_cds_by_gene(self, gene_feature_id_list=None):
        raise TypeError("The Genome type does not contain relationships between features." +
                        "  This method cannot return valid results for this data type.")

    def get_mrna_by_gene(self, gene_feature_id_list=None):

        raise TypeError("The Genome type does not contain relationships between Features." +
                        "  This method cannot return valid results for this data type.")


@fix_docs
class _GenomeAnnotation(ObjectAPI, GenomeAnnotationInterface):
    def __init__(self, services, token, ref):
        super(_GenomeAnnotation, self).__init__(services, token, ref)

    def _get_feature_containers(self, feature_id_list=None):
        if feature_id_list is None:
            feature_containers = self.get_data_subset(["feature_container_references"])["feature_container_references"].values()
        else:
            try:
                assert len(feature_id_list) > 0

                feature_lookup = self.get_data_subset(path_list=["feature_lookup"])["feature_lookup"]
                feature_containers = {}

                for x in feature_id_list:
                    for feature_ref in feature_lookup[x]:
                        if feature_ref[0] not in feature_containers:
                            feature_containers[feature_ref[0]] = []

                        feature_containers[feature_ref[0]].append(feature_ref[1])
            except TypeError:
                raise TypeError("A list of strings indicating Feature identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating Feature identifiers is required, received an empty list.")

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
            filters = {}

        for k in filters:
            if k not in self._valid_filters:
                raise KeyError("Invalid filter key {}, valid filters are {}".format(k, self._valid_filters))

        if group_by not in self._valid_groups:
            raise ValueError("Invalid group_by {}, valid group_by values are {}".format(group_by, self._valid_groups))

        data = self.get_data()

        # XXX: debugging
        #return {'by_' + group_by: []}
        # XXX

        feature_container_references = data["feature_container_references"]
        features = {}

        # process all filters
        if "type_list" in filters and filters["type_list"] is not None:
            if not isinstance(filters["type_list"], list):
                raise TypeError("A list of strings indicating Feature types is required.")
            elif len(filters["type_list"]) == 0:
                raise TypeError("A list of strings indicating Feature types is required, received an empty list.")

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
                        if r["contig_id"] == loc[0] and loc[2] == r["strand"]:
                            if loc[2] == "+" and \
                               max(loc[1], r["start"]) <= min(loc[1] + loc[3], r["start"] + r["length"]):
                                return True
                            elif loc[2] == "-" and \
                               max(loc[1] - loc[3], r["start"] - r["length"]) <= min(loc[1], r["start"]):
                                return True
                return False

            remove_features = []

            for f in features:
                if not is_feature_in_regions(features[f], filters["region_list"]):
                    remove_features.append(f)

            for f in remove_features:
                del features[f]

        if "function_list" in filters and filters["function_list"] is not None:
            if not isinstance(filters["function_list"], list):
                raise TypeError("A list of Feature function strings is required.")
            elif len(filters["function_list"]) == 0:
                raise TypeError("A list of Feature function strings is required, received an empty list.")

            remove_features = []

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
                raise TypeError("A list of Feature alias strings is required.")
            elif len(filters["alias_list"]) == 0:
                raise TypeError("A list of Feature alias strings is required, received an empty list.")

            remove_features = []

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
        results = {}

        if group_by == "type":
            results["by_type"] = {}
            for x in features:
                if features[x]["type"] not in results["by_type"]:
                    results["by_type"][features[x]["type"]] = []

                results["by_type"][features[x]["type"]].append(features[x]["feature_id"])
        elif group_by == "region":
            results["by_region"] = {}
            for x in features:
                for r in features[x]["locations"]:
                    contig_id = r[0]
                    strand = r[2]
                    start = r[1]
                    length = r[3]
                    range = "{}-{}".format(start,start+length)

                    if contig_id not in results["by_region"]:
                        results["by_region"][contig_id] = {}

                    if strand not in results["by_region"][contig_id]:
                        results["by_region"][contig_id][strand] = {}

                    if range not in results["by_region"][contig_id][strand]:
                        results["by_region"][contig_id][strand][range] = []

                    results["by_region"][contig_id][strand][range].append(features[x]["feature_id"])
        elif group_by == "function":
            results["by_function"] = {}
            for x in features:
                if features[x]["function"] not in results["by_function"]:
                    results["by_function"][features[x]["function"]] = []

                results["by_function"][features[x]["function"]].append(features[x]["feature_id"])
        elif group_by == "alias":
            results["by_alias"] = {}
            for x in features:
                if "aliases" in features[x]:
                    for alias in features[x]["aliases"]:
                        if alias not in results["by_alias"]:
                            results["by_alias"][alias] = []

                        results["by_alias"][alias].append(features[x]["feature_id"])

        return results

    def get_feature_type_counts(self, type_list=None):
        return self.get_data_subset(path_list=["counts_map"])["counts_map"]

    def _get_feature_data(self, data=None, feature_id_list=None):
        out = {}
        feature_containers = self._get_feature_containers(feature_id_list)

        if feature_id_list is not None:
            try:
                feature_refs = ["features/" + x for x in feature_id_list]
                assert len(feature_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating Feature " +
                                "identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating Feature " +
                                "identifiers is required, " +
                                "received an empty list.")

        for ref in feature_containers:
            # Get list of Feature IDs
            if feature_id_list is None:
                features = ObjectAPI(self.services, self._token, ref).get_data()["features"]
                working_list = features
            else:
                container = ObjectAPI(self.services, self._token, ref)
                features = container.get_data_subset(path_list=feature_refs)["features"]
                working_list = feature_id_list
            # Pull out a specific type of data from each Feature
            if data == "aliases":
                for feature_id in working_list:
                    if "aliases" in features[feature_id]:
                        out[feature_id] = features[feature_id]["aliases"]
                    else:
                        out[feature_id] = []
            elif data == "locations":
                for feature_id in working_list:
                    out[feature_id] = [
                        {"contig_id": loc[0],
                         "strand": loc[2],
                         "start": loc[1],
                         "length": loc[3]} \
                        for loc in features[feature_id]["locations"]]
            elif data == "dna":
                for feature_id in working_list:
                    out[feature_id] = features[feature_id]["dna_sequence"]
            elif data == "publications":
                for feature_id in working_list:
                    if "publications" in features[feature_id]:
                        out[feature_id] = features[feature_id]["publications"]
                    else:
                        out[feature_id] = []
            elif data == "functions":
                for feature_id in working_list:
                    if "function" in features[feature_id]:
                        out[feature_id] = features[feature_id]["function"]
                    else:
                        out[feature_id] = ""

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
        out_features = {}
        feature_containers = self._get_feature_containers(feature_id_list)

        def fill_out_feature(x):
            f = {
                "feature_id": x['feature_id'],
                "feature_type": x['type'],
                "feature_md5": x['md5'],
                "feature_dna_sequence": x['dna_sequence'],
                "feature_dna_sequence_length": x['dna_sequence_length'],
                "feature_locations": [{"contig_id": loc[0],
                                       "start": loc[1],
                                       "strand": loc[2],
                                       "length": loc[3]} for loc in x['locations']]
            }

            if 'function' in x:
                f["feature_function"] = x['function']
            else:
                f["feature_function"] = ""

            #if 'publications' in x:
            #    f["feature_publications"] = x['publications']
            #else:
            # TODO fix publications in thrift spec and code, problem with existing data
            f["feature_publications"] = []

            if 'aliases' in x:
                f["feature_aliases"] = x['aliases']
            else:
                f["feature_aliases"] = {}

            if 'notes' in x:
                f["feature_notes"] = x['notes']
            else:
                f["feature_notes"] = ""

            if 'inference' in x:
                f["feature_inference"] = x['inference']
            else:
                f["feature_inference"] = ""

            if 'quality' in x:
                f["feature_quality_score"] = x['quality']
            else:
                f["feature_quality_score"] = []

            if 'quality_warnings' in x:
                f["feature_quality_warnings"] = x['quality_warnings']
            else:
                f["feature_quality_warnings"] = []

            return f

        containers = {ref: ObjectAPI(self.services, self._token, ref) for ref in feature_containers}

        if feature_id_list is None:
            out_features = {x: fill_out_feature(v) for ref in containers \
                            for x,v in containers[ref].get_data()["features"].items()}
        else:
            for ref in feature_containers:
                path_list = ["features/" + f for f in feature_containers[ref]]
                subset_features = containers[ref].get_data_subset(path_list)["features"].items()
                out_features.update({x: fill_out_feature(v) for x,v in subset_features})

        return out_features

    def get_proteins(self):
        protein_container = ObjectAPI(self.services, self._token, self.get_data()["protein_container_ref"])
        result = protein_container.get_data()["proteins"]

        output = {}
        for x in result:
            output[x] = {}
            for k in result[x]:
                if k.startswith("protein_"):
                    output[x][k] = result[x][k]
                else:
                    output[x]["protein_" + k] = result[x][k]
        return output

    def _get_by_mrna(self, feature_type=None, mrna_feature_id_list=None):
        out = {}

        feature_container_references = self.get_data_subset(
            path_list=["feature_container_references"])["feature_container_references"]

        if "mRNA" in feature_container_references:
            try:
                mrna_refs = ["features/" + x for x in mrna_feature_id_list]
                assert len(mrna_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating Feature " +
                                "identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating Feature " +
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
                    out[mrna_id] = mrna_features[mrna_feature_key]["mRNA_properties"]["parent_gene"][1]
                else:
                    out[mrna_id] = None

        return out

    def get_mrna_utrs(self, mrna_feature_id_list=None):
        if mrna_feature_id_list is None:
            feature_container_references = self.get_data_subset(
                path_list=["feature_container_references"])["feature_container_references"]

            mrna_feature_container_ref = feature_container_references["mRNA"]
            mrna_feature_container = ObjectAPI(self.services,
                                               self._token,
                                               mrna_feature_container_ref)
            mrna_feature_id_list = mrna_feature_container.get_data()["features"].keys()

        # fetch the cds info we need
        cds_ids = self.get_cds_by_mrna(mrna_feature_id_list)
        cds_locations = self._get_feature_data("locations", cds_ids.values())

        # fetch the mrna Feature data
        mrna_data = self.get_features(mrna_feature_id_list)

        utrs = {}

        for mrna_id in mrna_data:
            mrna_locations = mrna_data[mrna_id]["feature_locations"]
            mrna_sequence = mrna_data[mrna_id]["feature_dna_sequence"]

            direction = cds_locations[cds_ids[mrna_id]][0]["strand"]

            utr5_locations = []
            utr3_locations = []
            utr5_sequence = []
            utr3_sequence = []
            offset = 0

            # if minus strand, 5' starts at the largest value, and we subtract length from start
            if direction == "-":
                cds_max = cds_locations[cds_ids[mrna_id]][0]["start"]
                cds_min = cds_locations[cds_ids[mrna_id]][-1]["start"] - \
                          cds_locations[cds_ids[mrna_id]][-1]["length"]

                for x in mrna_locations:
                    exon_max = x["start"]
                    exon_min = x["start"] - x["length"]

                    if exon_min > cds_max:
                        # the exon ends before the cds starts
                        utr5_locations.append(x)
                        utr5_sequence.append(mrna_sequence[offset:offset + x["length"]])
                    elif cds_max > exon_min and cds_max < exon_max:
                        # the cds starts inside this exon
                        utr_boundary = cds_max + 1
                        utr_length = exon_max - utr_boundary + 1

                        utr5_locations.append({
                            "contig_id": x["contig_id"],
                            "start": exon_max,
                            "strand": x["strand"],
                            "length": utr_length
                        })
                        utr5_sequence.append(mrna_sequence[offset:offset + utr_length])

                    if cds_min > exon_min and cds_min < exon_max:
                        # the cds ends inside this exon
                        utr_boundary = cds_min - 1
                        utr_length = utr_boundary - exon_min + 1

                        utr3_locations.append({
                            "contig_id": x["contig_id"],
                            "start": utr_boundary,
                            "strand": x["strand"],
                            "length": utr_length
                        })
                        utr3_sequence.append(mrna_sequence[offset:offset + utr_length])
                    elif exon_max < cds_min:
                        # the exon begins after the cds ends
                        utr3_locations.append(x)
                        utr3_sequence.append(mrna_sequence[offset:offset + x["length"]])

                    offset += x["length"]
            elif direction == "+":
                cds_max = cds_locations[cds_ids[mrna_id]][-1]["start"] + \
                          cds_locations[cds_ids[mrna_id]][-1]["length"]
                cds_min = cds_locations[cds_ids[mrna_id]][0]["start"]

                for x in mrna_locations:
                    exon_min = x["start"]
                    exon_max = x["start"] + x["length"]

                    if exon_max < cds_min:
                        # the exon ends before the cds starts
                        utr5_locations.append(x)
                        utr5_sequence.append(mrna_sequence[offset:offset + x["length"]])
                    elif cds_min > exon_min and cds_min < exon_max:
                        # the cds starts inside this exon
                        utr_boundary = cds_min - 1
                        utr_length = utr_boundary - exon_min + 1

                        utr5_locations.append({
                            "contig_id": x["contig_id"],
                            "start": exon_min,
                            "strand": x["strand"],
                            "length": utr_length
                        })
                        utr5_sequence.append(mrna_sequence[offset:offset + utr_length])

                    if cds_max > exon_min and cds_max < exon_max:
                        # the cds ends inside this exon
                        utr_boundary = cds_max + 1
                        utr_length = exon_max - utr_boundary + 1

                        utr3_locations.append({
                            "contig_id": x["contig_id"],
                            "start": utr_boundary,
                            "strand": x["strand"],
                            "length": utr_length
                        })
                        utr3_sequence.append(mrna_sequence[offset:offset + utr_length])
                    elif exon_min > cds_max:
                        # the exon starts after the cds ends
                        utr3_locations.append(x)
                        utr3_sequence.append(mrna_sequence[offset:offset + x["length"]])

                    offset += x["length"]
            else:
                raise Exception("Found location with unrecognized strand {}".format(direction))

            # save the final results
            utrs[mrna_id] = {}

            if len(utr5_locations) > 0:
                utrs[mrna_id]["5'UTR"] = {
                    "utr_locations": utr5_locations,
                    "utr_dna_sequence": "".join(utr5_sequence)
                }

            if len(utr3_locations) > 0:
                utrs[mrna_id]["3'UTR"] = {
                    "utr_locations": utr3_locations,
                    "utr_dna_sequence": "".join(utr3_sequence)
                }
        #end outer for loop

        return utrs

    def get_mrna_exons(self, mrna_feature_id_list=None):
        feature_container_references = self.get_data_subset(
            path_list=["feature_container_references"])["feature_container_references"]

        mrna_feature_container_ref = feature_container_references["mRNA"]
        mrna_feature_container = ObjectAPI(self.services,
                                           self._token,
                                           mrna_feature_container_ref)

        if mrna_feature_id_list is None:
            mrna_data = mrna_feature_container.get_data()
        else:
            mrna_data = mrna_feature_container.get_data_subset(
                path_list=["features/" + x for x in mrna_feature_id_list])

        exons = {}
        for mrna_id in mrna_data["features"]:
            feature_exons = []
            mrna_sequence = mrna_data["features"][mrna_id]["dna_sequence"]

            offset = 0
            for i in xrange(len(mrna_data["features"][mrna_id]["locations"])):
                exon_location = mrna_data["features"][mrna_id]["locations"][i]
                exon_sequence = mrna_sequence[offset:offset + exon_location[3]]

                feature_exons.append({"exon_location": {"contig_id": exon_location[0],
                                                        "start": exon_location[1],
                                                        "strand": exon_location[2],
                                                        "length": exon_location[3]},
                                       "exon_dna_sequence": exon_sequence,
                                       "exon_ordinal": i})

                offset += exon_location[3]

            # assign here to avoid multiple memory reallocations of the dict
            exons[mrna_id] = feature_exons

        return exons

    def get_cds_by_mrna(self, mrna_feature_id_list=None):
        return self._get_by_mrna("cds", mrna_feature_id_list)

    def get_gene_by_mrna(self, mrna_feature_id_list=None):
        return self._get_by_mrna("gene", mrna_feature_id_list)

    def _get_by_cds(self, feature_type=None, cds_feature_id_list=None):
        out = {}

        feature_container_references = self.get_data_subset(
            path_list=["feature_container_references"])["feature_container_references"]

        if "CDS" in feature_container_references:
            try:
                cds_refs = ["features/" + x for x in cds_feature_id_list]
                assert len(cds_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating Feature " +
                                "identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating Feature " +
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
        out = {}

        feature_container_references = self.get_data_subset(
            path_list=["feature_container_references"])["feature_container_references"]

        if "gene" in feature_container_references:
            try:
                gene_refs = ["features/" + x for x in gene_feature_id_list]
                assert len(gene_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating Feature " +
                                "identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating Feature " +
                                "identifiers is required, " +
                                "received an empty list.")

            gene_feature_container = ObjectAPI(self.services,
                                               self._token,
                                               feature_container_references["gene"])
            gene_features = gene_feature_container.get_data_subset(path_list=gene_refs)["features"]

            for gene_feature_key in gene_features:
                gene_id = gene_features[gene_feature_key]["feature_id"]
                out[gene_id] = []

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
@fix_docs
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
                raise TypeError(e.message)
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

        if group_by not in self._valid_groups:
            raise ValueError("Invalid group_by {}, valid group_by values are {}".format(group_by, self._valid_groups))

        if filters is not None:
            for k in filters:
                if k not in self._valid_filters:
                    raise KeyError("Invalid filter key {}, valid filters are {}".format(k, self._valid_filters))

            if "type_list" in filters:
                type_list = filters["type_list"]
            else:
                type_list = []

            if "region_list" in filters:
                region_list = [ttypes.Region(**x) for x in filters["region_list"]]
            else:
                region_list = []

            if "function_list" in filters:
                function_list = filters["function_list"]
            else:
                function_list = []

            if "alias_list" in filters:
                alias_list = filters["alias_list"]
            else:
                alias_list = []

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

        output = {x: {
            "feature_id": result[x].feature_id,
            "feature_type": result[x].feature_type,
            "feature_function": result[x].feature_function,
            "feature_aliases": result[x].feature_aliases,
            "feature_dna_sequence_length": result[x].feature_dna_sequence_length,
            "feature_dna_sequence": result[x].feature_dna_sequence,
            "feature_md5": result[x].feature_md5,
            "feature_locations": [{"contig_id": loc.contig_id,
                                   "start": loc.start,
                                   "strand": loc.strand,
                                   "length": loc.length
                                  } for loc in result[x].feature_locations],
            "feature_publications": result[x].feature_publications,
            "feature_quality_warnings": result[x].feature_quality_warnings,
            "feature_quality_score": result[x].feature_quality_score,
            "feature_notes": result[x].feature_notes,
            "feature_inference": result[x].feature_inference
        } for x in result}

        return output

    @logged(_ga_log)
    @client_method
    def get_proteins(self):
        result = self.client.get_proteins(self._token, self.ref)

        output = {}
        for x in result:
            output[x] = {}

            for k in result[x].__dict__:
                output[x][k] = result[x].__dict__[k]

        return output

    @logged(_ga_log)
    @client_method
    def get_feature_locations(self, feature_id_list=None):
        result = self.client.get_feature_locations(self._token, self.ref, feature_id_list)

        output = {}
        for x in result:
            output[x] = []

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
    def get_mrna_exons(self, mrna_feature_id_list=None):
        result = self.client.get_mrna_exons(self._token, self.ref, mrna_feature_id_list)

        output = {}
        for mrna_id in result:
            output[mrna_id] = []
            for exon in result[mrna_id]:
                region = exon.exon_location

                output[mrna_id].append({
                    "exon_location": {k: region.__dict__[k] for k in region.__dict__},
                    "exon_dna_sequence": exon.exon_dna_sequence,
                    "exon_ordinal": exon.exon_ordinal
                })

        return output

    @logged(_ga_log)
    @client_method
    def get_mrna_utrs(self, mrna_feature_id_list=None):
        result = self.client.get_mrna_utrs(self._token, self.ref, mrna_feature_id_list)

        output = {}
        for mrna_id in result:
            output[mrna_id] = {}
            for utr_id in result[mrna_id]:
                regions = result[mrna_id][utr_id].utr_locations
                output[mrna_id][utr_id] = {
                    "utr_locations": [{k: r.__dict__[k] for k in r.__dict__} for r in regions],
                    "utr_dna_sequence": result[mrna_id][utr_id].utr_dna_sequence
                }

        return output

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
