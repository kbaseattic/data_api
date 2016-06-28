"""
Unit tests for pbar (progress bar) module
"""
from . import shared
from doekbase.data_api.pbar import PBar
import unittest
import StringIO

def setup():
    shared.setup()

def test_pbar_noargs():
    PBar()

def test_pbar_1arg():
    PBar(100)

def test_pbar_2arg():
    PBar(total=100, width=60)

def test_pbar_total():
    try:
        PBar(total=0)
        assert False, "Unexpected success with total = 0"
    except:
        pass
    try:
        PBar(total=-12)
        assert False, "Unexpected success with total < 0"
    except:
        pass


def test_pbar_width():
    try:
        PBar(width=0)
        assert False, "Unexpected success with width = 0"
    except:
        pass
    try:
        PBar(width=-1)
        assert False, "Unexpected success with width < 0"
    except:
        pass


def test_pbar_inc():
    n = 100
    s = StringIO.StringIO()
    p = PBar(total=n, ostrm=s)
    for i in xrange(n):
        p.inc(1)
    p.done()

if __name__ == '__main__':
    unittest.main()
