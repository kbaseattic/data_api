
__author__ = 'Marcin Joachimiak <mjoachimiak@lbl.gov>'
__date__ = '11/06/15'

import doekbase.data_api
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
import time
import os

#method to return the core exons for a  gene locus, namely all exons found in all mRNA from that locus
def get_core_exons(gene, genome_annotation):

    #retrieve pairwise inter-feature relationships between geness, mRNAs, cds
    #the below section of code has method timings torecord performance
    t0 = time.time()
    listmrna=genome_annotation.get_mrna_by_gene([gene])[gene]    
    t1 = time.time()
    print "get_mrna_by_gene " , (t1-t0), "s"
    print listmrna

    t0 = time.time()
    listcds=genome_annotation.get_cds_by_gene([gene])[gene] 
    t1 = time.time()
    print "get_cds_by_gene " , (t1-t0), "s"   

    t0 = time.time()
    mrna_cds=genome_annotation.get_cds_by_mrna(listmrna)
    t1 = time.time()
    print "get_cds_by_mrna " , (t1-t0), "s"

    t0 = time.time()
    cds_mrna=genome_annotation.get_mrna_by_cds(listcds)
    t1 = time.time()
    print "get_mrna_by_cds " , (t1-t0), "s"


    #retrieve locations for genes, mRNAs, and cds
    t0 = time.time()
    gene_location=genome_annotation.get_feature_locations([gene]) 
    t1 = time.time()
    print "get_feature_locations " , (t1-t0), "s"

    t0 = time.time()
    mrna_location=genome_annotation.get_feature_locations(listmrna) 
    t1 = time.time()
    print "get_feature_locations " , (t1-t0), "s"

    t0 = time.time()
    cds_location=genome_annotation.get_feature_locations(listcds) 
    t1 = time.time()
    print "get_feature_locations " , (t1-t0), "s"

    

    mRNA_count=len(listmrna)

    exons_dict = {}
    #for all retrieve mRNA
    for mrna in listmrna:
        cds=mrna_cds[mrna]
        infomrna=mrna_location[mrna]
        infocds=cds_location[mrna_cds[mrna]]
        i=0
        #for all exons i the current mRNA
        for exon in infomrna:
            i=i+1
            start=exon['start']
            stop=start + exon['length']
            #create exon key based on start/stop coordinates
            key = "" + str(start)+"_"+str(stop)
            #if key exists increment value by 1
            if(bool(exons_dict.get(key))):
                exons_dict[key]  = exons_dict[key] + 1                
            #otherwise create key-value
            else:
                exons_dict[key] = 1
            #string+=exon['contig_id']  + "\tphytozome9_0" + "\texon\t"  + str(exon['start'])+ "\t" + str(stop) + "\t.\t" +  exon['strand']+ "\t.\t" + "ID=" + mrna +".exon." + str(i)  + ";" + "Parent="+ gene+"\n"
       
    dellist = []
    #for all exons
    for key in exons_dict:
        print key
        #if number of exons less than number of mRNAs, mark exon for deletion
        if(exons_dict[key] < mRNA_count):
            print "removing non-core exon " + key
            dellist.append(key)
           
    #delete non-core exons
    for key in dellist:
         del exons_dict[key]

    return exons_dict       


def run(ws_url='https://ci.kbase.us/services/ws/'):
    #use a KBase reference genome
    genomeref = "ReferenceGenomeAnnotations/kb|g.166819"
    #instantiate a new genome annotation API
    genome_annotation = GenomeAnnotationAPI(services = {"workspace_service_url": ws_url}, token=os.environ.get('KB_AUTH_TOKEN'), ref=genomeref)
    #pick first locus
    gene='kb|g.166819.locus.1'
    #retriee core exons for locus
    exons=get_core_exons(gene, genome_annotation)

    print "Core exon(s) found in all mRNAs for gene "+gene
    print exons



if __name__ == '__main__':
    run()
