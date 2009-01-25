import unittest

class WSGIAppTests(unittest.TestCase):
    def _callFUT(self, app):
        from repoze.bfg.wsgi import wsgiapp
        return wsgiapp(app)

    def test_decorator(self):
        context = DummyContext()
        request = DummyRequest()
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)

class TestNotFound(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.wsgi import NotFound
        return NotFound

    def _makeOne(self):
        return self._getTargetClass()()

    def test_no_message(self):
        environ = {}
        L = []
        def start_response(status, headers):
            L.append((status, headers))
        app = self._makeOne()
        result = app(environ, start_response)
        self.assertEqual(len(result), 1)
        self.failUnless('404 Not Found' in result[0])
        self.assertEqual(L[0][0], '404 Not Found')
        self.assertEqual(L[0][1], [('Content-Length', len(result[0])),
                                   ('Content-Type', 'text/html')])
        
    def test_with_message(self):
        environ = {'message':'<hi!>'}
        L = []
        def start_response(status, headers):
            L.append((status, headers))
        app = self._makeOne()
        result = app(environ, start_response)
        self.assertEqual(len(result), 1)
        self.failUnless('404 Not Found' in result[0])
        self.failUnless('&lt;hi!&gt;' in result[0])
        self.assertEqual(L[0][0], '404 Not Found')
        self.assertEqual(L[0][1], [('Content-Length', len(result[0])),
                                   ('Content-Type', 'text/html')])

class TestUnauthorized(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.wsgi import Unauthorized
        return Unauthorized

    def _makeOne(self):
        return self._getTargetClass()()

    def test_no_message(self):
        environ = {}
        L = []
        def start_response(status, headers):
            L.append((status, headers))
        app = self._makeOne()
        result = app(environ, start_response)
        self.assertEqual(len(result), 1)
        self.failUnless('401 Unauthorized' in result[0])
        self.assertEqual(L[0][0], '401 Unauthorized')
        self.assertEqual(L[0][1], [('Content-Length', len(result[0])),
                                   ('Content-Type', 'text/html')])
        
    def test_with_message(self):
        environ = {'message':'<hi!>'}
        L = []
        def start_response(status, headers):
            L.append((status, headers))
        app = self._makeOne()
        result = app(environ, start_response)
        self.assertEqual(len(result), 1)
        self.failUnless('401 Unauthorized' in result[0])
        self.failUnless('&lt;hi!&gt;' in result[0])
        self.assertEqual(L[0][0], '401 Unauthorized')
        self.assertEqual(L[0][1], [('Content-Length', len(result[0])),
                                   ('Content-Type', 'text/html')])

def dummyapp(environ, start_response):
    """ """

class DummyContext:
    pass

class DummyRequest:
    def get_response(self, application):
        return application


        
      

    

