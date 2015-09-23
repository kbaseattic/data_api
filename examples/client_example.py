"""
Example usage of Avro
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/20/15'

# Imports

# Stdlib
import argparse
import sys
# Local
from doekbase.data_api.genome import api
from doekbase.data_api.genome import avro_client  # keep!
from doekbase.data_api import registry
from doekbase.data_api.avro_rpc import AVRO_DEFAULT_PORT

# Constants and globals

# Classes and functions

def get_genome_api(kw):
    return registry.g_registry.get_client(api.NAMESPACE, registry.AVRO, **kw)

def get_objects(ref, kw):
    """Test simple Avro client.
    """
    gen_ann = get_genome_api(kw).get_info(ref)
    print('Got genome annotation id={} version={}'.format(
        gen_ann['ident'], gen_ann['version']['version']
    ))
    print('[DATA] {}'.format(gen_ann['info']))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ref', help='Object reference ID, e.g. 1019/4/1')
    ap.add_argument('--host', dest='host', default='localhost',
                    metavar='ADDR', help='Remote server host '
                                         '(default=%(default)s)')
    ap.add_argument('--port', dest='port', default=AVRO_DEFAULT_PORT,
                    metavar='PORT', help='Remote server port '
                                         '(default=%(default)d)')
    args = ap.parse_args()
    kw = {'host': args.host, 'port': args.port}
    get_objects(args.ref, kw)

if __name__ == '__main__':
    sys.exit(main())
