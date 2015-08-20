proto = {
    "namespace": "biokbase.data_api",
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
        { "type": "string", "name": "suffix"}
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
       {"type": "string", "name": "ident"}
       ]
    },
    {"name": "Taxon", "type": "record",
     "doc": "Taxon in a genome",
     "fields": [
       {"type": "SemVer", "name": "version"},
       {"type": "string", "name": "ident"},
       {"type": "array",  "name": "lineage",
        "items": "LineageItem"},
       {"type": "string", "name": "taxid",
        "doc": "Taxonomic ID"},
       {"type": "array", "name": "aliases",
        "item": "string"}
      ]
    }
  ],

  "messages": {
    "get": {
        "request": [{"name": "ref", "type": "ObjRef"}],
        "response": "GenomeAnnotation",
    },
    "get_taxon": {
        "request": [{"name": "ref", "type": "ObjRef"}],
        "response": "Taxon",
    }
  }
}


