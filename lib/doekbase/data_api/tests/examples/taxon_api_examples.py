"""
Example scripts for the Taxon API.

These scripts require a valid KBase authentication token to be
in the environment at runtime.

Unfortunately there is no really easy way to get this token right now. One
way to do it is to login to KBase, open a narrative (any narrative), and then
use the developer tools for your browser to get to a JavaScript console and then
print the value of the variable ``kb.token``.

Once you have this value, set it in your environment as KB_AUTH_TOKEN,
e.g., in the Unix bash shell::

    export KB_AUTH_TOKEN='un=myname|tokenid=abcdef012-0000-2222-3333-123456789abc|expiry=1469959033|client_id=myname|token_type=Bearer|SigningSubject=https://nexus.api.globusonline.org/goauth/keys/some-long-key-here|sig=123456...'

You can add this command to your login scripts (e.g. your "~/.bash_profile")
so it's not so painful in the future.

"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/18/15'

# Stdlib
import os
import sys
# Third-party
# Local

def eprint(msg):
    sys.stderr.write(msg + '\n')

def get_simple():
    from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
    taxon = TaxonAPI(token=os.environ.get('KB_AUTH_TOKEN'), ref='1019/4')
    eprint('Got taxon "{} ({})"'.format(taxon.get_scientific_name(),
                                        taxon.get_taxonomic_id()))
