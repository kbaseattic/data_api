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
    
    print "general object API methods using E.coli K12 Genome Annotation"
    
    print "object_api = biokbase.data_api.object.ObjectAPI()"
    object_api = biokbase.data_api.object.ObjectAPI(services, ref="testCondensedGenomeV2/GENOME_ANNOTATION_Escherichia_coli_K12")
    
    print "\n\nobject_api.get_schema()"
    pprint.pprint(object_api.get_schema())
    
    print "\n\nobject_api.get_typestring()"
    pprint.pprint(object_api.get_typestring())
    
    print "\n\nobject_api.get_info()"
    pprint.pprint(object_api.get_info())
    
    print "\n\nobject_api.get_history()"
    pprint.pprint(object_api.get_history())
    
    print "\n\nobject_api.get_provenance()"
    pprint.pprint(object_api.get_provenance())
    
    print "\n\nobject_api.get_id()"
    pprint.pprint(object_api.get_id())
    
    print "\n\nobject_api.get_name()"
    pprint.pprint(object_api.get_name())
    
    print "\n\nobject_api.get_stats()"
    pprint.pprint(object_api.get_stats())
    
    print "\n\nobject_api.get_data()"
    pprint.pprint(object_api.get_data())
    
    print "\n\nobject_api.get_data_subset([\"domain\"])"
    pprint.pprint(object_api.get_data_subset(["domain"]))
    

    print "\n\nAssembly API methods using E.coli K12"
    
    print "assembly_api = biokbase.data_api.assembly.AssemblyAPI()"
    assembly_api = biokbase.data_api.assembly.AssemblyAPI(services, ref="testCondensedGenomeV2/kb|g.0_assembly")
    
    print "\n\nassembly_api.get_assembly_id()"
    pprint.pprint(assembly_api.get_assembly_id())
    
    print "\n\nassembly_api.get_external_source_info()"
    pprint.pprint(assembly_api.get_external_source_info())
    
    print "\n\nassembly_api.get_stats()"
    pprint.pprint(assembly_api.get_stats())
    
    print "\n\nassembly_api.get_number_contigs()"
    pprint.pprint(assembly_api.get_number_contigs())
    
    print "\n\nassembly_api.get_contig_ids()"
    contig_ids = assembly_api.get_contig_ids()
    pprint.pprint(contig_ids)
    
    print "\n\nassembly_api.get_contigs_by_id()"
    contigs = assembly_api.get_contigs_by_id([contig_ids[0]])
    pprint.pprint(contigs)

        
    print "\n\nGenome Annotation API methods using E.coli K12"
    
    print "genome_annotation_api = biokbase.data_api.genome_annotation.GenomeAnnotationAPI()"
    genome_annotation_api = biokbase.data_api.genome_annotation.GenomeAnnotationAPI(services, ref="testCondensedGenomeV2/GENOME_ANNOTATION_Escherichia_coli_K12")
    
    print "\n\ngenome_annotation_api.get_taxon_ref()"
    taxon_ref = genome_annotation_api.get_taxon_ref()
    pprint.pprint(taxon_ref)
    
    print "\n\ngenome_annotation_api.get_assembly_ref()"
    assembly_ref = genome_annotation_api.get_assembly_ref()
    pprint.pprint(assembly_ref)
    
    print "\n\ngenome_annotation_api.get_feature_types()"
    feature_types = genome_annotation_api.get_feature_types()
    pprint.pprint(feature_types)
    
    print "\n\ngenome_annotation_api.get_feature_ids_by_type(['{0}'])".format(feature_types[0])
    pprint.pprint(genome_annotation_api.get_feature_ids_by_type([feature_types[0]]))
    
    print "\n\ngenome_annotation_api.get_feature_ids_by_region(contig_id_list=['{0}'],type_list=['{1}'])".format(contig_ids[0],feature_types[0])
    pprint.pprint(genome_annotation_api.get_feature_ids_by_region(contig_id_list=[contig_ids[0]], type_list=[feature_types[0]]))
    
    print "\n\ngenome_annotation_api.get_feature_ids_by_function()"
    pprint.pprint(genome_annotation_api.get_feature_ids_by_function())
    
    print "\n\ngenome_annotation_api.get_feature_ids_by_alias()"
    pprint.pprint(genome_annotation_api.get_feature_ids_by_alias())
    
    print "\n\ngenome_annotation_api.get_associated_feature_ids()"
    pprint.pprint(genome_annotation_api.get_associated_feature_ids())
    
    print "\n\ngenome_annotation_api.get_child_feature_ids()"
    pprint.pprint(genome_annotation_api.get_child_feature_ids())
    
    print "\n\ngenome_annotation_api.get_parent_feature_ids()"
    pprint.pprint(genome_annotation_api.get_parent_feature_ids())
    
    print "\n\ngenome_annotation_api.get_protein_ids_by_cds()"
    pprint.pprint(genome_annotation_api.get_protein_ids_by_cds())
    
    print "\n\ngenome_annotation_api.get_features_by_id()"
    pprint.pprint(genome_annotation_api.get_features_by_id())
    
    print "\n\ngenome_annotation_api.get_proteins()"
    pprint.pprint(genome_annotation_api.get_proteins())
    
    
    print "\n\nTaxon API methods for E.coli K12"
    
    print "taxon_api = biokbase.data_api.taxon.TaxonAPI()"
    taxon_api = biokbase.data_api.taxon.TaxonAPI(services, ref=taxon_ref)
    
    print "\n\ntaxon_api.get_parent()"
    pprint.pprint(taxon_api.get_parent())
    
    print "\n\ntaxon_api.get_children()"
    pprint.pprint(taxon_api.get_children())
    
    print "\n\ntaxon_api.get_genome_annotations()"
    pprint.pprint(taxon_api.get_genome_annotations())
    
    print "\n\ntaxon_api.get_taxonomic_lineage()"
    pprint.pprint(taxon_api.get_taxonomic_lineage())
    
    print "\n\ntaxon_api.get_scientific_name()"
    pprint.pprint(taxon_api.get_scientific_name())
    
    print "\n\ntaxon_api.get_taxonomic_id()"
    pprint.pprint(taxon_api.get_taxonomic_id())
    
    print "\n\ntaxon_api.get_domain()"
    pprint.pprint(taxon_api.get_domain())
    
    print "\n\ntaxon_api.get_aliases()"
    pprint.pprint(taxon_api.get_aliases())
    
    print "\n\ntaxon_api.get_genetic_code()"
    pprint.pprint(taxon_api.get_genetic_code())
