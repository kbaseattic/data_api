#!/usr/bin/env python

import unittest
import datetime
import json

import doekbase.data_api.annotation.genome_annotation
import doekbase.data_api.sequence.assembly.api

MB = 2**20 * 1.0

def calc_size(obj):
    return len(json.dumps(obj))/MB

class TestBenchmarkAssemblyObjects(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services = {
            "ci": {
                "workspace_service_url": "https://ci.kbase.us/services/ws/",
                "shock_service_url": "https://ci.kbase.us/services/shock-api/",
                "transform_service_url": "https://ci.kbase.us/services/transform/",
                "awe_service_url": "https://ci.kbase.us/services/awe_api/",
                "ujs_service_url": "https://ci.kbase.us/services/userandjobstate/",
                "handle_service_url": "https://ci.kbase.us/services/handle_service/"
            }
        }

        cls.public_workspace_name = "testOriginalGenome"
        cls.public_workspace_id = 641

        cls.genomes_order = ["kb|g.244916","kb|g.0","kb|g.3899","kb|g.140106"]

        cls.genomes = {"kb|g.244916": {"ref": "641/5/1"},
                       "kb|g.0": {"ref": "641/2/1"},
                       "kb|g.3899": {"ref": "641/7/1"},
                       "kb|g.140106": {"ref": "641/3/1"}}

        cls.fetch_contigs = {"kb|g.3899": ["kb|g.3899.c.2", "kb|g.3899.c.5"],
                             "kb|g.0": ["kb|g.0.c.1"],
                             "kb|g.244916": ["kb|g.244916.c.0"],
                             "kb|g.140106": ["kb|g.140106.c.0","kb|g.140106.c.10","kb|g.140106.c.100",
                                             "kb|g.140106.c.1000","kb|g.140106.c.10000",
                                             "kb|g.140106.c.100000","kb|g.140106.c.200000",
                                             "kb|g.140106.c.300000","kb|g.140106.c.400000",
                                             "kb|g.140106.c.500000","kb|g.140106.c.600000",
                                             "kb|g.140106.c.700000"]}

        cls.genome_annotation_api = doekbase.data_api.genome_annotation.GenomeAnnotationAPI(services=services["ci"])
        cls.assembly_api = doekbase.data_api.assembly.AssemblyAPI(services=services["ci"])

    def run(result=None):
        
        print "Existing Object Types"

        for g in genomes_order:
            # grab genome object
            print "\tFetching {0} ...".format(g)
            contigset_ref = ci_genome_annotation_api.get_assembly(genomes[g]["ref"])

            print "\tBasic stats about {0}".format(g)
            stats = ci_genome_annotation_api.get_stats(contigset_ref)

            print "\tFetching full set for {0} ...".format(g)
            startFetchAssembly = datetime.datetime.utcnow()
            contigs = ci_assembly_api.get_contigs(contigset_ref)
            endFetchAssembly = datetime.datetime.utcnow()
            print "\tFetched json of size {0} MB which took {1}".format(str(calc_size(contigs)),str(endFetchAssembly - startFetchAssembly))

            print "\tFetching subset {0} contigs from {1} ...".format(str(len(fetch_contigs[g])), g)
            startFetchAssembly = datetime.datetime.utcnow()
            subset_contigs = ci_assembly_api.get_contigs(contigset_ref, fetch_contigs[g])
            endFetchAssembly = datetime.datetime.utcnow()
            print "\tFetched json of size {0} MB which took {1}".format(str(calc_size(subset_contigs)),str(endFetchAssembly - startFetchAssembly))
            print "\t"

        assembly_workspace_name = "testCondensedGenomeV2"
        assemblies = ["kb|g.244916_assembly",
                      "kb|g.0_assembly",
                      "kb|g.3899_assembly",
                      "kb|g.140106_assembly"]

        fetch_contigs = {"kb|g.3899_assembly": ["kb|g.3899.c.2", "kb|g.3899.c.5"],
                   "kb|g.0_assembly": ["kb|g.0.c.1"],
                   "kb|g.244916_assembly": ["kb|g.244916.c.0"],
                   "kb|g.140106_assembly": ["kb|g.140106.c.0","kb|g.140106.c.10",
                                            "kb|g.140106.c.100","kb|g.140106.c.1000",
                                            "kb|g.140106.c.10000","kb|g.140106.c.100000",
                                            "kb|g.140106.c.200000","kb|g.140106.c.300000",
                                            "kb|g.140106.c.400000","kb|g.140106.c.500000",
                                            "kb|g.140106.c.600000","kb|g.140106.c.700000"]}

        print "Updated Object Types"

        for x in assemblies:
            print "\tBasic stats about {0}".format(x)
            stats = ci_genome_annotation_api.get_stats(assembly_workspace_name + "/" + x)

            print "\tFetching full set for {0} ...".format(x)
            startFetchAssembly = datetime.datetime.utcnow()
            contigs = ci_assembly_api.get_contigs(assembly_workspace_name + "/" + x)    
            endFetchAssembly = datetime.datetime.utcnow()
            print "\tFetched json of size {0} MB which took {1}".format(str(calc_size(contigs)),str(endFetchAssembly - startFetchAssembly))

            print "\tFetching subset {0} contigs from {1} ...".format(str(len(fetch_contigs[x])), x)
            startFetchAssembly = datetime.datetime.utcnow()
            subset_contigs = ci_assembly_api.get_contigs(assembly_workspace_name + "/" + x, fetch_contigs[x])    
            endFetchAssembly = datetime.datetime.utcnow()
            print "\tFetched json of size {0} MB which took {1}".format(str(calc_size(subset_contigs)),str(endFetchAssembly - startFetchAssembly))
            print "\t"

        print "Fetching each contig of kb|g.140106 sequentially"
        num_contigs = ci_assembly_api.get_number_contigs(assembly_workspace_name + "/" + "kb|g.140106_assembly")
        kbg140106_contig_ids = ci_assembly_api.get_contig_ids(assembly_workspace_name + "/" + "kb|g.140106_assembly")

        for x in kbg140106_contig_ids:
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
