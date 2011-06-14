import unittest

class TestBWCompat(unittest.TestCase):
    def test_bwcompat_notfound(self):
        from pyramid.exceptions import NotFound as one
        from pyramid.httpexceptions import HTTPNotFound as two
        self.assertTrue(one is two)

    def test_bwcompat_forbidden(self):
        from pyramid.exceptions import Forbidden as one
        from pyramid.httpexceptions import HTTPForbidden as two
        self.assertTrue(one is two)

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

    def test_response_equivalence(self):
        from pyramid.exceptions import NotFound
        from pyramid.httpexceptions import HTTPNotFound
        self.assertTrue(NotFound is HTTPNotFound)

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

    def test_response_equivalence(self):
        from pyramid.exceptions import Forbidden
        from pyramid.httpexceptions import HTTPForbidden
        self.assertTrue(Forbidden is HTTPForbidden)

