"""
Genome Annotation and Assembly converters.

Class hierarchy::

            base.Converter
              ^
              |
         +----+-----------------+
         |                      |
      AssemblyConverter     GenomeConverter

Usage::

    from doekbase.data_api.converters import genome

    # Genome annotation
    obj = genome.GenomeConverter(ref='6052/40/1', kbase_instance='ci')
    new_obj_ref = obj.convert(target_workspace_id)
    # NOTE: side-effect of this conversion is to also create a ContigSet
    # object, by converting the associated Assembly, in the same workspace.

    # Assembly
    obj = genome.AssemblyConverter(ref='6052/31/1', kbase_instance='ci')
    new_obj_ref = obj.convert(target_workspace_id)
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '5/12/16'

# Stdlib
import hashlib
import itertools
import logging
# Local
from . import base
from .base import DEBUG, INFO, WARN, ERROR
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.pbar import PBar

_log = logging.getLogger('data_api.converter.genome')

def set_converter_loglevel(level):
    """Set log level for converters in general"""
    logging.getLogger('data_api.converter').setLevel(level)

# Constants
contigset_type = 'KBaseGenomes.ContigSet-3.0'
ga_type = 'KBaseGenomeAnnotations.GenomeAnnotation-2.1'
genome_type = 'KBaseGenomes.Genome-8.0'

class GenomeConverter(base.Converter):
    """Convert a "new" GenomeAnnotation object to an "old"
       Genome/ContigSet object.
    """
    target_suffix = 'genome'

    def __init__(self, **kw):
        """Create the converter.

        See :class:`Converter` for keyword argument descriptions.
        """
        base.Converter.__init__(self, **kw)
        # Connect to API and retrieve object
        self.api_obj = GenomeAnnotationAPI(self.services, self.token, self.obj_ref)
        # overall genome MD5, see :meth:`_update_md5`, and `md5` property
        self._genome_md5 = hashlib.md5()
        self.proteins = None

    def convert(self, workspace_name, contigset_ref=None):
        taxon = self.api_obj.get_taxon()
        assembly = self.api_obj.get_assembly()
        contig_ids = assembly.get_contig_ids()
        contig_lengths = assembly.get_contig_lengths()
        self.proteins = self.api_obj.get_proteins()
        if contigset_ref is None:
            contigset_ref = self._create_contigset(assembly, workspace_name)
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
            'contigset_ref': contigset_ref
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
                'aliases': list(set(val['feature_aliases'].keys() + p_aliases))
            }
            if _log.isEnabledFor(logging.DEBUG):
                DEBUG('adding feature {} md5={}'.format(
                    feature['id'], feature.get('md5','<empty>')))
            yield feature
        if pbar:
            pbar.done()

    @staticmethod
    def _convert_feature_locations(locations):
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


class AssemblyConverter(base.Converter):
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
        base.Converter.__init__(self, **kw)
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
                'description': c_val.get('description', 'No description'),
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
                                         target_name=self.get_target_name(),
                                         metadata=self.metadata)

    @property
    def md5(self):
        return self._obj_prop('md5')

    @property
    def fasta_handle_ref(self):
        return self._obj_prop('fasta_handle_ref', default='')


#####################################################################
# High-level interface to convert new type to old type.
# This would be called by the KBase uploaders.
#####################################################################

class ConvertOldTypeException(Exception):
    def __init__(self, err, ws_url=None, source_ref=None):
        msg = 'Convert to legacy type. ref={ref} workspace={ws}: {err}'.format(
            ref=source_ref, ws=ws_url, err=err)
        Exception.__init__(self, msg)

def convert_genome(shock_url=None, handle_url=None, ws_url=None, obj_name=None,
                   ws_name=None, contigset_ref=None):
    """Convert uploaded GenomeAnnotation to a Genome + ContigSet object.

    Args:
        shock_url (str): Shock service URL
        handle_url (str): Handle service URL
        ws_url (str): Workspace service URL
        obj_name (str): Name of source object
        ws_name (str): Name of source object's workspace
        contigset_ref (str or None): If not None, reference to existing ContigSet that was converted
             from the existing Assembly. If None, a new ContigSet will be created.
    Returns:
        (str) Object reference of Genome object
    Raises:
        ConversionError, if conversion fails
    """
    # Add custom set of service URLs,
    # since the Converter is invoked with a named group of URLs.
    kb_services = 'upload'
    base.Converter.all_services[kb_services] = dict(
        workspace_service_url=ws_url, shock_service_url=shock_url,
        handle_service_url=handle_url)

    # create source reference from upload workspace and object names
    source_ref = '{}/{}'.format(ws_name, obj_name)

    # perform the conversion
    INFO('Begin: Convert source={}'.format(source_ref))
    try:
        converter = GenomeConverter(kbase_instance=kb_services, ref=source_ref)
        target_ref = converter.convert(ws_name, contigset_ref=contigset_ref)
    except Exception as e:
        ERROR('Failed: Convert source={}: {}'.format(source_ref, e))
        raise ConvertOldTypeException(e, ws_url=ws_url, source_ref=source_ref)
    INFO('Success: Convert source={} output={}'.format(source_ref, target_ref))
    return target_ref

def convert_assembly(shock_url=None, handle_url=None, ws_url=None, obj_name=None,
                   ws_name=None):
    """Convert uploaded Assembly to a ContigSet object.

    Args:
        shock_url (str): Shock service URL
        handle_url (str): Handle service URL
        ws_url (str): Workspace service URL
        obj_name (str): Name of source object
        ws_name (str): Name of source object's workspace
    Returns:
        (str) Object reference of ContigSet object
    Raises:
        ConversionError, if conversion fails
    """
    # Add custom set of service URLs,
    # since the Converter is invoked with a named group of URLs.
    kb_services = 'upload'
    base.Converter.all_services[kb_services] = dict(
        workspace_service_url=ws_url, shock_service_url=shock_url,
        handle_service_url=handle_url)

    # create source reference from upload workspace and object names
    source_ref = '{}/{}'.format(ws_name, obj_name)

    # perform the conversion
    INFO('Begin: Convert source={}'.format(source_ref))
    try:
        converter = AssemblyConverter(kbase_instance=kb_services, ref=source_ref)
        target_ref = converter.convert(ws_name)
    except Exception as e:
        ERROR('Failed: Convert source={}: {}'.format(source_ref, e))
        raise ConvertOldTypeException(e, ws_url=ws_url, source_ref=source_ref)
    INFO('Success: Convert source={} output={}'.format(source_ref, target_ref))
    return target_ref