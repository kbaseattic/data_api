import requests
import sys
import os
import json
import datetime
import re
import tempfile
import shutil
import string

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO as StringIO

from biokbase.data_api.object import ObjectAPI

CHUNK_SIZE = 2**30


class GenomeAnnotationAPI(ObjectAPI):
    def get_taxon_ref(self):
        typestring = self.get_typestring()

    # emit warnings for deprecation and getting taxon object instead
    def get_taxonomic_lineage(self, ref_list=None):
        pass

    # use feature_lookup
    def get_feature_ids_by_type(self, ref=None, feature_id_list=list(), type=None):
        features = self.get_data_subset(path_list=["features"])["features"]

        if len(feature_id_list) == 0:
            return features
        
        outFeatures = list()
        for f in feature_id_list:
            outFeatures.extend([x for x in features if x["id"] == f])

        return outFeatures

    def get_feature_ids_by_region(self, ref=None, contig_id_list=list(), start=0, stop=-1, strand="+", type=None):
        raise NotImplementedError

    def get_feature_ids_by_function(self, ref=None, function_list=None, type=None):
        raise NotImplementedError

    def get_feature_ids_by_alias(self, ref=None, alias_list=None, type=None):
        raise NotImplementedError

    def get_associated_feature_ids(self, ref=None, from_type=None, to_type=None, feature_id_list=None):
        raise NotImplementedError

    def get_child_feature_ids(self, ref=None, from_type=None, to_type=None, feature_id_list=None):
        raise NotImplementedError

    def get_parent_feature_ids(self, ref=None, from_type=None, to_type=None, feature_id_list=None):
        raise NotImplementedError

    def get_protein_ids_by_cds(self, ref=None, cds_id_list=None):
        raise NotImplementedError

    def get_features_by_id(self, ref=None, feature_id_list=None):
        raise NotImplementedError

    def get_proteins(self, ref=None, protein_id_list=None):
        raise NotImplementedError

    # helper methods
    def get_cds_by_mrna(self, ref=None, mrna_id_list=None):
        raise NotImplementedError
    
    def get_mrna_by_cds(self, ref=None, cds_id_list=None):
        raise NotImplementedError
    
    def get_gene_by_cds(self, ref=None, cds_id_list=None):
        raise NotImplementedError
    
    def get_gene_by_mrna(self, ref=None, mrna_id_list=None):
        raise NotImplementedError

    def get_children_cds_by_gene(self, ref=None, gene_id_list=None):
        raise NotImplementedError
    
    def get_children_mrna_by_gene(self, ref=None, gene_id_list=None):
        raise NotImplementedError
    
    def add_features(self, ref=None, feature_id_list=None):
        raise NotImplementedError

    def remove_features(self, ref=None, feature_id_list=None):
        raise NotImplementedError
        
    def replace_features(self, ref=None, feature_id_list=None):
        raise NotImplementedError

    def get_assembly_ref(self, ws_id):
        return self.get_data_subset(path_list=["contigset_ref"])["contigset_ref"]

    def replace_assembly(self, ws_id, assembly_id):
        raise NotImplementedError

