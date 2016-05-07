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
from doekbase.data_api.core import ObjectAPI
from doekbase.handle.Client import AbstractHandle as handleClient

# Set up logging

_log = logging.getLogger('ContigSet')
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
_log.addHandler(_log_handler)
_log.setLevel(logging.INFO)
DEBUG = lambda(s): _log.debug(s)
INFO = lambda(s): _log.info(s)
WARN = lambda(s): _log.warn(s)
ERROR = lambda(s): _log.error(s)


# Constants

contigset_type = 'KBaseGenomes.ContigSet-3.0'

class Converter(object):
    """Convert a new Genome Assembly object to an old ContigSet object.

    For larger Eukaryotes, the new ContigSet may not be able to fit the
    sequence. In this case the sequence for *all* contigs will be dropped
    and a warning will be printed. In some extreme cases, even the contigs
    without sequence will be over the object size limit (see `MAX_OBJECT_BYTES`),
    in which case the contigs will be empty and the resulting object will be
    just the top-level metadata.

    To use, initialize with the Assembly object reference and the KBase instance
    abbreviation, then call :meth:`convert()` with the target workspace.
    """
    MAX_OBJECT_BYTES = 1e9 # Maximum size of object allowed by workspace (1GB, with slop)

    all_services = {
        'ci': {
            "workspace_service_url": "https://ci.kbase.us/services/ws/",
            "shock_service_url": "https://ci.kbase.us/services/shock-api/",
            "handle_service_url": "https://ci.kbase.us/services/handle_service/"
        }
    }
    token = os.environ["KB_AUTH_TOKEN"]

    def __init__(self, kbase_instance='ci', ref=None):
        self.services = self.all_services[kbase_instance]
        self.asm_ref = ref
        # Connect to AssemblyAPI and retrieve Assembly object
        self.asm = AssemblyAPI(self.services, self.token, ref)
        self.asm_object = ObjectAPI(self.services, token=self.token, ref=ref)

        INFO('external source: {}'.format(
            self.asm_object.get_data_subset(["external_source"])))

        # connect to Handle service
        try:
            self.handle_client = handleClient(
                url=self.services['handle_service_url'], token=self.token)
        except Exception as err:
            ERROR('Cannot connect to handle service: {}'.format(err))
            raise

        # flags for handling over-large objects
        self.include_sequence, self.include_contigs = True, True

    def convert(self, workspace_id=None):
        """Create ContigSet and upload it to the workspace.

        Args:
            workspace_id (str or int): Numeric workspace identifier
        """
        INFO('building contig_set')
        contig_set_dict = self._build_contig_set()

        INFO('uploading workspace data')
        ws_name = 'kb|ws.{}'.format(workspace_id)
        self._upload_to_workspace(contig_set_dict, ws_name)

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
        fasta_ref, fasta_node, fasta_handle = self._get_fasta_info()
        a = self.asm # local alias
        contig_set_dict = {
            'id': a.get_assembly_id(),
            'name': a.get_assembly_id(),
            'md5': a.get_data_subset(['md5'])['md5'],
            'source_id': a.get_data_subset(['external_source_id'])['external_source_id'],
            'source': a.get_data_subset(['external_source'])['external_source'],
            'reads_ref': '',
            'fasta_ref': fasta_handle,
            'contigs': contigs_list,
        }

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
                 'Dropping sequence.')
        elif sequence_size > self.MAX_OBJECT_BYTES:
            WARN('Sequence ({:d}) size is too big. Dropping sequence.'.format(sequence_size))
            self.include_sequence = False

    def _build_contig_list(self, contigs):
        """Build list of contigs as dictionary for ContigSet.
        """
        contigs_list = []
        for c_id, c_val in contigs.iteritems():
            DEBUG("contig: {}".format(c_id))
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
        return contigs_list

    def _get_fasta_info(self):
        """Get FASTA reference, shock node ID, and handle ID
        """
        # Get FASTA ref
        fasta_ref = self.asm_object.get_data_subset(['fasta_handle_ref'])['fasta_handle_ref']
        INFO("got FASTA ref: {}".format(fasta_ref))
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
        """
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


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('workspace_id', default='6502')
    parser.add_argument('-a', dest='asmobj', help='Assembly object', metavar='ID',
                        default="ReferenceGenomeAnnotations/kb|g.166819_assembly")
    parser.add_argument('-v', dest='vb', action='count', default=0,
                        help='Increase verbosity (repeatable)')
    return parser.parse_args()

if __name__ == '__main__':
    args = _parse_args()
    if args.vb > 1:
        _log.setLevel(logging.DEBUG)
    elif args.vb > 0:
        _log.setLevel(logging.INFO)
    else:
        _log.setLevel(logging.WARN)
    INFO('Initialize converter')
    converter = Converter(ref=args.asmobj)
    INFO('Convert object')
    converter.convert(workspace_id=args.workspace_id)
    INFO('Done')
    sys.exit(0)

