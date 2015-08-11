#!/usr/bin/env python
import sys
import os
import json
import pprint

paths = sys.path[:]
my_location = os.path.split(os.path.dirname(__file__))[0]
lib_path = sorted([(x, len(os.path.commonprefix([x, my_location]))) for x in paths], cmp=lambda x,y: cmp(x[1],y[1]))[-1][0]
sys.path.insert(1,lib_path)

if __name__ == "__main__":
    import biokbase.data_api
    import biokbase.data_api.object
    import biokbase.data_api.assembly
    import biokbase.data_api.taxon
    import biokbase.data_api.genome_annotation
    
    from biokbase.data_api.tests.performance import WallClockTimer

    services = {
        "workspace_service_url": "https://ci.kbase.us/services/ws/",
        "shock_service_url": "https://ci.kbase.us/services/shock-api/",
    }
    
    print "Benchmarking API methods"
    
    old_ws = biokbase.data_api.browse(1011)    
    new_ws = biokbase.data_api.browse(1013)    
    
    old_genomes = [x for x in old_ws.ls() if x.type.split("-")[0] in biokbase.data_api.genome_annotation.TYPES]
    new_genomes = [x for x in new_ws.ls() if x.type.split("-")[0] in biokbase.data_api.genome_annotation.TYPES]

    def benchmark_genome(g):
        genome_annotation = g
        name = genome_annotation.get_name()

        print "getting timings for {0}".format(name)
        timings = dict()
        timings[name] = dict()
        timings[name]["taxon"] = dict()
        timings[name]["assembly"] = dict()
        timings[name]["annotation"] = dict()

        taxon = genome_annotation.get_taxon()    
        assembly = genome_annotation.get_assembly()

        with WallClockTimer() as t:
            taxon.get_taxonomic_id()
        timings[name]["taxon"]["get_taxonomic_id"] = t.elapsed

        with WallClockTimer() as t:
            taxon.get_kingdom()
        timings[name]["taxon"]["get_kingdom"] = t.elapsed

        with WallClockTimer() as t:
            taxon.get_domain()
        timings[name]["taxon"]["get_domain"] = t.elapsed

        with WallClockTimer() as t:
            taxon.get_genetic_code()
        timings[name]["taxon"]["get_genetic_code"] = t.elapsed

        with WallClockTimer() as t:
            taxon.get_scientific_name()
        timings[name]["taxon"]["get_scientific_name"] = t.elapsed

        with WallClockTimer() as t:
            taxon.get_aliases()
        timings[name]["taxon"]["get_aliases"] = t.elapsed

        with WallClockTimer() as t:
            taxon.get_scientific_lineage()
        timings[name]["taxon"]["get_scientific_lineage"] = t.elapsed

        pprint.pprint(timings[name]["taxon"])

        with WallClockTimer() as t:
            assembly.get_number_contigs()
        timings[name]["assembly"]["get_number_contigs"] = t.elapsed

        with WallClockTimer() as t:
            assembly.get_dna_size()
        timings[name]["assembly"]["get_dna_size"] = t.elapsed

        with WallClockTimer() as t:
            assembly.get_gc_content()
        timings[name]["assembly"]["get_gc_content"] = t.elapsed

        with WallClockTimer() as t:
            assembly.get_contig_lengths()
        timings[name]["assembly"]["get_contig_lengths"] = t.elapsed

        with WallClockTimer() as t:
            assembly.get_contig_gc_content()
        timings[name]["assembly"]["get_contig_gc_content"] = t.elapsed

        with WallClockTimer() as t:
            contig_ids = assembly.get_contig_ids()
        timings[name]["assembly"]["get_contig_ids"] = t.elapsed

        with WallClockTimer() as t:
            first_contig = assembly.get_contigs_by_id(contig_id_list=contig_ids[0])
        timings[name]["assembly"]["get_contigs:contig_0"] = t.elapsed

        pprint.pprint(timings[name]["assembly"])

        with WallClockTimer() as t:
            feature_types = genome_annotation.get_feature_types()
        timings[name]["annotation"]["get_feature_types"] = t.elapsed

        with WallClockTimer() as t:
            genome_annotation.get_feature_type_descriptions(feature_types)
        timings[name]["annotation"]["get_feature_type_descriptions"] = t.elapsed

        with WallClockTimer() as t:
            genome_annotation.get_feature_type_counts(feature_types)
        timings[name]["annotation"]["get_feature_type_counts"] = t.elapsed

        with WallClockTimer() as t:
            feature_ids = genome_annotation.get_feature_ids(type_list=["CDS"], 
                                                            region_list=[{"contig_id": contig_ids[0],
                                                                          "start": 0,
                                                                          "stop": 1E9,
                                                                          "strand": "?"}])
        timings[name]["annotation"]["get_feature_ids:CDS_contig_0"] = t.elapsed

        with WallClockTimer() as t:
            feature_id_list = list()
            for k in feature_ids:
                feature_id_list.extend(feature_ids[k])
            genome_annotation.get_features_by_id(feature_id_list)
        timings[name]["annotation"]["get_features:feature_ids"] = t.elapsed
        
        pprint.pprint(timings[name]["annotation"])
        return timings
    
    old_timings = dict()
    new_timings = dict()
    
    for g in old_genomes:
        old_timings.update(benchmark_genome(g.object))
    
    for n in new_genomes(n):
        new_timings.update(benchmark_genome(n.object))
        
    with open('old_genomes_bench.json', 'w') as old_timings_file:
        old_timings_file.write(json.dumps(old_timings))        
    
    with open('new_genomes_bench.json', 'w') as new_timings_file:
        new_timings_file.write(json.dumps(new_timings))
