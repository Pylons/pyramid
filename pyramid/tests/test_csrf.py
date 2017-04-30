import unittest

from pyramid import testing
from pyramid.config import Configurator


class TestLegacySessionCSRFStoragePolicy(unittest.TestCase):
    class MockSession(object):
        def __init__(self, current_token='02821185e4c94269bdc38e6eeae0a2f8'):
            self.current_token = current_token

        def new_csrf_token(self):
            self.current_token = 'e5e9e30a08b34ff9842ff7d2b958c14b'
            return self.current_token

        def get_csrf_token(self):
            return self.current_token

    def _makeOne(self):
        from pyramid.csrf import LegacySessionCSRFStoragePolicy
        return LegacySessionCSRFStoragePolicy()

    def test_register_session_csrf_policy(self):
        from pyramid.csrf import LegacySessionCSRFStoragePolicy
        from pyramid.interfaces import ICSRFStoragePolicy

        config = Configurator()
        config.set_csrf_storage_policy(self._makeOne())
        config.commit()

        policy = config.registry.queryUtility(ICSRFStoragePolicy)

        self.assertTrue(isinstance(policy, LegacySessionCSRFStoragePolicy))

    def test_session_csrf_implementation_delegates_to_session(self):
        policy = self._makeOne()
        request = DummyRequest(session=self.MockSession())

        self.assertEqual(
            policy.get_csrf_token(request),
            '02821185e4c94269bdc38e6eeae0a2f8'
        )
        self.assertEqual(
            policy.new_csrf_token(request),
            'e5e9e30a08b34ff9842ff7d2b958c14b'
        )

    def test_check_csrf_token(self):
        request = DummyRequest(session=self.MockSession('foo'))

        policy = self._makeOne()
        self.assertTrue(policy.check_csrf_token(request, 'foo'))
        self.assertFalse(policy.check_csrf_token(request, 'bar'))


class TestSessionCSRFStoragePolicy(unittest.TestCase):
    def _makeOne(self, **kw):
        from pyramid.csrf import SessionCSRFStoragePolicy
        return SessionCSRFStoragePolicy(**kw)

    def test_register_session_csrf_policy(self):
        from pyramid.csrf import SessionCSRFStoragePolicy
        from pyramid.interfaces import ICSRFStoragePolicy

        config = Configurator()
        config.set_csrf_storage_policy(self._makeOne())
        config.commit()

        policy = config.registry.queryUtility(ICSRFStoragePolicy)

        self.assertTrue(isinstance(policy, SessionCSRFStoragePolicy))

    def test_it_creates_a_new_token(self):
        request = DummyRequest(session={})

        policy = self._makeOne()
        policy._token_factory = lambda: 'foo'
        self.assertEqual(policy.get_csrf_token(request), 'foo')

    def test_get_csrf_token_returns_the_new_token(self):
        request = DummyRequest(session={'_csrft_': 'foo'})

        policy = self._makeOne()
        self.assertEqual(policy.get_csrf_token(request), 'foo')

        token = policy.new_csrf_token(request)
        self.assertNotEqual(token, 'foo')
        self.assertEqual(token, policy.get_csrf_token(request))

    def test_check_csrf_token(self):
        request = DummyRequest(session={})

        policy = self._makeOne()
        self.assertFalse(policy.check_csrf_token(request, 'foo'))

        request.session = {'_csrft_': 'foo'}
        self.assertTrue(policy.check_csrf_token(request, 'foo'))
        self.assertFalse(policy.check_csrf_token(request, 'bar'))


class TestCookieCSRFStoragePolicy(unittest.TestCase):
    def _makeOne(self, **kw):
        from pyramid.csrf import CookieCSRFStoragePolicy
        return CookieCSRFStoragePolicy(**kw)

    def test_register_cookie_csrf_policy(self):
        from pyramid.csrf import CookieCSRFStoragePolicy
        from pyramid.interfaces import ICSRFStoragePolicy

        config = Configurator()
        config.set_csrf_storage_policy(self._makeOne())
        config.commit()

        policy = config.registry.queryUtility(ICSRFStoragePolicy)

        self.assertTrue(isinstance(policy, CookieCSRFStoragePolicy))

    def test_get_cookie_csrf_with_no_existing_cookie_sets_cookies(self):
        response = MockResponse()
        request = DummyRequest()

        policy = self._makeOne()
        token = policy.get_csrf_token(request)
        request.response_callback(request, response)
        self.assertEqual(
            response.headerlist,
            [('Set-Cookie', 'csrf_token={}; Path=/'.format(token))]
        )

    def test_existing_cookie_csrf_does_not_set_cookie(self):
        request = DummyRequest()
        request.cookies = {'csrf_token': 'e6f325fee5974f3da4315a8ccf4513d2'}

        policy = self._makeOne()
        token = policy.get_csrf_token(request)

        self.assertEqual(
            token,
            'e6f325fee5974f3da4315a8ccf4513d2'
        )
        self.assertIsNone(request.response_callback)

    def test_new_cookie_csrf_with_existing_cookie_sets_cookies(self):
        request = DummyRequest()
        request.cookies = {'csrf_token': 'e6f325fee5974f3da4315a8ccf4513d2'}

        policy = self._makeOne()
        token = policy.new_csrf_token(request)

        response = MockResponse()
        request.response_callback(request, response)
        self.assertEqual(
            response.headerlist,
            [('Set-Cookie', 'csrf_token={}; Path=/'.format(token))]
        )

    def test_get_csrf_token_returns_the_new_token(self):
        request = DummyRequest()
        request.cookies = {'csrf_token': 'foo'}

        policy = self._makeOne()
        self.assertEqual(policy.get_csrf_token(request), 'foo')

        token = policy.new_csrf_token(request)
        self.assertNotEqual(token, 'foo')
        self.assertEqual(token, policy.get_csrf_token(request))

    def test_check_csrf_token(self):
        request = DummyRequest()

        policy = self._makeOne()
        self.assertFalse(policy.check_csrf_token(request, 'foo'))

        request.cookies = {'csrf_token': 'foo'}
        self.assertTrue(policy.check_csrf_token(request, 'foo'))
        self.assertFalse(policy.check_csrf_token(request, 'bar'))

class Test_get_csrf_token(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def _callFUT(self, *args, **kwargs):
        from pyramid.csrf import get_csrf_token
        return get_csrf_token(*args, **kwargs)

    def test_no_override_csrf_utility_registered(self):
        request = testing.DummyRequest()
        self._callFUT(request)

    def test_success(self):
        self.config.set_csrf_storage_policy(DummyCSRF())
        request = testing.DummyRequest()

        csrf_token = self._callFUT(request)

        self.assertEquals(csrf_token, '02821185e4c94269bdc38e6eeae0a2f8')


class Test_new_csrf_token(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def _callFUT(self, *args, **kwargs):
        from pyramid.csrf import new_csrf_token
        return new_csrf_token(*args, **kwargs)

    def test_no_override_csrf_utility_registered(self):
        request = testing.DummyRequest()
        self._callFUT(request)

    def test_success(self):
        self.config.set_csrf_storage_policy(DummyCSRF())
        request = testing.DummyRequest()

        csrf_token = self._callFUT(request)

        self.assertEquals(csrf_token, 'e5e9e30a08b34ff9842ff7d2b958c14b')


class Test_check_csrf_token(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

        # set up CSRF
        self.config.set_default_csrf_options(require_csrf=False)

    def _callFUT(self, *args, **kwargs):
        from ..csrf import check_csrf_token
        return check_csrf_token(*args, **kwargs)

    def test_success_token(self):
        request = testing.DummyRequest()
        request.method = "POST"
        request.POST = {'csrf_token': request.session.get_csrf_token()}
        self.assertEqual(self._callFUT(request, token='csrf_token'), True)

    def test_success_header(self):
        request = testing.DummyRequest()
        request.headers['X-CSRF-Token'] = request.session.get_csrf_token()
        self.assertEqual(self._callFUT(request, header='X-CSRF-Token'), True)

    def test_success_default_token(self):
        request = testing.DummyRequest()
        request.method = "POST"
        request.POST = {'csrf_token': request.session.get_csrf_token()}
        self.assertEqual(self._callFUT(request), True)

    def test_success_default_header(self):
        request = testing.DummyRequest()
        request.headers['X-CSRF-Token'] = request.session.get_csrf_token()
        self.assertEqual(self._callFUT(request), True)

    def test_failure_raises(self):
        from pyramid.exceptions import BadCSRFToken
        request = testing.DummyRequest()
        self.assertRaises(BadCSRFToken, self._callFUT, request,
                          'csrf_token')

    def test_failure_no_raises(self):
        request = testing.DummyRequest()
        result = self._callFUT(request, 'csrf_token', raises=False)
        self.assertEqual(result, False)


class Test_check_csrf_token_without_defaults_configured(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def _callFUT(self, *args, **kwargs):
        from ..csrf import check_csrf_token
        return check_csrf_token(*args, **kwargs)

    def test_success_token(self):
        request = testing.DummyRequest()
        request.method = "POST"
        request.POST = {'csrf_token': request.session.get_csrf_token()}
        self.assertEqual(self._callFUT(request, token='csrf_token'), True)

    def test_failure_raises(self):
        from pyramid.exceptions import BadCSRFToken
        request = testing.DummyRequest()
        self.assertRaises(BadCSRFToken, self._callFUT, request,
                          'csrf_token')

    def test_failure_no_raises(self):
        request = testing.DummyRequest()
        result = self._callFUT(request, 'csrf_token', raises=False)
        self.assertEqual(result, False)


class Test_check_csrf_origin(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ..csrf import check_csrf_origin
        return check_csrf_origin(*args, **kwargs)

    def test_success_with_http(self):
        request = testing.DummyRequest()
        request.scheme = "http"
        self.assertTrue(self._callFUT(request))

    def test_success_with_https_and_referrer(self):
        request = testing.DummyRequest()
        request.scheme = "https"
        request.host = "example.com"
        request.host_port = "443"
        request.referrer = "https://example.com/login/"
        request.registry.settings = {}
        self.assertTrue(self._callFUT(request))

    def test_success_with_https_and_origin(self):
        request = testing.DummyRequest()
        request.scheme = "https"
        request.host = "example.com"
        request.host_port = "443"
        request.headers = {"Origin": "https://example.com/"}
        request.referrer = "https://not-example.com/"
        request.registry.settings = {}
        self.assertTrue(self._callFUT(request))

    def test_success_with_additional_trusted_host(self):
        request = testing.DummyRequest()
        request.scheme = "https"
        request.host = "example.com"
        request.host_port = "443"
        request.referrer = "https://not-example.com/login/"
        request.registry.settings = {
            "pyramid.csrf_trusted_origins": ["not-example.com"],
        }
        self.assertTrue(self._callFUT(request))

    def test_success_with_nonstandard_port(self):
        request = testing.DummyRequest()
        request.scheme = "https"
        request.host = "example.com:8080"
        request.host_port = "8080"
        request.referrer = "https://example.com:8080/login/"
        request.registry.settings = {}
        self.assertTrue(self._callFUT(request))

    def test_fails_with_wrong_host(self):
        from pyramid.exceptions import BadCSRFOrigin
        request = testing.DummyRequest()
        request.scheme = "https"
        request.host = "example.com"
        request.host_port = "443"
        request.referrer = "https://not-example.com/login/"
        request.registry.settings = {}
        self.assertRaises(BadCSRFOrigin, self._callFUT, request)
        self.assertFalse(self._callFUT(request, raises=False))

    def test_fails_with_no_origin(self):
        from pyramid.exceptions import BadCSRFOrigin
        request = testing.DummyRequest()
        request.scheme = "https"
        request.referrer = None
        self.assertRaises(BadCSRFOrigin, self._callFUT, request)
        self.assertFalse(self._callFUT(request, raises=False))

    def test_fails_when_http_to_https(self):
        from pyramid.exceptions import BadCSRFOrigin
        request = testing.DummyRequest()
        request.scheme = "https"
        request.host = "example.com"
        request.host_port = "443"
        request.referrer = "http://example.com/evil/"
        request.registry.settings = {}
        self.assertRaises(BadCSRFOrigin, self._callFUT, request)
        self.assertFalse(self._callFUT(request, raises=False))

    def test_fails_with_nonstandard_port(self):
        from pyramid.exceptions import BadCSRFOrigin
        request = testing.DummyRequest()
        request.scheme = "https"
        request.host = "example.com:8080"
        request.host_port = "8080"
        request.referrer = "https://example.com/login/"
        request.registry.settings = {}
        self.assertRaises(BadCSRFOrigin, self._callFUT, request)
        self.assertFalse(self._callFUT(request, raises=False))


class DummyRequest(object):
    registry = None
    session = None
    response_callback = None

    def __init__(self, registry=None, session=None):
        self.registry = registry
        self.session = session
        self.cookies = {}

    def add_response_callback(self, callback):
        self.response_callback = callback


class MockResponse(object):
    def __init__(self):
        self.headerlist = []


class DummyCSRF(object):
    def new_csrf_token(self, request):
        return 'e5e9e30a08b34ff9842ff7d2b958c14b'

    def get_csrf_token(self, request):
        return '02821185e4c94269bdc38e6eeae0a2f8'
