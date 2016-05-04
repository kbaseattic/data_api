from doekbase.data_api.sequence.assembly.api import AssemblyAPI

services = {"workspace_service_url": "https://ci.kbase.us/services/ws/",
            "shock_service_url": "https://ci.kbase.us/services/shock-api/",
            "handle_service_url": "https://ci.kbase.us/services/handle_service/"}

import os
token = os.environ["KB_AUTH_TOKEN"]

from doekbase.data_api.core import ObjectAPI

from doekbase.handle.Client import AbstractHandle as handleClient


asm = AssemblyAPI(services, token, "ReferenceGenomeAnnotations/kb|g.166819_assembly")

asm_object = ObjectAPI(services, token=token, ref="ReferenceGenomeAnnotations/kb|g.166819_assembly")
print asm_object.get_data_subset(["external_source"])


#from Gavin's file converter
def upload_workspace_data(cs, ws_url, source_ref, target_ws, obj_name):
    ws = Workspace(ws_url, token=TOKEN)
    type_ = ws.translate_from_MD5_types([CS_MD5_TYPE])[CS_MD5_TYPE][0]
    ws.save_objects(
        {'workspace': target_ws,
         'objects': [{'name': obj_name,
                      'type': type_,
                      'data': cs,
                      'provenance': [{'script': SCRIPT_NAME,
                                      'script_ver': __VERSION__,
                                      'input_ws_objects': [source_ref],
                                      }]
                      }
                     ]
         }
    )




contigs = asm.get_contigs()

onlyshockseq = 0
#assembly length + 1000 x # contigs < 1G ?
if asm.get_dna_size() + 1000*asm.get_number_contigs() > 1000000000:
    print "storing contig sequence only in shock"
    onlyshockseq = 1

contigs_list = []
for c in contigs:
    print c
    contig_dict = dict()
    contig_dict['id'] = contigs[c]['contig_id']
    contig_dict['length'] = contigs[c]['length']
    contig_dict['name'] = contigs[c]['name']
    contig_dict['description'] = contigs[c]['description']        
    contig_dict['md5'] = contigs[c]['md5']    
    contig_dict['sequence'] =  contigs[c]['sequence'] 
    
    contigs_list.append(contig_dict)


contig_set_dict = dict()

contig_set_dict['md5'] = asm.get_data_subset(["md5"])
contig_set_dict['id'] = asm.get_assembly_id()
contig_set_dict['name'] = asm.get_assembly_id()
contig_set_dict['source'] = asm.get_data_subset(['external_source'])
contig_set_dict['source_id'] = asm.get_data_subset(['external_source_id'])

contig_set_dict['contigs'] = contigs_list



#pillaged from Assembly API
shock_node_id = None
fasta_ref = asm_object.get_data_subset(['fasta_handle_ref'])
try:
    hc = handleClient(url=services["handle_service_url"], token=token)
    print hc
    handle = hc.hids_to_handles([fasta_ref])
    print handle
    shock_node_id = handle["id"]
except Exception as e:
    print e
    print ("Failed to retrieve handle {} from {}".format(fasta_ref,
                                                             services["handle_service_url"]))

#this code currently gives an error, the handle is empty?


shock_node_id = fasta_ref
    
contig_set_dict['fasta_ref'] = shock_node_id


import json
upload_data = json.dumps(contig_set_dict)

#ref = str(info[6]) + '/' + str(info[0]) + '/' + str(info[4])
ref = str(0)+'/'+str(0)+"/"+str(0)
upload_workspace_data(
            contig_set_dict, services["workspace_service_url"], ref,
            args.destination_workspace_name, contig_set_dict['name'])



