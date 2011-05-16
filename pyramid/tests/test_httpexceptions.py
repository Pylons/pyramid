import unittest

class Test_abort(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from pyramid.httpexceptions import abort
        return abort(*arg, **kw)

    def test_status_404(self):
        from pyramid.httpexceptions import HTTPNotFound
        self.assertRaises(HTTPNotFound().exception.__class__,
                          self._callFUT, 404)

    def test_status_201(self):
        from pyramid.httpexceptions import HTTPCreated
        self.assertRaises(HTTPCreated().exception.__class__,
                          self._callFUT, 201)

    def test_extra_kw(self):
        from pyramid.httpexceptions import HTTPNotFound
        try:
            self._callFUT(404,  headers=[('abc', 'def')])
        except HTTPNotFound().exception.__class__, exc:
            self.assertEqual(exc.headers['abc'], 'def')
        else: # pragma: no cover
            raise AssertionError
        
class Test_redirect(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from pyramid.httpexceptions import redirect
        return redirect(*arg, **kw)

    def test_default(self):
        from pyramid.httpexceptions import HTTPFound
        try:
            self._callFUT('http://example.com')
        except HTTPFound().exception.__class__, exc:
            self.assertEqual(exc.location, 'http://example.com')
            self.assertEqual(exc.status, '302 Found')

    def test_custom_code(self):
        from pyramid.httpexceptions import HTTPMovedPermanently
        try:
            self._callFUT('http://example.com', 301)
        except HTTPMovedPermanently().exception.__class__, exc:
            self.assertEqual(exc.location, 'http://example.com')
            self.assertEqual(exc.status, '301 Moved Permanently')
        
    def test_extra_kw(self):
        from pyramid.httpexceptions import HTTPFound
        try:
            self._callFUT('http://example.com', headers=[('abc', 'def')])
        except HTTPFound().exception.__class__, exc:
            self.assertEqual(exc.location, 'http://example.com')
            self.assertEqual(exc.status, '302 Found')
            self.assertEqual(exc.headers['abc'], 'def')
            

class Test_default_httpexception_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from pyramid.httpexceptions import default_httpexception_view
        return default_httpexception_view(context, request)

    def test_call_with_response(self):
        from pyramid.response import Response
        r = Response()
        result = self._callFUT(r, None)
        self.assertEqual(result, r)

    def test_call_with_nonresponse(self):
        request = DummyRequest()
        result = self._callFUT(None, request)
        self.assertEqual(result, 'response')

class DummyRequest(object):
    def get_response(self, context):
        return 'response'
    
        
            
