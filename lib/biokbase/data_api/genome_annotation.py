import sys

from biokbase.data_api.object import ObjectAPI

FEATURE_DESCRIPTIONS = {
    "CDS": "Coding Sequence",
    "PEG": "Protein Encoding Genes",
    "rna": "RNA",
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

class GenomeAnnotationAPI(ObjectAPI):
    def __init__(self, services, ref):
        """
        Defines which types and type versions that are legal.
        """
        super(GenomeAnnotationAPI, self).__init__(services, ref)
        
        self._genome_types = ['KBaseGenomes.Genome-225de07e59f4fdc5d9b8bf0bcd12c498', 
                              'KBaseGenomes.Genome-aafaaa7df90d03b33258f4fa7790dcbe', 
                              'KBaseGenomes.Genome-93da9d2c8fb7836fb473dd9c1e4ca89e', 
                              'KBaseGenomes.Genome-1e1fce431960397da77cb092d27a50cf', 
                              'KBaseGenomes.Genome-c0526fae0ce1fd8d342ec94fc4dc510a', 
                              'KBaseGenomes.Genome-c0526fae0ce1fd8d342ec94fc4dc510a', 
                              'KBaseGenomes.Genome-51b05a5c27084ae56106e60df5b66df5']
        self._annotation_types = ['KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-d4301f53dab71e72d70ea5be6919696e', 
                                  'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-97253a4ad440116a6421ede1fca50cad', 
                                  'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-6935b73c720523e4541dd516bc13ef56', 
                                  'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-e3de51478246422db519fd4cbc9eb4cd']
        
        self._is_annotation_type = self._typestring in self._annotation_types
        self._is_genome_type = self._typestring in self._genome_types
        
        if not (self._is_annotation_type or self._is_genome_type):
            raise TypeError("Expecting KBaseGenomes.Genome or KBaseGenomesCondensedPrototypeV2.GenomeAnnotation, received {0}".format(self._typestring))

    def get_taxon(self):
        """
        Retrieves the Taxon assigned to this Genome Annotation.
        
        Returns:
            TaxonAPI
        """
        
        import biokbase.data_api.taxon
        
        if self._is_genome_type:
            return biokbase.data_api.taxon.TaxonAPI(self.services, ref=self.ref)
        elif self._is_annotation_type:
            return biokbase.data_api.taxon.TaxonAPI(self.services, ref=self.get_data_subset(path_list=["taxon_ref"])["taxon_ref"])

    def get_assembly(self):
        """
        Retrieves the Assembly used to create this Genome Annotation.
        
        Returns:
            AssemblyAPI
        """
        
        import biokbase.data_api.assembly
        
        if self._is_genome_type:
            return biokbase.data_api.assembly.AssemblyAPI(self.services, ref=self.get_data_subset(path_list=["contigset_ref"])["contigset_ref"])
        elif self._is_annotation_type:
            return biokbase.data_api.assembly.AssemblyAPI(self.services, ref=self.get_data_subset(path_list=["assembly_ref"])["assembly_ref"])
    
    def get_feature_types(self):
        if self._is_genome_type:
            features = self.get_data_subset(path_list=["features"])["features"]
            feature_types = set()
            for x in features:
                if x["type"] not in feature_types:
                    feature_types.add(x["type"])
            return feature_types
        elif self._is_annotation_type:
            return self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"].keys()

    def get_feature_type_descriptions(self, type_list=None):
        if type_list == None:
            return FEATURE_DESCRIPTIONS
        elif type(type_list) == type([]) and len(type_list) and \
             (type(type_list[0]) == type(u"") or type(type_list[0]) == type("")):
            return {x: FEATURE_DESCRIPTIONS[x] for x in FEATURE_DESCRIPTIONS if x in type_list}

    def get_number_of_each_feature_type(self):
        if self._is_genome_type:
            features = self.get_data_subset(path_list=["features"])["features"]
            feature_types = dict()
            for x in features:
                if x["type"] not in feature_types:
                    feature_types[x["type"]] = 1
                else:
                    feature_types[x["type"]] += 1
            return feature_types
        elif self._is_annotation_type:            
            feature_container_refs = self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"]
            feature_types = dict()
            for x in feature_container_refs:
                feature_types[x] = len(ObjectAPI(self.services, ref=feature_container_refs[x]).get_data()["features"])
            return feature_types            

    def get_feature_ids(self):
        if self._is_genome_type:
            features = self.get_data_subset(path_list=["features"])["features"]
            return [x['id'] for x in features]
        elif self._is_annotation_type:
            feature_container_references = self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"]
            
            out_ids = list()
            for x in feature_container_references:
                feature_container = ObjectAPI(self.services, feature_container_references[x])
                out_ids[x].extend(feature_container.get_data()["features"].keys())
            return out_ids

    def _genome_get_features_by_type(self, type_list=None, test=lambda x: True):
        features = self.get_data()["features"]
        print features
        #["features"]
        
        out_features = dict()            
        for x in features:
            out_features[x] = list()
            if x['type'] in type_list and test(x):
                if x['type'] not in out_features:
                    out_features[x['type']] = list()
                
                out_features[x['type']].append(x)
        return out_features

    def _annotation_get_features_by_type(self, type_list=None, test=lambda x: True):
        feature_container_references = self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"]
        
        out_ids = dict()                        
        for x in [k for k in feature_container_references if k in type_list]:
            feature_container = ObjectAPI(services=self.services, ref=feature_container_references[x])
            out_features[x] = [x for x in feature_container.get_data()["features"] if test(x)]
        return out_features

    def _genome_get_feature_ids_by_type(self, type_list=None, test=lambda x: True):
        features = self.get_data_subset(path_list=["features"])["features"]
        
        out_ids = dict()            
        for x in features:
            out_ids[x] = list()
            if x['type'] in type_list and test(x):
                out_ids[x['type']].append(x['id'])            
        return out_ids

    def _annotation_get_feature_ids_by_type(self, type_list=None, test=lambda x: True):
        feature_container_references = self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"]
        
        out_ids = dict()                        
        for x in [k for k in feature_container_references if k in type_list]:
            feature_container = ObjectAPI(services=self.services, ref=feature_container_references[x])
            out_ids[x] = list()
            features = feature_container.get_data()["features"]
            for f in features:
                if test(f):
                    out_ids[x].append(features[f]['feature_id'])
        return out_ids

    def get_feature_ids_by_type(self, type_list=None):
        if type(type_list) != type([]):
            raise TypeError("A list of strings indicating feature types is required.")
        elif len(type_list) == 0:
            raise TypeError("A list of strings indicating feature types is required, received an empty list.")
        
        if self._is_genome_type:
            return self._genome_get_feature_ids_by_type(type_list)
        elif self._is_annotation_type:
            return self._annotation_get_feature_ids_by_type(type_list)

    def get_feature_ids_by_contig_id(self, contig_id_list=None, type_list=None):
        if type_list == None:
            type_list = self.get_feature_types()
        
        if self._is_genome_type:
            return self._genome_get_feature_ids_by_type(type_list, lambda x: x[0] in contig_id_list)
        elif self._is_annotation_type:
            return self._annotation_get_feature_ids_by_type(type_list, lambda x: x[0] in contig_id_list)
                
    def get_feature_ids_by_region(self, contig_id_list=list(), start=0, stop=sys.maxint, strand="?", type_list=None):
        if type_list == None:
            type_list = self.get_feature_types()

        def is_feature_in_region(f):
            if (len(contig_id_list) == 0 or f[0] in contig_id_list) and \
               (f[2] == strand or strand == "?") and \
               (f[1] <= stop and start <= f[1] + f[3]):
                return True
            else:
                return False
        
        if self._is_genome_type:                            
            return self._genome_get_feature_ids_by_type(type_list, lambda x: is_feature_in_region(x))
        elif self._is_annotation_type:
            return self._annotation_get_feature_ids_by_type(type_list, lambda x: is_feature_in_region(x))

    def get_feature_ids_by_function(self, function_list=None, type_list=None):
        if function_list == None:
            raise TypeError("A list of feature function strings is required.")
        elif len(function_list) == 0:
            raise TypeError("A list of feature function strings is required, recieved an empty list.")
        
        if type_list == None:        
            type_list = self.get_feature_types()
        
        function_tokens = list()
        for x in function_list:
            function_tokens.extend(x.split())
        function_tokens = set(function_tokens)
        
        def is_function_in_feature(feature, function_tokens=function_tokens):
            tokens = feature['function'].split()            
            
            found = False
            for t in tokens:
                if t in function_tokens:
                    found = True
                    break
            return found
                
        if self._is_genome_type:
            out_ids = dict()
            for function in function_list:
                features = self._genome_get_features_by_type(type_list, lambda x: is_function_in_feature(x))
                for feature_type in features:
                    if feature_type not in out_ids:
                        out_ids[feature_type] = [x['id'] for x in features[feature_type]]
                    else:
                        out_ids[feature_type].extend([x['id'] for x in features[feature_type]])
            return out_ids
        elif self._is_annotation_type:
            out_ids = dict()
            for function in function_list:
                features = self._annotation_get_features_by_type(type_list, lambda x: is_function_in_feature(function, x))
                for feature_type in features:
                    if feature_type not in out_ids:
                        out_ids[feature_type] = [x['feature_id'] for x in features[feature_type]]
                    else:
                        out_ids[feature_type].extend([x['feature_id'] for x in features[feature_type]])
            return out_ids

    def get_feature_ids_by_alias(self, alias_list=None, type=None):
        if self._is_genome_type:
            features = self.get_data_subset(path_list=["features"])["features"]
            
            out_ids = dict()            
            for x in features:
                out_ids[x] = list()
                if x['type'] in type_list:
                    out_ids[x['type']].append(x['id'])
                
            return out_ids
        elif self._is_annotation_type:
            feature_container_references = self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"]
            
            out_ids = dict()                        
            for x in [k for k in feature_container_references if k in type_list]:
                feature_container = ObjectAPI(self.services, feature_container_references[x])
                out_ids[x] = feature_container.get_data()["features"].keys()
            return out_ids

    def get_associated_feature_ids(self, from_type=None, to_type=None, feature_id_list=None):
        raise NotImplementedError

    def get_child_feature_ids(self, from_type=None, to_type=None, feature_id_list=None):
        raise NotImplementedError

    def get_parent_feature_ids(self, from_type=None, to_type=None, feature_id_list=None):
        raise NotImplementedError

    def get_protein_ids_by_cds(self, cds_id_list=None):
        raise NotImplementedError

    def get_features_by_id(self, feature_id_list=None):
        if self._is_genome_type:
            features = self.get_data_subset(path_list=["features"])["features"]
            
            out_features = dict()            
            for x in features:
                if x['id'] in feature_id_list:
                    out_features[x['id']] = x
                
            return out_features
        elif self._is_annotation_type:
            feature_container_references = self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"]
            
            out_features = dict()                        
            for x in feature_container_references:
                feature_container = ObjectAPI(self.services, feature_container_references[x])
                features = feature_container.get_data()["features"]
                for f in features:
                    if f in feature_id_list:
                        out_features[f] = features[f]
            return out_features

    def get_proteins(self):
        if self._is_genome_type:
            features = self.get_data()["features"]
            
            proteins = dict()
            for f in features:
                if f.has_key("protein_translation") and len(f["protein_translation"]) > 0:
                    protein_id = f['id'] + ".protein"
                    proteins[protein_id] = dict()
        elif self._is_annotation_type:
            protein_container = ObjectAPI(self.services, self.get_data()["protein_container_ref"])
            return protein_container.get_data()["proteins"]

    def get_proteins_by_id(self, protein_id_list=None):
        raise NotImplementedError

    # helper methods
    def get_cds_by_mrna(self, mrna_id_list=None):
        raise NotImplementedError
    
    def get_mrna_by_cds(self, cds_id_list=None):
        raise NotImplementedError
    
    def get_gene_by_cds(self, cds_id_list=None):
        raise NotImplementedError
    
    def get_gene_by_mrna(self, mrna_id_list=None):
        raise NotImplementedError

    def get_children_cds_by_gene(self, gene_id_list=None):
        raise NotImplementedError
    
    def get_children_mrna_by_gene(self, gene_id_list=None):
        raise NotImplementedError
    
    def add_features(self, feature_id_list=None):
        raise NotImplementedError

    def remove_features(self, feature_id_list=None):
        raise NotImplementedError
        
    def replace_features(self, feature_id_list=None):
        raise NotImplementedError

    def replace_assembly(self, ws_id, assembly_id):
        raise NotImplementedError

