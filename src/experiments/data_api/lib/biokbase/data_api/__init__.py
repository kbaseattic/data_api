import os

def _get_token():
    try:
        token = os.environ["KB_AUTH_TOKEN"]
    except KeyError:
        raise Exception("Missing authentication token!  Set KB_AUTH_TOKEN environment variable.")
        
