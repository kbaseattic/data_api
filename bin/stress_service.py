#!/usr/bin/env python

import argparse
import os
import multiprocessing
from six import print_
import sys
import time

import doekbase.data_api
#from doekbase.data_api.taxonomy.taxon.api import TaxonClientAPI
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationClientAPI
from doekbase.data_api.sequence.assembly.api import AssemblyClientAPI
from doekbase.workspace.client import Workspace

PORTS = {
    'taxon': 9101,
    'assembly': 9102,
    'genome_annotation': 9103
}

token = os.environ["KB_AUTH_TOKEN"]

workspace_names = ["ReferenceEnsemblPlantGenomeAnnotations", "ReferenceGenomeAnnotations"]

def get_genome_annotation_url(host):
    return "http://{shost}:{port}".format(shost=host, port=PORTS['genome_annotation'])

def get_assembly_url(host):
    return "http://{shost}:{port}".format(shost=host, port=PORTS['assembly'])

def get_workspace_url(host):
    return "https://{khost}.kbase.us/services/ws/".format(khost=host)

def run(service_host, kbase_host):
    pid = os.getpid()
    ws = Workspace(url=get_workspace_url(kbase_host), token=token)
    for name in workspace_names:

        while 1:
            print('[{:d}] List objects'.format(pid))
            try:
                annotations = ws.list_objects({"workspaces": [name], "type": "KBaseGenomeAnnotations.GenomeAnnotation"})
                break
            except Exception as err:
                print('Retry on timeout: {}'.format(str(err)))

        print('[{:d}] Got {:d} objects'.format(pid, len(annotations)))
        for obj_num, obj in enumerate(annotations):
            ref = obj[7] + "/" + obj[1]
            print('[{:d}] Fetch {:d}/{:d}: {}'.format(pid, obj_num +1, len(annotations), ref))
            ga = GenomeAnnotationClientAPI(get_genome_annotation_url(service_host),token,ref)
            #taxon = TaxonClientAPI(services["taxon_service_url"],token,ga.get_taxon())
            assembly = AssemblyClientAPI(get_assembly_url(service_host), token, ga.get_assembly())
            while 1:
                try:
                    fids = ga.get_feature_ids()
                    fdata = ga.get_features()
                    cids = assembly.get_contig_ids()
                    contigs = assembly.get_contigs()
                except doekbase.data_api.exceptions.ServiceError as err:
                    print('[{:d}] Error: {}'.format(pid, err))
                    time.sleep(0.5)
                    print('[{:d}] Retrying'.format(pid))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='shost', help='service host (localhost)', default='localhost',
                        metavar='HOST')
    parser.add_argument('-k', dest='khost', help='kbase host (ci)', default='ci', metavar='HOST')
    parser.add_argument('-p', dest='par', help='run in parallel N times', default=1, metavar='N',
                        type=int)
    args = parser.parse_args()
    if args.par < 2:
        run(args.shost, args.khost)
    else:
        processes = []
        print_('start {} processes'.format(args.par))
        for i in range(args.par):
            print_('.', end='\r')
            process = multiprocessing.Process(target=run, args=(args.shost, args.khost))
            process.start()
            processes.append(process)
        print_('\njoin processes')
        for process in processes:
            print_('.', end='\r')
            process.join()
    return 0

if __name__ == '__main__':
    sys.exit(main())
