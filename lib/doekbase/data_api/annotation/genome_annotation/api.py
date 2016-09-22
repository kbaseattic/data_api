"""
Data API for Genome Annotation entities.  This API provides methods for retrieving the
Assembly and Taxon associated with an annotation, as well as retrieving individual Features.
"""

# stdlib imports
import abc
import hashlib

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

# 3rd party imports
#import blist

# local imports
from doekbase.data_api.core import ObjectAPI, fix_docs
from doekbase.data_api.util import get_logger
from doekbase.data_api.blob import blob
from . import create

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


def get_location_start_stop(location):
    start = 0
    stop = 0

    if location["strand"] == "+":
        start = location["start"]
        stop = location["start"] + location["length"] - 1
    elif location["strand"] == "-":
        start = location["start"] - location["length"] + 1
        stop = location["start"]
    else:
        raise TypeError("Location strand was {} instead of + or - !".format(location["strand"]))

    return start, stop


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
    def get_features(self, feature_id_list=None, exclude_sequence=False):
        """Retrieves all the available data for a genomes' Features.

        Args:

          feature_id_list (list<str>): List of Features to retrieve.
              If None, returns all Feature data.

          exclude_sequence: False
              If True, exclude DNA sequence from output.

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
    def get_proteins(self, cds_feature_id_list=None):
        """Retrieves all the available proteins for a genome.

        Args:

          cds_feature_id_list (list<str>): List of CDS features to retrieve proteins.
              If None, returns all proteins.

        Returns:

          dict: Mapping from CDS IDs to protein information with the following key/value pairs:

          - protein_id : str
              The identifier for the protein
          - protein_amino_acid_sequence : str
              The AA sequence for the protein
          - protein_md5 : str
              The MD5 of the protein sequence
          - protein_aliases : dict<list<str>>
              For each protein alias, there is a list of sources as key
        """
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

    @abc.abstractmethod
    def get_gff(self, gene_feature_id_list=None):
        """Create a GFF representation of this GenomeAnnotation.

        Args:
          gene_feature_id_list (list<str>): List of gene Feature ids to include in the GFF output.
            If None, returns GFF output for all gene Feature ids and related mRNA and CDS Features.
        Returns:
          (doekbase.data_api.blob.Blob) Temporary "blob" object
        See Also:
          :doc:`blob_api`
        """
        pass

    @abc.abstractmethod
    def save_summary(self):
        """Save a summary representation of this GenomeAnnotation.

        Args:
          None
        Returns:
           tuple (first element bool - Success/Failure, 2nd element is python summary object-
                 (Done so if do not have permissions to write to the ws, the summary object can still be retrieved))
        """
        pass

    @abc.abstractmethod
    def get_summary(self):
        """Retrieves a summary representation of this GenomeAnnotation.

        Args:
          None
        Returns:
          Dictionary containing summary information

          (Taxonomy summary information)
          - scientific_name: str
          - taxonomy_id: int
          - kingdom: str
          - scientific_lineage: list<str>
          - genetic_code: int
          - organism_aliases: list<str>

          (Assembly summary information)
          - assembly_source: str
          - assembly_source_id: str
          - assembly_source_origination_date: str
          - gc_content: double
          - dna_size: int
          - num_contigs: int
          - contig_ids: list<str>

          (Annotation summary information)
          - external_source: str
          - external_source_origination_date: str
          - release: str
          - original_source_file_name: str
          - feature_type_counts: dict<str, int>
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

    def get_features(self, feature_id_list=None, exclude_sequence=False):
        return self.proxy.get_features(feature_id_list, exclude_sequence)

    def get_proteins(self, cds_feature_id_list=None):
        return self.proxy.get_proteins(cds_feature_id_list)

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

    def get_gff(self, gene_feature_id_list=None):
        return self.proxy.get_gff(gene_feature_id_list)

    def save_summary(self):
        return self.proxy.save_summary()

    def get_summary(self):
        return self.proxy.get_summary()


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
        features = self.get_data_subset(['features/[*]/type'])['features']

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

        limited_keys = ['id']

        if group_by == "type" or "type_list" in filters:
            limited_keys.append('type')
        elif group_by == "region" or "region_list" in filters:
            limited_keys.append("location")
        elif group_by == "function" or "function_list" in filters:
            limited_keys.append("function")
        elif group_by == "alias" or "alias_list" in filters:
            limited_keys.append("aliases")

        features = self.get_data_subset(['features/[*]/' + k for k in limited_keys])['features']

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
        features = self.get_data_subset(["features/[*]/type"])["features"]

        if type_list is None:
            for x in features:
                if x["type"] not in counts:
                    counts[x["type"]] = 0

                counts[x["type"]] += 1
        else:
            if not isinstance(type_list, list):
                raise TypeError("A list of strings indicating Feature types is required.")
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
        features = self.get_data_subset(['features/[*]/location', 'features/[*]/id'])['features']

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
        features = self.get_data_subset(['features/[*]/dna_sequence', 'features/[*]/id'])['features']

        if feature_id_list is None:
            for x in features:
                if "dna_sequence" in x:
                    sequences[x['id']] = x["dna_sequence"]
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
                    if "dna_sequence" in x:
                        sequences[x['id']] = x["dna_sequence"]
                    else:
                        sequences[x['id']] = ""

        return sequences

    def get_feature_functions(self, feature_id_list=None):
        functions = {}
        features = self.get_data_subset(['features/[*]/function', 'features/[*]/id'])['features']

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
        features = self.get_data_subset(['features/[*]/aliases', 'features/[*]/id'])['features']

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
        features = self.get_data_subset(['features/[*]/publications', 'features/[*]/id'])['features']

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

    def get_features(self, feature_id_list=None, exclude_sequence=False):
        out_features = {}

        if exclude_sequence:
            limited_keys = ["function", "location", "md5", "type", "id", "aliases", "dna_sequence_length"]
            features = self.get_data_subset(["features/[*]/" + k for k in limited_keys])["features"]
        else:
            features = self.get_data()['features']

        def fill_out_feature(x):
            f = {
                "feature_id": x['id'],
                "feature_type": x['type'],
                "feature_function": x.get('function', ''),
                "feature_publications": [],
                "feature_notes": "",
                "feature_inference": "",
                "feature_quality_warnings": []
            }

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

            if 'aliases' in x:
                f["feature_aliases"] = {k: [] for k in x['aliases']}
            else:
                f["feature_aliases"] = {}

            if "feature_quality_score" in x:
                f["feature_quality_score"] = str(x['quality'])
            else:
                f["feature_quality_score"] = ""

            return f

        if feature_id_list is None:
            for x in features:
                out_features[x['id']] = fill_out_feature(x)
        else:
            if not isinstance(feature_id_list, list):
                raise TypeError("A list of strings indicating Feature identifiers is required.")
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

    def get_proteins(self, cds_feature_id_list=None):
        proteins = {}
        features = self.get_data_subset(['features/[*]/protein_translation', 'features/[*]/id'])['features']
        
        for f in features:
            if "protein_translation" in f and len(f["protein_translation"]) > 0:
                protein_id = f['id'] + ".protein"
                proteins[f['id']] = {}
                proteins[f['id']]["protein_id"] = protein_id
                proteins[f['id']]["protein_amino_acid_sequence"] = f["protein_translation"]
                proteins[f['id']]["protein_function"] = None
                proteins[f['id']]["protein_aliases"] = None
                proteins[f['id']]["protein_md5"] = hashlib.md5(f["protein_translation"].upper()).hexdigest()

                # may need to revisit this                
                proteins[f['id']]["protein_domain_locations"] = None
        
        return proteins                

    def get_mrna_utrs(self, mrna_feature_id_list=None):
        raise TypeError("The Genome type does not contain relationships between features." +
                        "  This method cannot return valid results for this data type.")

    def get_mrna_exons(self, mrna_feature_id_list=None):
        exons = {}

        limited_keys = ['location', 'id', 'type', 'dna_sequence']

        all_mrna_features = self.get_data_subset(['features/[*]/{}'.format(k) for k in limited_keys])['features']
        data = [x for x in all_mrna_features if x['type'] == 'mRNA']

        if mrna_feature_id_list:
            data = [x for x in data if x['id'] in mrna_feature_id_list]

        for feature_data in data:
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
                    "exon_ordinal": i + 1
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

    def get_gff(self, gene_feature_id_list=None, ref_only=False):
        taxon_id = self.get_taxon().get_scientific_name()

        assembly = self.get_assembly()
        source_info = assembly.get_external_source_info()
        contig_lengths = assembly.get_contig_lengths()
        contig_ids = contig_lengths.keys()

        gffdata = StringIO.StringIO()
        gffdata.write("##gff-version 3\n")
        gffdata.write("#!gff-spec-version 1.21\n")
        gffdata.write("#!processor KBase GFF3 downloader\n")
        #!genome-build TAIR10
        #!genome-build-accession NCBI_Assembly:GCF_000001735.3

        feature_types = self.get_feature_types()
        include_types = []

        if "gene" in feature_types:
            include_types.append("gene")

        if "locus" in feature_types:
            include_types.append("locus")

        feature_ids = self.get_feature_ids(filters={"type_list": include_types})["by_type"]

        genes_missing = False
        if "gene" not in feature_ids and "locus" not in feature_ids:
            genes_missing = True
        elif "gene" in feature_ids and len(feature_ids["gene"]) == 0:
            genes_missing = True
        elif "locus" in feature_ids and len(feature_ids["locus"]) == 0:
            genes_missing = True

        if genes_missing:
            # unable to proceed without gene information
            raise Exception("No genes present to generate the GFF format. {} {}".format(feature_types, feature_ids))

        gene_list = []
        if "gene" in feature_ids:
            gene_list.extend(feature_ids["gene"])

        if "locus" in feature_ids:
            gene_list.extend(feature_ids["locus"])

        feature_id_list = []
        map(feature_id_list.extend, [feature_ids[x] for x in feature_ids])
        feature_data = self.get_features(feature_id_list=feature_id_list)

        def get_gene_line(gene_id):
            aliases = feature_data[gene_id]["feature_aliases"]
            location = feature_data[gene_id]["feature_locations"][0]

            start, stop = get_location_start_stop(location)

            db_xref = "".join(["Dbxref={};".format(x) for x in aliases])

            # gff fields;
            # NC_003070.9	RefSeq	gene	3631	5899	.	+	.	ID=gene0;Dbxref=GeneID:839580,TAIR:AT1G01010;Name=NAC001;gbkey=Gene;gene=NAC001;gene_biotype=protein_coding;gene_synonym=ANAC001,NAC domain containing protein 1,NAC001,T25K16.1,T25K16_1;locus_tag=AT1G01010
            gene_line = "{}\t{}\tgene\t{}\t{}\t.\t{}\t.\tID={};Name={};{}\n".format(
                contig_id,
                source_info['external_source'],
                str(start),
                str(stop),
                location['strand'],
                gene_id,
                gene_id,
                db_xref)

            return gene_line

        genes_by_contig = {}

        for c in contig_ids:
            genes_by_contig[c] = {}

        for gene_id in gene_list:
            location = feature_data[gene_id]["feature_locations"][0]
            boundary = location["start"]

            if location["strand"] == "-":
                boundary = location["start"] - location["length"] + 1

            if boundary not in genes_by_contig[location["contig_id"]]:
                genes_by_contig[location["contig_id"]][boundary] = []

            genes_by_contig[location["contig_id"]][boundary].append(gene_id)

        for contig_id in sorted(genes_by_contig):
            ##NC_003070.9 1 30427671
            gffdata.write("##sequence-region {}\t1\t{}\n".format(contig_id,
                          str(contig_lengths[contig_id])))

            gffdata.write("##species {}\n".format(taxon_id))

            for boundary in sorted(genes_by_contig[contig_id]):
                # maybe sort the genes?
                for gene_id in genes_by_contig[contig_id][boundary]:
                    gffdata.write(get_gene_line(gene_id))

        gffdata.write("###")

        out = blob.BlobBuffer()
        out.write(gffdata.getvalue())

        return out

    def save_summary(self): 
        """Create the GenomeAnnotationSummary object for a GenomeAnnotation. 
           This object is specialized for Landing Page use. 
           Saves the GenomeAnnotationSummary to the same workspace as the GenomeAnnotation object.
        """ 
        raise TypeError("Summaries are not supported for objects of type Genome.")

    def get_summary(self):
        """Gets GenomeAnnotationSummary object for a GenomeAnnotation.
           This object is specialized for Landing Page use.
           Just get a dump of the GenomeAnnotationSummary object.
        """ 
        raise TypeError("Summaries are not supported for objects of type Genome.")


@fix_docs
class _GenomeAnnotation(ObjectAPI, GenomeAnnotationInterface):
    def __init__(self, services, token, ref):
        super(_GenomeAnnotation, self).__init__(services, token, ref)

    def _get_feature_containers(self, feature_id_list=None):
        if feature_id_list is None:
            feature_containers = self.get_data_subset(["feature_container_references"])\
                ["feature_container_references"].values()
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

        feature_container_references = self.get_data_subset(["feature_container_references"])\
            ["feature_container_references"]

        features = {}
        limited_keys = ['feature_id']

        if group_by == "type" or "type_list" in filters:
            limited_keys.append("type")
        if group_by == "region" or "region_list" in filters:
            limited_keys.append("locations")
        if group_by == "alias" or "alias_list" in filters:
            limited_keys.append("aliases")
        if group_by == "function" or "function_list" in filters:
            limited_keys.append("function")

        paths = ['features/*/' + k for k in limited_keys]

        # process all filters
        if "type_list" in filters and filters["type_list"] is not None:
            if not isinstance(filters["type_list"], list):
                raise TypeError("A list of strings indicating Feature types is required.")
            elif len(filters["type_list"]) == 0:
                raise TypeError("A list of strings indicating Feature types is required, received an empty list.")

            # only pull data for features that are in the type_list
            containers = [ObjectAPI(self.services,
                                    self._token,
                                    feature_container_references[r],
                                    [self.ref, feature_container_references[r]]).get_data_subset(paths)["features"]
                          for r in feature_container_references if r in filters["type_list"]]
        else:
            # pull down all features
            containers = [ObjectAPI(self.services,
                                    self._token,
                                    feature_container_references[r],
                                    [self.ref, feature_container_references[r]]).get_data_subset(paths)["features"]
                          for r in feature_container_references]

        for obj in containers:
            features.update(obj)

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

        if not data:
            raise Exception("Missing data element to _get_feature_data()!")

        if feature_id_list:
            subsets = []
            for x in feature_containers:
                subset = {}
                subset['ref'] = self.ref
                subset['obj_ref_path'] = [x]

                try:
                    subset['included'] = ["features/{}/{}".format(k, data) for k in feature_containers[x]]
                    assert len(subset['included']) > 0
                except TypeError:
                    raise TypeError("A list of strings indicating Feature " +
                                    "identifiers is required.")
                except AssertionError:
                    raise TypeError("A list of strings indicating Feature " +
                                    "identifiers is required, " +
                                    "received an empty list.")

                subsets.append(subset)

            containers = self.ws_client.get_objects2({'objects': subsets})['data']
        else:
            containers = self.ws_client.get_objects2({'objects':
                [{'ref': self.ref,
                  'included': ["features/*/{}".format(data)],
                  'obj_ref_path': [x]
                 } for x in feature_containers]})['data']

        for obj in containers:
            features = obj["data"]["features"]
            working_list = obj["data"]["features"]

            # Pull out a specific type of data from each Feature
            if "aliases" in data:
                for feature_id in working_list:
                    if "aliases" in features[feature_id]:
                        out[feature_id] = features[feature_id]["aliases"]
                    else:
                        out[feature_id] = []
            elif "locations" in data:
                for feature_id in working_list:
                    out[feature_id] = [
                        {"contig_id": loc[0],
                         "strand": loc[2],
                         "start": loc[1],
                         "length": loc[3]} \
                        for loc in features[feature_id]["locations"]]
            elif "dna_sequence" in data:
                for feature_id in working_list:
                    out[feature_id] = features[feature_id]["dna_sequence"]
            elif "publications" in data:
                for feature_id in working_list:
                    if "publications" in features[feature_id]:
                        out[feature_id] = features[feature_id]["publications"]
                    else:
                        out[feature_id] = []
            elif "function" in data:
                for feature_id in working_list:
                    if "function" in features[feature_id]:
                        out[feature_id] = features[feature_id]["function"]
                    else:
                        out[feature_id] = ""

        return out

    def get_feature_locations(self, feature_id_list=None):
        return self._get_feature_data("locations", feature_id_list)

    def get_feature_dna(self, feature_id_list=None):
        return self._get_feature_data("dna_sequence", feature_id_list)

    def get_feature_functions(self, feature_id_list=None):
        return self._get_feature_data("function", feature_id_list)

    def get_feature_aliases(self, feature_id_list=None):
        return self._get_feature_data("aliases", feature_id_list)

    def get_feature_publications(self, feature_id_list=None):
        return self._get_feature_data("publications", feature_id_list)

    def get_features(self, feature_id_list=None, exclude_sequence=False):
        feature_containers = self._get_feature_containers(feature_id_list)
        limited_keys = ["quality_warnings", "locations", "feature_id", "md5",
                        "type", "aliases", "function", "dna_sequence_length"]

        if feature_id_list is None:
            if exclude_sequence:
                subset_paths = ["features/*/" + k for k in limited_keys]
                containers = self.ws_client.get_objects2(
                    {'objects': [
                        {'ref': self.ref,
                         'included': subset_paths,
                         'obj_ref_path': [x]} for x in feature_containers]
                    })['data']
            else:
                containers = self.ws_client.get_objects2({'objects': [
                    {'ref': self.ref,
                     'obj_ref_path': [x]
                    } for x in feature_containers]})['data']
        else:
            if exclude_sequence:
                subsets = []
                for x in feature_containers:
                    subset = {}
                    subset['ref'] = self.ref
                    subset['included'] = ["features/{}/{}".format(f, k)
                                          for f in feature_containers[x] for k in limited_keys]
                    subset['obj_ref_path'] = [x]
                    subsets.append(subset)

                containers = self.ws_client.get_objects2({'objects': subsets})['data']
            else:
                subsets = []
                for x in feature_containers:
                    subset = {}
                    subset['ref'] = self.ref
                    subset['included'] = ["features/{}".format(f) for f in feature_containers[x]]
                    subset['obj_ref_path'] = [x]
                    subsets.append(subset)

                containers = self.ws_client.get_objects2({'objects': subsets})['data']

        out_features = {}
        for obj in containers:
            for k,v in obj["data"]["features"].items():
                out_features[k] = {
                    "feature_id": v['feature_id'],
                    "feature_type": v['type'],
                    "feature_md5": v['md5'],
                    "feature_locations": [{"contig_id": loc[0],
                                           "start": loc[1],
                                           "strand": loc[2],
                                           "length": loc[3]} for loc in v['locations']],
                    "feature_function": v.get("function", ""),
                    "feature_publications": [],
                    "feature_dna_sequence": v.get("dna_sequence", ""),
                    "feature_dna_sequence_length": v.get("dna_sequence_length", 0),
                    "feature_aliases": v.get("aliases", {}),
                    "feature_notes": v.get("notes", ""),
                    "feature_inference": v.get("inference", ""),
                    "feature_quality_score": v.get("quality", []),
                    "feature_quality_warnings": v.get("quality_warnings", [])
                }

        return out_features

    def get_proteins(self, cds_feature_id_list=None):
        container_references = self.get_data_subset(["feature_container_references", "protein_container_ref"])
        feature_container_references = container_references["feature_container_references"]

        if "CDS" in feature_container_references:
            cds_feature_container_ref = feature_container_references["CDS"]
            cds_feature_container = ObjectAPI(self.services,
                                              self._token,
                                              cds_feature_container_ref,
                                              [self.ref, cds_feature_container_ref])
        else:
            raise TypeError("No CDS features are present!")

        if cds_feature_id_list is None:
            cds_features = cds_feature_container.get_data_subset(["features/*/CDS_properties"])["features"]
        else:
            try:
                cds_refs = ["features/{}/CDS_properties".format(x) for x in cds_feature_id_list]
                assert len(cds_refs) > 0
            except TypeError:
                raise TypeError("A list of strings indicating Feature " +
                                "identifiers is required.")
            except AssertionError:
                raise TypeError("A list of strings indicating Feature " +
                                "identifiers is required, " +
                                "received an empty list.")

            cds_features = cds_feature_container.get_data_subset(path_list=cds_refs)["features"]

        # map the protein id to the CDS id, if the CDS maps to a protein
        protein_cds_map = {cds_features[x]["CDS_properties"]["codes_for_protein_ref"][1]: x for x in cds_features
                           if "codes_for_protein_ref" in cds_features[x]["CDS_properties"]}

        # grab the protein container and fetch the protein data
        protein_container = ObjectAPI(self.services,
                                      self._token,
                                      container_references["protein_container_ref"],
                                      [self.ref, container_references["protein_container_ref"]])
        result = protein_container.get_data()["proteins"]
        # filter out any proteins that do not map to a CDS in our list
        proteins = {x: result[x] for x in result if x in protein_cds_map}

        output = {}
        for x in proteins:
            protein_old, protein_new = proteins[x], {}
            for old_key in protein_old:
                new_key = old_key if old_key.startswith("protein_") else "protein_" + old_key
                protein_new[new_key] = protein_old[old_key]
            output[protein_cds_map[x]] = protein_new
        return output

    def _get_by_mrna(self, feature_type=None, mrna_feature_id_list=None):
        out = {}

        feature_container_references = self.get_data_subset(
            path_list=["feature_container_references"])["feature_container_references"]

        limited_keys = ['feature_id', 'mRNA_properties']

        if "mRNA" in feature_container_references:
            mrna_feature_container_ref = feature_container_references["mRNA"]
            mrna_feature_container = ObjectAPI(self.services,
                                               self._token,
                                               mrna_feature_container_ref,
                                               [self.ref, mrna_feature_container_ref])

            if mrna_feature_id_list:
                try:
                    mrna_refs = ["features/{}/{}".format(x, k) for x in mrna_feature_id_list for k in limited_keys]
                    assert len(mrna_refs) > 0
                except TypeError:
                    raise TypeError("A list of strings indicating Feature " +
                                    "identifiers is required.")
                except AssertionError:
                    raise TypeError("A list of strings indicating Feature " +
                                    "identifiers is required, " +
                                    "received an empty list.")
            else:
                mrna_refs = ["features/*/{}".format(k) for k in limited_keys]

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
        # fetch the cds info we need
        cds_ids_by_mrna = self._get_by_mrna("cds", mrna_feature_id_list)

        if len(cds_ids_by_mrna) == 0:
            return {}

        # filter out any mRNA ids that do not map to a CDS, since passing None (no CDS) will throw an Exception below
        cds_ids = [cds_ids_by_mrna[mrna_id] for mrna_id in cds_ids_by_mrna if cds_ids_by_mrna[mrna_id] is not None]
        cds_locations = self._get_feature_data("locations", cds_ids)

        # fetch the mrna Feature data
        if mrna_feature_id_list is None:
            mrna_feature_id_list = self.get_feature_ids(filters={"type_list": ["mRNA"]})["by_type"]["mRNA"]

        mrna_data = self.get_features(mrna_feature_id_list)

        utrs = {}

        for mrna_id in mrna_data:
            if cds_ids_by_mrna[mrna_id] is None:
                # without CDS, UTRs cannot be calculated
                utrs[mrna_id] = {}
                continue

            mrna_locations = mrna_data[mrna_id]["feature_locations"]
            mrna_sequence = mrna_data[mrna_id]["feature_dna_sequence"]

            direction = cds_locations[cds_ids_by_mrna[mrna_id]][0]["strand"]

            utr5_locations = []
            utr3_locations = []
            utr5_sequence = []
            utr3_sequence = []
            offset = 0

            # if minus strand, 5' starts at the largest value, and we subtract length from start
            if direction == "-":
                cds_max = cds_locations[cds_ids_by_mrna[mrna_id]][0]["start"]
                cds_min = cds_locations[cds_ids_by_mrna[mrna_id]][-1]["start"] - \
                          cds_locations[cds_ids_by_mrna[mrna_id]][-1]["length"]

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
                        non_utr_remainder = exon_max - utr_boundary - 1

                        utr3_locations.append({
                            "contig_id": x["contig_id"],
                            "start": utr_boundary,
                            "strand": x["strand"],
                            "length": utr_length
                        })
                        utr3_sequence.append(mrna_sequence[offset + non_utr_remainder:offset + x["length"]])
                    elif exon_max < cds_min:
                        # the exon begins after the cds ends
                        utr3_locations.append(x)
                        utr3_sequence.append(mrna_sequence[offset:offset + x["length"]])

                    offset += x["length"]
            elif direction == "+":
                cds_max = cds_locations[cds_ids_by_mrna[mrna_id]][-1]["start"] + \
                          cds_locations[cds_ids_by_mrna[mrna_id]][-1]["length"]
                cds_min = cds_locations[cds_ids_by_mrna[mrna_id]][0]["start"]

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
                        utr3_sequence.append(mrna_sequence[offset + (x["length"] - utr_length):offset + x["length"]])  
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

        if "mRNA" not in feature_container_references:
            raise TypeError("mRNA features are not present in this GenomeAnnotation!")

        mrna_feature_container_ref = feature_container_references["mRNA"]
        mrna_feature_container = ObjectAPI(self.services,
                                           self._token,
                                           mrna_feature_container_ref,
                                           [self.ref, mrna_feature_container_ref])

        limited_keys = ['locations', 'dna_sequence']

        if mrna_feature_id_list is None:
            mrna_data = mrna_feature_container.get_data_subset(
                path_list=["features/*/{}".format(k) for k in limited_keys])
        else:
            mrna_data = mrna_feature_container.get_data_subset(
                path_list=["features/{}/{}".format(x, k) for x in mrna_feature_id_list for k in limited_keys])

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
                                      "exon_ordinal": i + 1})

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

        limited_keys = ['feature_id', 'CDS_properties']

        if "CDS" in feature_container_references:
            try:
                cds_refs = ["features/{}/{}".format(x, k) for x in cds_feature_id_list for k in limited_keys]
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
                                              cds_feature_container_ref,
                                              [self.ref, cds_feature_container_ref])
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

        limited_keys = ['feature_id', 'gene_properties']

        if "gene" in feature_container_references:
            try:
                gene_refs = ["features/{}/{}".format(x, k) for x in gene_feature_id_list for k in limited_keys]
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
                                               feature_container_references["gene"],
                                               [self.ref, feature_container_references["gene"]])
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

    def get_gff(self, gene_feature_id_list=None):
        taxon = self.get_taxon()
        taxon_id = taxon.get_taxonomic_id()

        if taxon_id == -1:
            taxon_id = "unknown"

        assembly = self.get_assembly()
        source_info = assembly.get_external_source_info()
        contig_lengths = assembly.get_contig_lengths()
        contig_ids = contig_lengths.keys()

        gffdata = StringIO.StringIO()
        gffdata.write("##gff-version 3\n")
        gffdata.write("#!gff-spec-version 1.21\n")
        gffdata.write("#!processor KBase GFF3 downloader\n")
        #!genome-build TAIR10
        #!genome-build-accession NCBI_Assembly:GCF_000001735.3

        feature_types = self.get_feature_types()
        include_types = []

        if "gene" in feature_types:
            include_types.append("gene")

        if "locus" in feature_types:
            include_types.append("locus")

        mrna_missing = False
        if "mRNA" in feature_types:
            include_types.append("mRNA")
        else:
            mrna_missing = True

        cds_missing = False
        if "CDS" in feature_types:
            include_types.append("CDS")
        else:
            cds_missing = True

        feature_ids = self.get_feature_ids(filters={"type_list": include_types})["by_type"]

        genes_missing = False
        if "gene" not in feature_ids and "locus" not in feature_ids:
            genes_missing = True
        elif "gene" in feature_ids and len(feature_ids["gene"]) == 0:
            genes_missing = True
        elif "locus" in feature_ids and len(feature_ids["locus"]) == 0:
            genes_missing = True

        if genes_missing:
            # unable to proceed without gene information
            raise Exception("No genes present to generate the GFF format. {} {}".format(feature_types, feature_ids))

        gene_list = []
        if "gene" in feature_ids:
            gene_list.extend(feature_ids["gene"])

        if "locus" in feature_ids:
            gene_list.extend(feature_ids["locus"])

        if mrna_missing:
            mrna_by_gene_list = {g: [] for g in gene_list}
            cds_by_mrna_list = {}
            cds_by_gene_list = self.get_cds_by_gene(gene_list)
            exons_by_mrna = {}
        else:
            # retrieve pairwise inter-feature relationships between genes, mRNAs, CDSs
            mrna_by_gene_list = self.get_mrna_by_gene(gene_list)
            mrna_list = []
            map(mrna_list.extend, mrna_by_gene_list.values())
            cds_by_mrna_list = self.get_cds_by_mrna(mrna_list)
            cds_by_gene_list = self.get_cds_by_gene(gene_list)
            exons_by_mrna = self.get_mrna_exons(mrna_list)
            # TODO fetch UTR info
            #self.get_mrna_utrs(mrna_by_gene_list.values())

        feature_id_list = []
        map(feature_id_list.extend, [feature_ids[x] for x in feature_ids])
        feature_data = self.get_features(feature_id_list=feature_id_list)

        def parse_aliases(feature_id):
            if not "feature_aliases" in feature_data[feature_id]:
                return [], []

            aliases = feature_data[feature_id]["feature_aliases"]

            alias_values = []
            dbxref_values = []

            for x in aliases:
                for k in aliases[x]:
                    if k.startswith("Genbank"):
                        alias_values.append("Alias={};".format(x))
                    else:
                        dbxref_values.append("Dbxref={}:{};".format(k,x))

            return alias_values, dbxref_values

        def get_gene_line(gene_id):
            function_description = ""
            if "feature_function" in feature_data[gene_id]:
                function_description = feature_data[gene_id]["feature_function"]
            location = feature_data[gene_id]["feature_locations"][0]

            start, stop = get_location_start_stop(location)

            db_xref, alias = parse_aliases(gene_id)
            db_xref = "".join(db_xref)
            alias = "".join(alias)

            # gff fields;
            # NC_003070.9	RefSeq	gene	3631	5899	.	+	.	ID=gene0;Dbxref=GeneID:839580,TAIR:AT1G01010;Name=NAC001;gbkey=Gene;gene=NAC001;gene_biotype=protein_coding;gene_synonym=ANAC001,NAC domain containing protein 1,NAC001,T25K16.1,T25K16_1;locus_tag=AT1G01010
            gene_line = "{}\t{}\tgene\t{}\t{}\t.\t{}\t.\tID={};Name={};{}{}{}\n".format(
                contig_id,
                source_info['external_source'],
                str(start),
                str(stop),
                location['strand'],
                gene_id,
                gene_id,
                alias,
                db_xref,
                function_description)

            return gene_line

        def get_mrna_line(gene_id, mrna_id):
            function_description = ""
            if "feature_function" in feature_data[mrna_id]:
                function_description = feature_data[mrna_id]["feature_function"]
            locations = feature_data[mrna_id]["feature_locations"]
            lower_bound = None
            upper_bound = None

            # find min/max locations for this mrna
            for location in locations:
                start, stop = get_location_start_stop(location)

                if lower_bound is None or start < lower_bound:
                    lower_bound = start

                if upper_bound is None or stop > upper_bound:
                    upper_bound = stop

            db_xref, alias = parse_aliases(mrna_id)
            db_xref = "".join(db_xref)
            alias = "".join(alias)

            # TODO what do we do about trans-spliced genes with locations on both strands?
            # gff fields;
            # NC_003070.9	RefSeq	gene	3631	5899	.	+	.	ID=gene0;Dbxref=GeneID:839580,TAIR:AT1G01010;Name=NAC001;gbkey=Gene;gene=NAC001;gene_biotype=protein_coding;gene_synonym=ANAC001,NAC domain containing protein 1,NAC001,T25K16.1,T25K16_1;locus_tag=AT1G01010
            mrna_line = "{}\t{}\tmRNA\t{}\t{}\t.\t{}\t.\tID={};Parent={};Name={};{}{}{}\n".format(
                contig_id,
                source_info['external_source'],
                str(lower_bound),
                str(upper_bound),
                locations[0]['strand'],
                mrna_id,
                gene_id,
                mrna_id,
                alias,
                db_xref,
                function_description)

            return mrna_line

        def get_cds_lines(mrna_id, gene_id):
            cds_id = None
            if mrna_id:
                cds_id = cds_by_mrna_list[mrna_id]

            parent = ""

            if cds_id is None:
                try:
                    cds_id = cds_by_gene_list[gene_id][0]
                except IndexError:
                    cds_id = None

                if cds_id is None:
                    _log.warn("mRNA {} and gene {} do not have an associated CDS".format(mrna_id, gene_id))
                    return ""

                parent = "Parent={};".format(gene_id)
            else:
                parent = "Parent={};".format(mrna_id)

            function_description = ""
            if "feature_function" in feature_data[cds_id]:
                function_description = feature_data[cds_id]["feature_function"]

            locations = feature_data[cds_id]["feature_locations"]

            phase = 0
            running_length = 0
            cds_lines = []
            for location in locations:
                start, stop = get_location_start_stop(location)

                phase = (3 - running_length % 3) % 3

                db_xref, alias = parse_aliases(cds_id)
                db_xref = "".join(db_xref)
                alias = "".join(alias)

                cds_lines.append("{}\t{}\tCDS\t{}\t{}\t.\t{}\t{}\tID={};{}Name={};Derives_from={};{}{}{}\n".format(
                    contig_id,
                    source_info['external_source'],
                    str(start),
                    str(stop),
                    locations[0]['strand'],
                    str(phase),
                    cds_id,
                    parent,
                    cds_id,
                    gene_id,
                    alias,
                    db_xref,
                    function_description))

                running_length += location["length"]

            return "".join(cds_lines)

        # need a global counter for tracking exon order
        last_exon_id = 1
        def get_exon_lines(mrna_id, exons, start_exon_id):
            exon_count = 0
            exon_lines = []
            for x in exons:
                exon_id = "exon_{}".format(str(start_exon_id + exon_count))
                exon_count += 1

                location = x["exon_location"]

                start, stop = get_location_start_stop(location)

                exon_lines.append("{}\t{}\texon\t{}\t{}\t.\t{}\t.\tID={};Parent={};Name={};\n".format(
                    contig_id,
                    source_info['external_source'],
                    str(start),
                    str(stop),
                    location['strand'],
                    exon_id,
                    mrna_id,
                    exon_id))

            return "".join(exon_lines)

        genes_by_contig = {}

        for c in contig_ids:
            genes_by_contig[c] = {}

        for gene_id in gene_list:
            location = feature_data[gene_id]["feature_locations"][0]
            boundary = location["start"]

            if location["strand"] == "-":
                boundary = location["start"] - location["length"] + 1

            if boundary not in genes_by_contig[location["contig_id"]]:
                genes_by_contig[location["contig_id"]][boundary] = []

            genes_by_contig[location["contig_id"]][boundary].append(gene_id)

        if mrna_missing:
            for contig_id in sorted(genes_by_contig):
                ##NC_003070.9 1 30427671
                gffdata.write("##sequence-region {}\t1\t{}\n".format(contig_id,
                              str(contig_lengths[contig_id])))

                if taxon_id != -1:
                    #http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=3702
                    gffdata.write("##species http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id={}\n".format(
                                  str(taxon_id)))
                else:
                    gffdata.write("##species unknown\n")

                # NC_003070.9	RefSeq	region	1	30427671	.	+	.	ID=id0;Dbxref=taxon:3702;Name=1;chromosome=1;ecotype=Columbia;gbkey=Src;genome=chromosome;mol_type=genomic DNA
                gffdata.write("{}\t{}\tregion\t{}\t{}\t.\t+\t.\tID={};gbkey=Src;mol_type=genomic DNA\n".format(
                    contig_id,
                    source_info['external_source'],
                    1,
                    str(contig_lengths[contig_id]),
                    contig_id
                ))

                for boundary in sorted(genes_by_contig[contig_id]):
                    # maybe sort the genes?
                    for gene_id in genes_by_contig[contig_id][boundary]:
                        gffdata.write(get_gene_line(gene_id))
                        gffdata.write(get_cds_lines(None, gene_id))
        else:
            for contig_id in sorted(genes_by_contig):
                ##NC_003070.9 1 30427671
                gffdata.write("##sequence-region {}\t1\t{}\n".format(contig_id,
                              str(contig_lengths[contig_id])))

                if taxon_id != -1:
                    #http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=3702
                    gffdata.write("##species http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id={}\n".format(
                                  str(taxon_id)))
                else:
                    gffdata.write("##species unknown\n")

                # NC_003070.9	RefSeq	region	1	30427671	.	+	.	ID=id0;Dbxref=taxon:3702;Name=1;chromosome=1;ecotype=Columbia;gbkey=Src;genome=chromosome;mol_type=genomic DNA
                gffdata.write("{}\t{}\tregion\t{}\t{}\t.\t+\t.\tID={};gbkey=Src;mol_type=genomic DNA\n".format(
                    contig_id,
                    source_info['external_source'],
                    1,
                    str(contig_lengths[contig_id]),
                    contig_id
                ))

                for boundary in sorted(genes_by_contig[contig_id]):
                    # maybe sort the genes?
                    for gene_id in genes_by_contig[contig_id][boundary]:
                        gffdata.write(get_gene_line(gene_id))

                        for mrna_id in mrna_by_gene_list[gene_id]:
                            gffdata.write(get_mrna_line(gene_id, mrna_id))
                            exons = exons_by_mrna[mrna_id]
                            gffdata.write(get_exon_lines(mrna_id, exons, last_exon_id))
                            last_exon_id += len(exons)
                            gffdata.write(get_cds_lines(mrna_id, gene_id))

        gffdata.write("###")

        out = blob.BlobBuffer()
        out.write(gffdata.getvalue())

        return out

    def save_summary(self):
        summary_object = {}
        summary_object["genome_annotation_ref"] = self._info["object_reference_versioned"]

        # Taxon summary information
        taxon_object = self.get_taxon()
        summary_object["scientific_name"] = taxon_object.get_scientific_name()

        try:
            summary_object["taxonomy_id"] = taxon_object.get_taxonomic_id() 
        except AttributeError:
            summary_object["taxonomy_id"] = -1

        try:
            summary_object["kingdom"] = taxon_object.get_kingdom()
        except AttributeError:
            summary_object["kingdom"] = "kingdom not present"

        try:
            summary_object["genetic_code"] = taxon_object.get_genetic_code()
        except AttributeError:
            summary_object["genetic_code"] = 0

        try:
            summary_object["scientific_lineage"] = ";".join(taxon_object.get_scientific_lineage()) 
        except AttributeError:
            summary_object["scientific_lineage"] = "scientific lineage not present"

        summary_object["organism_aliases"] = taxon_object.get_aliases()

        if len(summary_object["organism_aliases"]) == 0:
            summary_object["organism_aliases"].append("No organism aliases present")

        # Assembly summary information
        assembly_object = self.get_assembly()
        assembly_source_info = assembly_object.get_external_source_info()

        try:
            summary_object["assembly_source"] = assembly_source_info["external_source"]
        except AttributeError:
            summary_object["assembly_source"] = "assembly source not present"

        try:
            summary_object["assembly_source_id"] = assembly_source_info["external_source_id"]
        except AttributeError:
            summary_object["assembly_source_id"] = "assembly source id not present"

        try:
            summary_object["assembly_source_origination_date"] = assembly_source_info["external_source_origination_date"]
        except AttributeError:
            summary_object["assembly_source_origination_date"] = "assembly_source_origination_date not present"

        assembly_stats_info = assembly_object.get_stats()
        summary_object["gc_content"] = assembly_stats_info["gc_content"]
        summary_object["dna_size"] = assembly_stats_info["dna_size"]
        summary_object["num_contigs"] = assembly_stats_info["num_contigs"]
        summary_object["contig_ids"] = assembly_object.get_contig_ids()

        # Annotation summary information
        annotation_info = self.get_data_subset(
            path_list=["external_source", "external_source_origination_date", "release", "original_source_file_name"])
        if annotation_info.has_key("external_source"):
            summary_object["external_source"] = annotation_info["external_source"]
        else:
            summary_object["external_source"] = "annotation source is not present"

        if annotation_info.has_key("external_source_origination_date"):
            summary_object["external_source_origination_date"] = annotation_info["external_source_origination_date"]
        else:
            summary_object["external_source_origination date"] = "annotation source date is not present"

        if annotation_info.has_key("release"):
            summary_object["release"] = annotation_info["release"]
        else:
            summary_object["release"] = "annotation release is not present"

        if annotation_info.has_key("original_source_file_name"):
            summary_object["original_source_file_name"] = annotation_info["original_source_file_name"]
        else:
            summary_object["original_source_file_name"] = "original source file name is unknown"

        summary_object["feature_counts_map"] = self.get_feature_type_counts()

        summary_object["assembly_ref"] = self.get_data_subset(path_list=["assembly_ref"])["assembly_ref"]
        summary_object["taxon_ref"] = self.get_data_subset(path_list=["taxon_ref"])["taxon_ref"]

        try: 
            alias_source_dict = self.get_data_subset(path_list=["alias_source_counts_map"])["alias_source_counts_map"]
            summary_object["alias_sources"] = alias_source_dict.keys()
        except: 
            summary_object["alias_sources"] = list()

        proteins = dict()
        proteins = self.get_proteins()
        summary_object["cds_coding_for_proteins_count"] = len(proteins) 

        summary_provenance = [
            {
                "script": __file__,
                "script_ver": "0.1",
                "description": "This summary object was generated by running the summary object " +
                               "creation on object {}".format(self.ref)
            }
        ]

        try:
            summary_save_info = self.ws_client.save_objects({
                "workspace": self._info["workspace_name"],
                "objects": [
                    {
                        "type": "KBaseGenomeAnnotations.GenomeAnnotationSummary",
                        "data": summary_object,
                        "name": "{}_summary".format(self._info["object_name"]),
                        "hidden": 1,
                        "provenance": summary_provenance
                    }
                ]
            })
            return True, summary_object
        except Exception, e:
            _log.debug("WS Save Summary Error: {0}".format(e))
            return False, summary_object

    def get_summary(self):
        refs = self.get_referrers()
        all_summary_types = sorted([t for t in refs if t.startswith("KBaseGenomeAnnotations.GenomeAnnotationSummary")])

        if len(all_summary_types) == 0:
            save_summary_result = self.save_summary()
            summary = save_summary_result[1]
        else:
            # the highest version type will be last, and there should only ever be one summary object per version
            latest_summary = refs[all_summary_types[-1]][0]
            summary = ObjectAPI(self.services,
                                self._token,
                                latest_summary).get_data()

        out = {
            "taxonomy": {
                "scientific_name": summary["scientific_name"],
                "taxonomy_id": summary["taxonomy_id"],
                "kingdom": summary["kingdom"],
                "scientific_lineage": [x.strip() for x in summary["scientific_lineage"].split(";")],
                "genetic_code": summary["genetic_code"],
                "organism_aliases": summary["organism_aliases"]
            },
            "assembly": {
                "assembly_source": summary["assembly_source"],
                "assembly_source_id": summary["assembly_source_id"],
                "assembly_source_date": summary["assembly_source_origination_date"],
                "gc_content": summary["gc_content"],
                "dna_size": summary["dna_size"],
                "num_contigs": summary["num_contigs"],
                "contig_ids": summary["contig_ids"]
            },
            "annotation": {
                "external_source": summary["external_source"],
                "external_source_date": summary["external_source_origination_date"],
                "release": summary["release"],
                "original_source_filename": summary["original_source_file_name"],
                "feature_type_counts": summary["feature_counts_map"]
            }
        }

        return out

def create_genome_annotation(services=None,
                             token=None,
                             workspace_identifier=None,
                             genome_annotation_name=None,
                             features=None,
                             proteins=None,
                             assembly_ref=None,
                             taxon_ref=None,
                             annotation_properties=None,
                             provenance=None):
    ga_ref = create.create_genome_annotation(services,
                                             token,
                                             workspace_identifier,
                                             genome_annotation_name,
                                             features,
                                             proteins,
                                             assembly_ref,
                                             taxon_ref,
                                             annotation_properties,
                                             provenance)
    GenomeAnnotationAPI(services, token, ga_ref).save_summary()
    return ga_ref