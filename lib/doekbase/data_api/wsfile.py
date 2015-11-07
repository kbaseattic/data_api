"""
Workspace implemented over files, using the mongomock package.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/3/15'

# Imports

# Stdlib
try:
    import cStringIO as StringIO
except:
    import StringIO
from datetime import datetime
import json
import logging
import msgpack
import os
import re
# Third-party
import mongomock as mm
# Local
from doekbase.data_api.util import get_logger, log_start, log_end
from doekbase.workspace.client import ServerError

# Logging

_log = get_logger(__name__)

# Globals

NUMERIC_REF_PAT = re.compile('\d+/\d+(/\d+)?')

# Exceptions

class LibError(ServerError):
    """To imitate server errors, raise this with a description
    of the error as the argument.
    """
    def __init__(self, description):
        super(LibError, self).__init__('ServerError', -32500, description)

# Functions and classes

ws_url_template = 'https://{}.kbase.us/services/ws/'

def workspace_to_file(ref, workspace='narrative', token=None):
    """Convert Workspace objects to the JSON format read by the
    mongomock module.

    Args:
      ref (str): Workspace object reference e.g. '1019/4/1'
      workspace (str): Name or full URL for workspace to contact
                       'narrative' or 'ci' are recognized
       token (str): KBase auth token
    Return:
       (dict) Object in the mock schema
    """
    from doekbase.workspace.client import Workspace
    if re.match(r'https://.*', workspace):
        url = workspace
    else:
        url = ws_url_template.format(workspace)
    if token is None:
        token = os.environ.get('KB_AUTH_TOKEN', '')
        if not token:
            raise ValueError('No `token` given and environment does not '
                             'contain value for KB_AUTH_TOKEN')
    ws = Workspace(url, token=token)
    objlist = ws.get_objects([{'ref': ref}])
    obj, oi = objlist[0], objlist[0]['info']
    canonical_ref = "{0}/{1}/{2}".format(oi[6], oi[0], oi[4])
    canonical_name = "{0}/{1}".format(oi[7], oi[1])
    # convert to our schema
    d = {'ref': canonical_ref,
         'type': oi[2],
         'name': canonical_name,
         'links': obj['refs'],
         'data': obj['data'],
         'metadata': oi[10]
         }
    _log.debug('workspace_to_file: returning record for: {}'
               .format(canonical_ref))
    return d

class WorkspaceFile(object):
    """Mock object for KBase Workspace service.

    You can use this in place of the doekbase.client.workspace.Workspace class.

    To insulate from changes in the workspace storage format, the input
    data is in a simplified and reduced schema. The input should be a list
    of JSON ojects, separated by commas and bracketed by "[ ]" like a
    normal JSON list. Each object should have these fields:

    * ref - object reference like "123/4"
    * type - Name of the type of this object, e.g. "FooType"
    * name - Name of this object, e.g. "PrototypeReferenceGenomes/kb|g.3157"
    * links - List of references, each in the same form as the 'ref' field.
    * data - JSON object with the data (whatever you want)
    """

    #: Use MessagePack encoding for workspace objects
    use_msgpack = True
    use_redis = False
    _loaded = {}  # static cache of loaded refs

    #: Version of the workspace we are emulating
    VERSION = '0.3.5'

    def __init__(self, working_directory):
        """Create file-based Workspace instance, using files in
        the given working directory.

        Additional files are added with the `load` method.

        Args:
          working_directory (str): Path to directory with files to load.
        """
        self._wd = working_directory
        # create client and collection
        client = mm.MongoClient()
        self.collection = client.db.collection
        # This monkey-patch avoids a copy of the parsed workspace object
        # as it is added to the mongomock collection. Of course, this
        # means that this dict MUST be treated as immutable by other code.
        self.collection._internalize_dict = lambda d: d
        # some internal state
        self._oids = {}

    def load(self, ref):
        """Load data from a given reference.

        The reference will be translated into a file to load,
        using the following formula:
        ``<working_directory> + '/' + <ref> + <ext>`,
        where ``<working_directory>`` is the path given to the class
        constructor, ``<ref>`` is the reference given to this
        function, and
        ``<ext>`` is a file extension '.msgpack' if
        `use_msgpack` is True and '.json' otherwise.

        Thus, for ``WorkspaceFile('/tmp/data').load('foo_bar')``,
        the path loaded would be '/tmp/data/foo_bar.msgpack'.

        See class documentation on format of input data.

        Args:
          ref (str): The reference

        Notes:
          * Post-condition: Object is loaded if and only if that reference was
            not loaded previously. Modification timestamp of the underlying
            file is NOT checked, you must manually invalidate modified
            data with :meth:`unload(ref)`.

        Raises:
          IOError: file not found or not readable.
          ValueError: parsing failed.
        """
        # log start
        t0 = log_start(_log, 'WorkspaceFile.load', level=logging.INFO,
                       kvp=dict(ref=ref))
        # stop if already loaded in the past
        if ref in self._loaded:
            # log done and return
            log_end(_log, t0, 'WorkspaceFile.load', level=logging.INFO,
                    kvp=dict(ref=ref, cached='yes'))
            return
        # create the full path from the reference
        ext = 'msgpack' if self.use_msgpack else 'json'
        full_path = '{}.{}'.format(os.path.join(self._wd, ref), ext)
        # open the file; raises IOError on failure
        f = open(full_path)
        # parse the file
        try:
            record = msgpack.load(f) if self.use_msgpack else json.load(f)
        except Exception as err:
            raise ValueError('Loading {}: {}'.format(full_path, err))
        finally:
            f.close()
        # cache the parsed data, both by reference and by 'name'
        # (if name is not the same as reference)
        #print("@@ REF={r} RECORD[ref]={rr} RECORD[name]={n}"
        #      .format(r=ref, rr=record['ref'], n=record['name']))
        self._loaded[ref] = record
        self._loaded[record['ref']] = record
        self._loaded[record['name']] = record
        #print('@@ STORE RECORD BY ({},{})'.format(record['ref'], record['name']))
        # insert the parsed data into mongomock
        self.collection.insert(record)
        # log done
        log_end(_log, t0, 'WorkspaceFile.load', level=logging.INFO,
                kvp=dict(ref=ref, cached='no'))

    def unload(self, ref):
        """Force reload of ``ref`` the next time.
        Does nothing if ``ref`` is not already loaded.

        Args:
          ref (str): The reference
        Post:
           ref is no longer loaded
        """
        if ref in self._loaded:
            del self._loaded[ref]

    # Public methods

    def copy_object(self, prm):
        # do nothing
        return

    def get_object_history(self, prm):
        return []

    def get_object_info_new(self, prm):
        ref = prm['objects'][0]['ref']
        records = self._find_ref(ref)
        result = [self._make_info_tuple(record, record['ref'])
                  for record in records]
        return result

    def get_object_provenance(self, prm):
        return []

    def get_object_subset(self, prm):
        """Note: this is not efficient. It actually looks at
        the whole object.
        """
        # loop over each specified subset, and add all results
        # to a single list in `result`
        result = []
        for subset in prm:
            ref, paths = subset['ref'], subset['included']
            # get matching records and data in the paths
            records = self._find_ref(ref)
            # add to result
            for r in records:
                extracted = {} # all extracted paths
                for p in paths:
                    d = r['data'] # alias
                    parts = p.split('/')

                    # Look for value matching path in 'd'
                    e = extracted
                    for i in xrange(len(parts) - 1):
                        if parts[i] in d:
                            d = d[parts[i]]

                            if parts[i] not in e and isinstance(d, dict):
                                e[parts[i]] = {}

                            if isinstance(e[parts[i]], dict):
                                e = e[parts[i]]
                        else:
                            break
                    else:
                        if parts[-1] in d:
                            e[parts[-1]] = d[parts[-1]]

                    _log.debug(extracted)
                if len(extracted) > 0:
                    #print("@@ add extracted: {}".format(extracted))
                    obj = self._make_object(r, ref, data=extracted)
                    result.append(obj)
        return result

    def get_objects(self, prm):
        result = []
        for refs in prm:
            ref = refs['ref']
            records = self._find_ref(ref)
            #print("@@ GO, got records: {}".format(records))
            objects = [self._make_object(record, ref) for record in records]
            result.extend(objects)
        return result

    def get_type_info(self, type_name):
        return self._make_type_info({'type': type_name})

    def list_referencing_objects(self, prm):
        result = []
        for refs in prm:
            ref_result = []
            ref = refs['ref']
            # find every record that refers to this one
            for rfr in self.collection.find({'links': ref}):
                info_tuple = self._make_info_tuple(rfr, rfr['ref'])
                ref_result.append(info_tuple)
            result.append(ref_result)
        return result

    def translate_to_MD5_types(self, types):
        m = {}
        for t in types:
            if t in MD5_TYPES:
                m[t] = MD5_TYPES[t]
            else:
                raise LibError('Type schema record was not found for {}'
                                  .format(t))
        return m

    def ver(self):
        return self.VERSION

    def get_children(self):
        return []

    # ___ Internal methods ___

    def _get_oid(self, ref):
        if ref in self._oids:
            return self._oids[ref]
        new_oid = len(self._oids)
        self._oids[ref] = new_oid
        return new_oid

    def _make_info(self, record, ref):
        """Make and return a single 'info' section.
        """
        assert re.match(NUMERIC_REF_PAT, ref)  # require numeric ref
        #print("@@ make_info from: {}".format(record))
        ws_id = int(ref.split('/')[0])
        oid = self._get_oid(ref)
        data = record['data']
        info = {'object_id': oid,
                'object_name': 'Object{:d}'.format(oid),
                'object_reference': ref,
                'object_reference_versioned': '{}/{}'.format(ref, '1'),
                'type_string': record['type'],
                'save_date': datetime.isoformat(datetime.now()),
                'version': 1,
                'saved_by': 'CookieMonster',
                'workspace_id': ws_id,
                'workspace_name': record['name'],
                'object_checksum': 0,
                'object_size': len(data),
                'object_metadata': record['metadata']
                }
        return info

    def _make_info_tuple(self, record, ref):
        """Make the object_info type tuple:

        0: obj_id objid, 1: obj_name name,
        2: type_string type, 3: timestamp save_date,
        4: int version, 5: username saved_by,
		6: ws_id wsid, 7: ws_name workspace,
		8: string chsum, 9: int size, 10: usermeta meta
        """
        assert re.match(NUMERIC_REF_PAT, ref)  # require numeric ref
        wsid = int(ref.split('/')[0])
        ver = int(ref.split('/')[-1])
        return (self._get_oid(ref), record['name'],
                record['type'], datetime.isoformat(datetime.now()),
                ver, 'joe',
                wsid, record['name'],
                '0', 0, {}
                )
    def _make_object(self, record, ref, data=None):
        canonical_ref = record['ref']
        r = {
            'data': data or record['data'],
            'object_info': self._make_info(record, canonical_ref),
            'provenance': [],
            'creator': 'Gonzo',
            'created': datetime.isoformat(datetime.now()),
            'refs': [],
            'copied': '',
            'copy_source_inaccessible': 0,
            'extracted_ids': {},
            'handle_error': '',
            'handle_stacktrace': ''
        }
        return r

    def _make_type_info(self, record):
        r = {
            'type_string': record['type'],
            'description': 'This is type {}'.format(record['type']),
            # 'spec_def': '',
            # 'json_schema': '{}',
            # 'parsing_structure': '{}',
            # 'module_vers': [1],
            # 'released_module_vers': [1],
            # 'type_vers' : ['1'],
            # 'released_type_vers': ['1'],
            # 'using_func_defs': [],
            # 'using_type_defs': [],
            # 'used_type_defs': []
        }
        return r

    def _find_ref(self, ref):
        """Find records by reference.

        Args:
          ref (str): numeric or named object reference
        Returns:
          list of records (may be an empty list)
        """
        #print("@@ looking for REF={} in KEYS={}".format(ref, self._loaded.keys()))
        result = []
        if ref in self._loaded:
            result.append(self._loaded[ref])
        return result

####

MD5_TYPES = {
    u'KBaseGenomes.Genome-0.1': u'KBaseGenomes.Genome-1e1fce431960397da77cb092d27a50cf',
    u'KBaseGenomes.Genome-1.0': u'KBaseGenomes.Genome-1e1fce431960397da77cb092d27a50cf',
    u'KBaseGenomes.Genome-2.0': u'KBaseGenomes.Genome-e0979de9df4baccca8bdd95f7565fde4',
    u'KBaseGenomes.Genome-3.0': u'KBaseGenomes.Genome-225de07e59f4fdc5d9b8bf0bcd12c498',
    u'KBaseGenomes.Genome-4.0': u'KBaseGenomes.Genome-c0526fae0ce1fd8d342ec94fc4dc510a',
    u'KBaseGenomes.Genome-5.0': u'KBaseGenomes.Genome-c0526fae0ce1fd8d342ec94fc4dc510a',
    u'KBaseGenomes.Genome-6.0': u'KBaseGenomes.Genome-aafaaa7df90d03b33258f4fa7790dcbe',
    u'KBaseGenomes.Genome-7.0': u'KBaseGenomes.Genome-93da9d2c8fb7836fb473dd9c1e4ca89e',
    u'KBaseGenomes.Genome-8.0': u'KBaseGenomes.Genome-51b05a5c27084ae56106e60df5b66df5',
    u'KBaseGenomes.ContigSet-3.0': u'KBaseGenomes.ContigSet-db7f518c9469d166a783d813c15d64e9',
    u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-0.1': u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-d4301f53dab71e72d70ea5be6919696e',
    u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-1.0': u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-d4301f53dab71e72d70ea5be6919696e',
    u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-1.1': u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-97253a4ad440116a6421ede1fca50cad',
    u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-2.0': u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-e3de51478246422db519fd4cbc9eb4cd',
    u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-2.1': u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-6935b73c720523e4541dd516bc13ef56',
    u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-3.0': u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-841a82daab5165ff77a4fd9aba899d93',
    u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-3.1': u'KBaseGenomesCondensedPrototypeV2.GenomeAnnotation-2d8e562a12357b92ce84c723e2663c10',
    u'KBaseGenomesCondensedPrototypeV2.Taxon-0.1': u'KBaseGenomesCondensedPrototypeV2.Taxon-ba7d1e3c906dba5b760e22f5d3bba2a2',
    u'KBaseGenomesCondensedPrototypeV2.Taxon-1.0': u'KBaseGenomesCondensedPrototypeV2.Taxon-ba7d1e3c906dba5b760e22f5d3bba2a2',
    u'KBaseGenomesCondensedPrototypeV2.Taxon-2.0': u'KBaseGenomesCondensedPrototypeV2.Taxon-f569f539547dd1eea6a59eb9aa0b2eda',
    u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-0.1': u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-3e6afdc52a0574ae18a8c66f6a4e10a3',
    u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-1.0': u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-3e6afdc52a0574ae18a8c66f6a4e10a3',
    u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-2.0': u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-c0f1fd6639ab3663d1a8373253981fdf',
    u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-3.0': u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-3cf973a339b0e6e18e8cade7b77272fe',
    u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-4.0': u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-9f300ab15a34a764eb32acc265983ef3',
    u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-5.0': u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-02ba9ba1340d07c0eb7401dcb9e51647',
    u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-6.0': u'KBaseGenomesCondensedPrototypeV2.FeatureContainer-3cf973a339b0e6e18e8cade7b77272fe',
    u'KBaseGenomesCondensedPrototypeV2.ProteinContainer-4.0': u'KBaseGenomesCondensedPrototypeV2.ProteinContainer-24986e79a34d6c0800b2008c974015b4',
    u'KBaseGenomesCondensedPrototypeV2.Assembly-0.1': u'KBaseGenomesCondensedPrototypeV2.Assembly-ffd679cc5c9ce4a3b1bb1a5c3960b42e',
    u'KBaseGenomesCondensedPrototypeV2.Assembly-1.0': u'KBaseGenomesCondensedPrototypeV2.Assembly-ffd679cc5c9ce4a3b1bb1a5c3960b42e',
    u'KBaseGenomesCondensedPrototypeV2.Assembly-1.1': u'KBaseGenomesCondensedPrototypeV2.Assembly-1ab165a65ef2bf6d7279107ac185fa99',
    u'KBaseGenomesCondensedPrototypeV2.Assembly-2.0': u'KBaseGenomesCondensedPrototypeV2.Assembly-d4a52a103bd75fb99714c2a330d80d20'
}