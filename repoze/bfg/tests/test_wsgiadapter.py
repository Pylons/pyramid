import unittest

from zope.component.testing import PlacelessSetup

class NaiveWSGIAdapterTests(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getTargetClass(self):
        from repoze.bfg.wsgiadapter import NaiveWSGIViewAdapter
        return NaiveWSGIViewAdapter

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_view_takes_no_args(self):
        response = DummyResponse()
        response.app_iter = ['Hello world']
        def view():
            return response
        request = DummyRequest()
        context = DummyContext()
        adapter = self._makeOne(context, request, view)
        environ = {}
        start_response = DummyStartResponse()
        result = adapter(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')

    def test_view_takes_pep_333_args(self):
        response = DummyResponse()
        response.app_iter = ['Hello world']
        def view(environ, start_response):
            response.environ = environ
            response.start_response = start_response
            return response
        request = DummyRequest()
        context = DummyContext()
        adapter = self._makeOne(context, request, view)
        environ = {}
        start_response = DummyStartResponse()
        result = adapter(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(response.environ, environ)
        self.assertEqual(response.start_response, start_response)

    def test_view_takes_zopey_args(self):
        request = DummyRequest()
        response = DummyResponse()
        response.app_iter = ['Hello world']
        def view(request):
            response.request = request
            return response
        context = DummyContext()
        adapter = self._makeOne(context, request, view)
        environ = {}
        start_response = DummyStartResponse()
        result = adapter(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(response.request, request)

    def test_view_is_response(self):
        request = DummyRequest()
        response = DummyResponse()
        response.app_iter = ['Hello world']
        context = DummyContext()
        adapter = self._makeOne(context, request, response)
        environ = {}
        start_response = DummyStartResponse()
        result = adapter(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')

    def test_view_returns_nonresponse(self):
        request = DummyRequest()
        def view(request):
            return None
        context = DummyContext()
        adapter = self._makeOne(context, request, view)
        environ = {}
        start_response = DummyStartResponse()
        self.assertRaises(ValueError, adapter, environ, start_response)


class DummyContext:
    pass

class DummyRequest:
    pass

class DummyResponse:
    status = '200 OK'
    headerlist = ()
    app_iter = ()
    
class DummyStartResponse:
    status = None
    headers = None
    def __call__(self, status, headers):
        self.status = status
        self.headers = headers
        

