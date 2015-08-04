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
            
    print "\n\nFetch the full JSON document for this object:"
    print "object_api.get_data()"
    pprint.pprint(object_api.get_data())
    
    print "\n\nFetch specific pieces of an object by path strings:"
    print "object_api.get_data_subset([\"domain\"])"
    pprint.pprint(object_api.get_data_subset(["domain"]))
    

    print "\n\nAssembly API methods using E.coli K12"
    
    print "assembly_api = biokbase.data_api.assembly.AssemblyAPI()"
    assembly_api = biokbase.data_api.assembly.AssemblyAPI(services, ref="testCondensedGenomeV2/kb|g.0_assembly")
    
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
    
    contig_ids = assembly_api.get_contig_ids(raw=True)
    pprint.pprint(contig_ids)

    print "\nUse the contig ids to fetch the contig sequences and metadata:"
    print "assembly_api.get_contigs_by_id([contig_ids[0]])"
    contigs = assembly_api.get_contigs_by_id([contig_ids[0]])
    pprint.pprint(contigs)

        
    print "\n\nGenome Annotation API methods using E.coli K12"
    
    print "genome_annotation_api = biokbase.data_api.genome_annotation.GenomeAnnotationAPI()"
    genome_annotation_api = biokbase.data_api.genome_annotation.GenomeAnnotationAPI(services, ref="testCondensedGenomeV2/GENOME_ANNOTATION_Escherichia_coli_K12")
    
    print "\n\nGet my connected Taxon:"
    print "genome_annotation_api.get_taxon()"
    print "# there is a data reference error here, the taxon ref for this genome annotation is incorrect and points to wheat"
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
    
    print "\nHmm, Terminators...let's see more about those:"
    print "genome_annotation_api.get_feature_ids_by_type(['{0}'])".format(feature_types[0])
    feature_ids = genome_annotation_api.get_feature_ids_by_type([feature_types[0]])
    pprint.pprint(feature_ids)
    
    #print "genome_annotation_api.get_feature_ids_by_region(contig_id_list=['{0}'],type_list=['{1}'])".format(contig_ids[0],feature_types[0])
    #pprint.pprint(genome_annotation_api.get_feature_ids_by_region(contig_id_list=[contig_ids[0]], type_list=[feature_types[0]]))
    
    #print "\n\ngenome_annotation_api.get_feature_ids_by_function(['gene'])"
    #pprint.pprint(genome_annotation_api.get_feature_ids_by_function(['gene']))
    
    #print "\n\ngenome_annotation_api.get_feature_ids_by_alias()"
    #pprint.pprint(genome_annotation_api.get_feature_ids_by_alias())
    
    #print "\n\ngenome_annotation_api.get_associated_feature_ids()"
    #pprint.pprint(genome_annotation_api.get_associated_feature_ids())
    
    #print "\n\ngenome_annotation_api.get_child_feature_ids()"
    #pprint.pprint(genome_annotation_api.get_child_feature_ids())
    
    #print "\n\ngenome_annotation_api.get_parent_feature_ids()"
    #pprint.pprint(genome_annotation_api.get_parent_feature_ids())
    
    #print "\n\ngenome_annotation_api.get_protein_ids_by_cds()"
    #pprint.pprint(genome_annotation_api.get_protein_ids_by_cds())
    
    print "\ngenome_annotation_api.get_features_by_id(feature_ids)"
    pprint.pprint(genome_annotation_api.get_features_by_id(feature_ids))
    
    #print "\n\ngenome_annotation_api.get_proteins()"
    #pprint.pprint(genome_annotation_api.get_proteins())
    
    
    print "\n\nTaxon API methods for E.coli K12"
    
    print "taxon_api = biokbase.data_api.taxon.TaxonAPI(services, ref='Taxon3/83333_taxon')"
    taxon_api = biokbase.data_api.taxon.TaxonAPI(services, ref="Taxon3/83333_taxon")
    
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
    print "taxon_api.get_genome_annotations()"
    pprint.pprint(taxon_api.get_genome_annotations())
