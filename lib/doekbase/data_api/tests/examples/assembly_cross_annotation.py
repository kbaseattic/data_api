
__author__ = 'Marcin Joachimiak <mjoachimiak@lbl.gov>'
__date__ = '11/06/15'

import doekbase.data_api
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
import os


def contig_gc(genome_annotation, genome="kb|g.166819"):
    assembly = genome_annotation.get_assembly()
    print "genome_annotation.get_assembly"

    #get assembly info
    assembly_details = dict()
    assembly_details["number_of_contigs"] = assembly.get_number_contigs()

    return assembly.get_contig_gc_content()

def run(ws_url='https://ci.kbase.us/services/ws/'):

    genomeref = "ReferenceGenomeAnnotations/kb|g.166819"
    genome_annotation = GenomeAnnotationAPI(services = {"workspace_service_url": ws_url}, token=os.environ.get('KB_AUTH_TOKEN'), ref=genomeref)
         
    gc = contig_gc(proteins)

    outfile = '166819_GC.txt'
    
    with open(outfile, 'w') as f:
        f.write(gc)



if __name__ == '__main__':
    run()
