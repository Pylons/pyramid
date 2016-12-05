import unittest

from zope.interface.interfaces import ComponentLookupError

from pyramid import testing
from pyramid.config import Configurator
from pyramid.events import BeforeRender


class Test_get_csrf_token(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def _callFUT(self, *args, **kwargs):
        from pyramid.csrf import get_csrf_token
        return get_csrf_token(*args, **kwargs)

    def test_no_csrf_utility_registered(self):
        request = testing.DummyRequest()

        with self.assertRaises(ComponentLookupError):
            self._callFUT(request)

    def test_success(self):
        self.config.set_default_csrf_options(implementation=DummyCSRF())
        request = testing.DummyRequest()

        csrf_token = self._callFUT(request)

        self.assertEquals(csrf_token, '02821185e4c94269bdc38e6eeae0a2f8')


class Test_new_csrf_token(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def _callFUT(self, *args, **kwargs):
        from pyramid.csrf import new_csrf_token
        return new_csrf_token(*args, **kwargs)

    def test_no_csrf_utility_registered(self):
        request = testing.DummyRequest()

        with self.assertRaises(ComponentLookupError):
            self._callFUT(request)

    def test_success(self):
        self.config.set_default_csrf_options(implementation=DummyCSRF())
        request = testing.DummyRequest()

        csrf_token = self._callFUT(request)

        self.assertEquals(csrf_token, 'e5e9e30a08b34ff9842ff7d2b958c14b')


class Test_csrf_token_template_global(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def _callFUT(self, *args, **kwargs):
        from pyramid.csrf import csrf_token_template_global
        return csrf_token_template_global(*args, **kwargs)

    def test_event_is_missing_request(self):
        event = BeforeRender({}, {})

        self._callFUT(event)

        self.assertNotIn('get_csrf_token', event)

    def test_request_is_missing_registry(self):
        request = DummyRequest(registry=None)
        del request.registry
        del request.__class__.registry
        event = BeforeRender({'request': request}, {})

        self._callFUT(event)

        self.assertNotIn('get_csrf_token', event)

    def test_csrf_utility_not_registered(self):
        request = testing.DummyRequest()
        event = BeforeRender({'request': request}, {})

        with self.assertRaises(ComponentLookupError):
            self._callFUT(event)

    def test_csrf_token_passed_to_template(self):
        config = Configurator()
        config.set_default_csrf_options(implementation=DummyCSRF())
        config.commit()

        request = testing.DummyRequest()
        request.registry = config.registry

        before = BeforeRender({'request': request}, {})
        config.registry.notify(before)

        self.assertIn('get_csrf_token', before)
        self.assertEqual(
            before['get_csrf_token'](),
            '02821185e4c94269bdc38e6eeae0a2f8'
        )


class TestSessionCSRF(unittest.TestCase):
    class MockSession(object):
        def new_csrf_token(self):
            return 'e5e9e30a08b34ff9842ff7d2b958c14b'

        def get_csrf_token(self):
            return '02821185e4c94269bdc38e6eeae0a2f8'

    def _makeOne(self):
        from pyramid.csrf import SessionCSRF
        return SessionCSRF()

    def test_register_session_csrf_policy(self):
        from pyramid.csrf import SessionCSRF
        from pyramid.interfaces import ICSRFPolicy

        config = Configurator()
        config.set_default_csrf_options(implementation=self._makeOne())
        config.commit()

        policy = config.registry.queryUtility(ICSRFPolicy)

        self.assertTrue(isinstance(policy, SessionCSRF))

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

    def test_verifying_token_invalid(self):
        policy = self._makeOne()
        request = DummyRequest(session=self.MockSession())

        result = policy.check_csrf_token(request, 'invalid-token')
        self.assertFalse(result)

    def test_verifying_token_valid(self):
        policy = self._makeOne()
        request = DummyRequest(session=self.MockSession())

        result = policy.check_csrf_token(
            request, '02821185e4c94269bdc38e6eeae0a2f8')
        self.assertTrue(result)


class TestCookieCSRF(unittest.TestCase):
    def _makeOne(self):
        from pyramid.csrf import CookieCSRF
        return CookieCSRF()

    def test_register_cookie_csrf_policy(self):
        from pyramid.csrf import CookieCSRF
        from pyramid.interfaces import ICSRFPolicy

        config = Configurator()
        config.set_default_csrf_options(implementation=self._makeOne())
        config.commit()

        policy = config.registry.queryUtility(ICSRFPolicy)

        self.assertTrue(isinstance(policy, CookieCSRF))

    def test_get_cookie_csrf_with_no_existing_cookie_sets_cookies(self):
        response = MockResponse()
        request = DummyRequest(response=response)

        policy = self._makeOne()
        token = policy.get_csrf_token(request)

        self.assertEqual(
            response.called_args,
            ('csrf_token', token),
        )
        self.assertEqual(
            response.called_kwargs,
            {
                'secure': False,
                'httponly': False,
                'domain': None,
                'path': '/',
                'overwrite': True
            }
        )

    def test_existing_cookie_csrf_does_not_set_cookie(self):
        response = MockResponse()
        request = DummyRequest(response=response)
        request.cookies = {'csrf_token': 'e6f325fee5974f3da4315a8ccf4513d2'}

        policy = self._makeOne()
        token = policy.get_csrf_token(request)

        self.assertEqual(
            token,
            'e6f325fee5974f3da4315a8ccf4513d2'
        )
        self.assertEqual(
            response.called_args,
            (),
        )
        self.assertEqual(
            response.called_kwargs,
            {}
        )

    def test_new_cookie_csrf_with_existing_cookie_sets_cookies(self):
        response = MockResponse()
        request = DummyRequest(response=response)
        request.cookies = {'csrf_token': 'e6f325fee5974f3da4315a8ccf4513d2'}

        policy = self._makeOne()
        token = policy.new_csrf_token(request)

        self.assertEqual(
            response.called_args,
            ('csrf_token', token),
        )
        self.assertEqual(
            response.called_kwargs,
            {
                'secure': False,
                'httponly': False,
                'domain': None,
                'path': '/',
                'overwrite': True
            }
        )

    def test_verifying_token_invalid_token(self):
        response = MockResponse()
        request = DummyRequest(response=response)
        request.cookies = {'csrf_token': 'e6f325fee5974f3da4315a8ccf4513d2'}

        policy = self._makeOne()
        self.assertFalse(
            policy.check_csrf_token(request, 'invalid-token')
        )

    def test_verifying_token_against_existing_cookie(self):
        response = MockResponse()
        request = DummyRequest(response=response)
        request.cookies = {'csrf_token': 'e6f325fee5974f3da4315a8ccf4513d2'}

        policy = self._makeOne()
        self.assertTrue(
            policy.check_csrf_token(request, 'e6f325fee5974f3da4315a8ccf4513d2')
        )


class Test_check_csrf_token(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

        # set up CSRF (this will also register SessionCSRF policy)
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

    def test_token_differing_types(self):
        from pyramid.compat import text_
        request = testing.DummyRequest()
        request.method = "POST"
        request.session['_csrft_'] = text_('foo')
        request.POST = {'csrf_token': b'foo'}
        self.assertEqual(self._callFUT(request, token='csrf_token'), True)


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
    cookies = {}

    def __init__(self, registry=None, session=None, response=None):
        self.registry = registry
        self.session = session
        self.response = response

    def add_response_callback(self, callback):
        callback(self, self.response)


class MockResponse(object):
    def __init__(self):
        self.called_args = ()
        self.called_kwargs = {}

    def set_cookie(self, *args, **kwargs):
        self.called_args = args
        self.called_kwargs = kwargs
        return


class DummyCSRF(object):
    def new_csrf_token(self, request):
        return 'e5e9e30a08b34ff9842ff7d2b958c14b'

    def get_csrf_token(self, request):
        return '02821185e4c94269bdc38e6eeae0a2f8'
