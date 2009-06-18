import unittest

class TestMakeRequestASCII(unittest.TestCase):
    def _callFUT(self, event):
        from repoze.bfg.request import make_request_ascii
        return make_request_ascii(event)

    def test_it(self):
        request = DummyRequest()
        event = DummyNewRequestEvent(request)
        self._callFUT(event)
        self.assertEqual(request.charset, None)

class TestSubclassedRequest(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.request import DEFAULT_REQUEST_FACTORIES
        return DEFAULT_REQUEST_FACTORIES[None]['factory']
    
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

class TestRequestFactory(unittest.TestCase):
    def _callFUT(self, environ):
        from repoze.bfg.request import request_factory
        return request_factory(environ)

    def _getRequestFactory(self, name_or_iface=None):
        from repoze.bfg.request import DEFAULT_REQUEST_FACTORIES
        return DEFAULT_REQUEST_FACTORIES[name_or_iface]['factory']

    def _makeRoute(self):
        route = DummyRoute()
        factories = {}
        def factory(environ):
            return environ
        for name in (None, 'GET', 'POST', 'PUT', 'DELETE', 'HEAD'):
            factories[name] = {'factory':factory}
        route.request_factories = factories
        return route

    def test_no_route_no_request_method(self):
        from repoze.bfg.interfaces import IRequest
        result = self._callFUT({})
        self.assertEqual(result.__class__, self._getRequestFactory())
        self.failUnless(IRequest.providedBy(result))

    def test_no_route_unknown(self):
        from repoze.bfg.interfaces import IRequest
        result = self._callFUT({'REQUEST_METHOD':'UNKNOWN'})
        self.assertEqual(result.__class__, self._getRequestFactory())
        self.failUnless(IRequest.providedBy(result))

    def test_no_route_get(self):
        from repoze.bfg.interfaces import IGETRequest
        result = self._callFUT({'REQUEST_METHOD':'GET'})
        self.assertEqual(result.__class__, self._getRequestFactory('GET'))
        self.failUnless(IGETRequest.providedBy(result))

    def test_no_route_post(self):
        from repoze.bfg.interfaces import IPOSTRequest
        result = self._callFUT({'REQUEST_METHOD':'POST'})
        self.assertEqual(result.__class__, self._getRequestFactory('POST'))
        self.failUnless(IPOSTRequest.providedBy(result))

    def test_no_route_put(self):
        from repoze.bfg.interfaces import IPUTRequest
        result = self._callFUT({'REQUEST_METHOD':'PUT'})
        self.assertEqual(result.__class__, self._getRequestFactory('PUT'))
        self.failUnless(IPUTRequest.providedBy(result))

    def test_no_route_delete(self):
        from repoze.bfg.interfaces import IDELETERequest
        result = self._callFUT({'REQUEST_METHOD':'DELETE'})
        self.assertEqual(result.__class__, self._getRequestFactory('DELETE'))
        self.failUnless(IDELETERequest.providedBy(result))

    def test_no_route_head(self):
        from repoze.bfg.interfaces import IHEADRequest
        result = self._callFUT({'REQUEST_METHOD':'HEAD'})
        self.assertEqual(result.__class__, self._getRequestFactory('HEAD'))
        self.failUnless(IHEADRequest.providedBy(result))

    def test_route_no_request_method(self):
        route = self._makeRoute()
        environ = {'bfg.routes.route':route}
        result = self._callFUT(environ)
        self.assertEqual(result, environ)

    def test_route_unknown(self):
        route = self._makeRoute()
        environ = {'bfg.routes.route':route, 'REQUEST_METHOD':'UNKNOWN'}
        result = self._callFUT(environ)
        self.assertEqual(result, environ)

    def test_route_known(self):
        route = self._makeRoute()
        environ = {'bfg.routes.route':route, 'REQUEST_METHOD':'GET'}
        result = self._callFUT(environ)
        self.assertEqual(result, environ)

class TestNamedRequestFactories(unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.request import named_request_factories
        return named_request_factories(name)

    def test_it_unnamed(self):
        factories = self._callFUT(None)
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IGETRequest
        from repoze.bfg.interfaces import IPOSTRequest
        from repoze.bfg.interfaces import IPUTRequest
        from repoze.bfg.interfaces import IDELETERequest
        from repoze.bfg.interfaces import IHEADRequest
        for alias, iface in (
            (None, IRequest),
            ('GET', IGETRequest),
            ('POST', IPOSTRequest),
            ('PUT', IPUTRequest),
            ('DELETE', IDELETERequest),
            ('HEAD', IHEADRequest),
            ):
            self.failUnless(alias in factories)
            self.failUnless(iface in factories)
            self.assertEqual(factories[alias], factories[iface])
            named_iface = factories[alias]['interface']
            named_factory = factories[alias]['factory']
            self.failUnless(named_iface.implementedBy(named_factory))
            self.assertEqual(factories[alias]['interface'], iface)
            self.assertEqual(factories[iface]['interface'], iface)
            self.assertEqual(factories[alias]['factory'].charset, 'utf-8')

    def test_it_named(self):
        factories = self._callFUT('name')
        from zope.interface.interface import InterfaceClass
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IGETRequest
        from repoze.bfg.interfaces import IPOSTRequest
        from repoze.bfg.interfaces import IPUTRequest
        from repoze.bfg.interfaces import IDELETERequest
        from repoze.bfg.interfaces import IHEADRequest
        for alias, iface in (
            (None, IRequest),
            ('GET', IGETRequest),
            ('POST', IPOSTRequest),
            ('PUT', IPUTRequest),
            ('DELETE', IDELETERequest),
            ('HEAD', IHEADRequest),
            ):
            self.failUnless(alias in factories)
            self.failUnless(iface in factories)
            self.assertEqual(factories[alias], factories[iface])
            self.assertEqual(factories[alias]['factory'].charset, 'utf-8')
            named_iface = factories[alias]['interface']
            named_factory = factories[alias]['factory']
            self.failUnless(named_iface.implementedBy(named_factory))

class TestDefaultRequestFactories(unittest.TestCase):
    def test_it(self):
        from repoze.bfg.request import DEFAULT_REQUEST_FACTORIES as factories
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IGETRequest
        from repoze.bfg.interfaces import IPOSTRequest
        from repoze.bfg.interfaces import IPUTRequest
        from repoze.bfg.interfaces import IDELETERequest
        from repoze.bfg.interfaces import IHEADRequest
        for alias, iface in (
            (None, IRequest),
            ('GET', IGETRequest),
            ('POST', IPOSTRequest),
            ('PUT', IPUTRequest),
            ('DELETE', IDELETERequest),
            ('HEAD', IHEADRequest),
            ):
            self.failUnless(alias in factories)
            self.failUnless(iface in factories)
            self.assertEqual(factories[alias], factories[iface])
            named_iface = factories[alias]['interface']
            named_factory = factories[alias]['factory']
            self.failUnless(named_iface.implementedBy(named_factory))
            self.assertEqual(factories[alias]['interface'], iface)
            self.assertEqual(factories[iface]['interface'], iface)
            self.assertEqual(factories[alias]['factory'].charset, 'utf-8')


class DummyRoute:
    pass

class DummyRequest:
    pass

class DummyNewRequestEvent:
    def __init__(self, request):
        self.request = request
        



