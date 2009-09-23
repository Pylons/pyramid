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

class TestRouteUrl(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.url import route_url
        return route_url(*arg, **kw)

    def test_with_elements(self):
        from repoze.bfg.interfaces import IRoutesMapper
        mapper = DummyRoutesMapper(result='/1/2/3')
        from zope.component import getSiteManager
        sm = getSiteManager()
        sm.registerUtility(mapper, IRoutesMapper)
        request = DummyRequest()
        result = self._callFUT('flub', request, 'extra1', 'extra2',
                               a=1, b=2, c=3, _query={'a':1},
                               _anchor=u"foo")
        self.assertEqual(result,
                         'http://example.com:5432/1/2/3/extra1/extra2?a=1#foo')

    def test_no_elements(self):
        from repoze.bfg.interfaces import IRoutesMapper
        mapper = DummyRoutesMapper(result='/1/2/3')
        from zope.component import getSiteManager
        sm = getSiteManager()
        sm.registerUtility(mapper, IRoutesMapper)
        request = DummyRequest()
        result = self._callFUT('flub', request, a=1, b=2, c=3, _query={'a':1},
                               _anchor=u"foo")
        self.assertEqual(result,
                         'http://example.com:5432/1/2/3?a=1#foo')

    def test_it_generation_error(self):
        from repoze.bfg.interfaces import IRoutesMapper
        mapper = DummyRoutesMapper(raise_exc=KeyError)
        from zope.component import getSiteManager
        sm = getSiteManager()
        sm.registerUtility(mapper, IRoutesMapper)
        mapper.raise_exc = KeyError
        request = DummyRequest()
        self.assertRaises(KeyError, self._callFUT, 'flub', request, a=1)

class TestStaticUrl(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.url import static_url
        return static_url(*arg, **kw)

    def test_notfound(self):
        from repoze.bfg.interfaces import IRoutesMapper
        from zope.component import getSiteManager
        mapper = DummyRoutesMapper(result='/1/2/3')
        sm = getSiteManager()
        sm.registerUtility(mapper, IRoutesMapper)
        request = DummyRequest()
        self.assertRaises(ValueError, self._callFUT, 'static/foo.css', request)

    def test_abspath(self):
        from repoze.bfg.interfaces import IRoutesMapper
        from zope.component import getSiteManager
        mapper = DummyRoutesMapper(result='/1/2/3')
        sm = getSiteManager()
        sm.registerUtility(mapper, IRoutesMapper)
        request = DummyRequest()
        self.assertRaises(ValueError, self._callFUT, '/static/foo.css', request)

    def test_found_rel(self):
        from repoze.bfg.interfaces import IRoutesMapper
        from repoze.bfg.static import StaticRootFactory
        from zope.component import getSiteManager
        factory = StaticRootFactory('repoze.bfg.tests:fixtures')
        routes = [DummyRoute('name', factory=factory)]
        mapper = DummyRoutesMapper(result='/1/2/3', routes = routes)
        sm = getSiteManager()
        sm.registerUtility(mapper, IRoutesMapper)
        request = DummyRequest()
        url = self._callFUT('fixtures/minimal.pt', request)
        self.assertEqual(url, 'http://example.com:5432/1/2/3')

    def test_found_abs(self):
        from repoze.bfg.interfaces import IRoutesMapper
        from repoze.bfg.static import StaticRootFactory
        from zope.component import getSiteManager
        factory = StaticRootFactory('repoze.bfg.tests:fixtures')
        routes = [DummyRoute('name', factory=factory)]
        mapper = DummyRoutesMapper(result='/1/2/3', routes = routes)
        sm = getSiteManager()
        sm.registerUtility(mapper, IRoutesMapper)
        request = DummyRequest()
        url = self._callFUT('repoze.bfg.tests:fixtures/minimal.pt', request)
        self.assertEqual(url, 'http://example.com:5432/1/2/3')

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
    raise_exc = None
    def __init__(self, result='/1/2/3', raise_exc=False, routes=()):
        self.result = result
        self.routes = routes

    def get_routes(self):
        return self.routes
        
    def generate(self, *route_args, **newargs):
        if self.raise_exc:
            raise self.raise_exc
        return self.result
    
class DummyRoute:
    def __init__(self, name, factory=None):
        self.name = name
        self.factory = factory
