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
    import biokbase.data_api.object
    import biokbase.data_api.assembly
    import biokbase.data_api.taxon
    import biokbase.data_api.genome_annotation

    services = {
        "workspace_service_url": "https://ci.kbase.us/services/ws/",
        "shock_service_url": "https://ci.kbase.us/services/shock-api/",
    }
    
    print "general object API methods using  Genome Annotation"
    
    print "object_api = biokbase.data_api.object.Data()"
    object_api = biokbase.data_api.object.ObjectAPI(services, ref="PrototypeReferenceGenomes/kb|g.3157")

    print "Pull back basic object info for any object type:"
    print "\n\nobject_api.get_typestring()"
    pprint.pprint(object_api.get_typestring())
    
    print "\n\nobject_api.get_info()"
    pprint.pprint(object_api.get_info())

    print "\n\nobject_api.get_id()"
    pprint.pprint(object_api.get_id())
    
    print "\n\nobject_api.get_name()"
    pprint.pprint(object_api.get_name())
    
    print "\n\nobject_api.get_history()"
    pprint.pprint(object_api.get_history())
    
    print "\n\nobject_api.get_provenance()"
    pprint.pprint(object_api.get_provenance())

    print "\n\nobject_api.get_schema()"
    pprint.pprint(object_api.get_schema())
            
    print "\n\nFetch the full JSON document for this object and tell me how big it is:"
    print "len(object_api.get_data())"
    pprint.pprint(len(object_api.get_data()))
    
    print "\n\nFetch specific pieces of an object by path strings:"
    print "object_api.get_data_subset([\"domain\"])"
    pprint.pprint(object_api.get_data_subset(["domain"]))
    

    print "\n\nAssembly API methods using "
    
    print "assembly_api = biokbase.data_api.assembly.AssemblyAPI()"
    assembly_api = biokbase.data_api.assembly.AssemblyAPI(services, ref="PrototypeReferenceGenomes/kb|g.3157_assembly")
    
    print "\n\nFetch basic info for an Assembly:"
    print "assembly_api.get_assembly_id()"
    pprint.pprint(assembly_api.get_assembly_id())
        
    print "\nassembly_api.get_stats()"
    pprint.pprint(assembly_api.get_stats())
    
    print "\nassembly_api.get_number_contigs()"
    pprint.pprint(assembly_api.get_number_contigs())

    print "\nFetch the information telling me about where this Assembly came from:"
    print "assembly_api.get_external_source_info()"    
    pprint.pprint(assembly_api.get_external_source_info())

    print "\nFetch the contig ids:"    
    print "contig_ids = assembly_api.get_contig_ids()"
    print "pprint.pprint(contig_ids)"
    
    contig_ids = assembly_api.get_contig_ids()
    pprint.pprint(contig_ids)

    print "\nUse the contig ids to fetch the contig sequences and metadata:"
    print "assembly_api.get_contigs_by_id([contig_ids[0]])"
    contigs = assembly_api.get_contigs_by_id([contig_ids[0]])
    pprint.pprint(contigs)

        
    print "\n\nGenome Annotation API methods using "
    
    print "genome_annotation_api = biokbase.data_api.genome_annotation.GenomeAnnotation()"
    genome_annotation_api = biokbase.data_api.genome_annotation.GenomeAnnotationAPI(services, ref="PrototypeReferenceGenomes/kb|g.3157")
    
    print "\n\nGet my connected Taxon:"
    print "genome_annotation_api.get_taxon()"
    taxon_api = genome_annotation_api.get_taxon()
    pprint.pprint(taxon_api)
    
    print "\nGet the Assembly connected to this Genome Annotation:"
    print "genome_annotation_api.get_assembly()"
    assembly_api = genome_annotation_api.get_assembly()
    pprint.pprint(assembly_api)

    print "\nShow me what feature types are contained in this Genome Annotation:"    
    print "genome_annotation_api.get_feature_types()"
    feature_types = genome_annotation_api.get_feature_types()
    pprint.pprint(feature_types)
    
    print "\nDescribe these feature types for me:"
    print "pprint.pprint(genome_annotation_api.get_feature_type_descriptions(feature_types))"
    pprint.pprint(genome_annotation_api.get_feature_type_descriptions(feature_types))
    
    print "\nHmm, how many features are there of each type?"
    print "genome_annotation_api.get_feature_type_counts()"
    counts = genome_annotation_api.get_feature_type_counts(feature_types)
    pprint.pprint(counts)
    
    target_types = [feature_types[0]]    
    
    print "\ngenome_annotation_api.get_feature_ids(type_list={0})".format(target_types)
    feature_ids_by_type = genome_annotation_api.get_feature_ids(type_list=target_types)
    pprint.pprint(len(feature_ids_by_type.values()))

    target_regions = [{"contig_id": "kb|g.3157.c.0", "strand": "?", "start": 0, "stop": 1000}]

    print "\ngenome_annotation_api.get_feature_ids(region_list={0})".format(target_regions)
    feature_ids_by_region = genome_annotation_api.get_feature_ids(region_list=target_regions)
    pprint.pprint(feature_ids_by_region)

    target_functions = ["polymerase"]

    print "\ngenome_annotation_api.get_feature_ids(function_list={0})".format(target_functions)
    feature_ids_by_function = genome_annotation_api.get_feature_ids(function_list=target_functions)
    pprint.pprint(feature_ids_by_function)

    target_aliases = ["dnaA"]

    print "\ngenome_annotation_api.get_feature_ids(alias_list={0})".format(target_aliases)
    feature_ids_by_alias = genome_annotation_api.get_feature_ids(alias_list=target_aliases)
    pprint.pprint(feature_ids_by_alias)

    print "\ngenome_annotation_api.get_feature_ids(type_list={0}, region_list={1}, function_list={2}, alias_list={3})".format(target_types,target_regions,target_functions,target_aliases)
    feature_ids_intersection = genome_annotation_api.get_feature_ids(type_list=target_types, 
                                                                     region_list=target_regions,
                                                                     function_list=target_functions,
                                                                     alias_list=target_aliases)
    pprint.pprint(feature_ids_intersection)
    feature_ids = feature_ids_intersection.values().join()
    
    print feature_ids
    
    #print "\n\ngenome_annotation_api.get_protein_ids_by_cds()"
    #pprint.pprint(genome_annotation_api.get_protein_ids_by_cds())
    
    print "\ngenome_annotation_api.get_features_by_id(feature_ids)"
    pprint.pprint(genome_annotation_api.get_features_by_id(feature_ids))

    print "\ngenome_annotation_api.get_feature_dna(feature_ids)"
    pprint.pprint(genome_annotation_api.get_feature_dna(feature_ids))

    print "\ngenome_annotation_api.get_feature_locations(feature_ids)"
    pprint.pprint(genome_annotation_api.get_feature_locations(feature_ids))

    print "\ngenome_annotation_api.get_feature_functions(feature_ids)"
    pprint.pprint(genome_annotation_api.get_feature_functions(feature_ids))

    print "\ngenome_annotation_api.get_feature_aliases(feature_ids)"
    pprint.pprint(genome_annotation_api.get_feature_aliases(feature_ids))

    print "\n\ngenome_annotation_api.get_proteins()"
    pprint.pprint(len(genome_annotation_api.get_proteins()))
    
    
    print "\n\nTaxon API methods for "
    
    print "\n\nPull back my taxonomy information:"        
    print "taxon_api.get_scientific_lineage()"
    pprint.pprint(taxon_api.get_scientific_lineage())
    
    print "\ntaxon_api.get_scientific_name()"
    pprint.pprint(taxon_api.get_scientific_name())
    
    print "\ntaxon_api.get_taxonomic_id()"
    pprint.pprint(taxon_api.get_taxonomic_id())
    
    print "\ntaxon_api.get_domain()"
    pprint.pprint(taxon_api.get_domain())
    
    print "\ntaxon_api.get_aliases()"
    pprint.pprint(taxon_api.get_aliases())
    
    print "\ntaxon_api.get_genetic_code()"
    pprint.pprint(taxon_api.get_genetic_code())

    print "\nTrace back up the Taxon lineage using get_parent() and get scientific name and ncbi tax id:"
    print "parent = taxon_api.get_parent()"
    print "while parent:"
    print "    pprint.pprint([parent.get_scientific_name(),parent.get_taxonomic_id()])"
    print "    parent = parent.get_parent()\n"
    
    parent = taxon_api.get_parent()
    while parent:
        pprint.pprint([parent.get_scientific_name(),parent.get_taxonomic_id()])
        parent = parent.get_parent()
    
    print "\nFind out what other E.Coli there are using get_parent() and get_children():"
    print "#Causing timeout problems, need to investigate more"
    print "parent = taxon_api.get_parent()"
    print "sibling_info = [(s.get_scientific_name(), s.get_taxonomic_id()) for s in parent.get_children()]"
    print "pprint.pprint(sibling_info)\n"
    
    parent = taxon_api.get_parent()
    children = parent.get_children()
    if children:
        sibling_info = [(s.get_scientific_name(), s.get_taxonomic_id()) for s in children]
        pprint.pprint(sibling_info)

    print "\nFind out what Genome Annotations reference my Taxon:"        
    print """
    annotations = taxon_api.get_genome_annotations()
    for g in annotations:
        pprint.pprint(g.get_name())
    """
    
    annotations = taxon_api.get_genome_annotations()
    for g in annotations:
        pprint.pprint(g.get_info())
