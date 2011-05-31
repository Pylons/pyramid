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

    def test_response_equivalence(self):
        from pyramid.exceptions import NotFound
        from pyramid.response import HTTPNotFound
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
        from pyramid.response import HTTPForbidden
        self.assertTrue(Forbidden is HTTPForbidden)

