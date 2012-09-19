import unittest

from pyramid.compat import text_

class TestXHRPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.config.predicates import XHRPredicate
        return XHRPredicate(val, None)
    
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

    def test_text(self):
        inst = self._makeOne(True)
        self.assertEqual(inst.text(), 'xhr = True')

    def test_phash(self):
        inst = self._makeOne(True)
        self.assertEqual(inst.phash(), 'xhr = True')

class TestRequestMethodPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.config.predicates import RequestMethodPredicate
        return RequestMethodPredicate(val, None)

    def test_ctor_get_but_no_head(self):
        inst = self._makeOne('GET')
        self.assertEqual(inst.val, ('GET', 'HEAD'))
    
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

    def test_text(self):
        inst = self._makeOne(('HEAD','GET'))
        self.assertEqual(inst.text(), 'request_method = GET,HEAD')

    def test_phash(self):
        inst = self._makeOne(('HEAD','GET'))
        self.assertEqual(inst.phash(), 'request_method = GET,HEAD')

class TestPathInfoPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.config.predicates import PathInfoPredicate
        return PathInfoPredicate(val, None)

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

    def test_text(self):
        inst = self._makeOne('/')
        self.assertEqual(inst.text(), 'path_info = /')

    def test_phash(self):
        inst = self._makeOne('/')
        self.assertEqual(inst.phash(), 'path_info = /')

class TestRequestParamPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.config.predicates import RequestParamPredicate
        return RequestParamPredicate(val, None)

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

    def test_text_exists(self):
        inst = self._makeOne('abc')
        self.assertEqual(inst.text(), 'request_param abc')

    def test_text_withval(self):
        inst = self._makeOne('abc=  1')
        self.assertEqual(inst.text(), 'request_param abc = 1')

    def test_phash_exists(self):
        inst = self._makeOne('abc')
        self.assertEqual(inst.phash(), 'request_param abc')

    def test_phash_withval(self):
        inst = self._makeOne('abc=   1')
        self.assertEqual(inst.phash(), "request_param abc = 1")

class TestMatchParamPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.config.predicates import MatchParamPredicate
        return MatchParamPredicate(val, None)

    def test___call___true_single(self):
        inst = self._makeOne('abc=1')
        request = Dummy()
        request.matchdict = {'abc':'1'}
        result = inst(None, request)
        self.assertTrue(result)


    def test___call___true_multi(self):
        inst = self._makeOne(('abc=1', 'def=2'))
        request = Dummy()
        request.matchdict = {'abc':'1', 'def':'2'}
        result = inst(None, request)
        self.assertTrue(result)
        
    def test___call___false(self):
        inst = self._makeOne('abc=1')
        request = Dummy()
        request.matchdict = {}
        result = inst(None, request)
        self.assertFalse(result)

    def test_text(self):
        inst = self._makeOne(('def=  1', 'abc =2'))
        self.assertEqual(inst.text(), 'match_param abc=2,def=1')

    def test_phash(self):
        inst = self._makeOne(('def=  1', 'abc =2'))
        self.assertEqual(inst.phash(), 'match_param abc=2,def=1')

class TestCustomPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.config.predicates import CustomPredicate
        return CustomPredicate(val, None)

    def test___call___true(self):
        def func(context, request):
            self.assertEqual(context, None)
            self.assertEqual(request, None)
            return True
        inst = self._makeOne(func)
        result = inst(None, None)
        self.assertTrue(result)
    
    def test___call___false(self):
        def func(context, request):
            self.assertEqual(context, None)
            self.assertEqual(request, None)
            return False
        inst = self._makeOne(func)
        result = inst(None, None)
        self.assertFalse(result)

    def test_text_func_has___text__(self):
        pred = predicate()
        pred.__text__ = 'text'
        inst = self._makeOne(pred)
        self.assertEqual(inst.text(), 'text')
         
    def test_text_func_repr(self):
        pred = predicate()
        inst = self._makeOne(pred)
        self.assertEqual(inst.text(), 'custom predicate: object predicate')

    def test_phash(self):
        pred = predicate()
        inst = self._makeOne(pred)
        self.assertEqual(inst.phash(), 'custom:1')

class TestTraversePredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.config.predicates import TraversePredicate
        return TraversePredicate(val, None)
    
    def test___call__traverse_has_remainder_already(self):
        inst = self._makeOne('/1/:a/:b')
        info = {'traverse':'abc'}
        request = Dummy()
        result = inst(info, request)
        self.assertEqual(result, True)
        self.assertEqual(info, {'traverse':'abc'})

    def test___call__traverse_matches(self):
        inst = self._makeOne('/1/:a/:b')
        info = {'match':{'a':'a', 'b':'b'}}
        request = Dummy()
        result = inst(info, request)
        self.assertEqual(result, True)
        self.assertEqual(info, {'match':
                                {'a':'a', 'b':'b', 'traverse':('1', 'a', 'b')}})

    def test___call__traverse_matches_with_highorder_chars(self):
        inst = self._makeOne(text_(b'/La Pe\xc3\xb1a/{x}', 'utf-8'))
        info = {'match':{'x':text_(b'Qu\xc3\xa9bec', 'utf-8')}}
        request = Dummy()
        result = inst(info, request)
        self.assertEqual(result, True)
        self.assertEqual(
            info['match']['traverse'],
            (text_(b'La Pe\xc3\xb1a', 'utf-8'),
             text_(b'Qu\xc3\xa9bec', 'utf-8'))
             )

    def test_text(self):
        inst = self._makeOne('/abc')
        self.assertEqual(inst.text(), 'traverse matchdict pseudo-predicate')

    def test_phash(self):
        inst = self._makeOne('/abc')
        self.assertEqual(inst.phash(), '')

class Test_CheckCSRFTokenPredicate(unittest.TestCase):
    def _makeOne(self, val, config):
        from pyramid.config.predicates import CheckCSRFTokenPredicate
        return CheckCSRFTokenPredicate(val, config)

    def test_text(self):
        inst = self._makeOne(True, None)
        self.assertEqual(inst.text(), 'check_csrf = True')

    def test_phash(self):
        inst = self._makeOne(True, None)
        self.assertEqual(inst.phash(), 'check_csrf = True')
        
    def test_it_call_val_True(self):
        inst = self._makeOne(True, None)
        request = Dummy()
        def check_csrf_token(req, val, raises=True):
            self.assertEqual(req, request)
            self.assertEqual(val, 'csrf_token')
            self.assertEqual(raises, False)
            return True
        inst.check_csrf_token  = check_csrf_token
        result = inst(None, request)
        self.assertEqual(result, True)

    def test_it_call_val_str(self):
        inst = self._makeOne('abc', None)
        request = Dummy()
        def check_csrf_token(req, val, raises=True):
            self.assertEqual(req, request)
            self.assertEqual(val, 'abc')
            self.assertEqual(raises, False)
            return True
        inst.check_csrf_token  = check_csrf_token
        result = inst(None, request)
        self.assertEqual(result, True)

    def test_it_call_val_False(self):
        inst = self._makeOne(False, None)
        request = Dummy()
        result = inst(None, request)
        self.assertEqual(result, True)

class predicate(object):
    def __repr__(self):
        return 'predicate'
    def __hash__(self):
        return 1
    
class Dummy(object):
    def __init__(self, **kw):
        self.__dict__.update(**kw)
        
