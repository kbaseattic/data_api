"""
Add simple, flexible caching layer.

Uses `dogpile caching http://dogpilecache.readthedocs.org/en/latest/index.html`_.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/26/15'

from dogpile.cache import make_region

def my_key_generator(namespace, fn, **kw):
    fname = fn.__name__

    def generate_key(*arg):
        return namespace + "_" + fname + "_".join(str(s) for s in arg)

    return generate_key

def get_redis_cache(redis_host='localhost', redis_port=6379):
    region = make_region(
        function_key_generator=my_key_generator
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
