def test_get_cds_by_mrna():
    print "Testing Genome Annotation API" 
    print "Fetching CDS by kb|g.3899.mRNA.0, kb|g.3899.mRNA.2066, kb|g.3899.mRNA.99999999999, kb|g.3899.CDS.1" 
 
    from biokbase.data_api.genome_annotation import GenomeAnnotationAPI 
 
    services = { 
        "workspace_service_url": "https://ci.kbase.us/services/ws/", 
        "shock_service_url": "https://ci.kbase.us/services/shock-api/", 
    } 
 
    ci_genome_annotation_api = GenomeAnnotationAPI(services=services, ref="PrototypeReferenceGenomes/kb|g.3899") 
    #last 2 in list are purposely invalid
    subset_features = ci_genome_annotation_api.get_cds_by_mrna(["kb|g.3899.mRNA.0","kb|g.3899.mRNA.2066", "kb|g.3899.mRNA.99999999999", "kb|g.3899.CDS.1"]) 
    print subset_features 
    assert len(subset_features) == 2





def test_get_mrna_by_cds():
    print "Testing Genome Annotation API" 
    print "Fetching mRNA by kb|g.3899.CDS.61899, kb|g.3899.CDS.63658, kb|g.3899.mRNA.99999999999, kb|g.3899.CDS.1" 
 
    from biokbase.data_api.genome_annotation import GenomeAnnotationAPI 
 
    services = { 
        "workspace_service_url": "https://ci.kbase.us/services/ws/", 
        "shock_service_url": "https://ci.kbase.us/services/shock-api/", 
    } 
 
    ci_genome_annotation_api = GenomeAnnotationAPI(services=services, ref="PrototypeReferenceGenomes/kb|g.3899") 
    #last 2 in list are purposely invalid
    subset_features = ci_genome_annotation_api.get_mrna_by_cds(["kb|g.3899.CDS.36740","kb|g.3899.CDS.36739", "kb|g.3899.mRNA.99999999999", "kb|g.3899.CDS.1"]) 
    print subset_features 
    assert len(subset_features) == 2



def test_get_gene_by_mrna():
    print "Testing Genome Annotation API" 
    print "Fetching genes by kb|g.3899.mRNA.0, kb|g.3899.mRNA.2066, kb|g.3899.mRNA.99999999999, kb|g.3899.CDS.1" 
 
    from biokbase.data_api.genome_annotation import GenomeAnnotationAPI 
 
    services = { 
        "workspace_service_url": "https://ci.kbase.us/services/ws/", 
        "shock_service_url": "https://ci.kbase.us/services/shock-api/", 
    } 
 
    ci_genome_annotation_api = GenomeAnnotationAPI(services=services, ref="PrototypeReferenceGenomes/kb|g.3899") 
    #last 2 in list are purposely invalid
    subset_features = ci_genome_annotation_api.get_gene_by_mrna(["kb|g.3899.mRNA.0","kb|g.3899.mRNA.2066", "kb|g.3899.mRNA.99999999999", "kb|g.3899.CDS.1"]) 
    print subset_features 
    assert len(subset_features) == 2





def test_get_gene_by_cds():
    print "Testing Genome Annotation API" 
    print "Fetching genes by kb|g.3899.CDS.61899, kb|g.3899.CDS.63658, kb|g.3899.mRNA.99999999999, kb|g.3899.CDS.1" 
 
    from biokbase.data_api.genome_annotation import GenomeAnnotationAPI 
 
    services = { 
        "workspace_service_url": "https://ci.kbase.us/services/ws/", 
        "shock_service_url": "https://ci.kbase.us/services/shock-api/", 
    } 
 
    ci_genome_annotation_api = GenomeAnnotationAPI(services=services, ref="PrototypeReferenceGenomes/kb|g.3899") 
    #last 2 in list are purposely invalid
    subset_features = ci_genome_annotation_api.get_gene_by_cds(["kb|g.3899.CDS.36740","kb|g.3899.CDS.36739", "kb|g.3899.mRNA.99999999999", "kb|g.3899.CDS.1"]) 
    print subset_features 
    assert len(subset_features) == 2



