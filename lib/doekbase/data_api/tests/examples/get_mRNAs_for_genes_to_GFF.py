# -*- coding: utf-8 -*-

__author__ = 'Marcin Joachimiak <mjoachimiak@lbl.gov>'
__date__ = '11/06/15'

import doekbase.data_api
from doekbase.data_api.annotation.genome_annotation import GenomeAnnotationAPI
import time
import os


def get_gff(gene,genome_annotation):
    t0 = time.time()
    listmrna=genome_annotation.get_mrna_by_gene([gene])[gene]    
    t1 = time.time()
    print "get_mrna_by_gene " , (t1-t0), "s"

    t0 = time.time()
    listcds=genome_annotation.get_cds_by_gene([gene])[gene] 
    t1 = time.time()
    print "get_cds_by_gene " , (t1-t0), "s"   

    t0 = time.time()
    mrna_cds=genome_annotation.get_cds_by_mrna(listmrna)
    t1 = time.time()
    print "get_cds_by_mrna " , (t1-t0), "s"

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

    t0 = time.time()
    cds_mrna=genome_annotation.get_mrna_by_cds(listcds)
    t1 = time.time()
    print "get_mrna_by_cds " , (t1-t0), "s"
    
    string=""
    for x in gene_location:
        info=gene_location[x][0]
        stop=info['start'] + info['length']
        string+=info['contig_id']  + "\tblah" + "\tgene\t"  + str(info['start']) + "\t" + str(stop) + "\t.\t" +  info['strand']+ "\t.\t" + "ID=" + x + ";" + "Name="+ x +"\n"
        
    for mrna in listmrna:
        cds=mrna_cds[mrna]
        infomrna=mrna_location[mrna]
        infocds=cds_location[mrna_cds[mrna]]
        i=0
        for exon in infomrna:
            i=i+1
            stop=exon['start'] + exon['length']
            string+=exon['contig_id']  + "\tblah" + "\texon\t"  + str(exon['start'])+ "\t" + str(stop) + "\t.\t" +  exon['strand']+ "\t.\t" + "ID=" + mrna +".exon." + str(i)  + ";" + "Parent="+ gene+"\n"
        j=0
        for cds in infocds:
            j=j+1
            stop=cds['start'] + cds['length']
            string+=cds['contig_id']  + "\tblah" + "\tCDS\t"  + str(cds['start']) + "\t" + str(stop) + "\t.\t" +  cds['strand']+ "\t.\t" + "ID="  + mrna_cds[mrna]  +".CDS." + str(j) + ";" + "Parent="+  mrna+"\n"
    return string       


def run(ws_url='https://ci.kbase.us/services/ws/'):

    genomeref = "PrototypeReferenceGenomes/kb|g.166828"
    genome_annotation = GenomeAnnotationAPI(services = {"workspace_service_url": ws_url}, token=os.environ.get('KB_AUTH_TOKEN'), ref=genomeref)
    genes=['kb|g.166828.locus.15345','kb|g.166828.locus.15346','kb|g.166828.locus.15347']

    gffdata=""
    for s in genes:
        gffdata+=get_gff(s,genome_annotation)

    outfile = 'g.166828.locus.15345_15346_15347.gff'
    print outfile
    with open(outfile, 'w') as f:
        f.write(gffdata)



if __name__ == '__main__':
    run()
