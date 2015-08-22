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
from biokbase.data_api.genome import avro_client  # keep!
from biokbase.data_api import registry


# Constants and globals

genome_api = registry.g_registry.get_client(api.NAMESPACE,
                                            registry.AVRO)

# Classes and functions

def get_objects(ref):
    """Test simple Avro client.
    """
    gen_ann = genome_api.get_info(ref)
    print('Got genome annotation id={} version={}'.format(
        gen_ann['ident'], gen_ann['version']['version']
    ))
    print('Info:\n{}'.format(gen_ann['info']))

def main():
    ref = sys.argv[1]
    get_objects(ref)

if __name__ == '__main__':
    sys.exit(main())