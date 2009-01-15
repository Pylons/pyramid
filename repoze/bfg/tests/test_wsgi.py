import unittest
from zope.testing.cleanup import cleanUp

class WSGIAppTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def test_decorator(self):
        body = 'Unauthorized'
        headerlist = [ ('Content-Type', 'text/plain'),
                       ('Content-Length', len(body)) ]
        status = '401 Unauthorized'
        def real_wsgiapp(environ, start_response):
            start_response(status, headerlist)
            return [body]
        from repoze.bfg.wsgi import wsgiapp
        wrapped = wsgiapp(real_wsgiapp)
        context = DummyContext()
        request = DummyRequest({})
        response = wrapped(context, request)
        self.assertEqual(response.status, status)
        self.assertEqual(response.headerlist, headerlist)
        self.assertEqual(response.app_iter, [body])

    def test_decorator_alternate_iresponsefactory(self):
        body = 'Unauthorized'
        headerlist = [ ('Content-Type', 'text/plain'),
                       ('Content-Length', len(body)) ]
        status = '401 Unauthorized'
        def real_wsgiapp(environ, start_response):
            start_response(status, headerlist)
            return [body]
        from repoze.bfg.wsgi import wsgiapp
        wrapped = wsgiapp(real_wsgiapp)
        context = DummyContext()
        request = DummyRequest({})
        from repoze.bfg.interfaces import IResponseFactory
        from zope.component import getGlobalSiteManager
        from webob import Response
        class Response2(Response):
            pass
        gsm = getGlobalSiteManager()
        gsm.registerUtility(Response2, IResponseFactory)
        response = wrapped(context, request)
        self.failUnless(isinstance(response, Response2))

    def test_decorator_startresponse_uncalled(self):
        body = 'Unauthorized'
        headerlist = [ ('Content-Type', 'text/plain'),
                       ('Content-Length', len(body)) ]
        status = '401 Unauthorized'
        def real_wsgiapp(environ, start_response):
            return [body]
        from repoze.bfg.wsgi import wsgiapp
        wrapped = wsgiapp(real_wsgiapp)
        context = DummyContext()
        request = DummyRequest({})
        self.assertRaises(RuntimeError, wrapped, context, request)

class DummyContext:
    pass

class DummyRequest:
    def __init__(self, environ):
        self.environ = environ


        
      

    

