"""
Test doekbase.data_api.service_core module
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '12/27/15'

from twisted import internet
from doekbase.data_api import service_core as sc
from doekbase.data_api import exceptions as dapi_exc
from doekbase.data_api.taxonomy.taxon.service import ttypes as tax_ttypes
from doekbase.data_api.taxonomy.taxon.service import thrift_service as \
    taxon_thrift_service
from  doekbase.data_api.taxonomy.taxon.service.interface import TaxonService
from doekbase.data_api.tests.shared import in_travis

import logging
import os
import signal
import unittest as ut

_log = logging.getLogger(__name__)

_travis = in_travis()

class Incomplete1(object):
    @sc.server_method
    def wrapped(self, *args, **kwargs):
        return 'Hello'

    @sc.server_method
    def wrapped_attribute_error(self, *args, **kwargs):
        raise AttributeError('X')

    @sc.server_method
    def wrapped_authn_error(self, *args, **kwargs):
        raise dapi_exc.AuthenticationError('X')

    @sc.server_method
    def wrapped_authz_error(self, *args, **kwargs):
        raise dapi_exc.AuthorizationError('X')

    @sc.server_method
    def wrapped_type_error(self, *args, **kwargs):
        raise TypeError('X')

    @sc.server_method
    def wrapped_other_error(self, *args, **kwargs):
        {'foo': 'bar'}['baz']  # raises KeyError

class Incomplete2(Incomplete1):
    ttypes = tax_ttypes

class Complete(Incomplete2):
    log = logging.getLogger('example')

class TestServerMethod(ut.TestCase):
    def test_server_method_incomplete_class(self):
        # Class missing required attributes raises AssertionError
        args = ('token', 'ref')
        x = Incomplete1()
        self.assertRaises(AssertionError, x.wrapped, *args)
        x = Incomplete2()
        self.assertRaises(AssertionError, x.wrapped, *args)
        x = Complete()
        self.assertEqual(x.wrapped(*args), 'Hello')

    def test_server_method_exceptions(self):
        # Raised exceptions are correct
        args = ('token', 'ref')
        x = Complete()
        self.assertRaises(tax_ttypes.AttributeException,
                          x.wrapped_attribute_error, *args)
        self.assertRaises(tax_ttypes.AuthenticationException,
                          x.wrapped_authn_error, *args)
        self.assertRaises(tax_ttypes.AuthorizationException,
                          x.wrapped_authz_error, *args)
        self.assertRaises(tax_ttypes.TypeException,
                          x.wrapped_type_error, *args)
        self.assertRaises(tax_ttypes.ServiceException,
                          x.wrapped_other_error, *args)

class TestBaseService(ut.TestCase):
    def test_constructor_bad_inputs(self):
        #BaseService constructor handles bad inputs correctly
        args = (logging.getLogger('test'), tax_ttypes, object)
        self.assertRaises(TypeError, sc.BaseService, *args)
        self.assertRaises(KeyError, sc.BaseService, *args, services={})

    def test_constructor(self):
        #BaseService constructor
        args = (logging.getLogger('test'), tax_ttypes, object)
        sc.BaseService(*args, services={'workspace_service_url': 1})

class TestBaseClientConnection(ut.TestCase):
    class FakeClient(object):
        Client = None
    class FakeClient2(object):
        Client = len

    def test_constructor_bad_inputs(self):
        #BaseClientConnection contructor handles bad inputs correctly
        good_url = 'http://localhost'
        self.assertRaises(AttributeError, sc.BaseClientConnection, object,
                          good_url)
        client = self.FakeClient()
        # client.Client not callable
        self.assertRaises(AttributeError, sc.BaseClientConnection, client,
                          good_url)
        client = self.FakeClient2()
        self.assertRaises(ValueError, sc.BaseClientConnection, client,
                          "bad url")
        self.assertRaises(AttributeError, sc.BaseClientConnection, client,
                          good_url)

class TestStartService(ut.TestCase):
    def test_start_service_bad_inputs(self):
        #start_service() handles bad inputs correctly
        # Bad api_class
        args = (object, object, logging.getLogger())
        self.assertRaises(AssertionError, sc.start_service, *args)
        # Bad port
        args = (TaxonService, object, logging.getLogger())
        self.assertRaises(AssertionError, sc.start_service, *args)

    def test_start_service(self):
        #start_service() works for semi-reasonable inputs
        args = (TaxonService, taxon_thrift_service, logging.getLogger())
        # make sure reactor loop stops immediately after it starts
        internet.reactor.callWhenRunning(sc.stop_service)
        # start the reactor loop
        sc.start_service(*args)

    def test_killpgrp(self):
        sc.os = MockOSModule(100)
        sc.kill_process_group(_log)
        self.assertEqual(sc.os.kill_pid, -sc.os.getpgid(sc.os.getpid()))
        self.assertEqual(sc.os.kill_signal, signal.SIGINT)
        sc.os = os # put it back!

    def test_start_service_twisted_exception(self):
        orig_reactor = sc.twisted.internet.reactor
        sc.twisted.internet.reactor = MockReactor()
        args = (TaxonService, taxon_thrift_service, logging.getLogger())
        self.assertRaises(RuntimeError, sc.start_service, *args)
        sc.twisted.internet.reactor = orig_reactor # set it back

class MockOSModule(object):
    """Fake OS module for testing the process group killing, without
    actually killing the process group.
    """
    def __init__(self, pid):
        self.pid = pid
        self.kill_pid, self.kill_signal = None, None

    def kill(self, pid, signal):
        self.kill_pid, self.kill_signal = pid, signal

    def getpid(self):
        return self.pid

    def getpgid(self, pid):
        return self.pid + 1

class MockReactor(object):
    """Fake Twisted reactor.
    """
    def __init__(self, fail=True):
        self._fail = fail

    def run(self):
        if self._fail:
            raise RuntimeError("MockReactor Fail")
    def listenTCP(self, *a, **k):
        return
    def addSystemEventTriegger(self, *a):
        return