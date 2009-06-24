import unittest

from repoze.bfg.testing import cleanUp

class ModelURLTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, model, request, *elements, **kw):
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
        self._registerContextURL()
        root = DummyContext()
        request = DummyRequest()
        result = self._callFUT(root, request)
        self.assertEqual(result, 'http://example.com/context/')

    def test_extra_args(self):
        self._registerContextURL()
        context = DummyContext()
        request = DummyRequest()
        result = self._callFUT(context, request, 'this/theotherthing', 'that')
        self.assertEqual(
            result,
            'http://example.com/context/this%2Ftheotherthing/that')

    def test_unicode_in_element_names(self):
        self._registerContextURL()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        context = DummyContext()
        request = DummyRequest()
        result = self._callFUT(context, request, uc)
        self.assertEqual(result,
                     'http://example.com/context/La%20Pe%C3%B1a')

    def test_element_names_url_quoted(self):
        self._registerContextURL()
        context = DummyContext()
        request = DummyRequest()
        result = self._callFUT(context, request, 'a b c')
        self.assertEqual(result, 'http://example.com/context/a%20b%20c')

    def test_with_query_dict(self):
        self._registerContextURL()
        context = DummyContext()
        request = DummyRequest()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        result = self._callFUT(context, request, 'a', query={'a':uc})
        self.assertEqual(result,
                         'http://example.com/context/a?a=La+Pe%C3%B1a')

    def test_with_query_seq(self):
        self._registerContextURL()
        context = DummyContext()
        request = DummyRequest()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        result = self._callFUT(context, request, 'a', query=[('a', 'hi there'),
                                                             ('b', uc)])
        self.assertEqual(result,
                     'http://example.com/context/a?a=hi+there&b=La+Pe%C3%B1a')

    def test_anchor_is_after_root_when_no_elements(self):
        self._registerContextURL()
        context = DummyContext()
        request = DummyRequest()
        result = self._callFUT(context, request, anchor='a')
        self.assertEqual(result,
                         'http://example.com/context/#a')

    def test_anchor_is_after_elements_when_no_qs(self):
        self._registerContextURL()
        context = DummyContext()
        request = DummyRequest()
        result = self._callFUT(context, request, 'a', anchor='b')
        self.assertEqual(result,
                         'http://example.com/context/a#b')

    def test_anchor_is_after_qs_when_qs_is_present(self):
        self._registerContextURL()
        context = DummyContext()
        request = DummyRequest()
        result = self._callFUT(context, request, 'a', 
                                query={'b':'c'}, anchor='d')
        self.assertEqual(result,
                         'http://example.com/context/a?b=c#d')

    def test_anchor_is_encoded_utf8_if_unicode(self):
        self._registerContextURL()
        context = DummyContext()
        request = DummyRequest()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8') 
        result = self._callFUT(context, request, anchor=uc)
        self.assertEqual(result,
                         'http://example.com/context/#La Pe\xc3\xb1a')

    def test_anchor_is_not_urlencoded(self):
        self._registerContextURL()
        context = DummyContext()
        request = DummyRequest()
        result = self._callFUT(context, request, anchor=' /#')
        self.assertEqual(result,
                         'http://example.com/context/# /#')

    def test_no_IContextURL_registered(self):
        # falls back to TraversalContextURL
        root = DummyContext()
        root.__name__ = ''
        root.__parent__ = None
        request = DummyRequest()
        request.environ = {}
        result = self._callFUT(root, request)
        self.assertEqual(result, 'http://example.com:5432/')

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

class TestRouteUrl(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.url import route_url
        return route_url(*arg, **kw)

    def test_it(self):
        from repoze.bfg.interfaces import IRoutesMapper
        mapper = DummyRoutesMapper({'flub':DummyRoute({})})
        from zope.component import getSiteManager
        sm = getSiteManager()
        sm.registerUtility(mapper, IRoutesMapper)
        args = {'a':'1', 'b':'2', 'c':'3'}
        environ = {'SERVER_NAME':'example.com', 'wsgi.url_scheme':'http',
                   'SERVER_PORT':'80', 'wsgiorg.routing_args':((), args)}
        request = DummyRequest(environ)
        result = self._callFUT(request, 'flub', a=1, b=2, c=3)
        self.assertEqual(result, 'http://example.com/1/2/3')

    def test_it_generation_error(self):
        from repoze.bfg.interfaces import IRoutesMapper
        mapper = DummyRoutesMapper({'flub':DummyRoute({})})
        from zope.component import getSiteManager
        sm = getSiteManager()
        sm.registerUtility(mapper, IRoutesMapper)
        args = {'a':'1', 'b':'2', 'c':'3'}
        mapper.raise_exc = True
        environ = {'SERVER_NAME':'example.com', 'wsgi.url_scheme':'http',
                   'SERVER_PORT':'80', 'wsgiorg.routing_args':((), args)}
        request = DummyRequest(environ)
        self.assertRaises(ValueError, self._callFUT, request, 'flub', a=1)
        
class DummyContext(object):
    def __init__(self, next=None):
        self.next = next
        
class DummyRequest:
    application_url = 'http://example.com:5432' # app_url never ends with slash
    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ

class DummyRoutesMapper:
    encoding = 'utf-8'
    hardcode_names = False
    sub_domains = []
    raise_exc = False
    def __init__(self, routes, generate_result='/1/2/3', raise_exc=False):
        self._routenames = routes
        self.generate_result = generate_result
        
    def generate(self, *route_args, **newargs):
        if self.raise_exc:
            from routes.util import GenerationException
            raise GenerationException
        return self.generate_result
    
class DummyRoute:
    filter = None
    static = False
    def __init__(self, defaults):
        self.defaults = defaults
        
        
