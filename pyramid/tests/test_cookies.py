import unittest
from pyramid import testing

class CookieMakeCookie(unittest.TestCase):
    def makeOne(self, name, value, **kw):
        from pyramid.cookies import make_cookie
        return make_cookie(name, value, **kw)

    def test_make_cookie_max_age(self):
        cookie = self.makeOne('test_cookie', 'value', max_age=500)

        self.assertTrue('test_cookie=value' in cookie)
        self.assertTrue('Max-Age=500;' in cookie)
        self.assertTrue('expires' in cookie)

    def test_make_cookie_expires(self):
        from datetime import (datetime, timedelta)

        cookie = self.makeOne('test_cookie', 'value', expires=datetime.utcnow()
                + timedelta(seconds=600))

        self.assertTrue('test_cookie=value' in cookie)
        self.assertTrue('expires' in cookie)
        self.assertTrue('Max-Age=' in cookie)

class CookieHelperTest(unittest.TestCase):
    def makeOne(self, name='uns', **kw):
        from pyramid.cookies import CookieHelper
        return CookieHelper(name, **kw)

    def test_cookie_creation(self):
        cookie = self.makeOne()
        
        from pyramid.cookies import CookieHelper
        self.assertTrue(isinstance(cookie, CookieHelper))

class SignedCookieHelperTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def makeOne(self, secret='seekrit', salt='salty', name='uns', **kw):
        from pyramid.cookies import SignedCookieHelper as CookieHelper
        return CookieHelper(secret, salt, name, **kw)

    def makeOneRequest(self):
        request = testing.DummyRequest()
        request.environ['HTTP_HOST'] = 'www.example.net'

        return request

    def test_cookie_name(self):
        cookie = self.makeOne()
        request = self.makeOneRequest()

        cookie_list = cookie.raw_headers(request, "test")

        for cookie in cookie_list:
            self.assertTrue(cookie[1].startswith('uns'))
            self.assertFalse('uns="";' in cookie[1])

    def test_cookie_expire(self):
        cookie = self.makeOne()
        request = self.makeOneRequest()

        cookie_list = cookie.raw_headers(request, None, max_age=0)

        for cookie in cookie_list:
            self.assertTrue('Max-Age=0;' in cookie[1])

    def test_cookie_max_age(self):
        cookie = self.makeOne()
        request = self.makeOneRequest()

        cookie_list = cookie.raw_headers(request, "test", max_age=60)

        for cookie in cookie_list:
            self.assertTrue('Max-Age=60;' in cookie[1])
            self.assertTrue('expires=' in cookie[1])

    def test_cookie_raw(self):
        cookie = self.makeOne()
        request  = self.makeOneRequest()

        cookie_list = cookie.raw_headers(request, "test")

        self.assertTrue(isinstance(cookie_list, list))

    def test_set_cookie(self):
        cookie = self.makeOne()
        request = self.makeOneRequest()

        ret = cookie.set_cookies(request, request.response, "test")

        self.assertEqual(ret, request.response)

    def test_no_cookie(self):
        cookie = self.makeOne()
        request = self.makeOneRequest()

        ret = cookie.get_value(request)

        self.assertEqual(None, ret)

    def test_with_cookies(self):
        cookie = self.makeOne()
        request = self.makeOneRequest()
        request.cookies['uns'] = "gAJVBHRlc3RxAS4KjKfwGmCkliC4ba99rWUdpy_riHzK7MQFPsb-SgYTgALHaSHrRkd3l-yE8c4w5ruxAKOyj2h5oF69Ix7ERZv_"

        ret = cookie.get_value(request)

        self.assertEqual(ret, "test")

    def test_with_bad_cookie_invalid_base64(self):
        cookie = self.makeOne()
        request = self.makeOneRequest()
        request.cookies['uns'] = "gAJVBHRlc3RxAS4KjKfwGmCkliC4ba99rWUdpy_{}riHzK7MQFPsbSgYTgALHaSHrRkd3lyE8c4w5ruxAKOyj2h5oF69Ix7ERZv_"

        self.assertRaises(ValueError, cookie.get_value, request)

    def test_with_bad_cookie_invalid_signature(self):
        cookie = self.makeOne(secret='sekrit!')
        request = self.makeOneRequest()
        request.cookies['uns'] = "InRlc3QiFLIoEwZcKG6ITQSqbYcUNnPljwOcGNs25JRVCSoZcx/uX+OA1AhssA+CNeVKpWksQa0ktMhuQDdjzmDwgzbptg=="

        self.assertRaises(ValueError, cookie.get_value, request)

    def test_with_wild_domain(self):
        cookie = self.makeOne(wild_domain=True)
        request = self.makeOneRequest()

        ret = cookie.raw_headers(request, "test")

        passed = False

        for cookie in ret:
            if 'Domain=.www.example.net' in cookie[1]:
                passed = True

        self.assertTrue(passed)
        self.assertEqual(len(ret), 3)

    def test_with_parent_domain(self):
        cookie = self.makeOne(parent_domain=True)
        request = self.makeOneRequest()

        ret = cookie.raw_headers(request, "test")

        passed = False

        for cookie in ret:
            if 'Domain=.example.net' in cookie[1]:
                passed = True

        self.assertTrue(passed)
        self.assertEqual(len(ret), 1)

    def test_with_domain(self):
        cookie = self.makeOne(domain="testing.example.net")
        request = self.makeOneRequest()

        ret = cookie.raw_headers(request, "test")

        passed = False

        for cookie in ret:
            if 'Domain=testing.example.net' in cookie[1]:
                passed = True

        self.assertTrue(passed)
        self.assertEqual(len(ret), 1)

    def test_flag_secure(self):
        cookie = self.makeOne(secure=True)
        request =self.makeOneRequest()

        ret = cookie.raw_headers(request, "test")

        for cookie in ret:
            self.assertTrue('; secure' in cookie[1])

    def test_flag_http_only(self):
        cookie = self.makeOne(httponly=True)
        request =self.makeOneRequest()

        ret = cookie.raw_headers(request, "test")

        for cookie in ret:
            self.assertTrue('; HttpOnly' in cookie[1])

    def test_http_host_port(self):
        cookie = self.makeOne()
        request = self.makeOneRequest()
        request.environ['HTTP_HOST'] = 'example.net:8080'

        ret = cookie.raw_headers(request, "test")

        for cookie in ret:
            self.assertFalse('example.net:8080' in cookie[1])

    def test_cookie_length(self):
        cookie = self.makeOne()
        request = self.makeOneRequest()

        longstring = 'a' * 4096
        self.assertRaises(ValueError, cookie.raw_headers, request, longstring)

    def test_very_long_key(self):
        longstring = 'a' * 1024
        cookie = self.makeOne(secret=longstring)
        request = self.makeOneRequest()

        ret = cookie.raw_headers(request, "test")
