import simplejson
import time
import sys
import biokbase.workspace.client
import re
import hashlib
import traceback
import os.path

def make_lineage(taxon_id=None,taxon_dict=None):
    lineages = list()
    length = 1
    if taxon_id == "1":
        print "in lineage 1"
    if taxon_id == "1":
        if taxon_id == "1":
            print "in lineage 3"
        length = 0
        return [length,""]        
    elif "parent_tax_id" in taxon_dict[taxon_id] and taxon_dict[taxon_id]["parent_tax_id"] != 1 :
        parent_tax_id = taxon_dict[taxon_id]["parent_tax_id"]
#        while parent_tax_id is not None:
        while parent_tax_id != "1":
            length = length + 1
            if "scientific_name" in taxon_dict[parent_tax_id]:
                lineages[:0]= [taxon_dict[parent_tax_id]["scientific_name"]]
            else:
                lineages[:0]= [""]
            if "parent_tax_id" in taxon_dict[parent_tax_id]:
                parent_tax_id = taxon_dict[parent_tax_id]["parent_tax_id"]
            else:
#                parent_tax_id = None
                parent_tax_id = 1
        if taxon_id == "1":
            print "in lineage 2"
        return [length,"; ".join(lineages)]
    else:
        if taxon_id == "1":
            print "in lineage 4"
        #one removed from root
        return [length,""]        



def make_taxons(wsname=None,wsurl=None, taxon_files_dir = None): 

    start  = time.time()
    print "Start time " + str(start)

    ws_client = biokbase.workspace.client.Workspace(wsurl)

    workspace_object = ws_client.get_workspace_info({'workspace':wsname})
    

    workspace_id = workspace_object[0]
    workspace_name = workspace_object[1]

    nodes_file =  "%s/nodes.dmp" % (taxon_files_dir[0])
    names_file =  "%s/names.dmp" % (taxon_files_dir[0]) 

    #MAKE THE UNKNOWN TAXON 
    unknown_taxon_dict = {"scientific_name":"Unknown","domain":"Unknown","scientific_lineage":"Unknown","genetic_code":0,"taxonomy_id":-1}
    unknown_not_saved = True
    unknown_provenance =  [{"script": __file__, "script_ver": "0.1", 
                            "description": "Unknown taxon created to seed catch all taxonomy for when a taxon can not be determined."}] 

    while unknown_not_saved:
        try:
            taxon_info =  ws_client.save_objects({"workspace": workspace_name,"objects":[ {"type":"KBaseGenomeAnnotations.Taxon",
                                                                                           "data":unknown_taxon_dict,
                                                                                           "name": "unknown_taxon",
                                                                                           "provenance":unknown_provenance}] })
            unknown_not_saved = False
        except Exception, e:
            print "SAVE FAILED ON UNKNOWN TAXON - GENERAL_EXCEPTION: " + str(sys.exc_info()[0]) + " Exception: " + str(e)
            sys.exit(1)

    taxon_dict = dict()
    #key is the taxonomy_id, values is an inner dict (parent_id, children_ids (list), 
    # genetic_code, scientific_name, aliases(list), lineage, parent_tax_id, 
    # rank, kingdom, embl_code, inherited_div_flag, inherited_GC_flag, mitochondrial_genetic_code, 
    # inherited_MGC_flag GenBank_hidden_flag hidden_subtree_flag division_id )

    #PHASE 1
    #OPEN BOTH FILES AND POPULATE DATA STRUCTURE

    node_dict = dict()

    print "NODES FILE : " + nodes_file
    if os.path.isfile(nodes_file): 
        print "Found nodes_lineage_File" 
        node_f = open(nodes_file, 'r') 

        for node_line in node_f: 
            temp_list = re.split(r'\t*\|\t*', node_line) 
            if temp_list[0] not in taxon_dict:
                taxon_dict[temp_list[0]] = dict()
#            if temp_list[0] != temp_list[1]:
            taxon_dict[temp_list[0]]["parent_tax_id"] = temp_list[1]
            
            if temp_list[0] == "1":
                print "FOUND ROOT"
            
            node_dict[temp_list[0]] = 1

            if temp_list[2] != '':
                taxon_dict[temp_list[0]]["rank"] = temp_list[2]
            if temp_list[3] != '':
                taxon_dict[temp_list[0]]["embl_code"] = temp_list[3]
            if temp_list[4] != '': 
                taxon_dict[temp_list[0]]["division_id"] = temp_list[4]
            if temp_list[5] != '':           
                taxon_dict[temp_list[0]]["inherited_div_flag"] = temp_list[5]
            if temp_list[6] != '':
                taxon_dict[temp_list[0]]["genetic_code"] = temp_list[6]
            if temp_list[7] != '':
                taxon_dict[temp_list[0]]["inherited_GC_flag"] = temp_list[7]
            if temp_list[8] != '':
                taxon_dict[temp_list[0]]["mitochondrial_genetic_code"] = temp_list[8]
            if temp_list[9] != '':
                taxon_dict[temp_list[0]]["inherited_MGC_flag"] = temp_list[9]
            if temp_list[10] != '':
                taxon_dict[temp_list[0]]["GenBank_hidden_flag"] = temp_list[10]
            if temp_list[11] != '':
                taxon_dict[temp_list[0]]["hidden_subtree_root_flag"] = temp_list[11]
            if temp_list[12] != '':
                taxon_dict[temp_list[0]]["comments"] = temp_list[12]

#            if temp_list[1] not in taxon_dict:
#                taxon_dict[temp_list[1]] = dict()
#            if "children_tax_ids" not in taxon_dict[temp_list[1]]:
#                taxon_dict[temp_list[1]]["children_tax_ids"]= list()
#            taxon_dict[temp_list[1]]["children_tax_ids"].append(temp_list[0])

        node_f.close()
    else:
        print "COULD NOT FIND nodes_File" 

    
    print "TOTAL NODE LENGTH " + str(len(node_dict))

    if "1" in taxon_dict:
        print str(taxon_dict["1"])
    
    if "2857" in taxon_dict:
        print "TRYING:" + str(taxon_dict["2857"])

    name_dict = dict()

    if os.path.isfile(names_file): 
        print "Found names_lineage_File" 
        name_f = open(names_file, 'r') 
 

        counter = 0
        for name_line in name_f: 
            temp_list = re.split(r'\t*\|\t*', name_line) 
            name_dict[temp_list[0]] = 1
            if temp_list[0] not in taxon_dict:
                print "Warning tax id %s in names file but not in nodes file" % (temp_list[0])
                continue
            if temp_list[3] == "scientific name":
                taxon_dict[temp_list[0]]["scientific_name"] = temp_list[1]
            else:
                if "aliases" not in taxon_dict[temp_list[0]]:
                    taxon_dict[temp_list[0]]["aliases"] = list()
                taxon_dict[temp_list[0]]["aliases"].append(temp_list[1])
#            counter = counter + 1
#            secondary_counter = 0
#            for item in temp_list:
#                print "Secondary Counter : " + str(secondary_counter) + " item: " + item
#                secondary_counter = secondary_counter + 1
#                if secondary_counter > 15:
#                    break
#            print "\n"
#            if counter > 5:
#                break
        name_f.close()
    else: 
        print "COULD NOT FIND names_File" 

    print "TOTAL NAME LENGTH " + str(len(name_dict))

    #PHASE 2
    #GO THROUGH TAXON_DICT and (compute lineages)(determine tree level)

    
    #key is level top is 1 and increasing down the tree.  Values are the list of tax_ids
    tax_level_dict = dict()
#    tax_level_list = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
#    counter = 1;    
    max_length = 1

    for taxon_id in taxon_dict:
        #Make lineages
        [length,taxon_dict[taxon_id]["lineage"]] = make_lineage(taxon_id, taxon_dict)

#        if taxon_id == "2857":
#            print "Tax id 2857 length = " + str(length)

#        if taxon_id == "7222":
#            print "Found 7222"
#            print "length for 7222: " + str(length)
#            print "Lineage for 7222: " + taxon_dict[taxon_id]["lineage"] + " :"

#        if length not in tax_level_list:
#            tax_level_list[length] = []
#        print "Level: " + str(length)

#        if length == 0:
#            print "Found a length of zero"
        if length not in tax_level_dict:
            tax_level_dict[length] = []
        tax_level_dict[length].append(taxon_id)
#        tax_level_list[length].append(taxon_id)
        if length > max_length:
            max_length = length

#        counter = counter + 1
#        print "Lineage: " + taxon_dict[taxon_id]["lineage"] 
#        if counter > 5:
#            break

    print "Max length : " + str(max_length)
#    tax_level_list = tax_level_list[:max_length]
#    sys.exit(0) 

    #(determine domain)(determine kingdom)(save objects)

    taxon_provenance = [{"script": __file__, "script_ver": "0.1", "description": "taxon generated from NCBI taxonomy names and nodes files downloaded on 7/20/2015."}]

    level_counter = 0

    for level_list_key in sorted(tax_level_dict.iterkeys()):
        level_list = tax_level_dict[level_list_key]
        print "Level Counter : " + str(level_counter) + " Length : " + str(len(tax_level_dict[level_list_key]))
        level_counter = level_counter + 1

    level_counter = 0
    objects_to_save_list = []
    save_counter = 0

#    print "Checking for issue"
#    if "2857" in taxon_dict:
#        print "pre_object exists : " + str(taxon_dict["2857"])
#    else:
#        print "2857 does not exist"

#    if "2857" in tax_level_list[7]:
#        print "Found in 7"
#    if "2857" in tax_level_list[8]:
#        print "Found in 8"
#    if "2857" in tax_level_list[9]:
#        print "Found in 9"




#    print "Debugging exit"
#    sys.exit(1)


    level_counter = 0
#    if 38 in tax_level_dict:
#        level_list = tax_level_dict[38]
    for level_list_key in sorted(tax_level_dict.iterkeys()):
        level_list = tax_level_dict[level_list_key]

        save_counter = 0
        print "Level Counter : " + str(level_counter) + " has a length of " + str(len(level_list))
        sys.stdout.flush()
        for taxon_id in level_list:
#            print "PROCESSING TAX ID : " + str(taxon_id)
#            if taxon_id == "1":
#                print "FOUND TAX 1 ROOT in save"
            taxon_object = dict()
            taxon_object_name = "%s_taxon" % (taxon_id)
            taxon_object["taxonomy_id"] = int(taxon_id)
            taxon_object["scientific_name"] = taxon_dict[taxon_id]["scientific_name"]
            taxon_object["scientific_lineage"] = taxon_dict[taxon_id]["lineage"]
            if taxon_id != "1":
                taxon_object["parent_taxon_ref"] = "%s/%s_taxon" % (workspace_name, taxon_dict[taxon_id]["parent_tax_id"])

            #Determine Domain
            if "Eukaryota" in taxon_dict[taxon_id]["lineage"]:
                taxon_object["domain"] = "Eukaryota"
            elif "Bacteria" in taxon_dict[taxon_id]["lineage"]:
                taxon_object["domain"] = "Bacteria"
            elif "Viruses" in taxon_dict[taxon_id]["lineage"]:
                taxon_object["domain"] = "Viruses"
            elif "Archaea" in taxon_dict[taxon_id]["lineage"]:
                taxon_object["domain"] = "Archaea"
            else:
                taxon_object["domain"] = "Unknown"

            #optional fields
            if "Fungi" in taxon_dict[taxon_id]["lineage"] and "Eukaryota" in taxon_dict[taxon_id]["lineage"]:
                taxon_object["kingdom"] = "Fungi"
            elif "Viridiplantae" in taxon_dict[taxon_id]["lineage"] and "Eukaryota" in taxon_dict[taxon_id]["lineage"]:
                taxon_object["kingdom"] = "Viridiplantae"
            elif "Metazoa" in taxon_dict[taxon_id]["lineage"] and "Eukaryota" in taxon_dict[taxon_id]["lineage"]:
                taxon_object["kingdom"] = "Metazoa"

            if "rank" in taxon_dict[taxon_id]:
                taxon_object["rank"] = taxon_dict[taxon_id]["rank"]
            if "embl_code" in taxon_dict[taxon_id]:
                taxon_object["embl_code"] = taxon_dict[taxon_id]["embl_code"]
            if "division_id" in taxon_dict[taxon_id]:
                taxon_object["division_id"] = int(taxon_dict[taxon_id]["division_id"])
            if "inherited_div_flag" in taxon_dict[taxon_id]:
                taxon_object["inherited_div_flag"] = int(taxon_dict[taxon_id]["inherited_div_flag"])
            if "genetic_code" in taxon_dict[taxon_id]:
                taxon_object["genetic_code"] = int(taxon_dict[taxon_id]["genetic_code"])

            if "inherited_GC_flag" in taxon_dict[taxon_id]:
                taxon_object["inherited_GC_flag"] = int(taxon_dict[taxon_id]["inherited_GC_flag"])
            if "mitochondrial_genetic_code" in taxon_dict[taxon_id]:
                taxon_object["mitochondrial_genetic_code"] = int(taxon_dict[taxon_id]["mitochondrial_genetic_code"])
            if "inherited_MGC_flag" in taxon_dict[taxon_id]:
                taxon_object["inherited_MGC_flag"] = int(taxon_dict[taxon_id]["inherited_MGC_flag"])
            if "GenBank_hidden_flag" in taxon_dict[taxon_id]:
                taxon_object["GenBank_hidden_flag"] = int(taxon_dict[taxon_id]["GenBank_hidden_flag"])
            if "hidden_subtree_root" in taxon_dict[taxon_id]:
                taxon_object["hidden_subtree_root"] = int(taxon_dict[taxon_id]["hidden_subtree_root"])
            if "comments" in taxon_dict[taxon_id]:
                taxon_object["comments"] = taxon_dict[taxon_id]["comments"]

            if "aliases" in taxon_dict[taxon_id]:
                taxon_object["aliases"] = taxon_dict[taxon_id]["aliases"]
            
#            objects_to_save_list.append( {"type":"KBaseGenomesCondensedPrototypeV2.Taxon",
#                                          "data":taxon_object, 
#                                          "name": taxon_object_name,
#                                          "provenance":taxon_provenance})
            save_counter = save_counter+1

#            if save_counter%1000 == 0 or save_counter == len(level_list):
        
            print "Save_Counter = " + str(save_counter)
            sys.stdout.flush()
            taxons_not_saved = True    
            save_start  = time.time()
            while taxons_not_saved:
                try:
                    taxon_info =  ws_client.save_objects({"workspace": workspace_name,"objects":[ {"type":"KBaseGenomeAnnotations.Taxon",
                                                                                                   "data":taxon_object, 
                                                                                                   "name": taxon_object_name, 
                                                                                                   "provenance":taxon_provenance}] }) 
                    taxons_not_saved = False 
                except biokbase.workspace.client.ServerError as err:
                    print "SAVE FAILED ON SAVE COUNTER " + str(save_counter) + " Taxon ID: " + str(taxon_id) + " ERROR: " + str(err)
                    #                        raise
                except KeyboardInterrupt:
                    print "Code execution stopped by user"
                    raise
                except:
                    print "SAVE FAILED ON SAVE COUNTER " + str(save_counter) + " Taxon ID: " + str(taxon_id) + " GENERAL_EXCEPTION: " + str(sys.exc_info()[0])
                #                        raise
#                objects_to_save_list = []
            save_end  = time.time()
            print  "elapsed time " + str(save_end - save_start) 
            sys.stdout.flush()

        level_counter = level_counter + 1

    end = time.time()
    print "End time " + str(end)
    print  "elapsed time " + str(end - start) 


if __name__ == "__main__":
    import argparse
    import os.path

    parser = argparse.ArgumentParser(description='Create TaxonObjects')
    parser.add_argument('--wsname', nargs='?', help='workspace name to populate', required=True)
    parser.add_argument('--wsurl', action='store', type=str, nargs='?', required=True)
    parser.add_argument('--taxon_files_dir', nargs=1, help='directory that holds names.dump and nodes.dump files.', required=True)
    args, unknown = parser.parse_known_args()

    try: 
        make_taxons(wsname = args.wsname, 
                    wsurl = args.wsurl,
                    taxon_files_dir = args.taxon_files_dir)
    except Exception, e: 
        raise
        #sys.exit(1) 
    sys.exit(0) 






