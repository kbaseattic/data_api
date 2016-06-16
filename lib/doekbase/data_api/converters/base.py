"""
Base classes for workspace object (new -> old) converters.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '5/28/16'

# Stdlib
import abc
import logging
import os
import re
# Local
from doekbase.workspace.client import Workspace
from doekbase.handle.Client import AbstractHandle as handleClient
from doekbase.data_api.core import version

# Set up logging
_log = logging.getLogger('data_api.converter')
_ = logging.StreamHandler()
_.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
_log.addHandler(_)
DEBUG = lambda(s): _log.debug(s)
INFO = lambda(s): _log.info(s)
WARN = lambda(s): _log.warn(s)
ERROR = lambda(s): _log.error(s)

class Converter(object):
    __metaclass__ = abc.ABCMeta
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
    token = os.environ.get("KB_AUTH_TOKEN", "")

    #: Override this in subclasses to create a naming convention
    #: between source and target objects. For example, change this to
    #: 'contigset' for created contigset objects.
    target_suffix = 'generic'

    #: Show this blurb in the converted object metadata
    ABOUT_BLURB = "Down-converted from a KBase " + \
    "{from_type} object. Methods using this type are being upgraded "\
    "to use the Data API."

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

    @abc.abstractmethod
    def convert(self, workspace_ref):
        """Convert to target object and place that object in gven workspace
        Args:
            workspace_ref (str): Workspace name or workspace ID

        Returns:
            (str) object reference in format 'workspace-id/object-id',
                  where both id's are integers.
        """
        pass

    @property
    def metadata(self):
        return self.api_obj.object_metadata

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
        target_ws = self._normalize_ws_to_name(target_ws)
        ws = self._connect_to_workspace()
        script_name = '{}.{}'.format(self.__class__.__module__, self.__class__.__name__)
        script_version = version()
        INFO('Creating object {} in workspace {}, script = {} v{}'.format(
            target_name, target_ws, script_name, script_version))
        if self.__class__.__name__.startswith('Genome'):
            new_type = 'GenomeAnnotation'
        else:
            new_type = 'Assembly'
        ws.save_objects(
            {'workspace': target_ws,
             'objects': [{'name': target_name,
                          'type': type_,
                          'data': data,
                          'provenance': [{'script': script_name,
                                          'script_ver': script_version,
                                          'input_ws_objects': [source_ref],
                                          }],
                          'meta': {'note': self.ABOUT_BLURB.format(from_type=new_type)}
                          }
                         ]
             }
        )
        return '{}/{}'.format(target_ws, target_name)

    def _connect_to_workspace(self):
        return Workspace(self.services['workspace_service_url'], token=self.token)

    def _normalize_ws_to_name(self, ws_id):
        """Make sure WS is not a number, but a name"""
        if re.match('\d+', ws_id):
            # fetch name from ID
            client = self._connect_to_workspace()
            wsi = {'id': ws_id}
            info = client.get_workspace_info(wsi)
            name = info[1]
        else:
            # it is already a name
            name = ws_id
        return name

    # Object property accessors

    @property
    def external_source(self):
        return self._obj_prop('external_source', default='unknown')

    @property
    def external_source_id(self):
        return self._obj_prop('external_source_id', default='')

    @property
    def object_name(self):
        return self.api_obj.get_info()['object_name']

    def _obj_prop(self, name, default=None):
        return self.api_obj.get_data_subset([name]).get(name, default)


class GenomeName(object):
    """Pick a proper name for uploaded or converted genome data.
    """
    # Configure with these prefixes/codes
    annotation_type = None # if None, do not add type for GA
    assembly_type = 'assembly'
    old_annotation_type = 'genome'
    old_assembly_type = 'contigset'
    legacy = 'legacy'
    legacy_prefix = False # false means suffix

    def __init__(self, base_name, source=None):
        """Ctor.

        Args:
            base_name (str): Base name, from user or uploader
            source (str or None): If not None, the source to add to name
        """
        self._kw = {'name': base_name}
        if source is None:
            self._base_format = '{name}_{type}'
        else:
            self._base_format = '{name}_{source}_{type}'
            self._kw['source'] = source
        # conditionally strip type for the genome annotation
        if self.annotation_type is None:
            self._ann_format = self._base_format[:self._base_format.rfind('_')]
            self._ann_kw = self._kw
        else:
            self._ann_format = self._base_format
            self._ann_kw = self._kw.copy()
            self._ann_kw['type'] = self.annotation_type

    def get_assembly(self):
        """Get name for Assembly object."""
        return self._base_format.format(type=self.assembly_type, **self._kw)

    def get_genome_annotation(self):
        """Get name for GA object."""
        return self._ann_format.format(**self._ann_kw)

    def get_contigset(self):
        """Get name for ContigSet object."""
        name = self._kw['name']
        if name.endswith('_' + self.assembly_type):
            # strip last component, the _assembly suffix, before
            # adding in the contigset suffix.
            name = name[:name.rfind('_')]
            self._kw['name'] = name
        if self.legacy_prefix:
            name_format = '{old}_' + self._base_format
        else:
            name_format = self._base_format + '_{old}'
        return name_format.format(old=self.legacy,
                                  type=self.old_assembly_type, **self._kw)

    def get_genome(self):
        """Get name for Genome object."""
        if self.legacy_prefix:
            name_format = '{old}_' + self._base_format
        else:
            name_format = self._base_format + '_{old}'
        return name_format.format(old=self.legacy,
                                  type=self.old_annotation_type,
                                  **self._kw)
