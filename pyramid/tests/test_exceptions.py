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

class Test_no_escape(unittest.TestCase):
    def _callFUT(self, val):
        from pyramid.exceptions import no_escape
        return no_escape(val)

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

class DummyRequest(object):
    exception = None

# from webob.request import Request
# from webob.exc import HTTPException 
# from webob.exc import WSGIHTTPException
# from webob.exc import HTTPMethodNotAllowed
# from webob.exc import _HTTPMove
# from webob.exc import HTTPExceptionMiddleware

# from nose.tools import eq_, ok_, assert_equal, assert_raises

# def test_HTTPException(self):
#     _called = []
#     _result = object()
#     def _response(environ, start_response):
#         _called.append((environ, start_response))
#         return _result
#     environ = {}
#     start_response = object()
#     exc = HTTPException('testing', _response)
#     ok_(exc.wsgi_response is _response)
#     ok_(exc.exception is exc)
#     result = exc(environ, start_response)
#     ok_(result is result)
#     assert_equal(_called, [(environ, start_response)])

# from webob.dec import wsgify
# @wsgify
# def method_not_allowed_app(req):
#     if req.method != 'GET':
#         raise HTTPMethodNotAllowed().exception
#     return 'hello!'


# def test_exception_with_unicode_data():
#     req = Request.blank('/', method=u'POST')
#     res = req.get_response(method_not_allowed_app)
#     assert res.status_int == 405

# def test_WSGIHTTPException_headers():
#     exc = WSGIHTTPException(headers=[('Set-Cookie', 'a=1'),
#                                      ('Set-Cookie', 'a=2')])
#     mixed = exc.headers.mixed()
#     assert mixed['set-cookie'] ==  ['a=1', 'a=2']

# def test_WSGIHTTPException_w_body_template():
#     from string import Template
#     TEMPLATE = '$foo: $bar'
#     exc = WSGIHTTPException(body_template = TEMPLATE)
#     assert_equal(exc.body_template, TEMPLATE)
#     ok_(isinstance(exc.body_template_obj, Template))
#     eq_(exc.body_template_obj.substitute({'foo': 'FOO', 'bar': 'BAR'}),
#         'FOO: BAR')

# def test_WSGIHTTPException_w_empty_body():
#     class EmptyOnly(WSGIHTTPException):
#         empty_body = True
#     exc = EmptyOnly(content_type='text/plain', content_length=234)
#     ok_('content_type' not in exc.__dict__)
#     ok_('content_length' not in exc.__dict__)

# def test_WSGIHTTPException___str__():
#     exc1 = WSGIHTTPException(detail='Detail')
#     eq_(str(exc1), 'Detail')
#     class Explain(WSGIHTTPException):
#         explanation = 'Explanation'
#     eq_(str(Explain()), 'Explanation')

# def test_WSGIHTTPException_plain_body_no_comment():
#     class Explain(WSGIHTTPException):
#         code = '999'
#         title = 'Testing'
#         explanation = 'Explanation'
#     exc = Explain(detail='Detail')
#     eq_(exc.plain_body({}),
#         '999 Testing\n\nExplanation\n\n Detail  ')

# def test_WSGIHTTPException_html_body_w_comment():
#     class Explain(WSGIHTTPException):
#         code = '999'
#         title = 'Testing'
#         explanation = 'Explanation'
#     exc = Explain(detail='Detail', comment='Comment')
#     eq_(exc.html_body({}),
#         '<html>\n'
#         ' <head>\n'
#         '  <title>999 Testing</title>\n'
#         ' </head>\n'
#         ' <body>\n'
#         '  <h1>999 Testing</h1>\n'
#         '  Explanation<br /><br />\n'
#         'Detail\n'
#         '<!-- Comment -->\n\n'
#         ' </body>\n'
#         '</html>'
#        )

# def test_WSGIHTTPException_generate_response():
#     def start_response(status, headers, exc_info=None):
#         pass
#     environ = {
#        'wsgi.url_scheme': 'HTTP',
#        'SERVER_NAME': 'localhost',
#        'SERVER_PORT': '80',
#        'REQUEST_METHOD': 'PUT',
#        'HTTP_ACCEPT': 'text/html'
#     }
#     excep = WSGIHTTPException()
#     assert_equal( excep(environ,start_response), [
#     '<html>\n'
#     ' <head>\n'
#     '  <title>None None</title>\n'
#     ' </head>\n'
#     ' <body>\n'
#     '  <h1>None None</h1>\n'
#     '  <br /><br />\n'
#     '\n'
#     '\n\n'
#     ' </body>\n'
#     '</html>' ]
#     )

# def test_WSGIHTTPException_call_w_body():
#     def start_response(status, headers, exc_info=None):
#         pass
#     environ = {
#        'wsgi.url_scheme': 'HTTP',
#        'SERVER_NAME': 'localhost',
#        'SERVER_PORT': '80',
#        'REQUEST_METHOD': 'PUT'
#     }
#     excep = WSGIHTTPException()
#     excep.body = 'test'
#     assert_equal( excep(environ,start_response), ['test'] )


# def test_WSGIHTTPException_wsgi_response():
#     def start_response(status, headers, exc_info=None):
#         pass
#     environ = {
#        'wsgi.url_scheme': 'HTTP',
#        'SERVER_NAME': 'localhost',
#        'SERVER_PORT': '80',
#        'REQUEST_METHOD': 'HEAD'
#     }
#     excep = WSGIHTTPException()
#     assert_equal( excep.wsgi_response(environ,start_response), [] )

# def test_WSGIHTTPException_exception_newstyle():
#     def start_response(status, headers, exc_info=None):
#         pass
#     environ = {
#        'wsgi.url_scheme': 'HTTP',
#        'SERVER_NAME': 'localhost',
#        'SERVER_PORT': '80',
#        'REQUEST_METHOD': 'HEAD'
#     }
#     excep = WSGIHTTPException()
#     exc.newstyle_exceptions = True
#     assert_equal( excep.exception(environ,start_response), [] )

# def test_WSGIHTTPException_exception_no_newstyle():
#     def start_response(status, headers, exc_info=None):
#         pass
#     environ = {
#        'wsgi.url_scheme': 'HTTP',
#        'SERVER_NAME': 'localhost',
#        'SERVER_PORT': '80',
#        'REQUEST_METHOD': 'HEAD'
#     }
#     excep = WSGIHTTPException()
#     exc.newstyle_exceptions = False
#     assert_equal( excep.exception(environ,start_response), [] )

# def test_HTTPMove():
#     def start_response(status, headers, exc_info=None):
#         pass
#     environ = {
#        'wsgi.url_scheme': 'HTTP',
#        'SERVER_NAME': 'localhost',
#        'SERVER_PORT': '80',
#        'REQUEST_METHOD': 'HEAD'
#     }
#     m = _HTTPMove()
#     assert_equal( m( environ, start_response ), [] )

# def test_HTTPMove_location_not_none():
#     def start_response(status, headers, exc_info=None):
#         pass
#     environ = {
#        'wsgi.url_scheme': 'HTTP',
#        'SERVER_NAME': 'localhost',
#        'SERVER_PORT': '80',
#        'REQUEST_METHOD': 'HEAD'
#     }
#     m = _HTTPMove(location='http://example.com')
#     assert_equal( m( environ, start_response ), [] )

# def test_HTTPMove_add_slash_and_location():
#     def start_response(status, headers, exc_info=None):
#         pass
#     environ = {
#        'wsgi.url_scheme': 'HTTP',
#        'SERVER_NAME': 'localhost',
#        'SERVER_PORT': '80',
#        'REQUEST_METHOD': 'HEAD'
#     }
#     assert_raises( TypeError, _HTTPMove, location='http://example.com', add_slash=True )

# def test_HTTPMove_call_add_slash():
#     def start_response(status, headers, exc_info=None):
#         pass
#     environ = {
#        'wsgi.url_scheme': 'HTTP',
#        'SERVER_NAME': 'localhost',
#        'SERVER_PORT': '80',
#        'REQUEST_METHOD': 'HEAD'
#     }
#     m = _HTTPMove()
#     m.add_slash = True
#     assert_equal( m( environ, start_response ), [] )

# def test_HTTPMove_call_query_string():
#     def start_response(status, headers, exc_info=None):
#         pass
#     environ = {
#        'wsgi.url_scheme': 'HTTP',
#        'SERVER_NAME': 'localhost',
#        'SERVER_PORT': '80',
#        'REQUEST_METHOD': 'HEAD'
#     }
#     m = _HTTPMove()
#     m.add_slash = True
#     environ[ 'QUERY_STRING' ] = 'querystring'
#     assert_equal( m( environ, start_response ), [] )

# def test_HTTPExceptionMiddleware_ok():
#     def app( environ, start_response ):
#         return '123'
#     application = app
#     m = HTTPExceptionMiddleware(application)
#     environ = {}
#     start_response = None
#     res = m( environ, start_response )
#     assert_equal( res, '123' )
    
# def test_HTTPExceptionMiddleware_exception():
#     def wsgi_response( environ, start_response):
#         return '123'
#     def app( environ, start_response ):
#         raise HTTPException( None, wsgi_response )
#     application = app
#     m = HTTPExceptionMiddleware(application)
#     environ = {}
#     start_response = None
#     res = m( environ, start_response )
#     assert_equal( res, '123' )

# def test_HTTPExceptionMiddleware_exception_exc_info_none():
#     class DummySys:
#         def exc_info(self):
#             return None
#     def wsgi_response( environ, start_response):
#         return start_response('200 OK', [], exc_info=None)
#     def app( environ, start_response ):
#         raise HTTPException( None, wsgi_response )
#     application = app
#     m = HTTPExceptionMiddleware(application)
#     environ = {}
#     def start_response(status, headers, exc_info):
#         pass
#     try:
#         from webob import exc
#         old_sys = exc.sys
#         sys = DummySys()
#         res = m( environ, start_response )
#         assert_equal( res, None )
#     finally:
#         exc.sys = old_sys
