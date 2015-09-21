import json
import datetime
import random

import doekbase.data_api

services = {
    "prod": {
        "workspace_service_url": "https://kbase.us/services/ws/",
        "shock_service_url": "https://kbase.us/services/shock-api/",
        "transform_service_url": "https://kbase.us/services/transform/",
        "awe_service_url": "https://kbase.us/services/awe_api/",
        "ujs_service_url": "https://kbase.us/services/userandjobstate/",
        "handle_service_url": "https://kbase.us/services/handle_service/"
    },
    "ci": {
        "workspace_service_url": "https://ci.kbase.us/services/ws/",
        "shock_service_url": "https://ci.kbase.us/services/shock-api/",
        "transform_service_url": "https://ci.kbase.us/services/transform/",
        "awe_service_url": "https://ci.kbase.us/services/awe_api/",
        "ujs_service_url": "https://ci.kbase.us/services/userandjobstate/",
        "handle_service_url": "https://ci.kbase.us/services/handle_service/"
    }
}

MB = 2**20 * 1.0

def calc_size(obj):
    return len(json.dumps(obj))/MB

def run2():
    assembly_workspace_name = "testCondensedGenomeV2"
    ci_assembly_api = doekbase.data_api.sequence.assembly.AssemblyAPI(services=services["ci"])

    print "Fetching each contig of kb|g.140106 sequentially"
    num_contigs = ci_assembly_api.get_number_contigs(assembly_workspace_name + "/" + "kb|g.140106_assembly")
    kbg140106_contig_ids = sorted(ci_assembly_api.get_contig_ids(assembly_workspace_name + "/" + "kb|g.140106_assembly"),cmp=lambda x,y: cmp(int(x.rsplit(".",1)[1]),int(y.rsplit(".",1)[1])))

    for x in kbg140106_contig_ids:
        print "Fetching {0}".format(x)
        startFetchAssembly = datetime.datetime.utcnow()
        subset_contigs = ci_assembly_api.get_contigs(assembly_workspace_name + "/" + "kb|g.140106_assembly", [x])
        endFetchAssembly = datetime.datetime.utcnow()
        print "\tFetched json of size {0} MB which took {1}".format(str(calc_size(subset_contigs)),str(endFetchAssembly - startFetchAssembly))

    randtrials = 10

    print "{0} trials of random selection of subsets of random number of contigs between 1 and {1} from kb|g.140106 and fetch them".format(str(randtrials),str(num_contigs))
    for i in xrange(randtrials):
        randsize = random.randint(1,num_contigs)
        contig_id_list = random.sample(kbg140106_contig_ids, randsize)

        startFetchAssembly = datetime.datetime.utcnow()
        subset_contigs = ci_assembly_api.get_contigs(assembly_workspace_name + "/" + assemblies["kb|g.140106_assembly"], contig_id_list)
        endFetchAssembly = datetime.datetime.utcnow()
        print "\tFetched json of size {0} MB which took {1}".format(str(calc_size(subset_contigs)),str(endFetchAssembly - startFetchAssembly))

def run():
    # ref = assembly_workspace_name + "/" + "kb|g.140106_assembly"
    # assembly_workspace_name = "testCondensedGenomeV2"
    # ci_assembly_api = assembly.AssemblyAPI(services=services["ci"], ref=ref)
    #
    # print "Fetching each contig of kb|g.140106 sequentially"
    # num_contigs = ci_assembly_api.get_number_contigs()
    # kbg140106_contig_ids = sorted(ci_assembly_api.get_contig_ids(),
    #     cmp=lambda x, y: cmp(int(x.rsplit(".",1)[1]),int(y.rsplit(".",1)[1])))
    #
    # for x in kbg140106_contig_ids:
    #     print "Fetching {0}".format(x)
    #     startFetchAssembly = datetime.datetime.utcnow()
    #     subset_contigs = ci_assembly_api.get_contigs(assembly_workspace_name + "/" + "kb|g.140106_assembly", [x])
    #     endFetchAssembly = datetime.datetime.utcnow()
    #     print "\tFetched json of size {0} MB which took {1}".format(str(calc_size(subset_contigs)),str(endFetchAssembly - startFetchAssembly))
    #
    # randtrials = 10
    #
    # print "{0} trials of random selection of subsets of random number of contigs between 1 and {1} from kb|g.140106 and fetch them".format(str(randtrials),str(num_contigs))
    # for i in xrange(randtrials):
    #     randsize = random.randint(1,num_contigs)
    #     contig_id_list = random.sample(kbg140106_contig_ids, randsize)
    #     startFetchAssembly = datetime.datetime.utcnow()
    #     subset_contigs = ci_assembly_api.get_contigs(assembly_workspace_name + "/" +
    #                                                  "kb|g.140106_assembly",
    #                                                  contig_id_list)
    #     endFetchAssembly = datetime.datetime.utcnow()
    #     print "\tFetched json of size {0} MB which took {1}".format(str(calc_size(subset_contigs)),str(endFetchAssembly - startFetchAssembly))
    return 0

if __name__ == '__main__':
    run()
