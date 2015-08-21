"""
Example usage of Avro
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/20/15'

# Imports

# Stdlib
import sys
# Local
from biokbase.data_api.genome import api
from biokbase.data_api.genome import avro_client

# Constants and globals

clients = api.genome_annotation_clients

# Classes and functions

def get_objects(ref):
    """Test simple Avro client.
    """
    client = clients.get_client(api.CLIENT_TYPE_AVRO)
    gen_ann = client.get(ref)
    print('got annotation')
    print('Got genome annotation id={} version={}'.format(
        gen_ann.ident, gen_ann.version.version
    ))

def main():
    ref = sys.argv[1]
    get_objects(ref)

if __name__ == '__main__':
    sys.exit(main())