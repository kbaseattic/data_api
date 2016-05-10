"""
Make a Genome from a GenomeAnnotation
"""
# Stdlib
import argparse
import itertools
import logging
import os
import sys
# Local
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
from doekbase.workspace.client import Workspace
from doekbase.handle.Client import AbstractHandle as handleClient

# Set up logging
_log = logging.getLogger('GenomeAnnotation')
_ = logging.StreamHandler()
_.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
_log.addHandler(_)
_log.setLevel(logging.INFO)
DEBUG = lambda(s): _log.debug(s)
INFO = lambda(s): _log.info(s)
WARN = lambda(s): _log.warn(s)
ERROR = lambda(s): _log.error(s)

# Constants
contigset_type = 'KBaseGenomes.ContigSet-3.0'
ga_type = 'KBaseGenomeAnnotations.GenomeAnnotation-2.1'


class Converter(object):
    """Convert a "new" GenomeAnnotation object to an "old" Genome/ContigSet object.
    """
    class FTCode(object):
        CDS = 'CDS'
        RNA = 'RNA'
        GENE = 'gene'
        PROTEIN = 'protein'

    all_services = {
        'ci': {
            "workspace_service_url": "https://ci.kbase.us/services/ws/",
            "shock_service_url": "https://ci.kbase.us/services/shock-api/",
            "handle_service_url": "https://ci.kbase.us/services/handle_service/"
        },
        'prod': {
            "workspace_service_url": "https://kbase.us/services/ws/",
            "shock_service_url": "https://kbase.us/services/shock-api/",
            "handle_service_url": "https://kbase.us/services/handle_service/"
        }
    }
    token = os.environ["KB_AUTH_TOKEN"]

    def __init__(self, kbase_instance='ci', ref=None, show_progress_bar=False):
        """Create the converter.

        You will need to run :meth:`convert`, with a target workspace
        identifier, to actually perform the conversion.

        Args:
            kbase_instance (str): Short code for instance of KBase ('prod' or 'ci')
            ref (str): KBase object reference for the source Assembly object,
                       e.g. "ReferenceGenomeAnnotations/kb|g.166819_assembly".
            show_progress_bar (bool): If True, show a progress bar on stdout.
        """
        self.services = self.all_services[kbase_instance]
        self.obj_ref = ref
        # Connect to API and retrieve object
        self.ga = GenomeAnnotationAPI(self.services, self.token, ref)

        INFO('external source: {}'.format(self.external_source))

        # connect to Handle service
        try:
            self.handle_client = handleClient(
                url=self.services['handle_service_url'], token=self.token)
        except Exception as err:
            ERROR('Cannot connect to handle service: {}'.format(err))
            raise

        self._show_pbar = show_progress_bar

    def convert(self, workspace_id):
        taxon = self.ga.get_taxon()
        assembly = self.ga.get_assembly()
        genome = {
            'id': self.external_source_id,
            'scientific_name': taxon.get_scientific_name(),
            'domain': taxon.get_domain(),
            'genetic_code': taxon.get_genetic_code(),
            'dna_size': assembly.get_dna_size(),
            'num_contigs': assembly.get_number_contigs(),
            'contig_lengths': assembly.get_contig_lengths(),
            'contig_ids': assembly.get_contig_ids(),
            'source': self.external_source,
            'source_id': self.external_source_id,
            'md5': self.md5,
            'taxonomy': taxon.get_scientific_lineage(),
            'gc_content': assembly.get_gc_content(),
            'complete': 1,
            'publications': []
        }
        # the Contig list is duplicated in both Genome and ContigSet,
        # per convention of the Genome uploader only the ContigSet field is populated

        INFO('populating features')
        genome['features']  = itertools.chain(self._get_proteins(),
                                              self._get_genes(),
                                              self._get_rna())

        INFO('uploading workspace data')

        ref = '{}/1/1'.format(workspace_id)

        # fill with proper ref
        genome['contigset_ref'] = ref

        name = genome['id']
        if isinstance(genome['id'], (int, long)):
            name = str(genome['id']) + "_Genome"

        INFO('uploading workspace data')
        ws_name = workspace_id
        target_ref = self._upload_to_workspace(genome, ws_name)
        return target_ref

    def _get_features_by_type(self, t):
        ids = self.ga.get_feature_ids(filters={'type_list': [t]})['by_type'].get(t, [])
        return self.ga.get_features(ids) if ids else []


    def _get_proteins(self):
        INFO('getting proteins')
        proteins = self.ga.get_proteins()
        cds_features = self._get_features_by_type(self.FTCode.CDS)
        for name, val in proteins.iteritems():
            DEBUG('add protein {}'.format(name))
            feature = {
                'id': name,
                'type': self.FTCode.PROTEIN,
                'function': val['function'],
                'protein_translation': val['protein_amino_acid_sequence'],
                'aliases': val['protein_aliases']
            }
            if name in cds_features:
                feature.update({
                'type': self.FTCode.CDS,
                'location': val['feature_locations'],
                'md5': val['feature_md5'],
                'dna_sequence': val['feature_dna_sequence'],
                'dna_sequence_length': val['feature_dna_sequence_length']
                })
            yield feature

    def _get_genes(self):
        return self._get_features(self.FTCode.GENE)

    def _get_rna(self):
        return self._get_features(self.FTCode.RNA)

    def _get_features(self, t):
        INFO('getting {}s'.format(t))
        features = self._get_features_by_type(t)
        for name, val in features.iteritems():
            DEBUG('add gene {}'.format(name))
            yield {
                'id': name,
                'type': t,
                'function': val['feature_function'],
                'protein_translation': '',
                'location': val['feature_locations'],
                'md5': val['feature_md5'],
                'dna_sequence': val['feature_dna_sequence'],
                'dna_sequence_length': val['feature_dna_sequence_length'],
                'aliases': val['feature_aliases']
            }

    def _upload_to_workspace(self, obj, target_ws):
        """Upload the data to the Workspace.
        Taken from Gavin's file converter.

        Args:
            obj (dict): Populated ContigSet structure
            target_ws (str): Reference to target workspace
        Returns:
            (str) Workspace reference for created object
        """
        source_ref = self.obj_ref
        ws = Workspace(self.services['workspace_service_url'], token=self.token)
        type_ = ga_type  # ws.translate_from_MD5_types([contigset_type])[contigset_type][0]
        ws.save_objects(
            {'workspace': target_ws,
             'objects': [{'name': obj['name'],
                          'type': type_,
                          'data': obj,
                          'provenance': [{'script': __name__,
                                          'script_ver': '1.2.3',
                                          'input_ws_objects': [source_ref],
                                          }]
                          }
                         ]
             }
        )
        return '{}/{}'.format(target_ws, obj['name'])


    # Object property accessors

    @property
    def external_source(self):
        return self._obj_prop('external_source')

    @property
    def external_source_id(self):
        return self._obj_prop('external_source_id')

    @property
    def fasta_handle_ref(self):
        return self._obj_prop('fasta_handle_ref')

    @property
    def md5(self):
        return self._obj_prop('md5')

    def _obj_prop(self, name):
        return self.ga.get_data_subset([name])[name]


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('workspace_id', default='6502')
    parser.add_argument('-o', dest='gaobj', help='GenomeAnnotation object (%(default)s)',
                        metavar='ID',
                        default="ReferenceGenomeAnnotations/kb|g.166819")
    parser.add_argument('-p', dest='progress', help='Show progress bar(s)',
                        action='store_true')
    parser.add_argument('-v', dest='vb', action='count', default=0,
                        help='Increase verbosity (repeatable)')
    return parser.parse_args()

def main():
    args = _parse_args()
    if args.vb > 1:
        _log.setLevel(logging.DEBUG)
    elif args.vb > 0:
        _log.setLevel(logging.INFO)
    else:
        _log.setLevel(logging.WARN)
    INFO('Initialize converter')
    converter = Converter(ref=args.gaobj, show_progress_bar=args.progress)
    INFO('Convert object')
    ref = converter.convert(workspace_id=args.workspace_id)
    INFO('Done.')
    print('Genome {} created'.format(ref))
    sys.exit(0)

    #genome_ref = '6838/146'#ReferenceGenomeAnnotations/kb|g.166819
    # ga_api = GenomeAnnotationAPI(services['ci'], token=token, ref=args.gaobj)
    # ga_object = ObjectAPI(services['ci'], token=token, ref=args.gaobj)
    # asm_object = ObjectAPI(services['ci'], token=token, ref=(args.gaobj+"_assembly"))
    # hey('external source: {}'.format(asm_object.get_data_subset(["external_source"])))
    # tax_api = ga_api.get_taxon()
    # asm_api = ga_api.get_assembly()

if __name__ == '__main__':
    main()
