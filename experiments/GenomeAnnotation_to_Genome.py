"""
Make a Genome from a GenomeAnnotation
"""
import argparse
import json
import logging
import os

from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.data_api.core import ObjectAPI

from doekbase.workspace.client import Workspace
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

GenomAnnotation_type = 'KBaseGenomeAnnotations.GenomeAnnotation-2.1'

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
    parser.add_argument('-g', dest='gaobj', help='GenomeAnnotation object', metavar='ID',
                        default="ReferenceGenomeAnnotations/kb|g.166819")
    args = parser.parse_args()
    return args

def main():

    args = parse_args()

    #genome_ref = '6838/146'#ReferenceGenomeAnnotations/kb|g.166819


    ga_api = GenomeAnnotationAPI(services, token=token, ref=args.gaobj)

    ga_object = ObjectAPI(services, token=token, ref=args.gaobj)
    asm_object = ObjectAPI(services, token=token, ref=(gaobj+"_assembly"))
    hey('external source: {}'.format(asm_object.get_data_subset(["external_source"])))

    tax_api = ga_api.get_taxon()

    asm_api = ga_api.get_assembly()


    genome_dict = dict()

    genome_dict['id'] = asm_object.get_data_subset(["external_source"])["external_source"]

    genome_dict['scientific_name'] = tax_api.get_scientific_name()
    genome_dict['domain'] = tax_api.get_domain()
    genome_dict['genetic_code'] = tax_api.get_genetic_code()
    genome_dict['dna_size'] = asm_api.get_dna_size()
    genome_dict['num_contigs'] = asm_api.get_number_contigs()

    genome_dict['contig_lengths'] = asm_api.get_contig_lengths()
    genome_dict['contig_ids'] = asm_api.get_contig_ids()
    genome_dict['source'] = asm_object.get_data_subset(["external_source_id"])["external_source_id"]
    genome_dict['source_id'] = asm_object.get_data_subset(["external_source"])["external_source"]
    genome_dict['md5'] = asm_object.get_data_subset(["md5"])["md5"]
    genome_dict['taxonomy'] = tax_api.get_scientific_lineage()
    genome_dict['gc_content'] = asm_api.get_gc_content()
    genome_dict['complete'] = 1

    #not loaded in GenomeAnnotation?
    #genome_dict['publications'] = 


    #the Contig list is duplicated in both Genome and ContigSet, 
    #per convention of the Genome uploader only the ContigSet field is populated

    feature_list = []
    proteins = ga_api.get_proteins()
    print "proteins"

    feature_ids = ga_api.get_feature_ids(filters={"type_list":['CDS']})
    if 'CDS' in feature_ids['by_type']:
        features_CDS = ga_api.get_features(feature_ids['by_type']['CDS'])
        print "CDS"

    for p in proteins:
        print p
        #print proteins[p].keys()
        feature_dict = dict()
        feature_dict['id'] = p

        if features_cds[p]:
            feature_dict['type'] = 'CDS'
        else :
              feature_dict['type'] = 'protein'        

        feature_dict['function'] = function = proteins[p]['function']
        feature_dict['protein_translation'] = proteins[p]['protein_amino_acid_sequence']        
        feature_dict['aliases'] = proteins[p]['protein_aliases']

        if features_cds[p]:
            feature_dict['location'] = features_cds[p]['feature_locations']        
            feature_dict['md5'] = features_cds[p]['feature_md5']
            feature_dict['dna_sequence'] = features_cds[p]['feature_dna_sequence'] 
            feature_dict['dna_sequence_length'] = features_cds[p]['feature_dna_sequence_length']


        feature_list.append(feature_dict)
        

    feature_ids_gene = ga_api.get_feature_ids(filters={"type_list":['gene']})
    print "ids gene"
    if 'gene' in feature_ids_gene['by_type']:
        features = ga_api.get_features(feature_ids_gene['by_type']['gene'])
        print"gene"

        for f in features:
            print f
            #print features[f]
            feature_dict = dict()
            feature_dict['id'] = features[f]['feature_id'] 
            feature_dict['location'] = features[f]['feature_locations']
            feature_dict['type'] = 'gene'
            feature_dict['function'] = features[f]['feature_function']
            feature_dict['md5'] = features[f]['feature_md5']
            feature_dict['protein_translation'] = ""
            feature_dict['dna_sequence'] = features[f]['feature_dna_sequence'] 
            feature_dict['dna_sequence_length'] = features[f]['feature_dna_sequence_length']
            feature_dict['aliases'] = features[f]['feature_aliases']
            feature_list.append(feature_dict)

        
        
    #RNA
    feature_ids_RNA = ga_api.get_feature_ids(filters={"type_list":['RNA']})
    print "ids RNA"

    if 'RNA' in feature_ids_RNA['by_type']:
        features = ga_api.get_features(feature_ids_RNA['by_type']['RNA'])
        print"gene"

        #obj.get_features(obj.get_feature_ids({'region_list':filters})['by_type']['gene'])

        for f in features:
            print f
            #print features[f]
            feature_dict = dict()
            feature_dict['id'] = features[f]['feature_id'] 
            feature_dict['location'] = features[f]['feature_locations']
            feature_dict['type'] = 'RNA'
            feature_dict['function'] = features[f]['feature_function']
            feature_dict['md5'] = features[f]['feature_md5']
            feature_dict['protein_translation'] = ""
            feature_dict['dna_sequence'] = features[f]['feature_dna_sequence'] 
            feature_dict['dna_sequence_length'] = features[f]['feature_dna_sequence_length']
            feature_dict['aliases'] = features[f]['feature_aliases']
            feature_list.append(feature_dict)



    genome_dict['features'] = feature_list



    _log.info('uploading workspace data')

    ref = '{}/1/1'.format(args.workspace_id)

    #fill with proper ref
    genome_dict['contigset_ref'] = ref


    name = genome_dict['id']
    if isinstance( genome_dict['id'], ( int, long ) ):
        name = str(genome_dict['id']) + "_Genome"

    ws_name = 'kb|ws.{}'.format(args.workspace_id)
    upload_workspace_data(
                genome_dict, services['ci']["workspace_service_url"], ref,
                ws_name, name)
    _log.info('done')

if __name__ == '__main__':
    main()
