"""
Data API for Assembly entities.  This API provides methods for retrieving
summary information such as GC content, total length, external source information
as well as methods for retrieving individual contig sequences and gathering contig lengths and contig GC.
"""

# Stdlib
import requests
import os
import re
import string
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO as StringIO

# Local
from biokbase.data_api.object import ObjectAPI

CHUNK_SIZE = 2**30

_CONTIGSET_TYPES = ['KBaseGenomes.ContigSet']
_ASSEMBLY_TYPES = ['KBaseGenomesCondensedPrototypeV2.Assembly']
TYPES = _CONTIGSET_TYPES + _ASSEMBLY_TYPES

class AssemblyAPI(ObjectAPI):
    """API for the assembled sequences associated with a Genome Annotation.
    """
    
    def __init__(self, services, ref):
        """Defines which types and type versions that are legal.
        """
        super(AssemblyAPI, self).__init__(services, ref)
        
        self._is_assembly_type = self._typestring.split('-')[0] in _ASSEMBLY_TYPES
        self._is_contigset_type = self._typestring.split('-')[0] in _CONTIGSET_TYPES
        
        if not (self._is_assembly_type or self._is_contigset_type):
            raise TypeError("Invalid type! Expected one of {0}, received {1}".format(TYPES, self._typestring))
    
    def get_assembly_id(self):
        """Retrieve the id for an Assembly.

        Returns:
          id: string identifier for the Assembly"""

        if self._is_contigset_type:
            return self.get_data_subset(path_list=["id"])["id"]
        elif self._is_assembly_type:
            return self.get_data_subset(path_list=["assembly_id"])["assembly_id"]        

    def get_genome_annotations(self):
        """Retrieve the GenomeAnnotations that refer to this Assembly.
        
        Returns:
          list<GenomeAnnotation>
        """
        
        import biokbase.data_api.genome_annotation            
        
        referrers = self.get_referrers()
        
        annotations = list()
        for object_type in referrers:
            if object_type.split('-')[0] in biokbase.data_api.genome_annotation.TYPES:
                for x in referrers[object_type]:
                    annotations.append(
                        biokbase.data_api.genome_annotation.GenomeAnnotationAPI(
                            self.services, ref=x))
        
        if len(annotations) == 0:
            return None
        else:
            return annotations
    
    def get_external_source_info(self):
        """Retrieve the external source information associated with this Assembly.
        
        Returns:
          id: string identifier for the Assembly"""        
        
        if self._is_assembly_type:
            return self.get_data_subset(path_list=["external_source",
                                                   "external_source_id",
                                                   "external_source_origination_date"])
        elif self._is_contigset_type:
            data = self.get_data_subset(path_list=["source","source_id"])
            
            output = dict()
            output["external_source"] = data["source"]
            output["external_source_id"] = data["source_id"]
            output["external_source_origination_date"] = "Unknown"
            return output

    def get_stats(self):
        """Retrieve the derived statistical information about this Assembly.
        
        Returns:
          gc_content: total guanine and cytosine content, counting all G and C only
          dna_size: total length of all dna sequence for this Assembly
          num_contigs: total number of contiguous sequences in this Assembly"""        
        
        if self._is_contigset_type:
            contigs = self.get_data()["contigs"]
            
            pattern = re.compile(r'g|G|c|C')
            
            total_gc = 0
            for c in contigs:
                total_gc += len([s for s in re.finditer(pattern, c["sequence"])])
            
            total_length = sum([x.length for x in contigs])

            data = dict()
            data["gc_content"] = total_gc/(total_length*1.0)
            data["dna_size"] = total_length
            data["num_contigs"] = len(contigs)            
            return data
        elif self._is_assembly_type:
            return self.get_data_subset(path_list=["gc_content","dna_size","num_contigs"])            

    def get_number_contigs(self):
        """Retrieve the number of contiguous sequences in this Assembly.
        
        Returns:
          int"""
        
        if self._is_contigset_type:
            return len(self.get_data()["contigs"])
        elif self._is_assembly_type:
            return self.get_data_subset(path_list=["num_contigs"])["num_contigs"]

    def get_gc_content(self):
        """Retrieve the total GC content for this Assembly.
        
        Returns:
          float"""
        
        if self._is_contigset_type:
            contigs = self.get_data()["contigs"]
            
            pattern = re.compile(r'g|G|c|C')
            
            total_gc = 0
            total_length = 0
            for c in contigs:
                total_length += c["length"]
                total_gc += len([s for s in re.finditer(pattern, c["sequence"])])
            
            return total_gc/(total_length*1.0)
        elif self._is_assembly_type:
            return self.get_data_subset(path_list=["gc_content"])["gc_content"]

    def get_dna_size(self):
        """Retrieve the total DNA size for this Assembly.
        
        Returns:
          int"""
        
        if self._is_contigset_type:
            contigs = self.get_data()["contigs"]
            return sum([c["length"] for c in contigs])
        elif self._is_assembly_type:
            return self.get_data_subset(path_list=["dna_size"])["dna_size"]

    def get_contig_lengths(self, contig_id_list=None):
        """Retrieve the ids for every contiguous sequence in this Assembly.
        
        Returns:
          dict<str>: <int>"""
        
        contigs = self.get_data()["contigs"]        
                
        if self._is_contigset_type:
            if contig_id_list == None:        
                contig_id_list = [c["id"] for c in contigs]

            result = {c["id"]: c["length"] for c in contigs if c["id"] in contig_id_list}
        elif self._is_assembly_type:
            if contig_id_list == None:        
                contig_id_list = [contigs[c]["contig_id"] for c in contigs]
            
            result = {c: contigs[c]["length"] for c in contig_id_list}
        return result

    def get_contig_gc_content(self, contig_id_list=None):
        """Retrieve the total GC content for each contiguous sequence of this Assembly.
        
        Returns:
          dict<str>: float"""
        contigs = self.get_data()["contigs"]
        
        pattern = re.compile(r'g|G|c|C')
        contigs_gc = dict()
        
        if self._is_contigset_type:
            if contig_id_list == None:
                contig_id_list = [c["id"] for c in contigs]
                        
            for c in contigs:
                contigs_gc[c["id"]] = len([s for s in re.finditer(pattern, c["sequence"])])/(c["length"] * 1.0)
            
            return contigs_gc
        elif self._is_assembly_type:
            if contig_id_list == None:
                contig_id_list = [contigs[c]["contig_id"] for c in contigs]
            
            #fetch with sequence data
            contigs = self.get_contigs_by_id(contig_id_list)            
            
            for c in contigs:
                contigs_gc[c] = len([s for s in re.finditer(pattern, contigs[c]["sequence"])])/(contigs[c]["length"] * 1.0)
            
        return contigs_gc

    def get_contig_ids(self):
        """Retrieve the ids for every contiguous sequence in this Assembly.
        
        Returns:
          list<str>"""
        
        if self._is_contigset_type:
            contigs = self.get_data()["contigs"]
            result = [c["id"] for c in contigs]
        elif self._is_assembly_type:
            contigs = self.get_data()["contigs"]
            result = [contigs[c]["contig_id"] for c in contigs]
        return result

    def get_contigs_by_id(self, contig_id_list=None):
        """Retrieve contiguous sequences from this Assembly by id.
        
        Args:
          contig_id_list: list<str>
        Returns:
          dict
          
          dictionary of contigs, with contig id as key
          contig value structure::

              {
                  'contig_id': string,
                  'length': integer,
                  'md5': string,
                  'name': string,
                  'description': string,
                  'is_complete': 0 or 1,
                  'is_circular': 0 or 1,
                  'sequence': string
              }
        """
        if contig_id_list is None:
            contig_id_list = self.get_data()["contigs"]
        
        if self._is_contigset_type:
            contigs = self.get_data()["contigs"]

            if len(contig_id_list) == 0:
                return contigs
            
            matches = [c for c in contigs if c["id"] in contig_id_list]
            outContigs = dict()
            for c in matches:
                outContigs[c["id"]] = c
            
            return outContigs            
        elif self._is_assembly_type:
            num_contigs = len(contig_id_list)
            obj_result = self.get_data_subset(path_list=["num_contigs","fasta_handle_ref"])
            total_contigs = obj_result["num_contigs"]
            fasta_ref = obj_result["fasta_handle_ref"]

            copy_keys = ["contig_id", "length", "md5", "name", "description", "is_complete", "is_circular"]

            header = dict()
            header["Authorization"] = "Oauth {0}".format(os.environ["KB_AUTH_TOKEN"])

            if num_contigs > total_contigs/3 or num_contigs == 0:
                assembly = self.get_data()
                contigs = assembly["contigs"]

                Retrieve_url = self.services["shock_service_url"] + "node/" + fasta_ref + "?download_raw"

                #Retrieve all sequence
                data = requests.get(Retrieve_url, headers=header, stream=True)                
                buffer = StringIO.StringIO()
                for chunk in data.iter_content(CHUNK_SIZE):
                    if chunk:
                        buffer.write(chunk)
                sequence_data = buffer.getvalue()
                buffer.close()

                if num_contigs == 0:
                    contig_id_list = contigs.keys()
                    num_contigs = total_contigs
                    assert num_contigs == len(contig_id_list)

                outContigs = dict()
                for i in xrange(num_contigs):
                    c = contig_id_list[i]
                    outContigs[c] = dict()
                    for k in copy_keys:
                        if contigs[c].has_key(k):
                            outContigs[c][k] = contigs[c][k]

                    outContigs[c]["sequence"] = sequence_data[contigs[c]["start_position"]:contigs[c]["start_position"] + contigs[c]["num_bytes"]].translate(None, string.whitespace)
            else:                
                assembly = self.get_data_subset(path_list=["contigs/" + c for c in contig_id_list])
                 
                contigs = assembly["contigs"]
                
                def fetch_contig(start, length):
                    fetch_url = self.services["shock_service_url"] + "node/" + fasta_ref + \
                                "?download&seek=" + str(start) + \
                                "&length=" + str(length)

                    #Retrieve individual sequences
                    data = requests.get(fetch_url, headers=header, stream=True)                
                    buffer = StringIO.StringIO()
                    try:
                        for chunk in data.iter_content(CHUNK_SIZE):
                            if chunk:
                                buffer.write(chunk)

                        sequence = buffer.getvalue().translate(None, string.whitespace)
                    except:
                        raise
                    finally:
                        buffer.close()
                    
                    return sequence
                                
                outContigs = dict()
                sorted_contigs = sorted(contig_id_list,
                                 cmp=lambda a,b: cmp(contigs[a]["start_position"], contigs[b]["start_position"]))

                for c in sorted_contigs:
                    outContigs[c] = dict()
                    for k in copy_keys:
                        if contigs[c].has_key(k):
                            outContigs[c][k] = contigs[c][k]

                    outContigs[c]["sequence"] = fetch_contig(contigs[c]["start_position"],contigs[c]["num_bytes"])

            return outContigs
