"""
Test the semantics module
"""
__author__ = 'dang'

import unittest

from ..semantics import *

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_type = Type({
            "name": "Object",
            "description": "Base object",
            "properties": [
                {"name": "id", "description": "UUID", "type": "string"},
                {"name": "owner", "description": "Name of owner",
                 "type": "string"}
            ],
            "statements": []
        })

        cls.contig_type = Type({
            "name": "Contig",
            "description": "Contiguous reads of an assembly",
            "properties": [
                {"name": "length", "type": "long"},
                {"name": "md5", "type": "string"},
                {"name": "refURL", "type": "string"},
                {"name": "assembly", "type": "string"},
                {"name": "species", "type": "string"}
            ],
            "statements": [
                (Statement.extends, "Object"),
                (Statement.agg, "Read"),
                (Statement.derived_from, "Assembly"),
                ("quiteDifferentFrom", "Banana")
            ]
        })

        ts = TypeSystem()
        ts.add(cls.base_type)
        ts.add(cls.contig_type)
        cls.types = ts

    def _debug(self):
        print("Base\n====")
        print(self.base_type.as_json())
        print("----")
        print(json.dumps(self.types.as_avro('Object'), indent=2))

        print("\nContig\n=====")
        print(self.contig_type.as_json())
        print("----")
        print(json.dumps(self.types.as_avro('Contig'), indent=2))

    def _match_field(self, field_list, **kwargs):
        nope = "---"
        n = 0
        for f in field_list:
            for k, v in kwargs.items():
                if f.get(k, nope) == v:
                    n += 1
        return n

    def test_base_property(self):
        num = self._match_field(self.base_type.properties, name="id")
        self.assertEqual(num, 1)

    def test_inherited_property(self):
        num = self._match_field(self.contig_type.properties, name="id")
        self.assertEqual(num, 0) # not in base def'n
        a = self.types.as_avro('Contig')
        num = self._match_field(a['fields'], name="id")
        self.assertEqual(num, 1) # but, yes, in created def'n


if __name__ == '__main__':
    unittest.main()
