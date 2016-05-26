"""
Genome Annotation and Assembly converters.

Class hierarchy::

            Converter [base class]
              ^
              |
         +----+-----------------+
         |                      |
      AssemblyConverter     GenomeConverter
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '5/12/16'

# Stdlib
import hashlib
import itertools
import logging
import os
# Local
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.workspace.client import Workspace
from doekbase.handle.Client import AbstractHandle as handleClient
from doekbase.data_api.pbar import PBar

# Set up logging
_log = logging.getLogger('data_api.converter')
_ = logging.StreamHandler()
_.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
_log.addHandler(_)
DEBUG = lambda(s): _log.debug(s)
INFO = lambda(s): _log.info(s)
WARN = lambda(s): _log.warn(s)
ERROR = lambda(s): _log.error(s)

def set_converter_loglevel(level):
    """Set log level for converters in general"""
    logging.getLogger('data_api.converter').setLevel(level)

# Constants
contigset_type = 'KBaseGenomes.ContigSet-3.0'
ga_type = 'KBaseGenomeAnnotations.GenomeAnnotation-2.1'
genome_type = 'KBaseGenomes.Genome-8.0'

class Converter(object):
    class FTCode(object):
        CDS = 'CDS'
        RNA = 'RNA'
        GENE = 'gene'

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

    #: Override this in subclasses to create a naming convention
    #: between source and target objects.
    target_suffix = 'generic'

    def __init__(self, kbase_instance='ci', ref=None, show_progress_bar=False):
        """Create the converter.

        You will need to run :meth:`convert`, with a target workspace
        identifier, to actually perform the conversion.

        Args:
            kbase_instance (str): Short code for instance of KBase ('prod' or 'ci')
            ref (str): KBase object reference for the source object
            show_progress_bar (bool): If True, show a progress bar on stdout.
        """
        self.services = self.all_services[kbase_instance]
        self._kb_instance = kbase_instance
        self.obj_ref = ref
        self.api_obj = None
        self._target_name = None

        # connect to Handle service
        try:
            self.handle_client = handleClient(
                url=self.services['handle_service_url'], token=self.token)
        except Exception as err:
            ERROR('Cannot connect to handle service: {}'.format(err))
            raise
        # progress-bar nonsense
        self._show_pbar = show_progress_bar

    def get_target_name(self):
        """Form the target object name from the source name of `self.api_obj`.
        Uses class variable `target_suffix` to form the new name.
        Result is cached and re-used after first call.

        Returns:
            (str) target name
        Raises:
            ValueError, if self.api_obj is None
        """
        if self.api_obj is None:
            raise ValueError('Cannot get target name if source object is '
                             'not yet defined.')
        if self._target_name is None:
            source_name = self.api_obj.get_info()['object_name']
            self._target_name = source_name + '_' + self.target_suffix
        return self._target_name

    def _upload_to_workspace(self, data=None, target_ws=None, target_name=None,
                             type_=None):
        """Upload the data to the Workspace.
        Taken from Gavin's file converter.

        Args:
            data (dict): Populated ContigSet structure
            target_ws (str): Reference to target workspace
        Returns:
            (str) Workspace reference for created object
        """
        source_ref = self.obj_ref
        ws = Workspace(self.services['workspace_service_url'], token=self.token)
        INFO('Creating object {} in workspace {}'.format(target_name, target_ws))
        ws.save_objects(
            {'workspace': target_ws,
             'objects': [{'name': target_name,
                          'type': type_,
                          'data': data,
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
        return self._obj_prop('external_source', default='unknown')

    @property
    def external_source_id(self):
        return self._obj_prop('external_source_id', default='')


    def _obj_prop(self, name, default=None):
        return self.api_obj.get_data_subset([name]).get(name, default)


class GenomeConverter(Converter):
    """Convert a "new" GenomeAnnotation object to an "old"
       Genome/ContigSet object.
    """
    target_suffix = 'genome'

    def __init__(self, **kw):
        """Create the converter.

        See :class:`Converter` for keyword argument descriptions.
        """
        Converter.__init__(self, **kw)
        # Connect to API and retrieve object
        self.api_obj = GenomeAnnotationAPI(self.services, self.token, self.obj_ref)
        # overall genome MD5, see :meth:`_update_md5`, and `md5` property
        self._genome_md5 = hashlib.md5()

    def convert(self, workspace_name):
        taxon = self.api_obj.get_taxon()
        assembly = self.api_obj.get_assembly()
        contig_ids = assembly.get_contig_ids()
        contig_lengths = assembly.get_contig_lengths()
        self.proteins = self.api_obj.get_proteins()
        genome = {
            'id': self.get_target_name(), #self.external_source_id,
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
            'features': itertools.chain(*self._get_features_except({})),
            'complete': 1,
            'publications': [],
            'contigset_ref': self._create_contigset(assembly, workspace_name)
            #'quality': {},
            #'close_genomes': [],
            #'analysis_events': []
        }

        # this is calculated as we go along, so need to add last
        genome['md5'] = self.md5

        target_ref = self._upload(genome, workspace_name)
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
        INFO('Creating ContigSet from associated Assembly object: {}'.format(asm_ref))
        converter = AssemblyConverter(kbase_instance=self._kb_instance, ref=asm_ref, show_progress_bar=self._show_pbar)
        return converter.convert(workspace_name)

    def _get_features_except(self, types):
        """Get all features except those in `types`.

        Args:
            types (set<str>): Set of feature types to ignore
        Returns:
             list of iterators for each feature type found
        """
        return [self._get_features(ftype)
                for ftype in self.api_obj.get_feature_types()
                if ftype not in types]

    def _get_features(self, t):
        INFO('Getting features type={}'.format(t))
        features = self._get_features_by_type(t)
        if self._show_pbar and len(features) > 0:
            pbar = PBar(total=len(features))
        else:
            pbar = None
            if len(features) == 0:
                INFO('No features of type={}'.format(t))
        # eagerly update MD5, so lazy evaluation doesn't change result
        for name, val in features.iteritems():
            self._update_md5(val['feature_md5'])
        # generate one feature at a time
        for name, val in features.iteritems():
            if pbar and not _log.isEnabledFor(logging.DEBUG):
                pbar.inc(1)
            # if this is a CDS that codes for a protein, add info
            if t == self.FTCode.CDS and name in self.proteins:
                p_val = self.proteins[name]
                p_trans = p_val['protein_amino_acid_sequence']
                p_aliases = p_val.get('protein_aliases', {}).keys()
            else: # not a CDS and/or it doesn't code for a protein
                p_trans, p_aliases = '', []
            feature = {
                'id': name,
                'type': t,
                'function': val['feature_function'],
                'protein_translation': p_trans,
                'location': self._convert_feature_locations(
                    val['feature_locations']),
                'md5': val['feature_md5'],
                'dna_sequence': val['feature_dna_sequence'],
                'dna_sequence_length': val['feature_dna_sequence_length'],
                'aliases': val['feature_aliases'].keys() + p_aliases
            }
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
        ids = self.api_obj.get_feature_ids(filters={'type_list': [t]})['by_type'].get(t, [])
        return self.api_obj.get_features(ids) if ids else {}

    def _upload(self, data, target_ws):
        """Upload the data to the Workspace.
        Taken from Gavin's file converter.

        Args:
            data (dict): Populated ContigSet structure
            target_ws (str): Reference to target workspace
        Returns:
            (str) Workspace reference for created object
        """
        INFO('Uploading object to workspace "{}"'.format(target_ws))
        return self._upload_to_workspace(
            data=data, type_=genome_type,
            target_name=self.get_target_name(),
            target_ws=target_ws)

    # Object property accessors

    @property
    def md5(self):
        return self._genome_md5.hexdigest()

    def _update_md5(self, val):
        """Add some more bytes to the MD5 hash.
        """
        self._genome_md5.update(val)


class AssemblyConverter(Converter):
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

    target_suffix = 'contigset'

    def __init__(self, **kw):
        """Create the converter.

        See :class:`Converter` for descriptions of keyword arguments.
        """
        Converter.__init__(self, **kw)
        # Connect to AssemblyAPI and retrieve Assembly object
        self.api_obj = AssemblyAPI(self.services, self.token, self.obj_ref)
        # flags for handling over-large objects
        self.include_sequence, self.include_contigs = True, True

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
        contigset_ref = self._upload(contig_set_dict, workspace_name)
        return contigset_ref

    def _build_contig_set(self):
        """Build ContigSet dict from the Data API Assembly object.
        """
        INFO('getting contigs')
        contigs = self.api_obj.get_contigs()

        self._check_size()

        # Build the contig list
        if self.include_contigs:
            INFO('building contig list, length={:d}'.format(len(contigs)))
            contigs_list = self._build_contig_list(contigs)
        else:
            contigs_list = []

        # Construct top-level metadata
        a = self.api_obj # local alias
        asm_id = a.get_assembly_id()
        contig_set_dict = {
            'id': asm_id,
            'name': self.get_target_name(),
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
        sequence_size = self.api_obj.get_dna_size()
        num_contigs = self.api_obj.get_number_contigs()
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

    def _upload(self, contig_set, target_ws):
        """Upload the contigset data to the Workspace.

        Args:
            contig_set (dict): Populated ContigSet structure
            target_ws (str): Reference to target workspace
        Returns:
            (str) Workspace reference for created object
        """
        return self._upload_to_workspace(data=contig_set, target_ws=target_ws,
                                         type_=contigset_type,
                                         target_name=self.get_target_name())

    @property
    def md5(self):
        return self._obj_prop('md5')

    @property
    def fasta_handle_ref(self):
        return self._obj_prop('fasta_handle_ref', default='')


