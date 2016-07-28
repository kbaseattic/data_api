#!/usr/bin/env python

import os
import requests
import sys

#import doekbase.data_api
from biokbase.workspace.client import Workspace

def make_summaries(
        workspace_name=None,
        workspace_service_url=None) :

    token = os.environ["KB_AUTH_TOKEN"]
    ws = Workspace(url=workspace_service_url, token=token)

    count = 0
    limit = 10000
    start = 1
    end = 10000
    done = False
    while not done:
        results = ws.list_objects({"workspaces": [workspace_name],
                                   "type": "KBaseGenomeAnnotations.GenomeAnnotation",
                                   "minObjectID": start,
                                   "maxObjectID": end,
                                   "limit": limit})

        if len(results) == 0:
            done = True

        for x in results:
            count += 1
            object_ref="{}/{}".format(x[6], x[0])
            print "Object Ref : {}".format(object_ref)
#            print "Object name : {}".format(str(x))

        start = end + 1
        end = end + 10000    


    print count



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace_name', nargs='?', help='workspace name to populate', required=True)
    parser.add_argument('--workspace_service_url', action='store', type=str, nargs='?', required=True) 

    args, unknown = parser.parse_known_args()
    make_summaries(workspace_name = args.workspace_name,
                   workspace_service_url = args.workspace_service_url)
    sys.exit(0)
