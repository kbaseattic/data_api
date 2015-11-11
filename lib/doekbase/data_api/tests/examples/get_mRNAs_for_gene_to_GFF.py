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

def get_gff(gene):
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
    
    string=""
    for x in gene_location:
        info=gene_location[x][0]
        stop=info['start'] + info['length']
        string+=info['contig_id']  + "\tphytozome9_0" + "\tgene\t"  + str(info['start']) + "\t" + str(stop) + "\t.\t" +  info['strand']+ "\t.\t" + "ID=" + x + ";" + "Name="+ x +"\n"
        
    for mrna in listmrna:
        cds=mrna_cds[mrna]
        infomrna=mrna_location[mrna]
        infocds=cds_location[mrna_cds[mrna]]
        i=0
        for exon in infomrna:
            i=i+1
            stop=exon['start'] + exon['length']
            string+=exon['contig_id']  + "\tphytozome9_0" + "\texon\t"  + str(exon['start'])+ "\t" + str(stop) + "\t.\t" +  exon['strand']+ "\t.\t" + "ID=" + mrna +".exon." + str(i)  + ";" + "Parent="+ gene+"\n"
        j=0
        for cds in infocds:
            j=j+1
            stop=cds['start'] + cds['length']
            string+=cds['contig_id']  + "\tphytozome9_0" + "\tCDS\t"  + str(cds['start']) + "\t" + str(stop) + "\t.\t" +  cds['strand']+ "\t.\t" + "ID="  + mrna_cds[mrna]  +".CDS." + str(j) + ";" + "Parent="+  mrna+"\n"
    return string       


genomeref = "PrototypeReferenceGenomes/kb|g.166828"
genome = ObjectAPI(services, token=token, ref=genomeref)
genome_annotation = GenomeAnnotationAPI(services, token, ref=genomeref)
gene='kb|g.166828.locus.15345'    
gffdata=get_gff(gene)


outfile = 'g.166828.locus.15345.gff'
print outfile
with open(outfile, 'w') as f:
    f.write(gffdata)
