"""
Avro protocol specification.

By putting this in a Python module, it is trivial to find and
load the protocol within the client and server:
  from biokbase.data_api.genome import avro_spec
"""
proto = """
{
    "namespace": "doekbase.data_api",
    "protocol": "GenomeAnnotation",

    "types": [
      {"name": "ObjRef", "type": "record",
       "doc": "Object reference",
       "fields": [
        {"name": "objid", "type": "string"}
        ]
        },
    {"name": "SemVer", "type": "record",
     "doc": "Semantic version",
      "fields": [
        { "type":"string", "name": "version" },
        { "type": "int", "name": "major"},
        { "type": "int", "name": "minor"},
        { "type": ["string", "null"], "name": "suffix"}
       ]
    },
    {"name": "LineageItem", "type": "record",
     "doc": "Single item in a phylogeny",
     "fields": [
          {"type": "string", "name":"pcode",
           "doc": "Phylogenetic code"
          },
          {"type": "string", "name": "value",
           "doc": "Value of this item"
          }
        ]
    },
    {"name": "GenomeAnnotation", "type": "record",
     "doc": "Genome annotation",
      "fields": [
       {"type": "SemVer", "name": "version"},
       {"type": "string", "name": "ident"},
       {"type": "string", "name": "info"}
       ]
    },
    {"name": "Taxon", "type": "record",
     "doc": "Taxon in a genome",
     "fields": [
       {"type": "SemVer", "name": "version"},
       {"type": "string", "name": "ident"},
       {"name": "lineage", "type": {
            "type": "array", "items": "LineageItem"}
        },
       {"type": "string", "name": "taxid",
        "doc": "Taxonomic ID"},
       {"name": "aliases", "type": {
           "type": "array", "items": "string"}
        }
      ]
    }
  ],

  "messages": {
    "get_info": {
        "request": [{"name": "ref", "type": "ObjRef"}],
        "response": "GenomeAnnotation"
    },
    "get_taxon": {
        "request": [{"name": "ref", "type": "ObjRef"}],
        "response": "Taxon"
    }
  }
}"""

