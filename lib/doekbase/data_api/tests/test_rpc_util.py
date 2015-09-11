"""
Test rpc_util functions
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/28/15'

# Imports

# stdlib
import re
# third-party
from nose.tools import raises
# local
from doekbase.data_api import rpc_util
from thrift.Thrift import TType

class Metadata:
    """SAMPLE object for testing validation, etc.

    Default metadata for an object.

    Attributes:
     - object_id
     - object_name
     - object_reference
     - object_reference_versioned
     - type_string
     - save_date
     - version
     - saved_by
     - workspace_id
     - workspace_name
     - object_checksum
     - object_size
     - object_metadata
    """

    thrift_spec = (
        None,  # 0
        (1, TType.STRING, 'object_id', None, None,),  # 1
        (2, TType.STRING, 'object_name', None, None,),  # 2
        (3, TType.STRING, 'object_reference', None, None,),  # 3
        (4, TType.STRING, 'object_reference_versioned', None, None,),  # 4
        (5, TType.STRING, 'type_string', None, None,),  # 5
        (6, TType.DOUBLE, 'save_timestamp', None, None,),  # 6
        (7, TType.STRING, 'version', None, None,),  # 7
        (8, TType.STRING, 'saved_by', None, None,),  # 8
        (9, TType.I64, 'workspace_id', None, None,),  # 9
        (10, TType.STRING, 'workspace_name', None, None,),  # 10
        (11, TType.STRING, 'object_checksum', None, None,),  # 11
        (12, TType.I64, 'object_size', None, None,),  # 12
        (13, TType.STRING, 'object_metadata', None, None,),  # 13
    )

    def __init__(self, object_id=None, object_name=None, object_reference=None,
                 object_reference_versioned=None, type_string=None,
                 save_timestamp=None, version=None, saved_by=None,
                 workspace_id=None, workspace_name=None, object_checksum=None,
                 object_size=None, object_metadata=None, ):
        self.object_id = object_id
        self.object_name = object_name
        self.object_reference = object_reference
        self.object_reference_versioned = object_reference_versioned
        self.type_string = type_string
        self.save_timestamp = save_timestamp
        self.version = version
        self.saved_by = saved_by
        self.workspace_id = workspace_id
        self.workspace_name = workspace_name
        self.object_checksum = object_checksum
        self.object_size = object_size
        self.object_metadata = object_metadata


@raises(rpc_util.InvalidField)
def test_thrift_validate_str_fail():
    rpc_util.thrift_validate(Metadata(object_id=12))

@raises(rpc_util.InvalidField)
def test_thrift_validate_int_fail():
    rpc_util.thrift_validate(Metadata(workspace_id='hello'))

@raises(rpc_util.InvalidField)
def test_thrift_validate_int_double_fail():
    rpc_util.thrift_validate(Metadata(workspace_id=3.5))

@raises(rpc_util.InvalidField)
def test_thrift_validate_double_fail():
    rpc_util.thrift_validate(Metadata(save_timestamp=['June']))

def test_thrift_validate_str():
    rpc_util.thrift_validate(Metadata(object_id='12'))
    rpc_util.thrift_validate(Metadata(object_id=u'12'))

def test_thrift_validate_int():
    rpc_util.thrift_validate(Metadata(workspace_id=12))

def test_thrift_validate_int_double():
    rpc_util.thrift_validate(Metadata(workspace_id=12.0))  # ok if int.
    rpc_util.thrift_validate(Metadata(workspace_id=12))

def test_thrift_validate_double():
    rpc_util.thrift_validate(Metadata(save_timestamp=123456))
    rpc_util.thrift_validate(Metadata(save_timestamp=123456.7))

def test_thrift_errmsg():
    val = 'really big'
    try:
        rpc_util.thrift_validate(Metadata(object_size=val))
    except rpc_util.InvalidField as err:
        msg = str(err)
        #print("@@ {}".format(msg))
        # make sure both type and value appear in error message
        assert val in msg  # note: assumes string value
        assert 'I64' in msg
