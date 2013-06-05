import unittest
from pyramid import testing

class TestUnencryptedCookieSession(unittest.TestCase):
    def _makeOne(self, request, **kw):
        from pyramid.session import UnencryptedCookieSessionFactoryConfig
        return UnencryptedCookieSessionFactoryConfig('secret', **kw)(request)

    def test_ctor_no_cookie(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        self.assertEqual(dict(session), {})

    def test_instance_conforms(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import ISession
        request = testing.DummyRequest()
        session = self._makeOne(request)
        verifyObject(ISession, session)

    def _serialize(self, accessed, state, secret='secret'):
        from pyramid.session import signed_serialize
        return signed_serialize((accessed, accessed, state), secret)
        
    def test_ctor_with_cookie_still_valid(self):
        import time
        request = testing.DummyRequest()
        cookieval = self._serialize(time.time(), {'state':1})
        request.cookies['session'] = cookieval
        session = self._makeOne(request)
        self.assertEqual(dict(session), {'state':1})
        
    def test_ctor_with_cookie_expired(self):
        request = testing.DummyRequest()
        cookieval = self._serialize(0, {'state':1})
        request.cookies['session'] = cookieval
        session = self._makeOne(request)
        self.assertEqual(dict(session), {})

    def test_ctor_with_bad_cookie(self):
        request = testing.DummyRequest()
        cookieval = 'abc'
        request.cookies['session'] = cookieval
        session = self._makeOne(request)
        self.assertEqual(dict(session), {})

    def test_changed(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        self.assertEqual(session.changed(), None)

    def test_invalidate(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        session['a'] = 1
        self.assertEqual(session.invalidate(), None)
        self.assertFalse('a' in session)

    def test__set_cookie_on_exception(self):
        request = testing.DummyRequest()
        request.exception = True
        session = self._makeOne(request)
        session._cookie_on_exception = False
        response = DummyResponse()
        self.assertEqual(session._set_cookie(response), False)

    def test__set_cookie_on_exception_no_request_exception(self):
        import webob
        request = testing.DummyRequest()
        request.exception = None
        session = self._makeOne(request)
        session._cookie_on_exception = False
        response = webob.Response()
        self.assertEqual(session._set_cookie(response), True)
        self.assertEqual(response.headerlist[-1][0], 'Set-Cookie')

    def test__set_cookie_cookieval_too_long(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        session['abc'] = 'x'*100000
        response = DummyResponse()
        self.assertRaises(ValueError, session._set_cookie, response)

    def test__set_cookie_real_webob_response(self):
        import webob
        request = testing.DummyRequest()
        session = self._makeOne(request)
        session['abc'] = 'x'
        response = webob.Response()
        self.assertEqual(session._set_cookie(response), True)
        self.assertEqual(response.headerlist[-1][0], 'Set-Cookie')

    def test__set_cookie_options(self):
        from pyramid.response import Response
        request = testing.DummyRequest()
        request.exception = None
        session = self._makeOne(request,
                                cookie_name = 'abc',
                                cookie_path = '/foo',
                                cookie_domain = 'localhost',
                                cookie_secure = True,
                                cookie_httponly = True,
                                )
        session['abc'] = 'x'
        response = Response()
        self.assertEqual(session._set_cookie(response), True)
        cookieval= response.headerlist[-1][1]
        val, domain, path, secure, httponly = [x.strip() for x in
                                               cookieval.split(';')]
        self.assertTrue(val.startswith('abc='))
        self.assertEqual(domain, 'Domain=localhost')
        self.assertEqual(path, 'Path=/foo')
        self.assertEqual(secure, 'secure')
        self.assertEqual(httponly, 'HttpOnly')

    def test_flash_default(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        session.flash('msg1')
        session.flash('msg2')
        self.assertEqual(session['_f_'], ['msg1', 'msg2'])

    def test_flash_allow_duplicate_false(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        session.flash('msg1')
        session.flash('msg1', allow_duplicate=False)
        self.assertEqual(session['_f_'], ['msg1'])

    def test_flash_allow_duplicate_true_and_msg_not_in_storage(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        session.flash('msg1', allow_duplicate=True)
        self.assertEqual(session['_f_'], ['msg1'])

    def test_flash_allow_duplicate_false_and_msg_not_in_storage(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        session.flash('msg1', allow_duplicate=False)
        self.assertEqual(session['_f_'], ['msg1'])

    def test_flash_mixed(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        session.flash('warn1', 'warn')
        session.flash('warn2', 'warn')
        session.flash('err1', 'error')
        session.flash('err2', 'error')
        self.assertEqual(session['_f_warn'], ['warn1', 'warn2'])

    def test_pop_flash_default_queue(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        queue = ['one', 'two']
        session['_f_'] = queue
        result = session.pop_flash()
        self.assertEqual(result, queue)
        self.assertEqual(session.get('_f_'), None)

    def test_pop_flash_nodefault_queue(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        queue = ['one', 'two']
        session['_f_error'] = queue
        result = session.pop_flash('error')
        self.assertEqual(result, queue)
        self.assertEqual(session.get('_f_error'), None)

    def test_peek_flash_default_queue(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        queue = ['one', 'two']
        session['_f_'] = queue
        result = session.peek_flash()
        self.assertEqual(result, queue)
        self.assertEqual(session.get('_f_'), queue)

    def test_peek_flash_nodefault_queue(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        queue = ['one', 'two']
        session['_f_error'] = queue
        result = session.peek_flash('error')
        self.assertEqual(result, queue)
        self.assertEqual(session.get('_f_error'), queue)

    def test_new_csrf_token(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        token = session.new_csrf_token()
        self.assertEqual(token, session['_csrft_'])

    def test_get_csrf_token(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        session['_csrft_'] = 'token'
        token = session.get_csrf_token()
        self.assertEqual(token, 'token')
        self.assertTrue('_csrft_' in session)

    def test_get_csrf_token_new(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        token = session.get_csrf_token()
        self.assertTrue(token)
        self.assertTrue('_csrft_' in session)

    def test_serialize_option(self):
        from pyramid.response import Response
        secret = 'secret'
        request = testing.DummyRequest()
        session = self._makeOne(request,
            signed_serialize=dummy_signed_serialize)
        session['key'] = 'value'
        response = Response()
        self.assertEqual(session._set_cookie(response), True)
        cookie = response.headerlist[-1][1]
        expected_cookieval = dummy_signed_serialize(
            (session.accessed, session.created, {'key': 'value'}), secret)
        response = Response()
        response.set_cookie('session', expected_cookieval)
        expected_cookie = response.headerlist[-1][1]
        self.assertEqual(cookie, expected_cookie)

    def test_deserialize_option(self):
        import time
        secret = 'secret'
        request = testing.DummyRequest()
        accessed = time.time()
        state = {'key': 'value'}
        cookieval = dummy_signed_serialize((accessed, accessed, state), secret)
        request.cookies['session'] = cookieval
        session = self._makeOne(request,
            signed_deserialize=dummy_signed_deserialize)
        self.assertEqual(dict(session), state)

def dummy_signed_serialize(data, secret):
    import base64
    from pyramid.compat import pickle, bytes_
    pickled = pickle.dumps(data)
    return base64.b64encode(bytes_(secret)) + base64.b64encode(pickled)

def dummy_signed_deserialize(serialized, secret):
    import base64
    from pyramid.compat import pickle, bytes_
    serialized_data = base64.b64decode(
        serialized[len(base64.b64encode(bytes_(secret))):])
    return pickle.loads(serialized_data)

class Test_manage_accessed(unittest.TestCase):
    def _makeOne(self, wrapped):
        from pyramid.session import manage_accessed
        return manage_accessed(wrapped)

    def test_accessed_set(self):
        request = testing.DummyRequest()
        session = DummySessionFactory(request)
        session.accessed = None
        wrapper = self._makeOne(session.__class__.get)
        wrapper(session, 'a')
        self.assertNotEqual(session.accessed, None)
        
    def test_already_dirty(self):
        request = testing.DummyRequest()
        session = DummySessionFactory(request)
        session._dirty = True
        session['a'] = 1
        wrapper = self._makeOne(session.__class__.get)
        self.assertEqual(wrapper.__doc__, session.get.__doc__)
        result = wrapper(session, 'a')
        self.assertEqual(result, 1)
        callbacks = request.response_callbacks
        self.assertEqual(len(callbacks), 0)

    def test_with_exception(self):
        import webob
        request = testing.DummyRequest()
        request.exception = True
        session = DummySessionFactory(request)
        session['a'] = 1
        wrapper = self._makeOne(session.__class__.get)
        self.assertEqual(wrapper.__doc__, session.get.__doc__)
        result = wrapper(session, 'a')
        self.assertEqual(result, 1)
        callbacks = request.response_callbacks
        self.assertEqual(len(callbacks), 1)
        response = webob.Response()
        result = callbacks[0](request, response)
        self.assertEqual(result, None)
        self.assertFalse('Set-Cookie' in dict(response.headerlist))

    def test_cookie_is_set(self):
        request = testing.DummyRequest()
        session = DummySessionFactory(request)
        session['a'] = 1
        wrapper = self._makeOne(session.__class__.get)
        self.assertEqual(wrapper.__doc__, session.get.__doc__)
        result = wrapper(session, 'a')
        self.assertEqual(result, 1)
        callbacks = request.response_callbacks
        self.assertEqual(len(callbacks), 1)
        response = DummyResponse()
        result = callbacks[0](request, response)
        self.assertEqual(result, None)
        self.assertEqual(session.response, response)

def serialize(data, secret):
    import hmac
    import base64
    from hashlib import sha1
    from pyramid.compat import bytes_
    from pyramid.compat import native_
    from pyramid.compat import pickle
    pickled = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
    sig = hmac.new(bytes_(secret), pickled, sha1).hexdigest()
    return sig + native_(base64.b64encode(pickled))

class Test_signed_serialize(unittest.TestCase):
    def _callFUT(self, data, secret):
        from pyramid.session import signed_serialize
        return signed_serialize(data, secret)

    def test_it(self):
        expected = serialize('123', 'secret')
        result = self._callFUT('123', 'secret')
        self.assertEqual(result, expected)
        
class Test_signed_deserialize(unittest.TestCase):
    def _callFUT(self, serialized, secret, hmac=None):
        if hmac is None:
            import hmac
        from pyramid.session import signed_deserialize
        return signed_deserialize(serialized, secret, hmac=hmac)

    def test_it(self):
        serialized = serialize('123', 'secret')
        result = self._callFUT(serialized, 'secret')
        self.assertEqual(result, '123')

    def test_invalid_bits(self):
        serialized = serialize('123', 'secret')
        self.assertRaises(ValueError, self._callFUT, serialized, 'seekrit')

    def test_invalid_len(self):
        class hmac(object):
            def new(self, *arg):
                return self
            def hexdigest(self):
                return '1234'
        serialized = serialize('123', 'secret123')
        self.assertRaises(ValueError, self._callFUT, serialized, 'secret',
                          hmac=hmac())
        
    def test_it_bad_encoding(self):
        serialized = 'bad' + serialize('123', 'secret')
        self.assertRaises(ValueError, self._callFUT, serialized, 'secret')
        
class Test_check_csrf_token(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ..session import check_csrf_token
        return check_csrf_token(*args, **kwargs)

    def test_success_token(self):
        request = testing.DummyRequest()
        request.params['csrf_token'] = request.session.get_csrf_token()
        self.assertEqual(self._callFUT(request, token='csrf_token'), True)

    def test_success_header(self):
        request = testing.DummyRequest()
        request.headers['X-CSRF-Token'] = request.session.get_csrf_token()
        self.assertEqual(self._callFUT(request, header='X-CSRF-Token'), True)

    def test_success_default_token(self):
        request = testing.DummyRequest()
        request.params['csrf_token'] = request.session.get_csrf_token()
        self.assertEqual(self._callFUT(request), True)

    def test_success_default_header(self):
        request = testing.DummyRequest()
        request.headers['X-CSRF-Token'] = request.session.get_csrf_token()
        self.assertEqual(self._callFUT(request), True)

    def test_failure_raises(self):
        from pyramid.httpexceptions import HTTPBadRequest
        request = testing.DummyRequest()
        self.assertRaises(HTTPBadRequest, self._callFUT, request, 'csrf_token')

    def test_failure_no_raises(self):
        request = testing.DummyRequest()
        result = self._callFUT(request, 'csrf_token', raises=False)
        self.assertEqual(result, False)

class DummySessionFactory(dict):
    _dirty = False
    _cookie_name = 'session'
    _cookie_max_age = None
    _cookie_path = '/'
    _cookie_domain = None
    _cookie_secure = False
    _cookie_httponly = False
    _timeout = 1200
    _secret = 'secret'
    def __init__(self, request):
        self.request = request
        dict.__init__(self, {})

    def _set_cookie(self, response):
        self.response = response

class DummyResponse(object):
    def __init__(self):
        self.headerlist = []
