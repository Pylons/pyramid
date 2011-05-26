import unittest

class TestNotFound(unittest.TestCase):
    def _makeOne(self, message):
        from pyramid.exceptions import NotFound
        return NotFound(message)

    def test_it(self):
        from pyramid.interfaces import IExceptionResponse
        e = self._makeOne('notfound')
        self.assertTrue(IExceptionResponse.providedBy(e))
        self.assertEqual(e.status, '404 Not Found')
        self.assertEqual(e.message, 'notfound')

class TestForbidden(unittest.TestCase):
    def _makeOne(self, message):
        from pyramid.exceptions import Forbidden
        return Forbidden(message)

    def test_it(self):
        from pyramid.interfaces import IExceptionResponse
        e = self._makeOne('forbidden')
        self.assertTrue(IExceptionResponse.providedBy(e))
        self.assertEqual(e.status, '403 Forbidden')
        self.assertEqual(e.message, 'forbidden')

class Test_abort(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from pyramid.exceptions import abort
        return abort(*arg, **kw)

    def test_status_404(self):
        from pyramid.exceptions import HTTPNotFound
        self.assertRaises(HTTPNotFound().exception.__class__,
                          self._callFUT, 404)

    def test_status_201(self):
        from pyramid.exceptions import HTTPCreated
        self.assertRaises(HTTPCreated().exception.__class__,
                          self._callFUT, 201)

    def test_extra_kw(self):
        from pyramid.exceptions import HTTPNotFound
        try:
            self._callFUT(404,  headers=[('abc', 'def')])
        except HTTPNotFound().exception.__class__, exc:
            self.assertEqual(exc.headers['abc'], 'def')
        else: # pragma: no cover
            raise AssertionError
        
class Test_redirect(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from pyramid.exceptions import redirect
        return redirect(*arg, **kw)

    def test_default(self):
        from pyramid.exceptions import HTTPFound
        try:
            self._callFUT('http://example.com')
        except HTTPFound().exception.__class__, exc:
            self.assertEqual(exc.location, 'http://example.com')
            self.assertEqual(exc.status, '302 Found')

    def test_custom_code(self):
        from pyramid.exceptions import HTTPMovedPermanently
        try:
            self._callFUT('http://example.com', 301)
        except HTTPMovedPermanently().exception.__class__, exc:
            self.assertEqual(exc.location, 'http://example.com')
            self.assertEqual(exc.status, '301 Moved Permanently')
        
    def test_extra_kw(self):
        from pyramid.exceptions import HTTPFound
        try:
            self._callFUT('http://example.com', headers=[('abc', 'def')])
        except HTTPFound().exception.__class__, exc:
            self.assertEqual(exc.location, 'http://example.com')
            self.assertEqual(exc.status, '302 Found')
            self.assertEqual(exc.headers['abc'], 'def')
            

class Test_default_exceptionresponse_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from pyramid.exceptions import default_exceptionresponse_view
        return default_exceptionresponse_view(context, request)

    def test_call_with_exception(self):
        context = Exception()
        result = self._callFUT(context, None)
        self.assertEqual(result, context)

    def test_call_with_nonexception(self):
        request = DummyRequest()
        context = Exception()
        request.exception = context
        result = self._callFUT(None, request)
        self.assertEqual(result, context)

class DummyRequest(object):
    exception = None
    def get_response(self, context):
        return 'response'
    
        
            
