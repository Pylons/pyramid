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
        from repoze.bfg.request import Request
        return Request
    
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

class DummyRequest:
    pass

class DummyNewRequestEvent:
    def __init__(self, request):
        self.request = request
        



