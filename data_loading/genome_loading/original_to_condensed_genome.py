import simplejson
import time
import sys
import biokbase.workspace.client
import re
import hashlib
import traceback
import os.path


def convert_original_genome_object_to_prototype(source_wsname=None,destination_wsname=None,taxon_wsname=None,source_wsurl=None, 
                                                destination_wsurl = None, lineage_files_dir = None, taxon_names_file=None, genomes = []): 

    source_ws_client = biokbase.workspace.client.Workspace(source_wsurl)
    destination_ws_client = biokbase.workspace.client.Workspace(destination_wsurl)

    source_workspace_object = source_ws_client.get_workspace_info({'workspace':source_wsname})
    source_workspace_id = source_workspace_object[0]
    source_workspace_name = source_workspace_object[1]

    destination_workspace_object = destination_ws_client.get_workspace_info({'workspace':destination_wsname})
    destination_workspace_id = destination_workspace_object[0]
    destination_workspace_name = destination_workspace_object[1]

    taxon_workspace_object = destination_ws_client.get_workspace_info({'workspace':taxon_wsname})
    taxon_workspace_id = taxon_workspace_object[0]
    taxon_workspace_name = taxon_workspace_object[1]

    genomes_without_taxon_refs = []

    #key scientific name, value is taxon object name (taxid_taxon)                                    
    scientific_names_lookup = dict()                                                                  
#    taxon_names_file = taxon_names_file[0]                                                            
 
    if os.path.isfile(taxon_names_file):                                                              
        print "Found taxon_names_File"                                                                
        name_f = open(taxon_names_file, 'r')                                                          
        for name_line in name_f:                                                                      
            temp_list = re.split(r'\t*\|\t*', name_line) 
#            is_scientific = False
#            if temp_list[3] == "scientific name":
#                is_scientific = True
            scientific_names_lookup[temp_list[1]] = "%s_taxon" % (str(temp_list[0]))              
#            if  'Gibberella zeae PH-1' in temp_list[1]:
#                print "Found  :Gibberella zeae PH-1: - result - ::"+temp_list[1]+"::"
        name_f.close()                                                                                
    else:
        print "COULD NOT Find taxon_names_File.  Exiting now."
        sys.exit(0)

#    print "Length of scientific names lookup : " + str(len(scientific_names_lookup))

#    if 'Gibberella zeae PH-1' in scientific_names_lookup :
#        print "FOUND THE SCIENTIFIC NAME"
#    else:
#        print "DID NOT FIND THE SCIENTIFIC NAME"

#    counter = 0
#    for sn_temp in scientific_names_lookup:
#        counter = counter +1
#        print "scientific_name :"+sn_temp+": value is :"+scientific_names_lookup[sn_temp]+":"
#        if counter > 10:
#            break

#    process_all_genomes = True
#    ordered_selected_genomes_list = []
#    max_genome_number = None
#    if (genomes): 
#        if (len(genomes) > 0):
#            g_regex = re.compile('kb\|g.\d+$')
#            process_all_genomes = False
#            genomes_list = args.genomes
#            genomes_dict = dict()
#            for genome in genomes_list:
#                g_match = g_regex.match(genome)
#                if (not g_match):
#                #genome string is not in expected format.
#                    print "Entered Genome : " + genome + " is not in valid format. Exiting program."
#                    logger.error("Entered Genome : " + genome + " is not in valid format.  Exiting program.")
#                    sys.exit(0)
#                selectedGidNumber = genome.split('.')[1]
#                genomes_dict[genome] = int(selectedGidNumber)
#            ordered_selected_genomes_list = sorted(genomes_dict.values())
#            logger.debug("Genome Numeric IDS entered : " + str(ordered_selected_genomes_list))
#            max_genome_number = ordered_selected_genomes_list[-1]
#        else:
#            logger.error("program was run with the genomes argument.  However no genomes were passed.")
#            print "program was run with the genomes argument.  However no genomes were passed."
#            sys.exit(0)

    objects_list = list()
    if len(genomes) > 0:
        names_list = list()
        for genome in genomes:
            names_list.append({'workspace':source_wsname,'name':genome})
        objects_list = [x['info'] for x in source_ws_client.get_objects(names_list)]
    else:
        # need to loop through to make sure we get all objects; limit of 5000 items returned by ws
        object_count = 1
        skipNum = 0
        limitNum = 5000
        while object_count != 0:
            this_list = source_ws_client.list_objects({"workspaces": [source_wsname],"type":"KBaseGenomes.Genome","limit":limitNum,"skip":skipNum})
            object_count=len(this_list)
            skipNum += limitNum
            objects_list.extend(this_list)


    if len(objects_list) > 0:
        print "\tWorkspace %s has %d matching objects" % (source_wsname, len(objects_list))
        object_counter = 0

#        if maxNumObjects < 1000:
#            objects_list = random.sample(objects_list,maxNumObjects)

        start_index = None
        end_index = None

        if start_index is None:
            start_index = 0
        if end_index is None:
            end_index = len(objects_list) - 1

        objects_list = objects_list[start_index:(end_index + 1)] 

        for x in objects_list:
            print "\t\tChecking %s, done with %s of all objects in %s" % (x[1], str(100.0 * float(object_counter)/len(objects_list)) + " %", source_workspace_name)
            
            if x[2].startswith("KBaseGenomes.Genome"):

                #convert the genome object
                #get the original genome object
                print >> sys.stderr, 'starting genome processing for ' + x[1]

                done = False
                while not done:
                    try:
                        original_genome = source_ws_client.get_objects([{"wsid": str(source_workspace_id), "objid": x[0]}])[0]
                        done = True
                    except Exception, e:
                        print str(e)
                        print "Having trouble getting " + str(x[0]) + " from workspace " + str(source_workspace_id)

                genome_annotation = dict()
                genome_annotation['genome_annotation_id'] = original_genome['data']['id']

                core_object_name = original_genome['info'][1]


#                temp_id = original_genome['data']['id']
#                temp_id = temp_id.replace("kb|","");

#                print "TEMP FILE ID : " + temp_id
                pattern = re.compile(r'kb\|') 
                lineage_file_name = core_object_name
                lineage_file_name = re.sub(pattern, '', lineage_file_name)

                potential_lineages_file = "%s/%s" % (lineage_files_dir[0],lineage_file_name)
#                potential_lineages_file = "%s/%s" % (lineage_files_dir[0],original_genome['data']['id'])
                print "TEMP FILE Open : " + potential_lineages_file
                gene_children_CDS_dict = dict()
                gene_children_mRNA_dict = dict()
                CDS_parent_gene_dict = dict()
                mRNA_parent_gene_dict = dict()
                CDS_associated_mRNA_dict = dict()
                mRNA_associated_CDS_dict = dict()

                pattern = re.compile(r'\s+')
                if os.path.isfile(potential_lineages_file):
                    print "Found Feature_lineage_File"
                    f = open(potential_lineages_file, 'r')
                    for line in f:
                        temp_list = re.split(r'\t+', line)
                        if "locus" in temp_list[0]:
                            mRNA = re.sub(pattern, '', temp_list[1]) 
#                            print "In Locus"
#                            mRNA = temp_list[1].replace("\n","")
#                            mRNA = mRNA.replace("\r","")
#                            print "MRNA = " + mRNA
                            if temp_list[0] not in gene_children_mRNA_dict:
                                gene_children_mRNA_dict[temp_list[0]] = []
                            gene_children_mRNA_dict[temp_list[0]].append(["mRNA",mRNA])
                            mRNA_parent_gene_dict[mRNA] = temp_list[0]
#                            print "mRNA = "+mRNA 
#                            print "Locus = "+temp_list[0] 
                        if "mRNA" in temp_list[0]:
                            CDS = re.sub(pattern, '', temp_list[1]) 
                            mRNA_associated_CDS_dict[temp_list[0]] = CDS
                            CDS_associated_mRNA_dict[CDS] = temp_list[0]
                    f.close()
                    
                    for mRNA in mRNA_associated_CDS_dict:
                        if mRNA in mRNA_parent_gene_dict:
                            temp_gene = mRNA_parent_gene_dict[mRNA]
                            temp_cds =  mRNA_associated_CDS_dict[mRNA]
                            if temp_gene not in gene_children_CDS_dict: 
                                gene_children_CDS_dict[temp_gene] = []
                            gene_children_CDS_dict[temp_gene].append(["CDS",temp_cds]) 
                            CDS_parent_gene_dict[temp_cds] = temp_gene
                else:
                    print "Could not find Feature_lineage_File"

                if 'source' in original_genome['data']:
                    genome_annotation['external_source'] = original_genome['data']['source']

                if 'domain' in original_genome['data']:
                    genome_annotation['domain'] = original_genome['data']['domain']
                else:
                    genome_annotation['domain'] = "unknown"
                genome_annotation['reference_annotation'] = 1

                if 'publications' in original_genome['data']:
                    genome_annotation['publications'] = original_genome['data']['publications']


                #Get the assembly (Dont care about the old name.  Have to match on "kbGenomeID_assembly"
                assembly_object_name = "%s_assembly" % (core_object_name)
                
                assembly_reference = None
                try: 
                    assembly_info = destination_ws_client.get_object_info_new({"objects": [{"wsid": str(destination_workspace_id), "name": assembly_object_name}], "includeMetadata": 0, "ignoreErrors": 0}) 
                    assembly_reference = "%s/%s/%s" % (assembly_info[0][6], assembly_info[0][0], assembly_info[0][4])
                except Exception, e: 
                    print "The assembly " + assembly_object_name + " from workspace " + str(destination_workspace_id) + " does not exist."

                #If it exists get the WS reference, otherwise empty reference and do a warning
                if assembly_reference is not None:
                    genome_annotation['assembly_ref'] = assembly_reference 
                else:
                    print "The assembly " + assembly_object_name + " from workspace " + str(destination_workspace_id) + " does not exist."
                    sys.exit(1) 

                taxon_id = None
                #Get the taxonomy.  
                #Look for that in the new workspace.
                taxon_object_name = None
                if 'scientific_name' in original_genome['data']:
                    if original_genome['data']['scientific_name'] in scientific_names_lookup:
                        taxon_object_name = scientific_names_lookup[original_genome['data']['scientific_name']]
                    else:
                        genomes_without_taxon_refs.append(original_genome['data']['id'])
                        taxon_object_name = "unknown_taxon" 
                        genome_annotation['notes'] = "Unable to find taxon from production genome's scientific name : %s ." % (original_genome['data']['scientific_name'] )
                    try: 
                        taxon_info = destination_ws_client.get_object_info([{"wsid": str(taxon_workspace_id), "name": taxon_object_name}],0) 
                        taxon_id = "%s/%s/%s" % (taxon_info[0][6], taxon_info[0][0], taxon_info[0][4]) 
                        print "Found name : " + taxon_object_name + " id: " + taxon_id 
                    except Exception, e: 
                        print str(e) 
                        print "The taxon " + taxon_object_name + " from workspace " + str(taxon_workspace_id) + " does not exist." 


                #TEMPORARY DEBUGGING
#                sys.exit(0)

                #If it exists get the WS reference, otherwise empty reference and do a warning
                if taxon_id is not None:
                    genome_annotation['taxon_ref'] = taxon_id 

                #Make the protein container and feature container.  Protein set will need to be stored first.
                protein_container = dict()
                protein_container['proteins'] = dict()
                protein_container_object_name = "%s_protein_container" % (core_object_name)
                original_features = []
                original_features = original_genome['data']['features']
                feature_type_containers = dict() #top level is the type, then it is features mapping as value.
                feature_lookup = dict()

                feature_count = 0
                for original_feature in original_features:
                    feature_count = feature_count + 1
                    new_feature = dict()                

                    #Copy over information
                    new_feature['feature_id'] = original_feature['id']

                    new_locations = []
                    for location in original_feature['location']:
                        new_locations.append([location[0],location[1],location[2],location[3]])
                    new_feature['locations'] = new_locations

                    if original_feature['type'] == "locus":
                        original_feature['type'] = "gene"

                    new_feature['type'] = original_feature['type']
                    feature_container_object_name = "%s_feature_container_%s" % (core_object_name,new_feature['type'])
                    feature_container_object_ref = "%s/%s" % (destination_workspace_name,feature_container_object_name)

                    if new_feature['feature_id'] in feature_lookup: 
                        feature_lookup[new_feature['feature_id']].append((feature_container_object_ref, new_feature['feature_id'])) 
                    else: 
                        feature_lookup[new_feature['feature_id']] = [(feature_container_object_ref, new_feature['feature_id'])] 

                    new_feature['function'] = original_feature['function']
                    if 'dna_sequence' in original_feature:
                        new_feature['md5'] = hashlib.md5(original_feature['dna_sequence'].upper()).hexdigest()
                        new_feature['dna_sequence'] = original_feature['dna_sequence']
                        new_feature['dna_sequence_length'] = original_feature['dna_sequence_length']
                    else:
                        new_feature['md5'] = ""
                        new_feature['dna_sequence'] = ""
                        new_feature['dna_sequence_length'] = 0

                    if 'publications' in original_feature:
                        new_feature['publications'] = original_feature['publications']

                    new_aliases = dict()
                    if 'aliases' in original_feature:
                        for alias in original_feature['aliases']:
                            if alias != "":
                                new_aliases[alias] = ['unknown']
                                if alias in feature_lookup:
                                    feature_lookup[alias].append((feature_container_object_ref,new_feature['feature_id']))
                                else:
                                    feature_lookup[alias] = [(feature_container_object_ref,new_feature['feature_id'])]                     
                        if len(new_aliases) > 0:
                            new_feature['aliases'] = new_aliases

                    if new_feature['type'] == 'CDS':
                        #if CDS make protein entry
                        protein = dict()
                        protein_id = original_feature['id']
                        if protein_id in protein_container['proteins']:
                            if original_feature['protein_translation'] != protein_container['proteins'][protein_id]['amino_acid_sequence']:
                                # Check vs md5 instead?
                                raise Exception("The same protein id %s has two different amino acid sequences" % (protein_id))
                            else:
                                if original_feature['function'] != protein_container['proteins'][protein_id]['function']: 
                                    protein_container['proteins'][protein_id]['function'] = protein_container['proteins'][protein_id]['function'] + "::" + original_feature['function']

                                if 'aliases' in protein_container['proteins'][protein_id]:
                                    aliases_temp = protein_container['proteins'][protein_id]['aliases']
                                    protein_container['proteins'][protein_id]['aliases'] = dict(new_aliases.items() + aliases_temp.items())
                        else:
                            protein['protein_id'] = protein_id
                            protein['amino_acid_sequence'] = original_feature['protein_translation']
                            protein['function'] = original_feature['function']
                            protein['aliases'] = new_aliases
                            protein['md5'] = hashlib.md5(original_feature['protein_translation'].upper()).hexdigest()                             
                            protein_container['proteins'][protein_id] = protein

                        #make CDS properties
                        CDS_properties = dict()
                        CDS_properties["codes_for_protein_ref"] = ("%s/%s" % (destination_workspace_name, protein_container_object_name), protein_id)
                        if original_feature['id'] in CDS_associated_mRNA_dict:
                            CDS_properties["associated_mRNA"] = ["mRNA",CDS_associated_mRNA_dict[original_feature['id']]] 
                        if original_feature['id'] in CDS_parent_gene_dict:
                            CDS_properties["parent_gene"] = ["gene",CDS_parent_gene_dict[original_feature['id']]]
                        new_feature['CDS_properties'] = CDS_properties 
                    elif new_feature['type'] == 'mRNA':
                        mRNA_properties = dict()
                        if original_feature['id'] in mRNA_associated_CDS_dict:
                            mRNA_properties["associated_CDS"] = ["CDS",mRNA_associated_CDS_dict[original_feature['id']]]
                        if original_feature['id'] in CDS_parent_gene_dict: 
                            mRNA_properties["parent_gene"] = ["gene",mRNA_parent_gene_dict[original_feature['id']]]
                        new_feature['mRNA_properties'] = mRNA_properties 

                    new_feature['quality_warnings'] = ["Not Implemented Yet"]

                    if new_feature['type'] == 'gene':
                        gene_properties = dict()
                        need_gene_properties = False
                        if original_feature['id'] in gene_children_CDS_dict:
                            gene_properties["children_CDS"] = gene_children_CDS_dict[original_feature['id']]
                            need_gene_properties = True
                        if original_feature['id'] in gene_children_mRNA_dict:
                            gene_properties["children_mRNA"] = gene_children_mRNA_dict[original_feature['id']]
                            need_gene_properties = True
                        if need_gene_properties:
                            new_feature['gene_properties'] = gene_properties 


                    #NEED MORE LOGIC HERE FOR PICKING UP ALL CHILDREN
#                        new_feature['gene_properties'] = gene_properties 

                    #see if it has lineages.  If it does, populate that data.
                    #WAIT INITIALLY


                    if new_feature['type'] not in feature_type_containers:
                        feature_type_containers[new_feature['type']] = dict()

                    feature_type_containers[new_feature['type']][new_feature['feature_id']] = new_feature

                    #print "Feature : %s" % str(new_feature)

                #def save_protein_container()                
                #save protein container 
                if len(protein_container['proteins']) > 0:
                    protein_container_provenance = [{"script": __file__, "script_ver": "0.1", "description": "proteins generated from old genome object %s in workspace %s " % (original_genome['data']['id'],source_wsname)}]
                    protein_container_not_saved = True
                    protein_container['protein_container_id'] = protein_container_object_name 
                    protein_container['name'] = protein_container_object_name 
                    protein_container['protein_count'] = len(protein_container['proteins']) 
                    while protein_container_not_saved:
                        try:
                            protein_container_info =  destination_ws_client.save_objects({"workspace": destination_workspace_name,"objects":[ { "type":"KBaseGenomesCondensedPrototypeV2.ProteinContainer","data":protein_container,"name": protein_container_object_name,"provenance":protein_container_provenance}]})
                            protein_container_not_saved = False
                        except biokbase.workspace.client.ServerError as err:
                            raise

                #def save_feature_container()
                #save feature containers.
                feature_container_references = dict()

                for type in feature_type_containers:
                    print "TYPE IN : " + type
                    feature_container_object_name = "%s_feature_container_%s" % (core_object_name,type)
                    feature_container_object_ref = "%s/%s" % (destination_workspace_name,feature_container_object_name) 
                    feature_container_references[type] = feature_container_object_ref
                    
                    feature_container = dict()
                    
                    feature_container['feature_container_id']= feature_container_object_name
                    feature_container['name']= feature_container_object_name
                    feature_container['type']= type
                    feature_container['features'] = feature_type_containers[type]
                    feature_container['assembly_ref'] = assembly_reference 
                    feature_container['feature_count'] = len(feature_type_containers[type])
                    feature_container_provenance = [{"script": __file__, "script_ver": "0.1", "description": "proteins generated from old genome object %s in workspace %s " % (original_genome['data']['id'],source_wsname)}]
                    feature_container_not_saved = True
                    while feature_container_not_saved: 
                        try: 
                            feature_container_info =  destination_ws_client.save_objects({"workspace":destination_workspace_name,"objects":[ { "type":"KBaseGenomesCondensedPrototypeV2.FeatureContainer","data":feature_container,"name": feature_container_object_name,"provenance":feature_container_provenance}]}) 
                            feature_container_not_saved = False 
                            print "Feature Container saved for %s" % (feature_container_object_name)
                        except biokbase.workspace.client.ServerError as err: 
                            raise

                #print "Feature lookup %s" % (feature_lookup)

                #def save_genome_annotation()

                #Then Finally store the GenomeAnnotation.
                genome_annotation['feature_lookup'] = feature_lookup
                genome_annotation['protein_container_ref'] = "%s/%s" % (destination_workspace_name, protein_container_object_name)
                genome_annotation['feature_container_references'] = feature_container_references
                genome_annotation_provenance = [{"script": __file__, "script_ver": "0.1", "description": "Genome Annotation generated from old genome object %s in workspace %s " % (original_genome['data']['id'],source_wsname)}] 
                genome_annotation_not_saved = True
                genome_annotation_object_name = core_object_name

                print "Genome Annotation id %s" % (genome_annotation['genome_annotation_id'])

                while genome_annotation_not_saved: 
                    try: 
                        genome_annotation_info =  destination_ws_client.save_objects({"workspace":destination_workspace_name,"objects":[ { "type":"KBaseGenomesCondensedPrototypeV2.GenomeAnnotation","data":genome_annotation,"name": genome_annotation_object_name,"provenance":genome_annotation_provenance}]}) 
                        genome_annotation_not_saved = False
                        print "Genome Annotation saved for %s" % (core_object_name) 
                    except biokbase.workspace.client.ServerError as err: 
                        raise
                object_counter = object_counter + 1

        if len(genomes_without_taxon_refs) > 0:
            print "GENOMES WITHOUT TAX REFERENCES \n" + "\n".join(genomes_without_taxon_refs)


#    with open(filename) as f:
#        content = f.read()
#    input_file_handle = open(filename, 'r')
#    content = input_file_handle.read()

#    start  = time.time()
#    save_info = ws.save_objects({"workspace":wsname,"objects":[ { "type":wstype,"data":simplejson.loads(content),"name":filename}]})
#    end = time.time()
#    print  >> sys.stderr, " saving " + wstype + " to ws, elapsed time " + str(end - start)


if __name__ == "__main__":
    import argparse
    import os.path

    parser = argparse.ArgumentParser(description='Create CondensedGenome from OriginalGenome')
    parser.add_argument('--source_wsname', nargs='?', help='workspace name to use grab from', required=True)
    parser.add_argument('--destination_wsname', nargs='?', help='workspace name to use to write to', required=True)
    parser.add_argument('--taxon_wsname', nargs='?', help='workspace name where the taxons are located.  Assumes destination ws url.', required=True)
    parser.add_argument('--source_wsurl',
                        action='store', type=str, nargs='?', required=True)
    parser.add_argument('--destination_wsurl',
                        action='store', type=str, nargs='?', required=True)
    parser.add_argument('--taxon_names_file', nargs='?', help='file with scientific name to taxon id mapping information in it.', required=True)  

#    parser.add_argument('--source_wsurl', nargs='1', required=True) 
#    parser.add_argument('--destination_wsurl', nargs='1', required=True) 
#    parser.add_argument('--source_wsurl', action='store', type=str, nargs='1', required=True) 
#    parser.add_argument('--destination_wsurl', action='store', type=str, nargs='1', required=True) 
    parser.add_argument('--lineage_files_dir', nargs=1, help='directory that holds lineage files for each genome with lineages.', required=True)
    parser.add_argument('genomes', action="store", nargs='*')
#    parser.add_argument('--genomes', action="store", nargs='*', help='list of genomes to do only')
    args, unknown = parser.parse_known_args()

    try: 
        convert_original_genome_object_to_prototype(source_wsname = args.source_wsname, 
                                                    destination_wsname = args.destination_wsname,
                                                    taxon_wsname = args.taxon_wsname,
                                                    taxon_names_file = args.taxon_names_file,
                                                    source_wsurl = args.source_wsurl,
                                                    destination_wsurl = args.destination_wsurl,
                                                    lineage_files_dir = args.lineage_files_dir,
                                                    genomes = args.genomes) 
    except Exception, e: 
        raise
        #sys.exit(1) 
    sys.exit(0) 






