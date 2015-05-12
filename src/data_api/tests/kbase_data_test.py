"""
Unit tests for kbase_data module
"""
__author__ = 'dang'

from StringIO import StringIO
import unittest

from .. import kbase_data

class MockTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_authenticated(self):
        client = kbase_data.MockDataClient()
        self.assertRaises(kbase_data.AuthenticationRequired, client.insert, {})

    def test_insert_simple(self):
        client = kbase_data.MockDataClient()
        client.authenticate()
        self.assertEqual(1, client.insert({}))

    def test_search_simple(self):
        client = kbase_data.MockDataClient()
        client.authenticate()
        obj = kbase_data.BioDatum()
        obj.measurements = {'hello': 'world'}
        client.insert(obj)
        result = client.search({'oid': obj.oid})
        self.assertEqual(1, len(result))
        self.assertEqual(result[0].measurements['hello'], 'world')

    def test_load_fasta(self):
        client = kbase_data.MockDataClient()
        client.authenticate()
        s = StringIO("> metadata\nGATTACAGATTACAGATTACA\n")
        s.name = "StringIO"
        src = kbase_data.FastaSource(s)
        oid = client.load(src)
        objects = client.search({'oid': oid})
        #print("Got back objects:")
        #for o in objects:
        #    print('--')
        #    print(o)
        self.assertEqual(len(objects), 1)
        file_hash = objects[0].measurements.get('Bytes.FASTA', None)
        self.assertNotEqual(file_hash, None)


if __name__ == '__main__':
    unittest.main()
