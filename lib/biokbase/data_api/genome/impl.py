"""
Implementation file.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/14/15'
"""
Data API for Genome Annotation entities.  This API provides methods for retrieving the
Assembly and Taxon associated with an annotation, as well as retrieving individual features.
"""
import os

import biokbase
#from biokbase.data_api import taxon..
#from biokbase.data_api.object import ObjectAPI

_GENOME_TYPES = ['KBaseGenomes.Genome']
_GENOME_ANNOTATION_TYPES = ['KBaseGenomesCondensedPrototypeV2.GenomeAnnotation']
TYPES = _GENOME_TYPES + _GENOME_ANNOTATION_TYPES

FEATURE_DESCRIPTIONS = {
    "CDS": "Coding Sequence",
    "PEG": "Protein Encoding Genes",
    "rna": "Ribonucliec Acid (RNA)",
    "crispr": "Clustered Regularly Interspaced Short Palindromic Repeats",
    "crs": "Clustered Regularly Interspaced Short Palindromic Repeats",
    "mRNA": "Messenger RNA",
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

# Bsae data object
##################

class KBaseDataAPI(object):
    def __init__(self, conn):
        self._conn = conn

    def get_object(self, ref, object_class):
        """Fetch a data object by reference.
        """
        cursor = self._conn.cursor()
        v = cursor.get_object_info_new({
            "objects": [{"ref": ref}],
            "includeMetadata": 0,
            "ignoreErrors": 0})[0]
        md5_type = cursor.translate_to_MD5_types([v[2]]).values()[0]
        kdo = object_class(v, md5_type)
        return kdo

    def get_data_subset(self, ref, path_list):
        """Retrieve a subset of data given a list of paths to the data elements.

        Returns:
          dict
        """
        cursor = self._conn.cursor()
        subset = cursor.get_object_subset([{'ref': ref, 'included': path_list}])
        return subset[0]['data']

class KBaseDataObject(object):

    types = []

    def __init__(self, v, type_):
        self._info = {
            "object_id": v[0],
            "object_name": v[1],
            "object_reference": "{0}/{1}".format(v[6], v[0]),
            "object_reference_versioned": "{0}/{1}/{2}"
                .format(v[6], v[0], v[4]),
            "type_string": v[2],
            "save_date": v[3],
            "version": v[4],
            "saved_by": v[5],
            "workspace_id": v[6],
            "workspace_name": v[7],
            "object_checksum": v[8],
            "object_size": v[9],
            "object_metadata": v[10]
        }
        self._id = self._info["object_id"]
        self._name = self._info["object_name"]
        self._typestring = type_
        self._bare_type = self._typestring.split('-')[0]
        self._version = self._info["version"]
        self._schema = None
        self._history = None
        self._provenance = None
        self._data = None
        #
        self.check_type()

    @property
    def info(self):
        return self._info

    @property
    def objid(self):
        return self._id

    @property
    def ref(self):
        return self._info['object_reference']

    @property
    def ref_ver(self):
        return self._info['object_reference_versioned']

    def check_type(self):
        if not self._bare_type in self.types:
            typelist = ','.join(self.types)
            raise TypeError("Invalid type! Expected one of ({0}), received {1}"
                            .format(typelist, self._bare_type))

###########

class GenomeAnnotationAPI(KBaseDataAPI):

    def get_info(self, ref):
        """Retrieve basic info about a GenomeAnnotation object.

        Args:
          ref (str): Reference identifier for object to retrieve.
        Returns:
          GenomeAnnotationObject instance
        """
        return self.get_object(ref, GenomeAnnotationObject)

    def get_taxon(self, obj):
        """Retrieves the genome's taxon.

        Args:
          obj (GenomeAnnotationObject): Containing genome
        Returns:
          TaxonObject
        """
        if obj.is_genome_type:
            taxon_ref = obj.ref
        elif obj.is_annotation_type:
            taxon_ref = self.get_data_subset(obj.ref, ["taxon_ref"])[
                "taxon_ref"]
        else:
            raise TypeError('Wrong object type')
        return self.get_object(taxon_ref, TaxonObject)

class GenomeAnnotationObject(KBaseDataObject):
    OLD_TYPES = ['KBaseGenomes.Genome']
    NEW_TYPES = ['KBaseGenomesCondensedPrototypeV2.GenomeAnnotation']
    types = OLD_TYPES + NEW_TYPES

    def __init__(self, v, type_):
        super(GenomeAnnotationObject, self).__init__(v, type_)

    @property
    def is_genome_type(self):
        return self._bare_type in self.OLD_TYPES

    @property
    def is_annotation_type(self):
        return self._bare_type in self.NEW_TYPES

############

class TaxonObject(KBaseDataObject):
    OLD_TYPES = ['KBaseGenomes.Genome']
    NEW_TYPES = ['KBaseGenomesCondensedPrototypeV2.Taxon']

    types = OLD_TYPES + NEW_TYPES

    def __init__(self, v, type_):
        super(TaxonObject, self).__init__(v, type_)

