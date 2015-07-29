import biokbase.data_api.assembly

def setup():
    pass

def teardown():
    pass

def test_assembly_api():
    print "Testing Assembly API"
    print "Fetching kb|g.140106.c.0"
    
    services = {
        "prod": {
            "workspace_service_url": "https://kbase.us/services/ws/",
            "shock_service_url": "https://kbase.us/services/shock-api/",
        },
        "ci": {
            "workspace_service_url": "https://ci.kbase.us/services/ws/",
            "shock_service_url": "https://ci.kbase.us/services/shock-api/",
        }
    }
    
    ci_assembly_api = biokbase.data_api.assembly.AssemblyAPI(services=services["ci"], ref="testCondensedGenomeV2/kb|g.140106_assembly")
    subset_contigs = ci_assembly_api.get_contigs_by_id(["kb|g.140106.c.0"])
    print subset_contigs
    assert len(subset_contigs) == 1

def test_genome_annotation_api():
    print "Testing Genome Annotation API"
    print "Fetching kb|g.140106.cds.0"

def test_taxon_api():
    print "Testing Taxon API"
    print "Fetching taxon for kb|g.140106"
    
    