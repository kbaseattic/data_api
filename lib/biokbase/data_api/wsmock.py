"""
Workspace mocking without a real MongoDB, using the mongomock package.

Usage:
  mock = WorkspaceMock('/path/to/mock_data.json')
  # OR: mock = WorkspaceMock(fileobj)
  api = TaxonAPI( ... )
  inject_mock(api, mock)
  # run tests, as usual, on API class
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/3/15'

# Imports

# Stdlib
from datetime import datetime
import json
# Third-party
import mongomock as mm

def inject_mock(api_instance, mock):
    orig = api_instance.ws_client
    api_instance.ws_client = mock
    return orig

class WorkspaceMock(object):
    """Mock object for KBase Workspace service.

    You can use this in place of the biokbase.client.workspace.Workspace class.

    To insulate from changes in the workspace storage format, the input
    data is in a simplified and reduced schema. The input should be a list
    of JSON ojects, separated by commas and bracketed by "[ ]" like a
    normal JSON list. Each object should have these fields:
        - ref (str): object reference like "123/4"
        - type (str): Name of the type of this object, e.g. "FooType"
        - name (str): Name of this workspace, e.g. "Workspace number 9",
        - metadata (dict): Object metadata fields (whatever you want)
        - links (list of str): List of references, each in the same form
                               as the 'ref' field.
        - data (dict): JSON object with the data (whatever you want)
    """
    def __init__(self, file_or_path):
        # create mock client and collection
        self.client = mm.MongoClient()
        self.collection = self.client.db.collection
        # open the input file
        if hasattr(file_or_path, 'read'):
            infile = file_or_path
        else:
            infile = open(file_or_path)
        # insert the file into mongomock
        for record in json.load(infile):
            self.collection.insert(record)
        # some internal state
        self._oids = {}

    # Public methods

    def copy_object(self, prm):
        # do nothing
        return

    def get_object_history(self, prm):
        return []

    def get_object_info_new(self, prm):
        ref = prm['objects'][0]['ref']
        records = self.collection.find({'ref': ref})
        result = [self._make_info(record, ref)
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
            records = self.collection.find({'ref': ref})
            # add to result
            for r in records:
                extracted = {} # all extracted paths
                d = r['data'] # alias
                for p in paths:
                    parts = p.split('.')
                    for part in parts[:-1]:
                        if d.has_key(part):
                            d = d[part]
                        else:
                            d = {}
                            break
                    if d:
                        e = extracted
                        for part in parts[:-1]:
                            if part not in e:
                                e[part] = {}
                            e = e[part]
                        e[parts[-1]] = d[parts[-1]]
                if extracted:
                    #print("@@ add extracted: {}".format(extracted))
                    obj = self._make_object(r, ref, data=extracted)
                    result.append(obj)
        return result

    def get_objects(self, prm):
        result = []
        for refs in prm:
            ref = refs['ref']
            records = self.collection.find({'ref': ref})
            #print("@@ GO, got records: {}".format(records))
            objects = [self._make_object(record, ref) for record in records]
            result.extend(objects)
        return result

    def get_type_info(self, type_name):
        return self._make_type_info({'type': type_name})

    def list_referencing_objects(self, prm):
        result = []
        for refs in prm:
            ref = refs['ref']
            for record in self.collection.find({'ref': ref}):
                r = self._make_info_tuple(record, ref)
                result.append(r)
        return result

    def translate_to_MD5_types(self, types):
        return {k: 'md5_' + k for k in types}

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
        """
        obj_id objid, obj_name name,
        type_string type, timestamp save_date,
        int version, username saved_by,
		ws_id wsid, ws_name workspace,
		string chsum, int size,
		usermeta meta
        """
        ver = '1'
        return (self._get_oid(ref), record['name'],
                record['type'], datetime.isoformat(datetime.now()),
                record['type'] + '/' + ver, None,
                ver, None
                )
    def _make_object(self, record, ref, data=None):
        r = {
            'data': data or record['data'],
            'object_info': self._make_info(record, ref),
            'provenance': [],
            'creator': 'Gonzo',
            'created': datetime.isocalendar(datetime.now()),
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

