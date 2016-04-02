import doekbase.data_api
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
#from doekbase.data_api.annotation.genome_annotation import GenomeAnnotationAPI
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.core import ObjectAPI
import time
import os

services = {"workspace_service_url": "https://ci.kbase.us/services/ws/",
            "shock_service_url": "https://ci.kbase.us/services/shock-api/"}


def get_gff(gene, genome_annotation):

    #retrieve pairwise inter-feature relationships between geness, mRNAs, cds
    #the below section of code has method timings torecord performance   
    t0 = time.time()
    listmrna=genome_annotation.get_mrna_by_gene([gene])[gene]    
    t1 = time.time()
    print "get_mrna_by_gene " , (t1-t0)

    t0 = time.time()
    listcds=genome_annotation.get_cds_by_gene([gene])[gene] 
    t1 = time.time()
    print "get_cds_by_gene " , (t1-t0)   

    t0 = time.time()
    mrna_cds=genome_annotation.get_cds_by_mrna(listmrna)
    t1 = time.time()
    print "get_cds_by_mrna " , (t1-t0)

    t0 = time.time()
    cds_mrna=genome_annotation.get_mrna_by_cds(listcds)
    t1 = time.time()
    print "get_mrna_by_cds " , (t1-t0)


    #retrieve locations for genes, mRNAs, and cds
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

    
    string=""
    #output the gene data
    for x in gene_location:
        info=gene_location[x][0]
        stop=info['start'] + info['length']
        string+=info['contig_id']  + "\tphytozome9_0" + "\tgene\t"  + str(info['start']) + "\t" + str(stop) + "\t.\t" +  info['strand']+ "\t.\t" + "ID=" + x + ";" + "Name="+ x +"\n"
        
    #output the mRNA data
    for mrna in listmrna:
        cds=mrna_cds[mrna]
        infomrna=mrna_location[mrna]
        infocds=cds_location[mrna_cds[mrna]]
        i=0
        #output exon gene data
        for exon in infomrna:
            i=i+1
            stop=exon['start'] + exon['length']
            string+=exon['contig_id']  + "\tphytozome9_0" + "\texon\t"  + str(exon['start'])+ "\t" + str(stop) + "\t.\t" +  exon['strand']+ "\t.\t" + "ID=" + mrna +".exon." + str(i)  + ";" + "Parent="+ gene+"\n"
        j=0
        #output the cds data
        for cds in infocds:
            j=j+1
            stop=cds['start'] + cds['length']
            string+=cds['contig_id']  + "\tphytozome9_0" + "\tCDS\t"  + str(cds['start']) + "\t" + str(stop) + "\t.\t" +  cds['strand']+ "\t.\t" + "ID="  + mrna_cds[mrna]  +".CDS." + str(j) + ";" + "Parent="+  mrna+"\n"
    return string       

def run(ws_url='https://ci.kbase.us/services/ws/'):
    #an example KBase reference genome
    genomeref = "ReferenceGenomeAnnotations/kb|g.166819"
    #instantiate a new genome annotation API
    genome_annotation = GenomeAnnotationAPI(services = {"workspace_service_url": ws_url}, token=os.environ.get('KB_AUTH_TOKEN'), ref=genomeref)
    #pick the first locus
    gene='kb|g.166819.locus.1'    
    #pick the first locus
    gffdata=get_gff(gene, genome_annotation)

    outfile = 'g.166819.locus.1.gff'
    print outfile
    with open(outfile, 'w') as f:
        f.write(gffdata)
