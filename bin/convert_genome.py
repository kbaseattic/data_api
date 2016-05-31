#!/usr/bin/env python
"""

"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '5/12/16'

# stdlib
import argparse
import logging
import os
import sys
# local
from doekbase.data_api.converters import base, genome
from doekbase.workspace.client import Workspace

_log = logging.getLogger('data_api.converter.script')
INFO = lambda s: _log.info(s)
ERROR = lambda s: _log.error(s)

example_ga = 'ReferenceGenomeAnnotations/kb|g.166819'
example_asm = 'ReferenceGenomeAnnotations/kb|g.166819_assembly'

def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('workspace', default='6502')
    parser.add_argument('-g', dest='gaobj', default=None,
                        help='GenomeAnnotation object, e.g. {}'.format(example_ga),
                        metavar='ID')
    parser.add_argument('-a', dest='asmobj',
                        help='Assembly object, e.g. {}'.format(example_asm),
                        metavar='ID')
    parser.add_argument('-p', dest='progress', help='Show progress bar(s)',
                        action='store_true')
    parser.add_argument('-v', dest='vb', action='count', default=0,
                        help='Increase verbosity (repeatable)')
    parser.add_argument('-k', dest='kbdep', default='ci', metavar='DEPLOYMENT',
                        help='KBase deployment, "ci" or "prod" (default=ci)')
    return parser.parse_args()

def main():
    args = _parse_args()
    kbase_instance = args.kbdep.lower()
    if not kbase_instance in ['ci', 'prod']:
        ERROR('-k option value must be "ci" or "prod"')
        sys.exit(1)
    if args.gaobj is not None and args.asmobj is not None:
        ERROR('choose either -a or -g, not both')
        sys.exit(2)
    if args.vb > 1:
        genome.set_converter_loglevel(logging.DEBUG)
    elif args.vb > 0:
        genome.set_converter_loglevel(logging.INFO)
    else:
        genome.set_converter_loglevel(logging.WARN)
    INFO('Initialize converter')
    if args.gaobj is not None:
        converter_class = genome.GenomeConverter
        source_type = 'GenomeAnnotation'
        what_is_created = 'Genome + ContigSet'
    else:
        converter_class = genome.AssemblyConverter
        source_type = 'Assembly'
        what_is_created = 'ContigSet'
    converter = converter_class(ref=args.gaobj,
                                show_progress_bar=args.progress,
                                kbase_instance=kbase_instance)
    INFO('Convert {} to {}'.format(source_type, what_is_created))
    # Get name for workspace
    workspace_name = args.workspace
    try:
        ws_int_id = int(workspace_name)
        workspace_name = Workspace(
            url=base.Converter.all_services[kbase_instance]['workspace_service_url'],
            token=base.Converter.token).get_workspace_info({'id': ws_int_id})[1]
        INFO('Workspace ID={} converted to name={}'.format(ws_int_id, workspace_name))
    except ValueError:
        pass
    ref = converter.convert(workspace_name=workspace_name)
    INFO('Done.')
    print('{} created, ref={}'.format(what_is_created, ref))
    sys.exit(0)

if __name__ == '__main__':
    main()
