#!/usr/bin/env python

if __name__ == "__main__":
    import os
    import json
    from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI

    services = {
        "workspace_service_url": "https://ci.kbase.us/services/ws/",
        "shock_service_url": "https://ci.kbase.us/services/shock-api/",
        "handle_service_url": "https://ci.kbase.us/services/handle_service/"
    }

    refs = ['8020/39/1', 
            '8020/103/1', 
            '8020/69/1', 
            '8020/58/1', 
            '8020/11/1',
            '8020/27/1',
            '8020/81/1']

    for r in refs:
        data = {}
        ga = GenomeAnnotationAPI(services, os.environ['KB_AUTH_TOKEN'], r)
        scientific_name = ga.get_taxon().get_scientific_name()
        filename = r.replace("/","_") + ".json"
        data['features'] = ga.get_features()        
        data['proteins'] = ga.get_proteins()
        data['assembly_ref'] = ga.get_assembly(ref_only=True)
        data['taxon_ref'] = ga.get_taxon(ref_only=True)
        f = open(filename, 'w')
        f.write(json.dumps(data))
        f.close()
