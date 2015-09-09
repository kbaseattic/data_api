"""
Unit tests for genome_annotation
"""

# Imports

# Stdlib
import logging
from unittest import skipUnless
# Local
from . import shared
from biokbase.data_api.annotation.genome_annotation import GenomeAnnotationAPI

# Logging

_log = logging.getLogger(__name__)

# Globals

genome = "PrototypeReferenceGenomes/kb|g.3899"

services = {}

# Feature container objects
workspaces = {
    '3899': {
        'gene': 'PrototypeReferenceGenomes/kb|g.3899_feature_container_gene',
        'cds': 'PrototypeReferenceGenomes/kb|g.3899_feature_container_CDS',
        'mrna': 'PrototypeReferenceGenomes/kb|g.3899_feature_container_mRNA'
    },
    '3157': {
        'cds': 'PrototypeReferenceGenomes/kb|g.3157_feature_container_CDS'
    }
}
shared.determine_can_connect(workspaces)

# Some purposely invalid object IDs
bad_obj = ['kb|g.3899.mRNA.99999999999', 'kb|g.3899.CDS.1']

# Functions and classes

# some shorthands

fetching_info = lambda idlist: _log.info(
    "Fetching CDS by: {}".format(', '.join(idlist)))

connect = lambda : GenomeAnnotationAPI(services=services, ref=genome)

def verify_feature_len(idlist, method, length=1):
    """Verify features returned by invoking `method` on `idlist`
    are exactly of the given `length`.
    Perform assertions. Length -1 means "is not None"
    """
    idlist = idlist + bad_obj
    api = connect()
    fetching_info(idlist)
    r = getattr(api, method)(idlist)  # get the data using provided method
    if length == -1:
        assert r is not None
    else:
        assert len(r) == length
    return r  # for re-using the result later

# Setup

def setup():
    global services
    shared.setup()
    services = shared.get_services()

# Tests

mrna_ids = ['kb|g.3899.mRNA.0', 'kb|g.3899.mRNA.2066']
cds_ids = ['kb|g.3899.CDS.36740', 'kb|g.3899.CDS.36739']
gene_ids = ['kb|g.3899.locus.26937', 'kb|g.3899.locus.26761']

_workspace = workspaces['3899']

@skipUnless(_workspace['mrna'] and _workspace['cds'], shared.connect_fail)
def test_get_cds_by_mrna():
    verify_feature_len(mrna_ids, 'get_cds_by_mrna', -1)

@skipUnless(_workspace['mrna'] and _workspace['cds'], shared.connect_fail)
def test_get_mrna_by_cds():
    verify_feature_len(cds_ids, 'get_mrna_by_cds', 2)

@skipUnless(_workspace['mrna'] and _workspace['gene'], shared.connect_fail)
def test_get_gene_by_mrna():
    verify_feature_len(mrna_ids, 'get_gene_by_mrna', 2)

@skipUnless(_workspace['gene'] and _workspace['cds'], shared.connect_fail)
def test_get_cds_by_gene():
    verify_feature_len(gene_ids, 'get_cds_by_gene', 2)

@skipUnless(_workspace['mrna'] and _workspace['gene'], shared.connect_fail)
def test_get_mrna_by_gene():
    verify_feature_len(gene_ids, 'get_mrna_by_gene', 2)

@skipUnless(_workspace['gene'] and _workspace['cds'], shared.connect_fail)
def test_get_gene_by_cds():
    verify_feature_len(cds_ids, 'get_gene_by_cds', 2)



