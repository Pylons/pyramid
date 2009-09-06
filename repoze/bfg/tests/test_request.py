import unittest
from repoze.bfg.testing import cleanUp

class TestMakeRequestASCII(unittest.TestCase):
    def _callFUT(self, event):
        from repoze.bfg.request import make_request_ascii
        return make_request_ascii(event)

    def test_it(self):
        request = DummyRequest()
        event = DummyNewRequestEvent(request)
        self._callFUT(event)
        self.assertEqual(request.charset, None)

class RequestTestBase(object):
    def _makeOne(self, environ):
        request = self._getTargetClass()(environ)
        return request

    def test_params_decoded_from_utf_8_by_default(self):
        environ = {
            'PATH_INFO':'/',
            'QUERY_STRING':'la=La%20Pe%C3%B1a'
            }
        request = self._makeOne(environ)
        self.assertEqual(request.GET['la'], u'La Pe\xf1a')

    def test_params_bystring_when_charset_None(self):
        environ = {
            'PATH_INFO':'/',
            'QUERY_STRING':'la=La%20Pe%C3%B1a'
            }
        request = self._makeOne(environ)
        request.charset = None
        self.assertEqual(request.GET['la'], 'La Pe\xc3\xb1a')

    def test_class_implements(self):
        from repoze.bfg.interfaces import IRequest
        klass = self._getTargetClass()
        self.assertTrue(IRequest.implementedBy(klass))

    def test_instance_provides(self):
        from repoze.bfg.interfaces import IRequest
        inst = self._makeOne({})
        self.assertTrue(IRequest.providedBy(inst))

class TestRequest(unittest.TestCase, RequestTestBase):
        def _getTargetClass(self):
            from repoze.bfg.request import Request
            return Request
    
class TestRouteRequest(unittest.TestCase, RequestTestBase):
        def _getTargetClass(self):
            from repoze.bfg.request import create_route_request_factory
            return create_route_request_factory('abc')

class TestRequestFactory(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, environ):
        from repoze.bfg.request import request_factory
        return request_factory(environ)

    def test_it_no_route(self):
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.request import Request
        result = self._callFUT({})
        self.assertEqual(result.__class__, Request)
        self.failUnless(IRequest.providedBy(result))

    def test_it_with_route_found(self):
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRouteRequest
        sm = getSiteManager()
        sm.registerUtility(DummyRequest, IRouteRequest, 'routename')
        route = DummyRoute('routename')
        result = self._callFUT({'bfg.routes.route':route})
        self.assertEqual(result.__class__, DummyRequest)

    def test_it_with_route_notfound(self):
        from repoze.bfg.request import Request
        route = DummyRoute('routename')
        result = self._callFUT({'bfg.routes.route':route})
        self.assertEqual(result.__class__, Request)

class Test_create_route_request_factory(unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.request import create_route_request_factory
        return create_route_request_factory(name)

    def test_it(self):
        from repoze.bfg.interfaces import IRouteRequest
        from repoze.bfg.interfaces import IRequest
        factory = self._callFUT('routename')
        self.failUnless(IRouteRequest.implementedBy(factory))
        self.failUnless(IRequest.implementedBy(factory))

class DummyRoute:
    def __init__(self, name):
        self.name = name
class DummyRequest:
    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ

class DummyNewRequestEvent:
    def __init__(self, request):
        self.request = request
        



