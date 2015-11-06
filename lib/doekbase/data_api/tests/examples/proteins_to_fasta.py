import doekbase.data_api
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.data_api.annotation.genome_annotation import GenomeAnnotationAPI
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.core import ObjectAPI


services = {"workspace_service_url": "https://ci.kbase.us/services/ws/",
            "shock_service_url": "https://ci.kbase.us/services/shock-api/"}


import os
token = os.environ["KB_AUTH_TOKEN"]


def get_aliases (data):
    string=""
    for keys in data:
        string += str(keys) + " "
    return string

def get_protein_fasta(data):
    i=0
    string =""
    for keys in data:
        i=i+1
        if (i >3):
            break
        geneinfo=data[keys]
        aliases=get_aliases(geneinfo["aliases"])
        function=geneinfo["function"]
        sequence = geneinfo["amino_acid_sequence"]
        string += ">" + keys  +" " + function + " " + aliases + " " + "\n" + sequence +  "\n"
    return string




genomeref = "PrototypeReferenceGenomes/kb|g.3899"
genome = ObjectAPI(services, token=token, ref=genomeref)
genome_annotation = GenomeAnnotationAPI(services, token, ref=genomeref)
    
proteins= genome_annotation.get_proteins()
fasta = get_protein_fasta(proteins)

outfile = '3899_prot.fasta'
print outfile
with open(outfile, 'w') as f:
    f.write(fasta)
