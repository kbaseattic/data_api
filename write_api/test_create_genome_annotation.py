#!/usr/bin/env python

if __name__ == "__main__":
    import os
    import json

    from doekbase.data_api.annotation.genome_annotation.api import create_genome_annotation

    # read in exchange file
    filename = "8020_39_1.json"
    with open(filename, 'r') as sample:
        data = json.loads(sample.read())

    services = {
        "workspace_service_url": "https://ci.kbase.us/services/ws/",
        "shock_service_url": "https://ci.kbase.us/services/shock-api/",
        "handle_service_url": "https://ci.kbase.us/services/handle_service/"
    }

    token = os.environ['KB_AUTH_TOKEN']

    results = create_genome_annotation(services,
                                       token,
                                       888888,
                                       "Test",
                                       data['features'],
                                       data['proteins'],
                                       data['assembly_ref'],
                                       data['taxon_ref'],
                                       {"test": ""})

    protein_container = results[0]
    pc_filename = "8020_39_1_pc.json"
    with open(pc_filename, 'w') as pc:
        pc.write(json.dumps(protein_container))

#    print "Warnings: {}".format(results[1])
    feature_containers = results[2]
    for feature_type in feature_containers:
        fc_filename = "8020_39_1_{}_fc.json".format(feature_type)
        with open(fc_filename, 'w') as fc:
            fc.write(json.dumps(feature_containers[feature_type]))
#    print feature_alias_lookup

    print "Finished"
