def setup():
    pass

def teardown():
    pass

def test_assembly_api():
    print "Testing Assembly API"
    print "Fetching kb|g.3157.c.0"

    from biokbase.data_api.assembly import AssemblyAPI

    services = {
        "workspace_service_url": "https://ci.kbase.us/services/ws/",
        "shock_service_url": "https://ci.kbase.us/services/shock-api/",
    }
        
    ci_assembly_api = AssemblyAPI(services=services, ref="PrototypeReferenceGenomes/kb|g.3157_assembly")
    subset_contigs = ci_assembly_api.get_contigs_by_id(["kb|g.3157.c.0"])
    print subset_contigs
    assert len(subset_contigs) == 1

def test_genome_annotation_api():
    print "Testing Genome Annotation API"
    print "Fetching kb|g.3157.peg.0"

    from biokbase.data_api.genome_annotation import GenomeAnnotationAPI

    services = {
        "workspace_service_url": "https://ci.kbase.us/services/ws/",
        "shock_service_url": "https://ci.kbase.us/services/shock-api/",
    }
    
    ci_genome_annotation_api = GenomeAnnotationAPI(services=services, ref="PrototypeReferenceGenomes/kb|g.3157")
    subset_features = ci_genome_annotation_api.get_features_by_id(["kb|g.3157.peg.0"])
    print subset_features
    assert len(subset_features) == 1

def test_taxon_api():
    print "Testing Taxon API"
    print "Fetching taxon for kb|g.3157"

    from biokbase.data_api.genome_annotation import GenomeAnnotationAPI

    services = {
        "workspace_service_url": "https://ci.kbase.us/services/ws/",
        "shock_service_url": "https://ci.kbase.us/services/shock-api/",
    }
    
    ci_taxon_api = GenomeAnnotationAPI(services=services, ref="PrototypeReferenceGenomes/kb|g.3157").get_taxon()
    scientific_name = ci_taxon_api.get_scientific_name()
    print scientific_name
    assert len(scientific_name) > 0
    