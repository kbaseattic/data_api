"""
Data API for Assembly entities.  This API provides methods for retrieving
summary information such as GC content, total length, external source information
as well as methods for retrieving individual contig sequences and gathering contig lengths and contig GC.
"""

# Stdlib
import abc
import itertools
import requests
import re
import string
import hashlib
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO as StringIO

# Local
from doekbase.data_api.core import ObjectAPI
from doekbase.data_api.util import PerfCollector, collect_performance

CHUNK_SIZE = 2**30

_CONTIGSET_TYPES = ['KBaseGenomes.ContigSet']
_ASSEMBLY_TYPES = ['KBaseGenomesCondensedPrototypeV2.Assembly']
TYPES = _CONTIGSET_TYPES + _ASSEMBLY_TYPES

g_stats = PerfCollector('AssemblyAPI')

class AssemblyInterface(object):
    """API for the assembled sequences associated with a Genome Annotation.
    """
    
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod    
    def get_assembly_id(self):
        """Retrieve the id for an Assembly.

        Returns:
          str: string identifier for the Assembly
        """
        pass

    @abc.abstractmethod    
    def get_genome_annotations(self):
        """Retrieve the GenomeAnnotations that refer to this Assembly.
        
        Returns:
          list<GenomeAnnotationAPI>: List of GenomeAnnotationAPI objects
        """
        pass
    
    @abc.abstractmethod    
    def get_external_source_info(self):
        """Retrieve the external source information for this Assembly.
        
        Returns:
          str: string identifier for the Assembly
        """
        pass

    @abc.abstractmethod    
    def get_stats(self):
        """Retrieve the derived statistical information about this Assembly.
        
        Returns:
          dict: Statistics with the following keys and values:

            gc_content : float
                proportion of guanine (G) and cytosine (C) content
            dna_size : int
                total length of all dna sequences
            num_contigs : int
                total number of contiguous sequences
        """
        pass

    @abc.abstractmethod    
    def get_number_contigs(self):
        """Retrieve the number of contiguous sequences in this Assembly.
        
        Returns:
          int
        """
        pass

    @abc.abstractmethod    
    def get_gc_content(self):
        """Retrieve the total GC content for this Assembly.
        
        Returns:
          float: Proportion of GC content, 0 <= x <= 1.
        """
        pass

    @abc.abstractmethod    
    def get_dna_size(self):
        """Retrieve the total DNA size for this Assembly.
        
        Returns:
          int: Total DNA size
        """
        pass

    @abc.abstractmethod    
    def get_contig_lengths(self, contig_id_list=None):
        """Retrieve the length for every contiguous sequence.
        
        Returns:
          dict<str,int>: Mapping of sequence identifiers to lengths.
        """
        pass

    @abc.abstractmethod    
    def get_contig_gc_content(self, contig_id_list=None):
        """Retrieve the total GC content for each contiguous sequence
        of this Assembly.
        
        Returns:
          dict<str,float>: Mapping of sequence identifiers to GC content.
        """
        pass

    @abc.abstractmethod    
    def get_contig_ids(self):
        """Retrieve the ids for every contiguous sequence in this Assembly.
        
        Returns:
          list<str>: Sequence identifiers
        """
        pass

    @abc.abstractmethod    
    def get_contigs(self, contig_id_list=None):
        """Retrieve contiguous sequences from this Assembly by id.
        
        Args:
          contig_id_list: list<str>
        Returns:
          dict<str,dict>: dictionary of contigs, with contig id as key
          and each value itself a dict with the following key/value pairs:

          contig_id : str
            the contig identifier
          length : integer
            length of the contig
          md5 : string
            hex-digest of MD5 hash of the contig's contents,
          name : string
            name of the contig
          description : string
            description of the contig
          is_complete : int
             0 if this contig is complete, 1 otherwise
          is_circular : int
             0 or 1
          sequence : string
             actual contents of the sequence for this contig
        """
        pass



class AssemblyAPI(ObjectAPI, AssemblyInterface):
    def __init__(self, services, token, ref):
        """Defines which types and type versions that are legal.
        """
        super(AssemblyAPI, self).__init__(services, token, ref)
        
        is_assembly_type = self._typestring.split('-')[0] in _ASSEMBLY_TYPES
        is_contigset_type = self._typestring.split('-')[0] in _CONTIGSET_TYPES
        
        if not (is_assembly_type or is_contigset_type):
            raise TypeError("Invalid type! Expected one of {0}, received {1}".format(TYPES, self._typestring))

        if is_assembly_type:
            self.proxy = _Prototype(services, token, ref)
        else:
            self.proxy = _KBaseGenomes_ContigSet(services, token, ref)
    
    def get_assembly_id(self):
        return self.proxy.get_assembly_id()

    def get_genome_annotations(self):
        return self.proxy.get_genome_annotations()
    
    def get_external_source_info(self):
        return self.proxy.get_external_source_info()

    def get_stats(self):
        return self.proxy.get_stats()

    def get_number_contigs(self):
        return self.proxy.get_number_contigs()

    def get_gc_content(self):
        return self.proxy.get_gc_content()

    def get_dna_size(self):
        return self.proxy.get_dna_size()

    def get_contig_lengths(self, contig_id_list=None):
        return self.proxy.get_contig_lengths(contig_id_list)

    def get_contig_gc_content(self, contig_id_list=None):
        return self.proxy.get_contig_gc_content(contig_id_list)

    def get_contig_ids(self):
        return self.proxy.get_contig_ids()

    def get_contigs(self, contig_id_list=None):
        return self.proxy.get_contigs(contig_id_list)


class _KBaseGenomes_ContigSet(ObjectAPI, AssemblyInterface):
    def __init__(self, services, token, ref):
        super(_KBaseGenomes_ContigSet, self).__init__(services, token, ref)
        self._gc_pattern = re.compile(r'g|G|c|C')

    def get_assembly_id(self):
        return self.get_data_subset(path_list=["id"])["id"]
    
    def get_genome_annotations(self):
        from doekbase.data_api.annotation.genome_annotation import TYPES as genome_annotation_types
        from doekbase.data_api.annotation.genome_annotation import GenomeAnnotationAPI
        annotations = list()
        referrers = self.get_referrers()
        for x in referrers:
            if x.split("-")[0] in genome_annotation_types:
                for ref in referrers[x]:
                    annotations.append(
                        GenomeAnnotationAPI(self.services, self._token, ref)
                    )
        return annotations
    
    def get_external_source_info(self):
        data = self.get_data_subset(path_list=["source","source_id"])
        
        output = dict()
        output["external_source"] = data["source"]
        output["external_source_id"] = data["source_id"]
        output["external_source_origination_date"] = "Unknown"
        
        return output

    def get_stats(self):
        contigs = self.get_data()["contigs"]

        total_gc = 0
        for i, c in enumerate(contigs):
            total_gc += self._sequence_gc(i, c["sequence"])
        
        total_length = 0
        
        for x in contigs:
            if "length" in x:
                total_length += x["length"]
            else:
                total_length += len(x["sequence"])

        data = dict()
        data["gc_content"] = total_gc/(total_length*1.0)
        data["dna_size"] = total_length
        data["num_contigs"] = len(contigs)            
        
        return data

    def get_number_contigs(self):
        return len(self.get_data()["contigs"])

    def get_gc_content(self):
        contigs = self.get_data()["contigs"]
        
        pattern = re.compile(r'g|G|c|C')
        
        total_gc = 0
        total_length = 0
        for i, c in enumerate(contigs):
            if "length" in c:
                total_length += c["length"]
            else:
                total_length += len(c["sequence"])
            
            total_gc += self._sequence_gc(i, c["sequence"])
        
        return total_gc/(total_length*1.0)

    def get_dna_size(self):
        contigs = self.get_data()["contigs"]
        return sum([c["length"] for c in contigs])

    def get_contig_lengths(self, contig_id_list=None):
        contigs = self.get_data()["contigs"]        
        
        if contig_id_list is None:        
            contig_id_list = [c["id"] for c in contigs]

        contig_lengths = dict()
        for c in contigs:
            if c["id"] in contig_id_list:
                if "length" in c:
                    contig_lengths[c["id"]] = c["length"]
                else:
                    contig_lengths[c["id"]] = len(c["sequence"])
        
        return contig_lengths
        
    def get_contig_gc_content(self, contig_id_list=None):
        contigs = self.get_data()["contigs"]
        
        contigs_gc = dict()
        
        if contig_id_list is None:
            contig_id_list = [c["id"] for c in contigs]
                    
        for i, c in enumerate(contigs):
            if c["id"] in contig_id_list:
                if "length" in c:
                    length = c["length"]
                else:
                    length = len(c["sequence"])

                contigs_gc[c["id"]] = (1. * self._sequence_gc(i, c['sequence'])
                                       / length)
        
        return contigs_gc

    def get_contig_ids(self):
        contigs = self.get_data()["contigs"]
        return [c["id"] for c in contigs]

    @collect_performance(g_stats, prefix='old.')
    def get_contigs(self, contig_id_list=None):
        contigs = dict()

        raw_contigs = self.get_data()["contigs"]

        make_md5 = lambda x: hashlib.md5(x["sequence"].upper()).hexdigest()

        for i, c in enumerate(raw_contigs):
            if contig_id_list and c['id'] not in contig_id_list:
                continue
            cid = {'contig_id': c['id'],
                   'sequence': c['sequence'],
                   'length': c.get('length', None) or len(c['sequence']),
                   'md5': c.get('md5', None) or make_md5(c),
                   'name': c.get('name', None),
                   'description': c.get('description', None),
                   'is_complete': c.get('complete', 0),
                   'is_circular': c.get('replicon_geometry','Unkown')
                   }
            #contigs[c["id"]] = dict()
            #contigs[c["id"]]["contig_id"] = c["id"]
            #contigs[c["id"]]["sequence"] = c["sequence"]
            # if "length" in c:
            #     contigs[c["id"]]["length"] = c["length"]
            # else:
            #     contigs[c["id"]]["length"] = len(c["sequence"])
            #
            # if "md5" in c:
            #     contigs[c["id"]]["md5"] = c["md5"]
            # else:
            #     contigs[c["id"]]["md5"] = hashlib.md5(c["sequence"].upper()).hexdigest()
            # if "name" in c:
            #     contigs[c["id"]]["name"] = c["name"]
            # else:
            #     contigs[c["id"]]["name"] = None
            #
            # if "description" in c:
            #     contigs[c["id"]]["description"] = c["description"]
            # else:
            #     contigs[c["id"]]["description"] = None
            #
            # if "complete" in c:
            #     contigs[c["id"]]["is_complete"] = c["complete"]
            # else:
            #     contigs[c["id"]]["is_complete"] = 0
            #
            # if "replicon_geometry" in c:
            #     contigs[c["id"]]["is_circular"] = c["replicon_geometry"]
            # else:
            #     contigs[c["id"]]["is_circular"] = "Unknown"

            gc_count = self._sequence_gc(i, c['sequence'])
            cid['gc_content'] = gc_count / cid['length'] * 1.0

            contigs[c['id']] = cid

        return contigs            

    def _sequence_gc(self, index, sequence):
        """Get GC content for a sequence.

            May refer to a cached value, if the cache is available.
        """
        self._current_sequence = sequence
        name = 'gc-{:d}'.format(index)
        r =  self._cache.get_derived_data(self._calc_sequence_gc, name)
        return r

    def _calc_sequence_gc(self):
        """Calculate "G/C Content" by counting G's and C's in the
           sequence and dividing the total by the sequence length.
        """
        matches = re.finditer(self._gc_pattern, self._current_sequence)
        return sum(itertools.imap(lambda x: 1, matches))

class _Prototype(ObjectAPI, AssemblyInterface):
    def __init__(self, services, token, ref):
        super(_Prototype, self).__init__(services, token, ref)

    def get_assembly_id(self):
        return self.get_data_subset(path_list=["assembly_id"])["assembly_id"]        

    def get_genome_annotations(self):
        import doekbase.data_api.annotation.genome_annotation
        
        referrers = self.get_referrers()

        annotations = list()
        for object_type in referrers:
            if object_type.split('-')[0] in doekbase.data_api.annotation.genome_annotation.TYPES:
                for x in referrers[object_type]:
                    annotations.append(doekbase.data_api.annotation.genome_annotation.GenomeAnnotationAPI(
                        self.services, self._token, ref=x))
        
        return annotations
    
    def get_external_source_info(self):
        return self.get_data_subset(path_list=["external_source",
                                               "external_source_id",
                                               "external_source_origination_date"])

    def get_stats(self):
        return self.get_data_subset(path_list=["gc_content","dna_size","num_contigs"])            

    def get_number_contigs(self):
        return self.get_data_subset(path_list=["num_contigs"])["num_contigs"]

    def get_gc_content(self):
        return self.get_data_subset(path_list=["gc_content"])["gc_content"]

    def get_dna_size(self):
        return self.get_data_subset(path_list=["dna_size"])["dna_size"]

    def get_contig_lengths(self, contig_id_list=None):
        if contig_id_list is None:        
            contigs = self.get_data()["contigs"]        
            return {c: contigs[c]["length"] for c in contigs}
        else:        
            contigs = self.get_data_subset(["contigs/" + x for x in contig_id_list])["contigs"]        
            return {c: contigs[c]["length"] for c in contig_id_list}

    def get_contig_gc_content(self, contig_id_list=None):
        if contig_id_list is None:        
            contigs = self.get_data()["contigs"]        
            return {c: contigs[c]["gc_content"] for c in contigs}
        else:        
            contigs = self.get_data_subset(["contigs/" + x for x in contig_id_list])["contigs"]        
            return {c: contigs[c]["gc_content"] for c in contig_id_list}

    def get_contig_ids(self):
        contigs = self.get_data()["contigs"]
        return [contigs[c]["contig_id"] for c in contigs]

    @collect_performance(g_stats, prefix='new.')
    def get_contigs(self, contig_id_list=None):
        data = self.get_data()

        if contig_id_list is None:
            contig_id_list = data["contigs"].keys()
        
        num_contigs = len(contig_id_list)
        total_contigs = data["num_contigs"]
        fasta_ref = data["fasta_handle_ref"]
        contigs = data["contigs"]

        copy_keys = ["contig_id", "length", "md5", "name", "description", "is_complete", "is_circular"]

        header = dict()
        header["Authorization"] = "Oauth {0}".format(self._token)

        if num_contigs > total_contigs/3 or num_contigs == 0:
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
                    if k in contigs[c]:
                        outContigs[c][k] = contigs[c][k]

                outContigs[c]["sequence"] = sequence_data[contigs[c]["start_position"]:contigs[c]["start_position"] + \
                                            contigs[c]["num_bytes"]].translate(None, string.whitespace)
        else:                
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
                    if k in contigs[c]:
                        outContigs[c][k] = contigs[c][k]

                outContigs[c]["sequence"] = fetch_contig(contigs[c]["start_position"],contigs[c]["num_bytes"])

        return outContigs
