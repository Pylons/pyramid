import unittest
from zope.testing.cleanup import cleanUp

class WSGIAppTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def test_decorator(self):
        from repoze.bfg.wsgi import wsgiapp
        wrapped = wsgiapp(dummyapp)
        context = DummyContext()
        request = DummyRequest()
        response = wrapped(context, request)
        self.assertEqual(response, dummyapp)

def dummyapp(environ, start_response):
    """ """

class DummyContext:
    pass

class DummyRequest:
    def get_response(self, application):
        return application


        
      

    

