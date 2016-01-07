
__author__ = 'Marcin Joachimiak <mjoachimiak@lbl.gov>'
__date__ = '11/06/15'

import doekbase.data_api
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
import os

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
        if(geneinfo["aliases"] != None):
            aliases=get_aliases(geneinfo["aliases"])
            function=geneinfo["function"]
            sequence = geneinfo["amino_acid_sequence"]
            string += ">" + keys  +" " + function + " " + aliases + " " + "\n" + sequence +  "\n"
    return string

def run(ws_url='https://ci.kbase.us/services/ws/'):

    genomeref = "ReferenceGenomeAnnotations/kb|g.166819"
    genome_annotation = GenomeAnnotationAPI(services = {"workspace_service_url": ws_url}, token=os.environ.get('KB_AUTH_TOKEN'), ref=genomeref)
        
    proteins= genome_annotation.get_proteins()
    fasta = get_protein_fasta(proteins)

    outfile = '166819_prot.fasta'
    
    with open(outfile, 'w') as f:
        f.write(fasta)



if __name__ == '__main__':
    run()
