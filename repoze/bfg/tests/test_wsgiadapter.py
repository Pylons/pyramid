import unittest

class NaiveWSGIAdapterTests(unittest.TestCase):
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
        adapter = self._makeOne(view, request)
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
        adapter = self._makeOne(view, request)
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
        adapter = self._makeOne(view, request)
        environ = {}
        start_response = DummyStartResponse()
        result = adapter(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(response.request, request)

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
        

