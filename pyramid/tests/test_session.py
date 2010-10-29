import unittest
from pyramid import testing

class TestInsecureCookieSession(unittest.TestCase):
    def _makeOne(self, request, **kw):
        from pyramid.session import InsecureCookieSessionFactoryConfig
        return InsecureCookieSessionFactoryConfig('secret', **kw)(request)

    def test_ctor_no_cookie(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        self.assertEqual(dict(session), {})

    def _serialize(self, accessed, state, secret='secret'):
        from pyramid.session import serialize
        return serialize((accessed, accessed, state), secret)
        
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

    def test_changed(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        self.assertEqual(session.changed(), None)

    def test_invalidate(self):
        request = testing.DummyRequest()
        session = self._makeOne(request)
        session['a'] = 1
        self.assertEqual(session.invalidate(), None)
        self.failIf('a' in session)

    def test__set_cookie_on_exception(self):
        request = testing.DummyRequest()
        request.exception = True
        session = self._makeOne(request)
        session._cookie_on_exception = False
        response = DummyResponse()
        self.assertEqual(session._set_cookie(response), False)
        
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

    def test__set_cookie_other_kind_of_response(self):
        request = testing.DummyRequest()
        request.exception = None
        session = self._makeOne(request)
        session['abc'] = 'x'
        response = DummyResponse()
        self.assertEqual(session._set_cookie(response), True)
        self.assertEqual(len(response.headerlist), 1)

    def test__set_cookie_options(self):
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
        response = DummyResponse()
        self.assertEqual(session._set_cookie(response), True)
        self.assertEqual(len(response.headerlist), 1)
        cookieval= response.headerlist[0][1]
        val, domain, path, secure, httponly = [x.strip() for x in
                                               cookieval.split(';')]
        self.failUnless(val.startswith('abc='))
        self.assertEqual(domain, 'Domain=localhost')
        self.assertEqual(path, 'Path=/foo')
        self.assertEqual(secure, 'secure')
        self.assertEqual(httponly, 'HttpOnly')

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
        self.failIf('Set-Cookie' in dict(response.headerlist))

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
    try:
        from hashlib import sha1
    except ImportError: # pragma: no cover
        import sha as sha1

    try:
        import cPickle as pickle
    except ImportError: # pragma: no cover
        import pickle

    import hmac
    import base64
    pickled = pickle.dumps('123', pickle.HIGHEST_PROTOCOL)
    sig = hmac.new(secret, pickled, sha1).hexdigest()
    return sig + base64.standard_b64encode(pickled)

class Test_serialize(unittest.TestCase):
    def _callFUT(self, data, secret):
        from pyramid.session import serialize
        return serialize(data, secret)

    def test_it(self):
        expected = serialize('123', 'secret')
        result = self._callFUT('123', 'secret')
        self.assertEqual(result, expected)
        
class Test_deserialize(unittest.TestCase):
    def _callFUT(self, serialized, secret, hmac=None):
        if hmac is None:
            import hmac
        from pyramid.session import deserialize
        return deserialize(serialized, secret, hmac=hmac)

    def test_it(self):
        serialized = serialize('123', 'secret')
        result = self._callFUT(serialized, 'secret')
        self.assertEqual(result, '123')

    def test_invalid_bits(self):
        serialized = serialize('123', 'secret')
        result = self._callFUT(serialized, 'seekrit')
        self.assertEqual(result, None)

    def test_invalid_len(self):
        class hmac(object):
            def new(self, *arg):
                return self
            def hexdigest(self):
                return '1234'
        serialized = serialize('123', 'secret123')
        result = self._callFUT(serialized, 'secret', hmac=hmac())
        self.assertEqual(result, None)
        
    def test_it_bad_encoding(self):
        serialized = 'bad' + serialize('123', 'secret')
        result = self._callFUT(serialized, 'secret')
        self.assertEqual(result, None)
        

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
