import unittest

from pyramid.compat import text_

class TestXHRPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.config.predicates import XHRPredicate
        return XHRPredicate(val)
    
    def test___call___true(self):
        inst = self._makeOne(True)
        request = Dummy()
        request.is_xhr = True
        result = inst(None, request)
        self.assertTrue(result)
        
    def test___call___false(self):
        inst = self._makeOne(True)
        request = Dummy()
        request.is_xhr = False
        result = inst(None, request)
        self.assertFalse(result)

    def test___text__(self):
        inst = self._makeOne(True)
        self.assertEqual(inst.__text__(), 'xhr = True')

    def test___phash__(self):
        inst = self._makeOne(True)
        self.assertEqual(inst.__phash__(), 'xhr:True')

class TestRequestMethodPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.config.predicates import RequestMethodPredicate
        return RequestMethodPredicate(val)
    
    def test___call___true_single(self):
        inst = self._makeOne('GET')
        request = Dummy()
        request.method = 'GET'
        result = inst(None, request)
        self.assertTrue(result)
        
    def test___call___true_multi(self):
        inst = self._makeOne(('GET','HEAD'))
        request = Dummy()
        request.method = 'GET'
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___false(self):
        inst = self._makeOne(('GET','HEAD'))
        request = Dummy()
        request.method = 'POST'
        result = inst(None, request)
        self.assertFalse(result)

    def test___text__(self):
        inst = self._makeOne(('HEAD','GET'))
        self.assertEqual(inst.__text__(), 'request method = GET,HEAD')

    def test___phash__(self):
        inst = self._makeOne(('HEAD','GET'))
        self.assertEqual(inst.__phash__(), ['request_method:GET',
                                            'request_method:HEAD'])

class TestPathInfoPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.config.predicates import PathInfoPredicate
        return PathInfoPredicate(val)

    def test_ctor_compilefail(self):
        from pyramid.exceptions import ConfigurationError
        self.assertRaises(ConfigurationError, self._makeOne, '\\')
    
    def test___call___true(self):
        inst = self._makeOne(r'/\d{2}')
        request = Dummy()
        request.upath_info = text_('/12')
        result = inst(None, request)
        self.assertTrue(result)
        
    def test___call___false(self):
        inst = self._makeOne(r'/\d{2}')
        request = Dummy()
        request.upath_info = text_('/n12')
        result = inst(None, request)
        self.assertFalse(result)

    def test___text__(self):
        inst = self._makeOne('/')
        self.assertEqual(inst.__text__(), 'path_info = /')

    def test___phash__(self):
        inst = self._makeOne('/')
        self.assertEqual(inst.__phash__(), 'path_info:/')

class TestRequestParamPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.config.predicates import RequestParamPredicate
        return RequestParamPredicate(val)

    def test___call___true_exists(self):
        inst = self._makeOne('abc')
        request = Dummy()
        request.params = {'abc':1}
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___true_withval(self):
        inst = self._makeOne('abc=1')
        request = Dummy()
        request.params = {'abc':'1'}
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___false(self):
        inst = self._makeOne('abc')
        request = Dummy()
        request.params = {}
        result = inst(None, request)
        self.assertFalse(result)

    def test___text__exists(self):
        inst = self._makeOne('abc')
        self.assertEqual(inst.__text__(), 'request_param abc')

    def test___text__withval(self):
        inst = self._makeOne('abc=  1')
        self.assertEqual(inst.__text__(), 'request_param abc = 1')

    def test___phash__exists(self):
        inst = self._makeOne('abc')
        self.assertEqual(inst.__phash__(), 'request_param:abc=None')

    def test___phash__withval(self):
        inst = self._makeOne('abc=   1')
        self.assertEqual(inst.__phash__(), "request_param:abc='1'")

class Dummy(object):
    def __init__(self, **kw):
        self.__dict__.update(**kw)
        
