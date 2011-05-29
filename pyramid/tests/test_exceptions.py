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
        self.assertRaises(HTTPNotFound, self._callFUT, 404)

    def test_status_201(self):
        from pyramid.exceptions import HTTPCreated
        self.assertRaises(HTTPCreated, self._callFUT, 201)

    def test_extra_kw(self):
        from pyramid.exceptions import HTTPNotFound
        try:
            self._callFUT(404,  headers=[('abc', 'def')])
        except HTTPNotFound, exc:
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
        except HTTPFound, exc:
            self.assertEqual(exc.location, 'http://example.com')
            self.assertEqual(exc.status, '302 Found')

    def test_custom_code(self):
        from pyramid.exceptions import HTTPMovedPermanently
        try:
            self._callFUT('http://example.com', 301)
        except HTTPMovedPermanently, exc:
            self.assertEqual(exc.location, 'http://example.com')
            self.assertEqual(exc.status, '301 Moved Permanently')
        
    def test_extra_kw(self):
        from pyramid.exceptions import HTTPFound
        try:
            self._callFUT('http://example.com', headers=[('abc', 'def')])
        except HTTPFound, exc:
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

class Test__no_escape(unittest.TestCase):
    def _callFUT(self, val):
        from pyramid.exceptions import _no_escape
        return _no_escape(val)

    def test_null(self):
        self.assertEqual(self._callFUT(None), '')

    def test_not_basestring(self):
        self.assertEqual(self._callFUT(42), '42')

    def test_unicode(self):
        class DummyUnicodeObject(object):
            def __unicode__(self):
                return u'42'
        duo = DummyUnicodeObject()
        self.assertEqual(self._callFUT(duo), u'42')

class TestWSGIHTTPException(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.exceptions import WSGIHTTPException
        return WSGIHTTPException

    def _getTargetSubclass(self, code='200', title='OK',
                           explanation='explanation', empty_body=False):
        cls = self._getTargetClass()
        class Subclass(cls):
            pass
        Subclass.empty_body = empty_body
        Subclass.code = code
        Subclass.title = title
        Subclass.explanation = explanation
        return Subclass

    def _makeOne(self, *arg, **kw):
        cls = self._getTargetClass()
        return cls(*arg, **kw)

    def test_ctor_sets_detail(self):
        exc = self._makeOne('message')
        self.assertEqual(exc.detail, 'message')

    def test_ctor_sets_comment(self):
        exc = self._makeOne(comment='comment')
        self.assertEqual(exc.comment, 'comment')

    def test_ctor_calls_Exception_ctor(self):
        exc = self._makeOne('message')
        self.assertEqual(exc.message, 'message')

    def test_ctor_calls_Response_ctor(self):
        exc = self._makeOne('message')
        self.assertEqual(exc.status, 'None None')

    def test_ctor_extends_headers(self):
        exc = self._makeOne(headers=[('X-Foo', 'foo')])
        self.assertEqual(exc.headers.get('X-Foo'), 'foo')

    def test_ctor_sets_body_template_obj(self):
        exc = self._makeOne(body_template='${foo}')
        self.assertEqual(
            exc.body_template_obj.substitute({'foo':'foo'}), 'foo')

    def test_ctor_with_empty_body(self):
        cls = self._getTargetSubclass(empty_body=True)
        exc = cls()
        self.assertEqual(exc.content_type, None)
        self.assertEqual(exc.content_length, None)

    def test_ctor_with_body_doesnt_set_default_app_iter(self):
        exc = self._makeOne(body='123')
        self.assertEqual(exc.app_iter, ['123'])

    def test_ctor_with_unicode_body_doesnt_set_default_app_iter(self):
        exc = self._makeOne(unicode_body=u'123')
        self.assertEqual(exc.app_iter, ['123'])

    def test_ctor_with_app_iter_doesnt_set_default_app_iter(self):
        exc = self._makeOne(app_iter=['123'])
        self.assertEqual(exc.app_iter, ['123'])

    def test_ctor_with_body_sets_default_app_iter_html(self):
        cls = self._getTargetSubclass()
        exc = cls('detail')
        body = list(exc.app_iter)[0]
        self.assertTrue(body.startswith('<html'))
        self.assertTrue('200 OK' in body)
        self.assertTrue('explanation' in body)
        self.assertTrue('detail' in body)
        
    def test_ctor_with_body_sets_default_app_iter_text(self):
        cls = self._getTargetSubclass()
        exc = cls('detail')
        exc.content_type = 'text/plain'
        body = list(exc.app_iter)[0]
        self.assertEqual(body, '200 OK\n\nexplanation\n\n\ndetail\n\n')

    def test__str__detail(self):
        exc = self._makeOne()
        exc.detail = 'abc'
        self.assertEqual(str(exc), 'abc')
        
    def test__str__explanation(self):
        exc = self._makeOne()
        exc.explanation = 'def'
        self.assertEqual(str(exc), 'def')

    def test_wsgi_response(self):
        exc = self._makeOne()
        self.assertTrue(exc is exc.wsgi_response)

    def test_exception(self):
        exc = self._makeOne()
        self.assertTrue(exc is exc.exception)

    def test__default_app_iter_no_comment_plain(self):
        cls = self._getTargetSubclass()
        exc = cls()
        exc.content_type = 'text/plain'
        body = list(exc._default_app_iter())[0]
        self.assertEqual(body, '200 OK\n\nexplanation\n\n\n\n\n')

    def test__default_app_iter_with_comment_plain(self):
        cls = self._getTargetSubclass()
        exc = cls(comment='comment')
        exc.content_type = 'text/plain'
        body = list(exc._default_app_iter())[0]
        self.assertEqual(body, '200 OK\n\nexplanation\n\n\n\ncomment\n')
        
    def test__default_app_iter_no_comment_html(self):
        cls = self._getTargetSubclass()
        exc = cls()
        exc.content_type = 'text/html'
        body = list(exc._default_app_iter())[0]
        self.assertFalse('<!-- ' in body)

    def test__default_app_iter_with_comment_html(self):
        cls = self._getTargetSubclass()
        exc = cls(comment='comment & comment')
        exc.content_type = 'text/html'
        body = list(exc._default_app_iter())[0]
        self.assertTrue('<!-- comment &amp; comment -->' in body)

    def test_custom_body_template_no_environ(self):
        cls = self._getTargetSubclass()
        exc = cls(body_template='${location}', location='foo')
        exc.content_type = 'text/plain'
        body = list(exc._default_app_iter())[0]
        self.assertEqual(body, '200 OK\n\nfoo')

    def test_custom_body_template_with_environ(self):
        cls = self._getTargetSubclass()
        from pyramid.request import Request
        request = Request.blank('/')
        exc = cls(body_template='${REQUEST_METHOD}', request=request)
        exc.content_type = 'text/plain'
        body = list(exc._default_app_iter())[0]
        self.assertEqual(body, '200 OK\n\nGET')

    def test_body_template_unicode(self):
        from pyramid.request import Request
        cls = self._getTargetSubclass()
        la = unicode('/La Pe\xc3\xb1a', 'utf-8')
        request = Request.blank('/')
        request.environ['unicodeval'] = la
        exc = cls(body_template='${unicodeval}', request=request)
        exc.content_type = 'text/plain'
        body = list(exc._default_app_iter())[0]
        self.assertEqual(body, '200 OK\n\n/La Pe\xc3\xb1a')

class TestRenderAllExceptionsWithoutArguments(unittest.TestCase):
    def _doit(self, content_type):
        from pyramid.exceptions import status_map
        L = []
        self.assertTrue(status_map)
        for v in status_map.values():
            exc = v()
            exc.content_type = content_type
            result = list(exc.app_iter)[0]
            if exc.empty_body:
                self.assertEqual(result, '')
            else:
                self.assertTrue(exc.status in result)
            L.append(result)
        self.assertEqual(len(L), len(status_map))
            
    def test_it_plain(self):
        self._doit('text/plain')

    def test_it_html(self):
        self._doit('text/html')

class Test_HTTPMove(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.exceptions import _HTTPMove
        return _HTTPMove(*arg, **kw)

    def test_it_location_not_passed(self):
        exc = self._makeOne()
        self.assertEqual(exc.location, '')

    def test_it_location_passed(self):
        exc = self._makeOne(location='foo')
        self.assertEqual(exc.location, 'foo')

class TestHTTPForbidden(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.exceptions import HTTPForbidden
        return HTTPForbidden(*arg, **kw)

    def test_it_result_not_passed(self):
        exc = self._makeOne()
        self.assertEqual(exc.result, None)

    def test_it_result_passed(self):
        exc = self._makeOne(result='foo')
        self.assertEqual(exc.result, 'foo')
        
class DummyRequest(object):
    exception = None

