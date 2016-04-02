from __future__ import print_function
from sys import getsizeof, stderr
from itertools import chain
from collections import deque

try:
    from reprlib import repr
except ImportError:
    pass

import simplejson
import time
import sys
#import biokbase.workspace.client
import doekbase.workspace.client
import re
import hashlib
import traceback
import os.path


def total_size(o, handlers={}, verbose=False):
    """ Returns the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: dict_handler,
                    set: iter,
                    frozenset: iter
                   }
    all_handlers.update(handlers)     # user handlers take precedence
    seen = set()                      # track which object id's have already been seen
    default_size = getsizeof(0)       # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:       # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        if verbose:
            print(s, type(o), repr(o), file=stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)


def make_taxon_lookup(wsname=None,wsurl=None, taxon_names_file = None): 

    start  = time.time()
    print ("Start time " + str(start))

#    ws_client = biokbase.workspace.client.Workspace(wsurl)
    ws_client = doekbase.workspace.client.Workspace(wsurl)
    workspace_object = ws_client.get_workspace_info({'workspace':wsname})
    

    workspace_id = workspace_object[0]
    workspace_name = workspace_object[1]

    names_file = taxon_names_file

    #key is the taxonomy_id, values is an inner dict (parent_id, children_ids (list), 
    # genetic_code, scientific_name, aliases(list), lineage, parent_tax_id, 
    # rank, kingdom, embl_code, inherited_div_flag, inherited_GC_flag, mitochondrial_genetic_code, 
    # inherited_MGC_flag GenBank_hidden_flag hidden_subtree_flag division_id )

    #PHASE 1
    #OPEN FILE AND POPULATE DATA STRUCTURE
    scientific_names_lookup = dict()

    if os.path.isfile(taxon_names_file): 
        print ("Found taxon_names_File") 
        name_f = open(taxon_names_file, 'r') 
        for name_line in name_f: 
            temp_list = re.split(r'\t*\|\t*', name_line) 
            top_key = temp_list[1][0:3]
            if top_key not in scientific_names_lookup:
                scientific_names_lookup[top_key] = dict()
            scientific_names_lookup[top_key][temp_list[1]] = temp_list[0] 
        name_f.close() 
    else: 
        raise Exception("The taxon names file does not exist") 


    #Save taxon_lookup_object
    taxon_lookup_dict = dict()
    taxon_lookup_dict["taxon_lookup"] = scientific_names_lookup

#    dict_size = sys.getsizeof(taxon_lookup_dict)
#    key_size = sys.getsizeof(taxon_lookup_dict.keys())
#    print "DICT SIZE : %s , KEYS SIZE : %s " % (str(dict_size),str(key_size))

    tax_keys = taxon_lookup_dict["taxon_lookup"].keys()

    print ("Tax keys length : " + str(len(tax_keys)))
    print("Dict size : " + str(total_size(taxon_lookup_dict, verbose=False)))
    print("Key Size : " + str(total_size(tax_keys, verbose=False)))

    provenance =  [{"script": __file__, "script_ver": "0.1", 
                    "description": "Lookup created from the names.dmp file from NCBI"}] 

    try: 
        taxon_info =  ws_client.save_objects({"workspace": workspace_name,"objects":[ {"type":"KBaseGenomeAnnotations.TaxonLookup", 
                                                                                       "data":taxon_lookup_dict, 
                                                                                       "name": "taxon_lookup", 
                                                                                       "provenance":provenance}] }) 
        unknown_not_saved = False 
    except Exception, e: 
        print ("SAVE FAILED ON TAXON LOOKUP - GENERAL_EXCEPTION: " + str(sys.exc_info()[0]) + " Exception: " + str(e)) 
        sys.exit(1) 



if __name__ == "__main__":
    import argparse
    import os.path

    parser = argparse.ArgumentParser(description='Create TaxonObjects')
    parser.add_argument('--wsname', nargs='?', help='workspace name to populate', required=True)
    parser.add_argument('--wsurl', action='store', type=str, nargs='?', required=True)
    parser.add_argument('--taxon_names_file', nargs='?', help='path and name to the names.dump file.', required=True)
    args, unknown = parser.parse_known_args()

    try: 
        make_taxon_lookup(wsname = args.wsname, 
                          wsurl = args.wsurl,
                          taxon_names_file = args.taxon_names_file)
    except Exception, e: 
        raise
        #sys.exit(1) 
    sys.exit(0) 






