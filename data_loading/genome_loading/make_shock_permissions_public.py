#!/usr/bin/env python

import os
import requests

import doekbase.data_api
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.workspace.client import Workspace
from doekbase.handle.Client import AbstractHandle as handleClient

services = {
#    "workspace_service_url": "https://ci.kbase.us/services/ws/",
#    "shock_service_url": "https://ci.kbase.us/services/shock-api/",
#    "handle_service_url": "https://ci.kbase.us/services/handle_service/"
#    "workspace_service_url": "https://next.kbase.us/services/ws/",
#    "shock_service_url": "https://next.kbase.us/services/shock-api/",
#    "handle_service_url": "https://next.kbase.us/services/handle_service/"
    "workspace_service_url": "https://kbase.us/services/ws/",
    "shock_service_url": "https://kbase.us/services/shock-api/",
    "handle_service_url": "https://kbase.us/services/handle_service/"
}

token = os.environ["KB_AUTH_TOKEN"]
ws = Workspace(url=services["workspace_service_url"], token=token)
hc = handleClient(url=services["handle_service_url"], token=token)

fix_workspace = "ReferenceEnsemblPlantGenomeAnnotations"

count = 0
limit = 10000
skip = 0
done = False
while not done:
    results = ws.list_objects({"workspaces": [fix_workspace],
                               "type": "KBaseGenomeAnnotations.Assembly",
                               "skip": skip,
                               "limit": limit})

    if len(results) == 0:
        done = True

    for x in results:
        count += 1
        ac = AssemblyAPI(services, token, ref="{}/{}".format(fix_workspace, x[1]))
        handle_ref = ac.get_data()["fasta_handle_ref"]
        shock_node_id = None
        
        try:
            handle = hc.hids_to_handles([handle_ref])[0]
            shock_node_id = handle["id"]
        except Exception, e:
            print "Failed to retrieve handle {} from {}".format(handle_ref,
                                                                services["handle_service_url"])
            _log.exception(e)
            shock_node_id = handle_ref

        print "#"*80
        print x[1], shock_node_id
        print "#"*80

        header = {}
        header["Authorization"] = "Oauth {}".format(token)

        request_url = services["shock_service_url"] + "/node/" + shock_node_id + "/acl/"
        response = requests.get(request_url, headers=header)
        if not response.json()["data"]["public"]["read"]:
            print "NOT PUBLIC"

        response = requests.put(request_url + "public_read", headers=header)    
        print response.json()

        #response = requests.put(request_url + "read?users=" + users[0], headers=header)    
        #print response.json()

        #response = requests.get(request_url, headers=header)
        #print response.json()

    skip += 10000

print count
