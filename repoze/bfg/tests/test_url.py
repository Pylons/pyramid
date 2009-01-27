import unittest

from zope.testing.cleanup import cleanUp

class ModelURLTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, model, request, *elements, **kw):
        self._registerContextURL()
        from repoze.bfg.url import model_url
        return model_url(model, request, *elements, **kw)

    def _registerContextURL(self):
        from repoze.bfg.interfaces import IContextURL
        from zope.interface import Interface
        from zope.component import getGlobalSiteManager
        class DummyContextURL(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'http://example.com/context/'
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(DummyContextURL, (Interface, Interface),
                            IContextURL)

    def test_root_default(self):
        root = DummyContext()
        request = DummyRequest()
        result = self._callFUT(root, request)
        self.assertEqual(result, 'http://example.com/context/')

    def test_extra_args(self):
        context = DummyContext()
        request = DummyRequest()
        result = self._callFUT(context, request, 'this/theotherthing', 'that')
        self.assertEqual(
            result,
            'http://example.com/context/this/theotherthing/that')

    def test_unicode_in_element_names(self):
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        context = DummyContext()
        request = DummyRequest()
        result = self._callFUT(context, request, uc)
        self.assertEqual(result,
                     'http://example.com/context/La%20Pe%C3%B1a')

    def test_element_names_url_quoted(self):
        context = DummyContext()
        request = DummyRequest()
        result = self._callFUT(context, request, 'a b c')
        self.assertEqual(result, 'http://example.com/context/a%20b%20c')

    def test_with_query_dict(self):
        context = DummyContext()
        request = DummyRequest()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        result = self._callFUT(context, request, 'a', query={'a':uc})
        self.assertEqual(result,
                         'http://example.com/context/a?a=La+Pe%C3%B1a')

    def test_with_query_seq(self):
        context = DummyContext()
        request = DummyRequest()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        result = self._callFUT(context, request, 'a', query=[('a', 'hi there'),
                                                             ('b', uc)])
        self.assertEqual(result,
                     'http://example.com/context/a?a=hi+there&b=La+Pe%C3%B1a')

class UrlEncodeTests(unittest.TestCase):
    def _callFUT(self, query, doseq=False):
        from repoze.bfg.url import urlencode
        return urlencode(query, doseq)

    def test_ascii_only(self):
        result = self._callFUT([('a',1), ('b',2)])
        self.assertEqual(result, 'a=1&b=2')

    def test_unicode_key(self):
        la = unicode('LaPe\xc3\xb1a', 'utf-8')
        result = self._callFUT([(la, 1), ('b',2)])
        self.assertEqual(result, 'LaPe%C3%B1a=1&b=2')

    def test_unicode_val_single(self):
        la = unicode('LaPe\xc3\xb1a', 'utf-8')
        result = self._callFUT([('a', la), ('b',2)])
        self.assertEqual(result, 'a=LaPe%C3%B1a&b=2')

    def test_unicode_val_multiple(self):
        la = [unicode('LaPe\xc3\xb1a', 'utf-8')] * 2
        result = self._callFUT([('a', la), ('b',2)], doseq=True)
        self.assertEqual(result, 'a=LaPe%C3%B1a&a=LaPe%C3%B1a&b=2')

    def test_dict(self):
        result = self._callFUT({'a':1})
        self.assertEqual(result, 'a=1')
        
class DummyContext(object):
    def __init__(self, next=None):
        self.next = next
        
class DummyRequest:
    application_url = 'http://example.com:5432' # app_url never ends with slash

