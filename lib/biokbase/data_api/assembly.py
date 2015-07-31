"""
Operations on Assembly data type.
"""
import requests
import os
import re
import string

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO as StringIO

from biokbase.data_api.object import ObjectAPI

CHUNK_SIZE = 2**30


class AssemblyAPI(ObjectAPI):
    """
    API for the assembled sequences associated with a Genome Annotation.            
    """
    
    def __init__(self, services, ref):
        """
        Defines which types and type versions that are legal.
        """
        super(AssemblyAPI, self).__init__(services, ref)
        
        self._contigset_types = ["KBaseGenomes.ContigSet-e4511babc29d2d0428645ce8d2c0ad77",
                                 "KBaseGenomes.ContigSet-d3262fe600c857ab28d45297fae38ed1",
                                 "KBaseGenomes.ContigSet-a5dafc82a37e8e354b39e705d3c03044",
                                 "KBaseGenomes.ContigSet-db7f518c9469d166a783d813c15d64e9"]
        self._assembly_types = ["KBaseGenomesCondensedPrototypeV2.Assembly-ffd679cc5c9ce4a3b1bb1a5c3960b42e"]
        
        self._is_assembly_type = self._typestring in self._assembly_types
        self._is_contigset_type = self._typestring in self._contigset_types

    def get_assembly_id(self):
        """
        Fetch the id for an Assembly.

        Args:
            None        
        Returns:
            id: string identifier for the Assembly
        """
        typestring = self.get_typestring()

        if self._is_contigset_type:
            return self.get_data_subset(path_list=["id"])["id"]
        elif self._is_assembly_type:
            return self.get_data_subset(path_list=["assembly_id"])["assembly_id"]        
    
    def get_external_source_info(self):
        """
        Fetch the external source information associated with this Assembly.
        
        Args:
            None
        Returns:
            id: string identifier for the Assembly
        """        
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
        """
        Fetch the derived statistical information about this Assembly.
        
        Args:
            None
        Returns:
            gc_content: total guanine and cytosine content, counting all G and C only
            dna_size: total length of all dna sequence for this Assembly
            num_contigs: total number of contiguous sequences in this Assembly        
        """        
        if self._is_contigset_type:
            contigs = self.get_data()
            
            pattern = re.compile(r'g|G|c|C')
            total_gc = sum([len(enumerate(re.finditer(pattern, x.sequence))) for x in contigs])
            total_length = sum([x.length in contigs])

            data = dict()
            data["gc_content"] = total_gc/(total_length*1.0)
            data["dna_size"] = total_length
            data["num_contigs"] = len(contigs)            
            return data
        elif self._is_assembly_type:
            return self.get_data_subset(path_list=["gc_content","dna_size","num_contigs"])            

    #def add_contigs(self, contig_map=None):
    #    """
    #    Add contigs to this assembly.
    #    
    #    Args:
    #        contig_map: a dictionary of contig ids to
    #            {
    #              'contig_id': string,
    #              'name': string,
    #              'description': string,
    #              'is_complete': 0 or 1,
    #              'is_circular': 0 or 1
    #            }
    #    Returns:
    #                          
    #    """
    #    returns None
    
    #def remove_contigs(self):
    #    raise NotImplementedError
    
    #def replace_contigs(self):
    #    raise NotImplementedError

    def get_number_contigs(self):
        """
        Retrieve the number of contiguous sequences in this Assembly.
        
        Args:
            None
        Returns:
            integer
        """
        if self._is_contigset_type:
            return len(self.get_data()["contigs"])
        elif self._is_assembly_type:
            return self.get_data_subset(path_list=["num_contigs"])["num_contigs"]

    def get_contig_ids(self):
        """
        Retrieve the ids for every contiguous sequence in this Assembly.
        
        Args:
            None
        Returns:
            list of string identifiers
        """
        typestring = self.get_typestring()

        if self._is_contigset_type:
            contigs = self.get_data()["contigs"]
            return [c["id"] for c in contigs]
        elif self._is_assembly_type:
            contigs = self.get_data()["contigs"]
            return [contigs[c]["contig_id"] for c in contigs]
        else:
            raise TypeError("Invalid type! Expected KBaseGenomes.ContigSet <= 3.0 or KBaseGenomesCondensedPrototype.Assembly <= 1.0, received " + info[2])

    def get_contigs_by_id(self, contig_id_list=list()):
        """
        Retrieve contiguous sequences from this Assembly by id.
        
        Args:
            contig_id_list: list of string identifiers
        Returns:
            dictionary of contigs, with contig id as key
            contig value structure
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

                fetch_url = self.services["shock_service_url"] + "node/" + fasta_ref + "?download_raw"

                #fetch all sequence
                data = requests.get(fetch_url, headers=header, stream=True)                
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
                assembly = self.get_data_subset(path_list=["contigs/" + x for x in contig_id_list])
                 
                contigs = assembly["contigs"]
                
                def fetch_contig(start, length):
                    fetch_url = self.services["shock_service_url"] + "node/" + fasta_ref + \
                                "?download&seek=" + str(start) + \
                                "&length=" + str(length)

                    #fetch individual sequences
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
        else:
            raise TypeError("Invalid type! Expected KBaseGenomes.ContigSet <= 3.0 or KBaseGenomesCondensedPrototype.Assembly <= 1.0, received " + info[2])
