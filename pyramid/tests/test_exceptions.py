import unittest

class TestExceptionResponse(unittest.TestCase):
    def _makeOne(self, message):
        from pyramid.exceptions import ExceptionResponse
        return ExceptionResponse(message)
    
    def test_app_iter(self):
        exc = self._makeOne('')
        self.failUnless('<code></code>' in exc.app_iter[0])

    def test_headerlist(self):
        exc = self._makeOne('')
        headerlist = exc.headerlist
        headerlist.sort()
        app_iter = exc.app_iter
        clen = str(len(app_iter[0]))
        self.assertEqual(headerlist[0], ('Content-Length', clen))
        self.assertEqual(headerlist[1], ('Content-Type', 'text/html'))

    def test_withmessage(self):
        exc = self._makeOne('abc&123')
        self.failUnless('<code>abc&amp;123</code>' in exc.app_iter[0])

class TestNotFound(unittest.TestCase):
    def _makeOne(self, message):
        from pyramid.exceptions import NotFound
        return NotFound(message)

    def test_it(self):
        from pyramid.exceptions import ExceptionResponse
        e = self._makeOne('notfound')
        self.failUnless(isinstance(e, ExceptionResponse))
        self.assertEqual(e.status, '404 Not Found')

class TestForbidden(unittest.TestCase):
    def _makeOne(self, message):
        from pyramid.exceptions import Forbidden
        return Forbidden(message)

    def test_it(self):
        from pyramid.exceptions import ExceptionResponse
        e = self._makeOne('unauthorized')
        self.failUnless(isinstance(e, ExceptionResponse))
        self.assertEqual(e.status, '403 Forbidden')
