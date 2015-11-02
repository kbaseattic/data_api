"""
Unit tests for genome_annotation
"""
import logging
from unittest import skipUnless

from . import shared

from doekbase.data_api.core import ObjectAPI


_log = logging.getLogger(__name__)

t_ref = "ReferenceTaxons/242159_taxon"
t = None


def setup():
    shared.setup()
    global t
    t = ObjectAPI(shared.services, shared.token, t_ref)


####### Object API tests


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_info():
    _log.info("Input {}".format(t))
    info = t.get_info()
    _log.info("Output {}".format(info))

    info_keys = ["object_id",
                 "object_name",
                 "object_reference",
                 "object_reference_versioned",
                 "type_string",
                 "save_date",
                 "version",
                 "saved_by",
                 "workspace_id",
                 "workspace_name",
                 "object_checksum",
                 "object_size",
                 "object_metadata"]

    assert isinstance(info, dict)
    for k in info_keys:
        assert k in info
        # TODO assert type of each entry


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_schema():
    _log.info("Input {}".format(t))
    schema = t.get_schema()
    _log.info("Output {}".format(schema))

    assert isinstance(schema, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_typestring():
    _log.info("Input {}".format(t))
    typestring = t.get_typestring()
    _log.info("Output {}".format(typestring))

    assert isinstance(typestring, basestring) or isinstance(typestring, unicode)
    assert len(typestring) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_history():
    _log.info("Input {}".format(t))
    history = t.get_history()
    _log.info("Output {}".format(history))

    assert isinstance(history, list)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_provenance():
    _log.info("Input {}".format(t))
    provenance = t.get_provenance()
    _log.info("Output {}".format(provenance))

    assert isinstance(provenance, list)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_id():
    _log.info("Input {}".format(t))
    object_id = t.get_id()
    _log.info("Output {}".format(object_id))

    assert isinstance(object_id, (int, long) )


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_version():
    _log.info("Input {}".format(t))
    version = t.get_version()
    _log.info("Output {}".format(version))

    assert isinstance(version, basestring) or isinstance(version, unicode)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_name():
    _log.info("Input {}".format(t))
    name = t.get_name()
    _log.info("Output {}".format(name))

    assert isinstance(name, basestring) or isinstance(name, unicode)
    assert len(name) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_data():
    _log.info("Input {}".format(t))
    data = t.get_data()
    _log.info("Output {}".format(data))

    assert isinstance(data, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_data_subset():
    _log.info("Input {}".format(t))
    subset = t.get_data_subset(["scientific_name"])
    _log.info("Output {}".format(subset))

    assert isinstance(subset, dict)
    assert "scientific_name" in subset


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_referrers():
    _log.info("Input {}".format(t))
    referrers = t.get_referrers()
    _log.info("Output {}".format(referrers))

    assert referrers is not None

#TODO add test for copy method
#def test_copy():