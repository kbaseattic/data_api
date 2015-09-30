"""
Add simple, flexible caching layer.

Uses `dogpile caching http://dogpilecache.readthedocs.org/en/latest/index.html`_.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/26/15'

## Imports

# Third-party
from dogpile.cache import make_region

## Functions and Classes

def ref_key_generator(namespace, fn, **kw):
    """Return a function that generates a key.

    Args:
        namespace (str): Namespace for all keys
        ref (str): KBase reference
        kw (dict): Additional keywords
    Return:
        Function taking variable number of arguments, each of which
        will be converted to a string and concatenated with underscores,
        prefixed by the namespace and reference string, to create the key.
    """
    name = fn.__name__
    def generate_key(*arg):
        return namespace + "_" + name + "_".join(str(s) for s in arg)

    return generate_key

def get_redis_cache(redis_host='localhost', redis_port=6379):
    """Get a new redis cache 'region' object.

    Args:
        redis_host (str): Hostname or IP for Redis server
        redis_port (int): Redis server listening port
    Returns:
        An object, of type CacheRegion
    """
    region = make_region(
        function_key_generator=ref_key_generator
    ).configure(
        'dogpile.cache.redis',
        arguments={
            'host': redis_host,
            'port': redis_port,
            'db': 0,
            'redis_expiration_time': 60 * 60 * 2,  # 2 hours
            'distributed_lock': True
        }
    )
    return region

