"""
Mapping of KBaseGenomes.spec
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '4/3/15'

# Imports

import argparse
import json
import os
import pprint
import sys
import tempfile
import time

import avro.datafile
import avro.io
import avro.schema

# Util

class Timer(object):
    def __init__(self):
        self.t = [None, None]

    def start(self):
        self.t[0] = time.time()

    def end(self, e="an_event", n=0, item="item"):
       self.t[1] = time.time()
       t = self.t[1] - self.t[0]
       if n > 0:
           r, g = n / t, t / n
           print("{e}: {t:.3f} sec for {n:d} {i}s: {r:f} {i}s/sec, {g:f} sec/{i}".format(
               e=e, t=t, i=item, r=r, g=g, n=n))
       else:
           print("{}: {:.3f} sec".format(e, t))

TM = Timer()

"""
Avro
====

Informational sites:
    * http://www.infoq.com/articles/ApacheAvro

"""

# Keep track of loaded schemata
avsc_names = avro.schema.Names()

def load_avro(name):
    path = os.path.join("schema", name + ".avsc")
    json_data = json.load(open(path))
    buf = open(path).read()
    schema = avro.schema.make_avsc_object(json_data, avsc_names)
    return schema

def write_contigset(schema, f):
    writer = avro.io.DatumWriter(schema)
    avro_file = avro.datafile.DataFileWriter(f, writer,
                                             writers_schema=schema)
    cset = [{'name': 'contig{:d}'.format(i),
             'length': 10,
             'md5': 'thisisanmd5hash',
             'refURL': 'http://www.google.com',
             'assembly': 'not sure what this should look like',
             'species': 'e.coli'} for i in range(1000)]
    TM.start()
    avro_file.append({"contigs": cset})
    avro_file.close()
    TM.end("avro.write", n=1000)

def read_contigset(f, rec_callback=None):
    reader = avro.io.DatumReader()
    avro_file = avro.datafile.DataFileReader(f, reader)

    TM.start()
    records = [r for r in avro_file]
    TM.end("avro.read", n=len(records) * len(records[0]['contigs']))

    if rec_callback:
        for record in records:
            rec_callback(record)

def run_avro():
    # Write a contigset (to a tempoarary file)
    # note: dependencies must be loaded first (DFS)
    load_avro("contig")
    contig_set = load_avro("contigset")
    f = tempfile.NamedTemporaryFile(delete=False)
    write_contigset(contig_set, f)

    # Read contigset back and print it
    f = open(f.name) # re-open file
    stat = os.stat(f.name)
    print("File size: {:d}KB".format(stat.st_size // 1000))
    #read_contigset(f, pprint.PrettyPrinter().pprint)
    read_contigset(f)

    # remove the file
    os.unlink(f.name)

"""
Thrift
======
"""

def run_thrift():
    print("TBD")

"""
Protobuf
========
"""

def run_protobuf():
    print("TBD")

###########

TOOLS = ["avro", "thrift", "protobuf"]
TOOLS_STR = ", ".join(TOOLS)

def main():
    p = argparse.ArgumentParser(description="Run some examples")
    p.add_argument("tool", help="Choose tool: "  + TOOLS_STR)
    args = p.parse_args()
    tool = args.tool.lower()
    if tool not in TOOLS:
        p.error("'tool' must be one of: " + TOOLS_STR)
    func = eval("run_" + tool)
    func()
    return 0

if __name__ == '__main__':
    sys.exit(main())