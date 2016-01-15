
__author__ = 'Marcin Joachimiak <mjoachimiak@lbl.gov>'
__date__ = '11/06/15'

import doekbase.data_api
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
import os
import json

#skeleton method demoonstrating how to retrieve various data about an assembly
def contig_gc(genome_annotation, genome="kb|g.166819"):
    assembly = genome_annotation.get_assembly()
    print "genome_annotation.get_assembly"

    assembly_details = dict()
    #retrieve the contig gc content
    contig_gcs = assembly.get_contig_gc_content()
    assembly_details["contig_gcs"] = contig_gcs

    return assembly_details["contig_gcs"]

def run(ws_url='https://ci.kbase.us/services/ws/'):

    #an example KBase reference genome
    genomeref = "ReferenceGenomeAnnotations/kb|g.166819"
    #creating a new GenomeAnnotation object
    genome_annotation = GenomeAnnotationAPI(services = {"workspace_service_url": ws_url}, token=os.environ.get('KB_AUTH_TOKEN'), ref=genomeref)
         
    gc = contig_gc(genome_annotation, genomeref)

    print gc

    outfile = '166819_GC.txt'
    
    with open(outfile, 'w') as f:
        f.write(json.dumps(gc))



if __name__ == '__main__':
    run()
