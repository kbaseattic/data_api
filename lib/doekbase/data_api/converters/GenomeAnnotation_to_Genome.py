"""
Make a Genome from a GenomeAnnotation
"""
# Stdlib
import argparse
import hashlib
import itertools
import logging
import os
import sys
# Local
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
from doekbase.workspace.client import Workspace
from doekbase.handle.Client import AbstractHandle as handleClient
from doekbase.data_api.converters import Assembly_to_ContigSet
from doekbase.data_api.pbar import PBar

# Set up logging
_log = logging.getLogger('data_api.converter.GenomeAnnotation_to_Genome')
_ = logging.StreamHandler()
_.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
_log.addHandler(_)
DEBUG = lambda(s): _log.debug(s)
INFO = lambda(s): _log.info(s)
WARN = lambda(s): _log.warn(s)
ERROR = lambda(s): _log.error(s)

def _set_converter_loglevel(level):
    """Set log level for converters in general"""
    logging.getLogger('data_api.converter').setLevel(level)

# Constants
contigset_type = 'KBaseGenomes.ContigSet-3.0'
ga_type = 'KBaseGenomeAnnotations.GenomeAnnotation-2.1'
genome_type = 'KBaseGenomes.Genome-8.0'


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
        self._kb_instance = kbase_instance
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
        # progress-bar nonsense
        self._show_pbar = show_progress_bar
        # overall genome MD5, see `_update_md5` and md5 property
        self._genome_md5 = hashlib.md5()

    def convert(self, workspace_name):
        taxon = self.ga.get_taxon()
        assembly = self.ga.get_assembly()
        contig_ids = assembly.get_contig_ids()
        contig_lengths = assembly.get_contig_lengths()
        genome = {
            'id': self.external_source_id,
            'scientific_name': taxon.get_scientific_name(),
            'domain': taxon.get_domain(),
            'genetic_code': taxon.get_genetic_code(),
            'dna_size': assembly.get_dna_size(),
            'num_contigs': assembly.get_number_contigs(),
            'contig_ids': contig_ids,
            'contig_lengths': [contig_lengths[cid] for cid in contig_ids],
            'source': self.external_source,
            'source_id': self.external_source_id,
            'taxonomy': ';'.join(taxon.get_scientific_lineage()),
            'gc_content': assembly.get_gc_content(),
            'complete': 1,
            'publications': [],
            'features': list(itertools.chain(self._get_proteins(),
                                              self._get_genes(),
                                              self._get_rna())),
            'contigset_ref': self._create_contigset(assembly, workspace_name)
            #'quality': {},
            #'close_genomes': [],
            #'analysis_events': []
        }

        # this is calculated as we go along, so need to add last
        genome['md5'] = self.md5

        # the Contig list is duplicated in both Genome and ContigSet,
        # per convention of the Genome uploader only the ContigSet field is populated

        INFO('uploading workspace data')
        target_ref = self._upload_to_workspace(genome, workspace_name)
        return target_ref

    def _create_contigset(self, asm, workspace_name):
        """Invoke the Assembly to ContigSet converter to create a new ContigSet object.

        Args:
            - asm (Assembly): Genome Assembly object associated with this Annotation.
            - workspace_name (str): Target workspace name
        Returns:
            Workspace reference for new ContigSet
        """
        asm_info = asm.get_info()
        asm_ref = asm_info['object_reference_versioned']
        INFO('creating ContigSet from associated Assembly object: {}'.format(asm_ref))
        converter = Assembly_to_ContigSet.Converter(kbase_instance=self._kb_instance, ref=asm_ref,
                                                    show_progress_bar=self._show_pbar)
        return converter.convert(workspace_name)

    def _get_proteins(self):
        INFO('getting proteins')
        proteins = self.ga.get_proteins()
        cds_features = self._get_features_by_type(self.FTCode.CDS)
        if self._show_pbar and len(proteins) > 0:
            pbar = PBar(total=len(proteins))
        else:
            pbar = None
            if len(proteins) == 0:
                INFO('No proteins')
        in_cds_features = 0
        for name, val in proteins.iteritems():
            if pbar and not _log.isEnabledFor(logging.DEBUG):
                pbar.inc(1)
            try:
                feature = {
                    'id': name,
                    'type': self.FTCode.PROTEIN,
                    'function': val['protein_function'],
                    'protein_translation': val['protein_amino_acid_sequence'],
                    'aliases': val.get('protein_aliases',{}).keys()
                }
                if name in cds_features:
                    in_cds_features += 1
                    cds_val = cds_features[name]
                    feature.update({
                    'type': self.FTCode.CDS,
                    'location': self._convert_feature_locations(cds_val.get('feature_locations',[])),
                    'md5': cds_val['feature_md5'],
                    'dna_sequence': cds_val.get('feature_dna_sequence',''),
                    'dna_sequence_length': cds_val['feature_dna_sequence_length']
                    })
                    feature['aliases'].extend(
                        cds_val['feature_aliases'].keys())
                    self._update_md5(feature['md5'])
                else:
                    INFO('protein {} not CDS'.format(name))
            except KeyError as err:
                ERROR('populating feature {}: bad value: {}'.format(name, val))
                raise
            if _log.isEnabledFor(logging.DEBUG):
                DEBUG('adding protein {} md5={}'.format(
                    feature['id'], feature.get('md5','<empty>')))
            yield feature
        if pbar:
            pbar.done()
        INFO('{:d} proteins also CDS, {:d} proteins were not'.format(
            in_cds_features, len(proteins) - in_cds_features))

    def _get_genes(self):
        return self._get_features(self.FTCode.GENE)

    def _get_rna(self):
        return self._get_features(self.FTCode.RNA)

    def _get_features(self, t):
        INFO('getting features type={}'.format(t))
        features = self._get_features_by_type(t)
        if self._show_pbar and len(features) > 0:
            pbar = PBar(total=len(features))
        else:
            pbar = None
            if len(features) == 0:
                INFO('No features of type={}'.format(t))
        for name, val in features.iteritems():
            if pbar and not _log.isEnabledFor(logging.DEBUG):
                pbar.inc(1)
            feature = {
                'id': name,
                'type': t,
                'function': val['feature_function'],
                'protein_translation': '',
                'location': self._convert_feature_locations(
                    val['feature_locations']),
                'md5': val['feature_md5'],
                'dna_sequence': val['feature_dna_sequence'],
                'dna_sequence_length': val['feature_dna_sequence_length'],
                'aliases': val['feature_aliases'].keys()
            }
            self._update_md5(feature['md5'])
            if _log.isEnabledFor(logging.DEBUG):
                DEBUG('adding feature {} md5={}'.format(
                    feature['id'], feature.get('md5','<empty>')))
            yield feature
        if pbar:
            pbar.done()

    def _convert_feature_locations(self, locations):
        """Convert feature location dict returned from
        GenomeAnnotation API `get_features()` to the tuple in the Genome.
        """
        return [(loc['contig_id'], loc['start'], loc['strand'], loc['length'])
                for loc in locations]

    def _get_features_by_type(self, t):
        ids = self.ga.get_feature_ids(filters={'type_list': [t]})['by_type'].get(t, [])
        return self.ga.get_features(ids) if ids else {}

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
        type_ = genome_type  # ws.translate_from_MD5_types([contigset_type])[contigset_type][0]
        target_name = self.ga.get_info()['object_name'] + '_Genome'
        INFO('Creating object {} in workspace {}'.format(target_name, target_ws))
        ws.save_objects(
            {'workspace': target_ws,
             'objects': [{'name': target_name,
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
        return '{}/{}'.format(target_ws, target_name)


    # Object property accessors

    @property
    def external_source(self):
        return self._obj_prop('external_source',default='unknown')

    @property
    def external_source_id(self):
        return self._obj_prop('external_source_id', default='')

    @property
    def fasta_handle_ref(self):
        return self._obj_prop('fasta_handle_ref', default='')

    @property
    def md5(self):
        return self._genome_md5.hexdigest()

    def _update_md5(self, val):
        self._genome_md5.update(val)

    def _obj_prop(self, name, default=None):
        return self.ga.get_data_subset([name]).get(name, default)


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('workspace', default='6502')
    parser.add_argument('-o', dest='gaobj', help='GenomeAnnotation object (%(default)s)',
                        metavar='ID',
                        default="ReferenceGenomeAnnotations/kb|g.166819")
    parser.add_argument('-p', dest='progress', help='Show progress bar(s)',
                        action='store_true')
    parser.add_argument('-v', dest='vb', action='count', default=0,
                        help='Increase verbosity (repeatable)')
    parser.add_argument('-k', dest='kbdep', default='ci', metavar='DEPLOYMENT',
                        help='KBase deployment, "ci" or "prod" (default=ci)')
    return parser.parse_args()

def main():
    args = _parse_args()
    kbase_instance = args.kbdep.lower()
    if not kbase_instance in ['ci', 'prod']:
        ERROR('-k option value must be "ci" or "prod"')
        sys.exit(1)
    if args.vb > 1:
        _set_converter_loglevel(logging.DEBUG)
    elif args.vb > 0:
        _set_converter_loglevel(logging.INFO)
    else:
        _set_converter_loglevel(logging.WARN)
    INFO('Initialize converter')
    converter = Converter(ref=args.gaobj, show_progress_bar=args.progress,
                          kbase_instance=kbase_instance)
    INFO('Convert object')
    # Get name for workspace
    workspace_name = args.workspace
    try:
        ws_int_id = int(workspace_name)
        workspace_name = Workspace(url=Converter.all_services[kbase_instance]['workspace_service_url'], token=Converter.token).get_workspace_info({'id': ws_int_id})[1]
        INFO('Workspace ID={} converted to name={}'.format(ws_int_id, workspace_name))
    except ValueError:
        pass
    ref = converter.convert(workspace_name=workspace_name)
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
