"""
Workspace implemented over files, using the mongomock package.

Usage:
  mock = WorkspaceFile('/path/to/mock_data.json')
  # OR: mock = WorkspaceFile(fileobj)
  api = TaxonAPI( ... )
  inject_mock(api, mock)
  # run tests, as usual, on API class
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
from biokbase.data_api.util import get_logger, log_start, log_end
from biokbase.workspace.client import ServerError

# Logging

_log = get_logger('kbase.data_api.wsfile')

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
    from biokbase.workspace.client import Workspace
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

    You can use this in place of the biokbase.client.workspace.Workspace class.

    To insulate from changes in the workspace storage format, the input
    data is in a simplified and reduced schema. The input should be a list
    of JSON ojects, separated by commas and bracketed by "[ ]" like a
    normal JSON list. Each object should have these fields:
        - ref (str): object reference like "123/4"
        - type (str): Name of the type of this object, e.g. "FooType"
        - name (str): Name of this object, e.g. "PrototypeReferenceGenomes/kb|g.3157"
        - links (list of str): List of references, each in the same form
                               as the 'ref' field.
        - data (dict): JSON object with the data (whatever you want)
    """

    use_msgpack = True

    def __init__(self):
        """Create file-based Workspace instance.
        Additional files are added with the `load` method.
        """
        # create client and collection
        client = mm.MongoClient()
        self.collection = client.db.collection
        # This monkey-patch avoids a copy of the parsed workspace object
        # as it is added to the mongomock collection. Of course, this
        # means that this dict MUST be treated as immutable by other code.
        # But in this case, the dict is 'record' in the `load` function
        # that goes out of scope immediately.
        self.collection._internalize_dict = lambda d: d
        # some internal state
        self._oids = {}

    def load(self, file_or_path):
        """load data from a file or name of a file into the workspace.

        See class documentation on format of input data.
        """
        # open the input file
        if hasattr(file_or_path, 'read'):
            infile = file_or_path
        else:
            infile = open(file_or_path)
        # insert the file into mongomock
        method = msgpack.load if self.use_msgpack else json.load
        try:
            record = FileObjectCache(method).get(infile, infile)
        except TypeError as err:
            raise ValueError("Bad type for input file {}: {}"
                             .format(infile, err))
        #t0 = log_start(_log, 'collection.insert', level=logging.DEBUG,
        #               kvp={'file': infile})
        self.collection.insert(record)
        #log_end(_log, t0, 'collection.insert', level=logging.DEBUG,
        #        kvp={'file': infile})

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
                d = r['data'] # alias
                for p in paths:
                    parts, found = p.split('/'), True
                    # Look for value matching path in 'd'
                    for part in parts:
                        if d.has_key(part):
                            d = d[part]
                        else:
                            found = False
                            break
                    # If we got a value at the leaf (which is now
                    # in 'd'), then add the path and value to '(e)xtracted'
                    if found:
                        e = extracted # alias
                        for part in parts[:-1]:
                            if part not in e:
                                e[part] = {} # create new empty container
                            e = e[part] # descend
                        e[parts[-1]] = d
                if extracted:
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

    # ___ Internal methods ___

    def _get_oid(self, ref):
        if ref in self._oids:
            return self._oids[ref]
        n = len(self._oids)
        self._oids[ref] = n + 1
        return n

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
        ver = '1'
        return (self._get_oid(ref), record['name'],
                record['type'], datetime.isoformat(datetime.now()),
                record['type'] + '/' + ver, None,
                ver, None,
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
        records = list(self.collection.find({'ref': ref}))
        # If nothing is returned, then try to look for the
        # records by the name (unless the regex shows that it
        # is definitely _not_ a name).
        if len(records) == 0 and not NUMERIC_REF_PAT.match(ref):
            #print("@@ look by name for '{}'".format(ref))
            records = list(self.collection.find({'name': ref}))
        return records


class FileObjectCache(object):
    """Simple memory cache for files that uses the
    modification time of the file to see whether to
    reload.
    """
    cache = {}

    def __init__(self, meth):
        """Create with a method to invoke when creating
        the cached object.
        """
        self.method = meth

    def get(self, path, *args, **kwargs):
        """Get from cache, or create if not found.

        Args:
          path: Path to file
          args: Pass these to create method
          kwargs: Pass these to create method
        Returns:
          New or cached return value from self.method
        """
        if hasattr(path, 'name'):  # file object
            path = path.name
        elif not isinstance(path, basestring):
            import StringIO
            if isinstance(path, StringIO.StringIO):
                return self.method(*args, **kwargs)
            raise TypeError('Not string, file, or StringIO.StringIO')
        # construct key with path and modif. time
        mtime = os.path.getmtime(path)
        key = '{}--{}'.format(path, mtime)
        # look for object by that key
        if key in self.cache:
            # if found, return it
            return self.cache[key]
        # if not found, create new object,
        # add it to the cache, and return it
        obj = self.method(*args, **kwargs)
        self.cache[key] = obj
        return obj

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
    u'KBaseGenomesCondensedPrototypeV2.Assembly-0.1': u'KBaseGenomesCondensedPrototypeV2.Assembly-ffd679cc5c9ce4a3b1bb1a5c3960b42e',
    u'KBaseGenomesCondensedPrototypeV2.Assembly-1.0': u'KBaseGenomesCondensedPrototypeV2.Assembly-ffd679cc5c9ce4a3b1bb1a5c3960b42e',
    u'KBaseGenomesCondensedPrototypeV2.Assembly-1.1': u'KBaseGenomesCondensedPrototypeV2.Assembly-1ab165a65ef2bf6d7279107ac185fa99',
    u'KBaseGenomesCondensedPrototypeV2.Assembly-2.0': u'KBaseGenomesCondensedPrototypeV2.Assembly-d4a52a103bd75fb99714c2a330d80d20'
}