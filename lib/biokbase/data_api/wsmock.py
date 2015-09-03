"""
Workspack mocking without a real MongoDB, using the mongomock package.

Input data should be a list of JSON objects (i.e. the outer
delimiter should be "[ ]"), each in the following form:
    {
        "ref": "<object-reference>",
        "type": "<workspace-type>",
        "name": "<workspace-name>",
        "metadata": { <object-metadata> },
        "data": {
            <object-data>
        }
    }

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

    def _get_oid(self, ref):
        if ref in self._oids:
            return self._oids[ref]
        n = len(self._oids)
        self._oids[ref] = n + 1
        return n

    def get_object_history(self, prm):
        return []

    def get_object_info_new(self, prm):
        ref = prm['objects'][0]['ref']
        ws_id = int(ref.split('/')[0])
        records = self.collection.find({'ref': ref})
        result = []
        for record in records:
            oid = self._get_oid(ref)
            data = record['data']
            r = {'object_id': oid,
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
            result.append(r)
        return result

    def get_object_provenance(self, prm):
        return []

    def get_object_subset(self, prm):
        # loop over each specified subset, and add all results
        # to a single list in `result`
        result = []
        for subset in prm:
            ref, paths = subset['ref'], subset['included']
            # transform paths into desired fields in 'data'
            fields = {'data': 1, '_id': 0}
            # get matching records and data in the paths
            records = self.collection.find({'ref': ref}, fields)
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
                    result.append(extracted)
        return result

# get_objects
# get_type_info
# list_referencing_objects
# translate_to_MD
# copy_object
# get_object_history
# get_object_info_new
# get_object_provenance
# get_object_subset
# get_objects
# get_type_info
# list_referencing_objects
# translate_to_MD
#
