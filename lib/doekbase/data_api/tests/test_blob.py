"""
Unit tests for assembly
"""
import logging

from . import shared
from doekbase.data_api.blob import blob
import unittest

def setup():
    shared.setup()

def test_blob_base():
    try:
        b = blob.Blob()
        assert False, "Unexpected success instantiating base Blob class"
    except TypeError:
        pass

def test_blob_shock_noargs():
    try:
        b = blob.BlobShockNode()
    except ValueError:
        pass

def test_blob_shock_read():
    b = blob.BlobShockNode(url="")

if __name__ == '__main__':
    unittest.main()
