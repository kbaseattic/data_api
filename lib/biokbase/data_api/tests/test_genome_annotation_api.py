"""
Unit tests for genome_annotation
"""
import logging
from unittest import skipUnless

from . import shared

from biokbase.data_api.genome_annotation import GenomeAnnotationAPI

_log = logging.getLogger(__name__)

genome = "PrototypeReferenceGenomes/kb|g.3899"

def setup():
    shared.setup()

@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_mrna():
    """Testing Genome Annotation API"""

    _log.info("Fetching CDS by kb|g.3899.mRNA.0, kb|g.3899.mRNA.2066, kb|g.3899.mRNA.99999999999, kb|g.3899.CDS.1")

    ci_genome_annotation_api = GenomeAnnotationAPI(services=shared.services,
                                                   ref=genome)
    #last 2 in list are purposely invalid
    subset_features = ci_genome_annotation_api.get_cds_by_mrna(["kb|g.3899.mRNA.0","kb|g.3899.mRNA.2066", "kb|g.3899.mRNA.99999999999", "kb|g.3899.CDS.1"]) 
    print subset_features 
    assert len(subset_features) == 2

@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_cds():
    """Testing Genome Annotation API"""
    print "Fetching mRNA by kb|g.3899.CDS.61899, kb|g.3899.CDS.63658, kb|g.3899.mRNA.99999999999, kb|g.3899.CDS.1" 
    ci_genome_annotation_api = GenomeAnnotationAPI(services=shared.services,
                                                   ref=genome)
    #last 2 in list are purposely invalid
    subset_features = ci_genome_annotation_api.get_mrna_by_cds(["kb|g.3899.CDS.36740","kb|g.3899.CDS.36739", "kb|g.3899.mRNA.99999999999", "kb|g.3899.CDS.1"]) 
    print subset_features 
    assert len(subset_features) == 2

@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_mrna():
    """Testing Genome Annotation API"""
    print "Fetching genes by kb|g.3899.mRNA.0, kb|g.3899.mRNA.2066, kb|g.3899.mRNA.99999999999, kb|g.3899.CDS.1" 

    ci_genome_annotation_api = GenomeAnnotationAPI(services=shared.services,
                                                   ref=genome)
    #last 2 in list are purposely invalid
    subset_features = ci_genome_annotation_api.get_gene_by_mrna(["kb|g.3899.mRNA.0","kb|g.3899.mRNA.2066", "kb|g.3899.mRNA.99999999999", "kb|g.3899.CDS.1"]) 
    print subset_features 
    assert len(subset_features) == 2

@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_children_cds_by_gene():
    """Testing Genome Annotation API"""
    print "Fetching CDS by gene kb|g.3899.locus.26937,kb|g.3899.locus.26761, kb|g.3899.mRNA.99999999999, kb|g.3899.CDS.1" 

    ci_genome_annotation_api = GenomeAnnotationAPI(services=shared.services, ref=genome)
    #last 2 in list are purposely invalid
    subset_features = ci_genome_annotation_api.get_children_cds_by_gene(["kb|g.3899.locus.26937","kb|g.3899.locus.26761", "kb|g.3899.mRNA.99999999999", "kb|g.3899.CDS.1"]) 
    print subset_features 
    assert len(subset_features) == 2

@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_children_mrna_by_gene():
    """Testing Genome Annotation API"""
    print "Fetching mRNA by gene kb|g.3899.locus.26937, kb|g.3899.locus.26761, kb|g.3899.mRNA.99999999999, kb|g.3899.CDS.1" 

    ci_genome_annotation_api = GenomeAnnotationAPI(services=shared.services, ref=genome)
    #last 2 in list are purposely invalid
    subset_features = ci_genome_annotation_api.get_children_mrna_by_gene(["kb|g.3899.locus.26937","kb|g.3899.locus.26761", "kb|g.3899.mRNA.99999999999", "kb|g.3899.CDS.1"]) 
    print subset_features 
    assert len(subset_features) == 2

@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_cds():
    """Testing Genome Annotation API"""
    print "Fetching genes by kb|g.3899.CDS.61899, kb|g.3899.CDS.63658, kb|g.3899.mRNA.99999999999, kb|g.3899.CDS.1" 
 

    ci_genome_annotation_api = GenomeAnnotationAPI(services=shared.services, ref=genome)
    #last 2 in list are purposely invalid
    subset_features = ci_genome_annotation_api.get_gene_by_cds(["kb|g.3899.CDS.36740","kb|g.3899.CDS.36739", "kb|g.3899.mRNA.99999999999", "kb|g.3899.CDS.1"]) 
    print subset_features 
    assert len(subset_features) == 2



