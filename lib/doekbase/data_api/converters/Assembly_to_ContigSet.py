"""
Make a ContigSet object from an Assembly object.
"""

# Imports

# Stdlib
import argparse
import logging
import os
import sys
# Local
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.workspace.client import Workspace
from doekbase.handle.Client import AbstractHandle as handleClient
from doekbase.data_api.pbar import PBar # progress-bar

# Set up logging

_log = logging.getLogger('data_api.converter.Assembly_to_Contigset')
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
_log.addHandler(_log_handler)
DEBUG = lambda(s): _log.debug(s)
INFO = lambda(s): _log.info(s)
WARN = lambda(s): _log.warn(s)
ERROR = lambda(s): _log.error(s)

def _set_converter_loglevel(level):
    """Set log level for converters in general"""
    logging.getLogger('data_api.converter').setLevel(level)

# Constants

contigset_type = 'KBaseGenomes.ContigSet-3.0'

class Converter(object):
    """Convert a "new" Genome Assembly object to an "old" ContigSet object.

    For larger Eukaryotes, the sequence may not fit in a single workspace
    object (limit is in `MAX_OBJECT_BYTES`), which is how the ContigSet stores it.
    In this case, the sequence for *all* contigs will be dropped
    and a warning will be printed. In some extreme cases in which even the contigs
    without sequence will be over the object size limit, the list of contigs will be
    empty (zero-length) and the resulting object will be just the top-level metadata.

    To perform the conversion, construct this class with the Assembly object
    reference and the KBase instance abbreviation (see keys of `all_services`), then
    call :meth:`convert()` with the target workspace.
    """
    MAX_OBJECT_BYTES = 1e9 # Maximum size of object allowed by workspace (1GB, with slop)

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
        """
        self.services = self.all_services[kbase_instance]
        self.asm_ref = ref
        # Connect to AssemblyAPI and retrieve Assembly object
        self.asm = AssemblyAPI(self.services, self.token, ref)

        INFO('external source: {}'.format(self.external_source))

        # connect to Handle service
        try:
            self.handle_client = handleClient(
                url=self.services['handle_service_url'], token=self.token)
        except Exception as err:
            ERROR('Cannot connect to handle service: {}'.format(err))
            raise

        # flags for handling over-large objects
        self.include_sequence, self.include_contigs = True, True

        self._show_pbar = show_progress_bar

    def convert(self, workspace_name=None):
        """Create ContigSet and upload it to the workspace.

        Args:
            workspace_name (str): Workspace identifier (name)
        Returns:
            (str) Workspace reference of created object
        """
        INFO('building contig_set')
        contig_set_dict = self._build_contig_set()

        INFO('uploading workspace data')
        contigset_ref = self._upload_to_workspace(contig_set_dict, workspace_name)
        return contigset_ref

    def _build_contig_set(self):
        """Build ContigSet dict from the Data API Assembly object.
        """
        INFO('getting contigs')
        contigs = self.asm.get_contigs()

        self._check_size()

        # Build the contig list
        if self.include_contigs:
            INFO('building contig list, length={:d}'.format(len(contigs)))
            contigs_list = self._build_contig_list(contigs)
        else:
            contigs_list = []

        # Construct top-level metadata
        a = self.asm # local alias
        asm_id = a.get_assembly_id()
        contig_set_dict = {
            'id': asm_id,
            'name': asm_id,
            'md5': self.md5,
            'source_id': self.external_source_id,
            'source': self.external_source,
            'reads_ref': '',
            'contigs': contigs_list,
        }
        fasta_ref, fasta_node, fasta_handle = self._get_fasta_info()
        if fasta_handle is not None:
            contig_set_dict['fasta_ref'] = fasta_handle

        return contig_set_dict

    def _check_size(self):
        """Logic for dropping sequence, or all contigs, if they are too big.

        Results are recorded in instance variables `include_sequence` and `include_contigs`.
        """
        sequence_size = self.asm.get_dna_size()
        num_contigs = self.asm.get_number_contigs()
        contigs_size = num_contigs * 1000
        if contigs_size > self.MAX_OBJECT_BYTES:
            self.include_sequence = False
            self.include_contigs = False
            WARN('Contig size ({:d} =~ {:d} bytes) is too big, even without sequence. '
                 'Dropping all contigs! All that will remain is metadata.'
                 .format(num_contigs, contigs_size))
        elif sequence_size + contigs_size > self.MAX_OBJECT_BYTES:
            self.include_sequence = False
            WARN('Sequence ({:d}) and contigs ({:d} =~ {:d} bytes) size together is too big. '
                 'Dropping sequence.'.format(sequence_size, num_contigs, contigs_size))
        elif sequence_size > self.MAX_OBJECT_BYTES:
            WARN('Sequence ({:d}) size is too big. Dropping sequence.'.format(sequence_size))
            self.include_sequence = False

    def _build_contig_list(self, contigs):
        """Build list of contigs as dictionary for ContigSet.
        """
        pbar = PBar(len(contigs), 60) if self._show_pbar else None
        contigs_list = []
        for c_id, c_val in contigs.iteritems():
            if _log.isEnabledFor(logging.DEBUG):
                DEBUG("contig: {}".format(c_id))
            elif pbar:
                pbar.inc(1)
            contig_dict = {
                'id': c_val['contig_id'],
                'length': c_val['length'],
                'md5': c_val['md5'],
                'sequence': c_val['sequence'] if self.include_sequence else '',
                'name': c_val['name'],
                'description': c_val['description'],
                # 'genetic_code': ??,
                # 'cell_compartment': ??,
                # 'replicon_geometry': ??,
                # 'complete': ??,
            }
            contigs_list.append(contig_dict)
        if pbar:
            pbar.done()
        return contigs_list

    def _get_fasta_info(self):
        """Get FASTA reference, shock node ID, and handle ID
        """
        # Get FASTA ref
        fasta_ref = self.fasta_handle_ref
        if fasta_ref is None:
            WARN('no FASTA handle ref. found in Assembly')
            return None, None, None
        INFO('got FASTA ref: {}'.format(fasta_ref))
        # Get Handle for FASTA ref
        handles = self.handle_client.hids_to_handles([fasta_ref])
        if len(handles) != 1:
            if len(handles) > 1:
                raise ValueError('Too many handles ({:d}) for FASTA ref "{}"'
                                 .format(len(handles), fasta_ref))
            else:
                raise ValueError('No handles for FASTA ref {}'.format(fasta_ref))
        fasta_handle = handles[0]['hid']
        fasta_node = handles[0]['id']
        INFO('handle ID: {}'.format(fasta_handle))
        return fasta_ref, fasta_node, fasta_handle

    def _upload_to_workspace(self, contig_set, target_ws):
        """Upload the contigset data to the Workspace.
        Taken from Gavin's file converter.

        Args:
            contig_set (dict): Populated ContigSet structure
            target_ws (str): Reference to target workspace
        Returns:
            (str) Workspace reference for created object
        """
        INFO('Uploading "{}" to target workspace: {}'.format(contig_set['name'], target_ws))
        source_ref = self.asm_ref
        ws = Workspace(self.services['workspace_service_url'], token=self.token)
        type_ = contigset_type #ws.translate_from_MD5_types([contigset_type])[contigset_type][0]
        ws.save_objects(
            {'workspace': target_ws,
             'objects': [{'name': contig_set['name'],
                          'type': type_,
                          'data': contig_set,
                          'provenance': [{'script': __name__,
                                          'script_ver': '1.2.3',
                                          'input_ws_objects': [source_ref],
                                          }]
                          }
                         ]
             }
        )
        return '{}/{}'.format(target_ws, contig_set['name'])

    # Object property accessors

    @property
    def external_source(self):
        return self._asm_prop('external_source', default='unknown')

    @property
    def external_source_id(self):
        return self._asm_prop('external_source_id', default='')

    @property
    def fasta_handle_ref(self):
        return self._asm_prop('fasta_handle_ref')

    @property
    def md5(self):
        return self._asm_prop('md5')

    def _asm_prop(self, name, default=None):
        return self.asm.get_data_subset([name]).get(name, default)


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('workspace', default='6502')
    parser.add_argument('-a', dest='asmobj', help='Assembly object (%(default)s)', metavar='ID',
                        default="ReferenceGenomeAnnotations/kb|g.166819_assembly")
    parser.add_argument('-p', dest='progress', help='Show progress bar(s)',
                        action='store_true')
    parser.add_argument('-v', dest='vb', action='count', default=0,
                        help='Increase verbosity (repeatable)')
    return parser.parse_args()

if __name__ == '__main__':
    args = _parse_args()
    if args.vb > 1:
        _set_converter_loglevel(logging.DEBUG)
    elif args.vb > 0:
        _set_converter_loglevel(logging.INFO)
    else:
        _set_converter_loglevel(logging.WARN)
    INFO('Initialize converter')
    converter = Converter(ref=args.asmobj, show_progress_bar=args.progress)
    INFO('Convert object')
    # Get name for workspace
    workspace_name = args.workspace
    try:
        ws_int_id = int(workspace_name)
        workspace_name = Workspace(url=Converter.all_services['ci'], token=Converter.token).get_workspace_info(ws_int_id)[1]
        INFO('Workspace ID={} converted to name={}'.format(ws_int_id, workspace_name))
    except ValueError:
        pass
    ref = converter.convert(workspace_name=workspace_name)
    INFO('Done.')
    print('ContigSet {} created'.format(ref))
    sys.exit(0)

