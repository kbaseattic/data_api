"""
Make a ContigSet
"""
import argparse
import json
import logging
import os
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.workspace.client import Workspace
from doekbase.data_api.core import ObjectAPI
from doekbase.handle.Client import AbstractHandle as handleClient

services = {
    'ci': {
        "workspace_service_url": "https://ci.kbase.us/services/ws/",
        "shock_service_url": "https://ci.kbase.us/services/shock-api/",
        "handle_service_url": "https://ci.kbase.us/services/handle_service/"
    }
}

token = os.environ["KB_AUTH_TOKEN"]

contigset_type = 'KBaseGenomes.ContigSet-3.0'

_log = logging.getLogger('ContigSet')
_ = logging.StreamHandler()
_.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
_log.addHandler(_)
_log.setLevel(logging.INFO)

def hey(s):
    _log.info(s)


#from Gavin's file converter
def upload_workspace_data(cs, ws_url, source_ref, target_ws, obj_name):
    ws = Workspace(ws_url, token=token)
    type_ = contigset_type #ws.translate_from_MD5_types([contigset_type])[contigset_type][0]
    ws.save_objects(
        {'workspace': target_ws,
         'objects': [{'name': obj_name,
                      'type': type_,
                      'data': cs,
                      'provenance': [{'script': 'fakey',
                                      'script_ver': '1.2.3',
                                      'input_ws_objects': [source_ref],
                                      }]
                      }
                     ]
         }
    )

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('workspace_id', default='6502')
    parser.add_argument('-a', dest='asmobj', help='Assembly object', metavar='ID',
                        default="ReferenceGenomeAnnotations/kb|g.166819_assembly")
    args = parser.parse_args()
    return args

def main():

    args = parse_args()
    asm = AssemblyAPI(services['ci'], token, args.asmobj)
    asm_object = ObjectAPI(services['ci'], token=token, ref=args.asmobj)
    hey('external source: {}'.format(asm_object.get_data_subset(["external_source"])))

    hey('getting contigs')
    contigs = asm.get_contigs()

    # assembly length + 1000 x # contigs < 1G ?
    onlyshockseq = asm.get_dna_size() + 1000*asm.get_number_contigs() > 1000000000

    hey('building contig list')
    contigs_list = []
    for c in contigs:
        hey("contig: {}".format(c))
        contig_dict = dict()
        contig_dict['id'] = contigs[c]['contig_id']
        contig_dict['length'] = contigs[c]['length']
        contig_dict['name'] = contigs[c]['name']
        contig_dict['description'] = contigs[c]['description']
        contig_dict['md5'] = contigs[c]['md5']
        contig_dict['sequence'] =  contigs[c]['sequence']

        contigs_list.append(contig_dict)

    hey('building contig_set')
    contig_set_dict = dict()

    contig_set_dict['md5'] = asm.get_data_subset(["md5"])['md5']
    contig_set_dict['id'] = asm.get_assembly_id()
    contig_set_dict['name'] = asm.get_assembly_id()
    contig_set_dict['source'] = asm.get_data_subset(['external_source'])['external_source']
    contig_set_dict['source_id'] = asm.get_data_subset(['external_source_id'])['external_source_id']

    contig_set_dict['contigs'] = contigs_list



    #pillaged from Assembly API
    fasta_ref = asm_object.get_data_subset(['fasta_handle_ref'])['fasta_handle_ref']
    hey("got FASTA ref: {}".format(fasta_ref))

    try:
        hc = handleClient(url=services['ci']["handle_service_url"], token=token)
        hey('handle client: {}'.format(hc))
        handle = hc.hids_to_handles([fasta_ref])[0]
        hey('handle value: {}'.format(handle))
        handle_id = handle['id']
        hey('handle ID: {}'.format(handle_id))
    except Exception as e:
        print e
        print ("Failed to retrieve handle {} from {}"
               .format(fasta_ref,
                       services['ci']["handle_service_url"]))


    #shock_node_id = fasta_ref

    contig_set_dict['fasta_ref'] = fasta_ref


    _log.info('uploading workspace data')

    ref = '{}/1/1'.format(args.workspace_id)
    ws_name = 'kb|ws.{}'.format(args.workspace_id)
    upload_workspace_data(
                contig_set_dict, services['ci']["workspace_service_url"], ref,
                ws_name, contig_set_dict['name'])
    _log.info('done')

if __name__ == '__main__':
    main()
