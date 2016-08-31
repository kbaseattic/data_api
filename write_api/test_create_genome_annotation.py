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

        # assumes kbasetest user
        ref = create_genome_annotation(services,
                                       token,
                                       10362,
                                       data['annotation_properties']['genome_annotation_id'],
                                       data['features'],
                                       data['proteins'],
                                       data['assembly_ref'],
                                       data['taxon_ref'],
                                       data['annotation_properties'])

        end = datetime.datetime.utcnow()
        print "Input data for {} was {} MB and took {}\n".format(t,
                                                                 os.stat(test_organisms[t]).st_size/(1.0*1024*1024),
                                                                 end - start)
        print "GenomeAnnotation reference: {}".format(ref)

    print "Finished"
