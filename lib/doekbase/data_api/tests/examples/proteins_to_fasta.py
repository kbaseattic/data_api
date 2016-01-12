
__author__ = 'Marcin Joachimiak <mjoachimiak@lbl.gov>'
__date__ = '11/06/15'

import doekbase.data_api
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
import os


def get_protein_fasta(data):
    i=0
    string =""
    #for each protein in the annotation
    for keys in data:
        i=i+1
        #limit it to 3 proteins for testing
        if (i >3):
            break
        geneinfo=data[keys]

        #retrieve gene id alias, function, and peptide swquence data
        if(geneinfo["protein_aliases"] != None):
            aliases="".join(geneinfo["protein_aliases"])
            if(geneinfo["protein_function"] != None):
                function=geneinfo["protein_function"]
            sequence = geneinfo["protein_amino_acid_sequence"]
            string += ">" + keys  +" " + function + " " + aliases + " " + "\n" + sequence +  "\n"
    return string

def run(ws_url='https://ci.kbase.us/services/ws/'):

    #an example KBase reference genome
    genomeref = "ReferenceGenomeAnnotations/kb|g.166819"

    #creating a new GenomeAnnotation object
    genome_annotation = GenomeAnnotationAPI(services = {"workspace_service_url": ws_url}, token=os.environ.get('KB_AUTH_TOKEN'), ref=genomeref)
        
    #return all protein objects from this genome
    proteins= genome_annotation.get_proteins()
    #format the proteins in FASTA format
    fasta = get_protein_fasta(proteins)

    outfile = '166819_prot.fasta'
    
    with open(outfile, 'w') as f:
        f.write(fasta)



if __name__ == '__main__':
    run()
