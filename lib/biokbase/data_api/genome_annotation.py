import sys

from biokbase.data_api.object import ObjectAPI

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

class GenomeAnnotationAPI(ObjectAPI):
    def __init__(self, services, ref):
        """
        Defines which types and type versions that are legal."""
        
        super(GenomeAnnotationAPI, self).__init__(services, ref)
        
        self._is_annotation_type = self._typestring.split('-')[0] in _GENOME_ANNOTATION_TYPES
        self._is_genome_type = self._typestring.split('-')[0] in _GENOME_TYPES
        
        if not (self._is_annotation_type or self._is_genome_type):
            raise TypeError("Invalid type! Expected one of {0}, received {1}".format(TYPES, self._typestring))

    def get_taxon(self):
        """
        Retrieves the Taxon assigned to this Genome Annotation.
        
        Returns:
          TaxonAPI"""
        
        import biokbase.data_api.taxon
        
        if self._is_genome_type:
            return biokbase.data_api.taxon.TaxonAPI(self.services, ref=self.ref)
        elif self._is_annotation_type:
            return biokbase.data_api.taxon.TaxonAPI(self.services, ref=self.get_data_subset(path_list=["taxon_ref"])["taxon_ref"])

    def get_assembly(self):
        """
        Retrieves the Assembly used to create this Genome Annotation.
        
        Returns:
          AssemblyAPI"""
        
        import biokbase.data_api.assembly
        
        if self._is_genome_type:
            return biokbase.data_api.assembly.AssemblyAPI(self.services, ref=self.get_data_subset(path_list=["contigset_ref"])["contigset_ref"])
        elif self._is_annotation_type:
            return biokbase.data_api.assembly.AssemblyAPI(self.services, ref=self.get_data_subset(path_list=["assembly_ref"])["assembly_ref"])
    
    def get_feature_types(self):
        """
        Retrieves the Genome Feature type identifiers available from this Genome Annotation.
        
        Returns:
          list<str>"""
        
        if self._is_genome_type:
            features = self.get_data_subset(path_list=["features"])["features"]
            feature_types = list()
            for x in features:
                if x["type"] not in feature_types:
                    feature_types.append(x["type"])
            return feature_types
        elif self._is_annotation_type:
            return self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"].keys()

    def get_feature_type_descriptions(self, type_list=None):
        """
        Retrieves a descriptive string for each feature type identifier.
        
        Returns:
          dict"""
        
        if type_list == None:
            return FEATURE_DESCRIPTIONS
        elif type(type_list) == type([]) and len(type_list) > 0 and \
             (type(type_list[0]) == type(u"") or type(type_list[0]) == type("")):
            return {x: FEATURE_DESCRIPTIONS[x] for x in FEATURE_DESCRIPTIONS if x in type_list}
        else:
            raise TypeError()

    #def get_feature_ids(self, type_list=None, region_list=None, function_list=None, alias_list=None):
        #"""
        #Retrieves feature ids based on filters such as feature types, regions, functional descriptions, aliases.
        
        #Returns:
          #list<str>"""
        
        #if self._is_genome_type:
            #features = self.get_data_subset(path_list=["features"])["features"]
            #return [x['id'] for x in features]
        #elif self._is_annotation_type:
            #feature_container_references = self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"]
            
            #out_ids = list()
            #for x in feature_container_references:
                #feature_container = ObjectAPI(self.services, feature_container_references[x])
                #out_ids.extend(feature_container.get_data()["features"].keys())
            #return out_ids

    def get_feature_type_counts(self, type_list=None):
        """
        Retrieve the number of Genome Features contained in this Genome Annotation by Feature type identifier.
        
        Returns:
          dict<str>:<int>"""        
        
        if type(type_list) != type([]):
            raise TypeError("A list of strings indicating feature types is required.")
        elif len(type_list) == 0:
            raise TypeError("A list of strings indicating feature types is required, received an empty list.")
        
        if self._is_genome_type:
            counts = self._genome_get_feature_type_counts(type_list)            
        elif self._is_annotation_type:
            counts = self._annotation_get_feature_type_counts(type_list)
            
        return counts

    def get_feature_ids_by_type(self, type_list=None):
        """
        Retrieves Genome Feature identifiers from this Genome Annotation by Feature type identifier.
        
        Returns:
          dict<str>:list<str>"""        
        
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

    def get_feature_ids_by_alias(self, alias_list=None, type_list=None):
        """
        Retrieve Genome Feature identifiers based on a list of Genome Feature alias strings.
        
        Returns:
          dict<str>: list<str>"""
        
        if self._is_genome_type:
            features = self.get_data_subset(path_list=["features"])["features"]
            
            out_ids = dict()            
            for x in features:
                out_ids[x] = list()
                if x['type'] in type_list:
                    out_ids[x['type']].append(x['id'])
                
            return out_ids
        elif self._is_annotation_type:
            feature_lookup = self.get_data_subset(path_list=["feature_lookup"])["feature_lookup"]
            feature_containers = dict()
            
            out_ids = dict()            
            for alias in alias_list:
                out_ids[alias] = list()           
                ref = feature_lookup[alias][0]
                
                if ref not in feature_containers:
                    feature_containers[ref] = list()
                
                feature_containers[ref].append(feature_lookup[alias][1])
            
            for alias in alias_list:
                for ref in out_ids[alias]:
                    container = ObjectAPI(self.services, ref)
                    
                    if container.get_data_subset(["type"])["type"] in type_list:
                        out_ids[alias] = feature_containers[alias]
                    
                out_ids[x] = feature_container.get_data()["features"].keys()
            return out_ids

    #def get_cds_protein(self, cds_id_list=None):
        #if cds_id_list == None:
            #cds_id_list = self.get_feature_ids_by_type(["CDS"])
        
        #if self._is_genome_type:
            #return None
        #elif self._is_annotation_type:
            #feature_lookup = self.get_data_subset(path_list=["feature_lookup"])["feature_lookup"]            
            
            #cds_feature_container = ObjectAPI(self.services, ref=feature_lookup)            
            
            #for x in cds_id_list:
                #for feature_ref in feature_lookup[x]:
                    #if feature_ref[0] not in feature_containers:
                        #feature_containers[feature_ref[0]] = list()
                    
                    #feature_containers[feature_ref[0]].append(feature_ref[1])
            
            #locations = dict()
            #for ref in feature_containers:
                #features = ObjectAPI(self.services, ref).get_data_subset(path_list=["features/" + x for x in feature_id_list])["features"]
                
                #for feature_id in feature_id_list:
                    #locations[feature_id] = list()
                    #for loc in features[feature_id]["location"]:
                        #locations[feature_id].append({
                            #"contig_id": loc[0],
                            #"strand": loc[2],
                            #"start": loc[1],
                            #"length": loc[3]
                        #})
            
            #return locations        

    def get_feature_locations(self):
        if type(feature_id_list) != type([]):
            raise TypeError("A list of strings indicating feature identifiers is required.")
        elif len(feature_id_list) == 0:
            raise TypeError("A list of strings indicating feature identifiers is required, received an empty list.")        
        
        if self._is_genome_type:
            features = self.get_data_subset(path_list=["features"])["features"]
            
            locations = dict()            
            for x in features:
                if x['id'] in feature_id_list:
                    locations[x['id']] = list()
                    
                    for loc in x['location']:
                        locations[x['id']].append({
                            "contig_id": loc[0],
                            "strand": loc[2],
                            "start": loc[1],
                            "length": loc[3]
                        })                            
            return locations
        elif self._is_annotation_type:
            feature_lookup = self.get_data_subset(path_list=["feature_lookup"])["feature_lookup"]

            feature_containers = dict()
            
            for x in feature_id_list:
                for feature_ref in feature_lookup[x]:
                    if feature_ref[0] not in feature_containers:
                        feature_containers[feature_ref[0]] = list()
                    
                    feature_containers[feature_ref[0]].append(feature_ref[1])
            
            locations = dict()
            for ref in feature_containers:
                features = ObjectAPI(self.services, ref).get_data_subset(path_list=["features/" + x for x in feature_id_list])["features"]
                
                for feature_id in feature_id_list:
                    locations[feature_id] = list()
                    for loc in features[feature_id]["location"]:
                        locations[feature_id].append({
                            "contig_id": loc[0],
                            "strand": loc[2],
                            "start": loc[1],
                            "length": loc[3]
                        })
            
            return locations
    
    def get_feature_dna(self, feature_id_list=None):
        pass

    def get_feature_functions(self, feature_id_list=None):
        pass

    def get_feature_aliases(self, feature_id_list=None):
        pass
    
    def get_feature_publications(self, feature_id_list=None):
        pass

    #def get_feature_quality(self, feature_id_list=None):
    #    pass

    def get_features_by_id(self, feature_id_list=None):
        if feature_id_list == None:
            feature_id_list = self.get_feature_ids()
                
        if self._is_genome_type:
            features = self.get_data_subset(path_list=["features"])["features"]
            
            out_features = dict()            
            for x in features:
                if x['id'] in feature_id_list:
                    out_features[x['id']] = dict()
                    out_features[x['id']]["feature_id"] = x['id']
                    out_features[x['id']]["feature_type"] = x['type']
                    out_features[x['id']]["feature_function"] = x['function']
                    out_features[x['id']]["feature_locations"] = x['locations']
                    out_features[x['id']]["feature_md5"] = x['md5']
                    out_features[x['id']]["feature_dna_sequence"] = x['dna_sequence']
                    
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
                    
                    if x.has_key():
                        out_features[x['id']]["feature_quality_score"] = x['quality']
                    else:
                        out_features[x['id']]["feature_quality_score"] = -1
                    
                    out_features[x['id']]["feature_quality_warnings"] = None
                
            return out_features
        elif self._is_annotation_type:
            feature_lookup = self.get_data_subset(path_list=["feature_lookup"])["feature_lookup"]

            feature_containers = dict()
            
            for x in feature_id_list:
                print x, feature_lookup[x]
                for feature_ref in feature_lookup[x]:
                    if feature_ref[0] not in feature_containers:
                        feature_containers[feature_ref[0]] = list()
                    
                    feature_containers[feature_ref[0]].append(feature_ref[1])
            
            out_features = dict()
            for ref in feature_containers:
                features = ObjectAPI(self.services, ref).get_data_subset(path_list=["features/" + x for x in feature_id_list])["features"]
                for x in feature_id_list:
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
        if self._is_genome_type:
            features = self.get_data()["features"]
            
            proteins = dict()
            for f in features:
                if f.has_key("protein_translation") and len(f["protein_translation"]) > 0:
                    protein_id = f['id'] + ".protein"
                    proteins[protein_id] = dict()
                
                #TODO finish this
        elif self._is_annotation_type:
            protein_container = ObjectAPI(self.services, self.get_data()["protein_container_ref"])
            return protein_container.get_data()["proteins"]

    def get_proteins_by_id(self, protein_id_list=None):
        raise NotImplementedError

    # helper methods
    def get_cds_by_mrna(self, mRNA_feature_id_list=None):
        if type(mRNA_feature_id_list) != type([]): 
            raise TypeError("A list of strings indicating mRNA feature identifiers is required.") 
        elif len(mRNA_feature_id_list) == 0: 
            raise TypeError("A list of strings indicating mRNA feature identifiers is required, received an empty list.") 
 
        return_dict = dict()
        if self._is_genome_type: 
            #This type of genome object does not support this call. 
            return return_dict
        elif self._is_annotation_type:
            data = self.get_data_subset(path_list=["feature_lookup", "feature_container_references"])
            feature_lookup = data["feature_lookup"]
            feature_container_references = data["feature_container_references"]

            mRNA_feature_container_ref = None;
            if "mRNA" in feature_container_references:
                mRNA_feature_container_ref = feature_container_references["mRNA"]
            else:
                #Does not have mRNA annotations in this genome
                return return_dict

            mRNA_features = ObjectAPI(self.services, mRNA_feature_container_ref).get_data_subset(path_list=["features/" + x for x in mRNA_feature_id_list])["features"]

            for mRNA_feature_key in mRNA_features:
                mRNA_id = mRNA_features[mRNA_feature_key]["feature_id"]
                if "mRNA_properties" in  mRNA_features[mRNA_feature_key]:
                    if "associated_CDS" in   mRNA_features[mRNA_feature_key]["mRNA_properties"]:
                        return_dict[mRNA_id] =  mRNA_features[mRNA_feature_key]["mRNA_properties"]["associated_CDS"][1]
                    else:
                        return_dict[mRNA_id] = None
                else:
                    return_dict[mRNA_id] = None

            return return_dict

    
    def get_mrna_by_cds(self, cds_feature_id_list=None):
        if type(cds_feature_id_list) != type([]): 
            raise TypeError("A list of strings indicating CDS feature identifiers is required.") 
        elif len(cds_feature_id_list) == 0: 
            raise TypeError("A list of strings indicating CDS feature identifiers is required, received an empty list.") 
 
        return_dict = dict() 
        if self._is_genome_type: 
            #This type of genome object does not support this call. 
            return return_dict 
        elif self._is_annotation_type: 
            data = self.get_data_subset(path_list=["feature_lookup", "feature_container_references"]) 
            feature_lookup = data["feature_lookup"] 
            feature_container_references = data["feature_container_references"] 
 
            cds_feature_container_ref = None; 
            if "CDS" in feature_container_references: 
                cds_feature_container_ref = feature_container_references["CDS"] 
            else: 
                #Does not have CDS annotations in this genome                                                                                                                                 
                return return_dict 
 
            cds_features = ObjectAPI(self.services, cds_feature_container_ref).get_data_subset(path_list=["features/" + x for x in cds_feature_id_list])["features"] 
 
            for cds_feature_key in cds_features: 
                cds_id = cds_features[cds_feature_key]["feature_id"] 
                if "CDS_properties" in  cds_features[cds_feature_key]: 
                    if "associated_mRNA" in   cds_features[cds_feature_key]["CDS_properties"]: 
                        return_dict[cds_id] =  cds_features[cds_feature_key]["CDS_properties"]["associated_mRNA"][1] 
                    else: 
                        return_dict[cds_id] = None 
                else: 
                    return_dict[cds_id] = None 
 
            return return_dict 

    
    def get_gene_by_cds(self, cds_feature_id_list=None):
        if type(cds_feature_id_list) != type([]): 
            raise TypeError("A list of strings indicating CDS feature identifiers is required.")
        elif len(cds_feature_id_list) == 0: 
            raise TypeError("A list of strings indicating CDS feature identifiers is required, received an empty list.")
 
        return_dict = dict()
        if self._is_genome_type: 
            #This type of genome object does not support this call.
            return return_dict
        elif self._is_annotation_type: 
            data = self.get_data_subset(path_list=["feature_lookup", "feature_container_references"])
            feature_lookup = data["feature_lookup"]
            feature_container_references = data["feature_container_references"]
 
            cds_feature_container_ref = None;
            if "CDS" in feature_container_references: 
                cds_feature_container_ref = feature_container_references["CDS"] 
            else:
                #Does not have CDS annotations in this genome
                return return_dict 
 
            cds_features = ObjectAPI(self.services, cds_feature_container_ref).get_data_subset(path_list=["features/" + x for x in cds_feature_id_list])["features"] 
 
            for cds_feature_key in cds_features:
                cds_id = cds_features[cds_feature_key]["feature_id"] 
                if "CDS_properties" in  cds_features[cds_feature_key]: 
                    if "associated_mRNA" in   cds_features[cds_feature_key]["CDS_properties"]:
                        return_dict[cds_id] =  cds_features[cds_feature_key]["CDS_properties"]["parent_gene"][1]
                    else:
                        return_dict[cds_id] = None
                else:
                    return_dict[cds_id] = None
 
            return return_dict

    
    def get_gene_by_mrna(self, mRNA_feature_id_list=None):
        if type(mRNA_feature_id_list) != type([]):
            raise TypeError("A list of strings indicating mRNA feature identifiers is required.")
        elif len(mRNA_feature_id_list) == 0:
            raise TypeError("A list of strings indicating mRNA feature identifiers is required, received an empty list.")
 
        return_dict = dict() 
        if self._is_genome_type: 
            #This type of genome object does not support this call.   
            return return_dict 
        elif self._is_annotation_type:
            data = self.get_data_subset(path_list=["feature_lookup", "feature_container_references"])
            feature_lookup = data["feature_lookup"] 
            feature_container_references = data["feature_container_references"]
 
            mRNA_feature_container_ref = None; 
            if "mRNA" in feature_container_references:
                mRNA_feature_container_ref = feature_container_references["mRNA"]
            else: 
                #Does not have mRNA annotations in this genome  
                return return_dict
            mRNA_features = ObjectAPI(self.services, mRNA_feature_container_ref).get_data_subset(path_list=["features/" + x for x in mRNA_feature_id_list])["features"] 
 
            for mRNA_feature_key in mRNA_features: 
                mRNA_id = mRNA_features[mRNA_feature_key]["feature_id"] 
                if "mRNA_properties" in  mRNA_features[mRNA_feature_key]:
                    if "parent_gene" in   mRNA_features[mRNA_feature_key]["mRNA_properties"]: 
                        return_dict[mRNA_id] =  mRNA_features[mRNA_feature_key]["mRNA_properties"]["parent_gene"][1] 
                    else:
                        return_dict[mRNA_id] = None
                else:
                    return_dict[mRNA_id] = None
 
            return return_dict

    def get_children_cds_by_gene(self, gene_id_list=None):
        raise NotImplementedError
    
    def get_children_mrna_by_gene(self, gene_id_list=None):
        raise NotImplementedError

    def _genome_get_features_by_type(self, type_list=None, test=lambda x: True):
        """
        Retrieves Genome Features from a KBaseGenomes.Genome object, filtering on Feature type.
        
        Returns:
          dict"""
        
        features = self.get_data()["features"]
        
        out_features = dict()            
        for x in features:
            out_features[x] = list()
            if x['type'] in type_list and test(x):
                if x['type'] not in out_features:
                    out_features[x['type']] = list()
                
                out_features[x['type']].append(x)
        return out_features

    def _annotation_get_features_by_type(self, type_list=None, test=lambda x: True):
        """
        Retrieves Genome Features from a KBaseGenomesCondensedPrototypeV2.GenomeAnnotation object, filtering on Feature type.

        Returns:
          dict"""
        
        feature_container_references = self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"]
        
        out_ids = dict()                        
        for x in [k for k in feature_container_references if k in type_list]:
            feature_container = ObjectAPI(services=self.services, ref=feature_container_references[x])
            out_features[x] = [x for x in feature_container.get_data()["features"] if test(x)]
        return out_features

    def _genome_get_feature_ids_by_type(self, type_list=None, test=lambda x: True):
        """
        Retrieves Genome Features from a KBaseGenomes.Genome object, filtering on Feature type.

        Returns:
          dict"""

        features = self.get_data_subset(path_list=["features"])["features"]
        
        out_ids = dict()            
        for x in features:
            out_ids[x] = list()
            if x['type'] in type_list and test(x):
                out_ids[x['type']].append(x['id'])            
        return out_ids

    def _annotation_get_feature_ids_by_type(self, type_list=None, test=lambda x: True):
        """
        Retrieves Genome Features from a KBaseGenomesCondensedPrototypeV2.GenomeAnnotation object, filtering on Feature type.

        Returns:
          dict<str>:<list<str>>"""

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

    def _genome_get_feature_type_counts(self, type_list=None):
        """
        Retrieves Genome Features from a KBaseGenomes.Genome object, filtering on Feature type.

        Returns:
          dict"""

        features = self.get_data_subset(path_list=["features"])["features"]
        
        counts = dict()          
        
        for t in type_list:
            counts[t] = 0        
        
        for x in features:
            if x['type'] in type_list:
                counts[x['type']] += 1            
        
        return counts

    def _annotation_get_feature_type_counts(self, type_list=None):
        """
        Retrieves number of Genome Features from a KBaseGenomesCondensedPrototypeV2.GenomeAnnotation object, filtering on Feature type.

        Returns:
          dict<str>:<list<str>>"""

        feature_container_references = self.get_data_subset(path_list=["feature_container_references"])["feature_container_references"]
        
        counts = dict()
        
        for t in type_list:
            counts[t] = 0
        
        for x in [k for k in feature_container_references if k in type_list]:
            feature_container = ObjectAPI(services=self.services, ref=feature_container_references[x])
            counts[x] = feature_container.get_data()["feature_count"]
        return counts
