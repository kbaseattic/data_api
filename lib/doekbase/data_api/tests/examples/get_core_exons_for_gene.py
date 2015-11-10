import doekbase.data_api
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.data_api.annotation.genome_annotation import GenomeAnnotationAPI
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.core import ObjectAPI
import time

services = {"workspace_service_url": "https://ci.kbase.us/services/ws/",
            "shock_service_url": "https://ci.kbase.us/services/shock-api/"}


import os
token = os.environ["KB_AUTH_TOKEN"]

def get_core_exons(gene):
    t0 = time.time()
    listmrna=genome_annotation.get_mrna_by_gene([gene])[gene]    
    t1 = time.time()
    print "get_mrna_by_gene " , (t1-t0)
    print listmrna

    t0 = time.time()
    listcds=genome_annotation.get_cds_by_gene([gene])[gene] 
    t1 = time.time()
    print "get_cds_by_gene " , (t1-t0)   

    t0 = time.time()
    mrna_cds=genome_annotation.get_cds_by_mrna(listmrna)
    t1 = time.time()
    print "get_cds_by_mrna " , (t1-t0)

    t0 = time.time()
    gene_location=genome_annotation.get_feature_locations([gene]) 
    t1 = time.time()
    print "get_feature_locations " , (t1-t0)

    t0 = time.time()
    mrna_location=genome_annotation.get_feature_locations(listmrna) 
    t1 = time.time()
    print "get_feature_locations " , (t1-t0)

    t0 = time.time()
    cds_location=genome_annotation.get_feature_locations(listcds) 
    t1 = time.time()
    print "get_feature_locations " , (t1-t0)

    t0 = time.time()
    cds_mrna=genome_annotation.get_mrna_by_cds(listcds)
    t1 = time.time()
    print "get_mrna_by_cds " , (t1-t0)

    mRNA_count=len(listmrna)

    exons_dict = {}
    for mrna in listmrna:
        cds=mrna_cds[mrna]
        infomrna=mrna_location[mrna]
        infocds=cds_location[mrna_cds[mrna]]
        i=0
        for exon in infomrna:
            i=i+1
            start=exon['start']
            stop=start + exon['length']
            key = "" + str(start)+"_"+str(stop)
            if(bool(exons_dict.get(key))):
                exons_dict[key]  = exons_dict[key] + 1                
            else:
                exons_dict[key] = 1
            #string+=exon['contig_id']  + "\tphytozome9_0" + "\texon\t"  + str(exon['start'])+ "\t" + str(stop) + "\t.\t" +  exon['strand']+ "\t.\t" + "ID=" + mrna +".exon." + str(i)  + ";" + "Parent="+ gene+"\n"
       
    dellist = []
    for key in exons_dict:
        print key
        if(exons_dict[key] < mRNA_count):
            print "removing exon " + key
            dellist.append(key)
           
    for key in dellist:
         del exons_dict[key]

    return exons_dict       


genomeref = "PrototypeReferenceGenomes/kb|g.166828"
genome = ObjectAPI(services, token=token, ref=genomeref)
genome_annotation = GenomeAnnotationAPI(services, token, ref=genomeref)
gene='kb|g.166828.locus.15345'    
exons=get_core_exons(gene)


print "Core exons found in all mRNAs for gene "+gene
print exons
