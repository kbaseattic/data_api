#!/usr/bin/env python

if __name__ == "__main__":
    import os
    import json
    import datetime

    from doekbase.data_api.annotation.genome_annotation.api import create_genome_annotation

    services = {
        "workspace_service_url": "https://ci.kbase.us/services/ws/",
        "shock_service_url": "https://ci.kbase.us/services/shock-api/",
        "handle_service_url": "https://ci.kbase.us/services/handle_service/"
    }

    token = os.environ['KB_AUTH_TOKEN']

    test_organisms = {"Saccharomyces cerevisiae S288c": "8020_103_1.json",
                      "Apple mosaic virus": "8020_69_1.json",
                      "Red Algae 10D": "8020_39_1.json",
                      "Arabidopsis thaliana Ensembl": "8020_11_1.json",
                      "Arabidopsis thaliana Ensembl (chromosome 2 only)": "8020_58_1.json",
                      "E.coli K-12 substr. MG1655": "8020_27_1.json"}

    for t in test_organisms:
        start = datetime.datetime.utcnow()

        print "creating JSON files for {}".format(t)

        # read in exchange file
        with open(test_organisms[t], 'r') as sample:
            data = json.loads(sample.read())

        results = create_genome_annotation(services,
                                           token,
                                           888888,
                                           data['annotation_properties']['genome_annotation_id'],
                                           data['features'],
                                           data['proteins'],
                                           data['assembly_ref'],
                                           data['taxon_ref'],
                                           data['annotation_properties'])

        id = test_organisms[t].split(".json")[0]

        protein_container = results[0]
        pc_filename = "{}_pc.json".format(id)
        with open(pc_filename, 'w') as pc:
            "creating {}".format(pc_filename)
            pc.write(json.dumps(protein_container))

        feature_containers = results[2]
        for feature_type in feature_containers:
            fc_filename = "{}_{}_fc.json".format(id, feature_type)
            "creating {}".format(fc_filename)
            with open(fc_filename, 'w') as fc:
                fc.write(json.dumps(feature_containers[feature_type]))

        end = datetime.datetime.utcnow()
        print "Input data for {} was {} MB and took {}\n".format(t,
                                                                 os.stat(test_organisms[t]).st_size/(1.0*1024*1024),
                                                                 end - start)

    print "Finished"
