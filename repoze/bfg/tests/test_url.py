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

    def _registerContextURL(self, reg):
        from repoze.bfg.interfaces import IContextURL
        from zope.interface import Interface
        class DummyContextURL(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'http://example.com/context/'
        reg.registerAdapter(DummyContextURL, (Interface, Interface),
                            IContextURL)

    def test_root_default(self):
        request = _makeRequest()
        self._registerContextURL(request.registry)
        root = DummyContext()
        result = self._callFUT(root, request)
        self.assertEqual(result, 'http://example.com/context/')

    def test_extra_args(self):
        request = _makeRequest()
        self._registerContextURL(request.registry)
        context = DummyContext()
        result = self._callFUT(context, request, 'this/theotherthing', 'that')
        self.assertEqual(
            result,
            'http://example.com/context/this%2Ftheotherthing/that')

    def test_unicode_in_element_names(self):
        request = _makeRequest()
        self._registerContextURL(request.registry)
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        context = DummyContext()
        result = self._callFUT(context, request, uc)
        self.assertEqual(result,
                     'http://example.com/context/La%20Pe%C3%B1a')

    def test_element_names_url_quoted(self):
        request = _makeRequest()
        self._registerContextURL(request.registry)
        context = DummyContext()
        result = self._callFUT(context, request, 'a b c')
        self.assertEqual(result, 'http://example.com/context/a%20b%20c')

    def test_with_query_dict(self):
        request = _makeRequest()
        self._registerContextURL(request.registry)
        context = DummyContext()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        result = self._callFUT(context, request, 'a', query={'a':uc})
        self.assertEqual(result,
                         'http://example.com/context/a?a=La+Pe%C3%B1a')

    def test_with_query_seq(self):
        request = _makeRequest()
        self._registerContextURL(request.registry)
        context = DummyContext()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        result = self._callFUT(context, request, 'a', query=[('a', 'hi there'),
                                                             ('b', uc)])
        self.assertEqual(result,
                     'http://example.com/context/a?a=hi+there&b=La+Pe%C3%B1a')

    def test_anchor_is_after_root_when_no_elements(self):
        request = _makeRequest()
        self._registerContextURL(request.registry)
        context = DummyContext()
        result = self._callFUT(context, request, anchor='a')
        self.assertEqual(result,
                         'http://example.com/context/#a')

    def test_anchor_is_after_elements_when_no_qs(self):
        request = _makeRequest()
        self._registerContextURL(request.registry)
        context = DummyContext()
        result = self._callFUT(context, request, 'a', anchor='b')
        self.assertEqual(result,
                         'http://example.com/context/a#b')

    def test_anchor_is_after_qs_when_qs_is_present(self):
        request = _makeRequest()
        self._registerContextURL(request.registry)
        context = DummyContext()
        result = self._callFUT(context, request, 'a', 
                                query={'b':'c'}, anchor='d')
        self.assertEqual(result,
                         'http://example.com/context/a?b=c#d')

    def test_anchor_is_encoded_utf8_if_unicode(self):
        request = _makeRequest()
        self._registerContextURL(request.registry)
        context = DummyContext()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8') 
        result = self._callFUT(context, request, anchor=uc)
        self.assertEqual(result,
                         'http://example.com/context/#La Pe\xc3\xb1a')

    def test_anchor_is_not_urlencoded(self):
        request = _makeRequest()
        self._registerContextURL(request.registry)
        context = DummyContext()
        result = self._callFUT(context, request, anchor=' /#')
        self.assertEqual(result,
                         'http://example.com/context/# /#')

    def test_no_IContextURL_registered(self):
        # falls back to TraversalContextURL
        root = DummyContext()
        root.__name__ = ''
        root.__parent__ = None
        request = _makeRequest()
        request.environ = {}
        result = self._callFUT(root, request)
        self.assertEqual(result, 'http://example.com:5432/')

    def test_no_registry_on_request(self):
        from repoze.bfg.threadlocal import get_current_registry
        reg = get_current_registry()
        request = DummyRequest()
        self._registerContextURL(reg)
        root = DummyContext()
        result = self._callFUT(root, request)
        self.assertEqual(result, 'http://example.com/context/')

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
        request = _makeRequest()
        mapper = DummyRoutesMapper(result='/1/2/3')
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = self._callFUT('flub', request, 'extra1', 'extra2',
                               a=1, b=2, c=3, _query={'a':1},
                               _anchor=u"foo")
        self.assertEqual(result,
                         'http://example.com:5432/1/2/3/extra1/extra2?a=1#foo')

    def test_no_elements(self):
        from repoze.bfg.interfaces import IRoutesMapper
        request = _makeRequest()
        mapper = DummyRoutesMapper(result='/1/2/3')
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = self._callFUT('flub', request, a=1, b=2, c=3, _query={'a':1},
                               _anchor=u"foo")
        self.assertEqual(result,
                         'http://example.com:5432/1/2/3?a=1#foo')

    def test_it_generation_error(self):
        from repoze.bfg.interfaces import IRoutesMapper
        request = _makeRequest()
        mapper = DummyRoutesMapper(raise_exc=KeyError)
        request.registry.registerUtility(mapper, IRoutesMapper)
        mapper.raise_exc = KeyError
        self.assertRaises(KeyError, self._callFUT, 'flub', request, a=1)

    def test_generate_doesnt_receive_query_or_anchor(self):
        from repoze.bfg.interfaces import IRoutesMapper
        mapper = DummyRoutesMapper(result='')
        from zope.component import getSiteManager
        sm = getSiteManager()
        sm.registerUtility(mapper, IRoutesMapper)
        request = DummyRequest()
        result = self._callFUT('flub', request, _query=dict(name='some_name'))
        self.assertEqual(mapper.kw, {}) # shouldnt have anchor/query
        self.assertEqual(result, 'http://example.com:5432?name=some_name')

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
        request = _makeRequest()
        mapper = DummyRoutesMapper(result='/1/2/3')
        request.registry.registerUtility(mapper, IRoutesMapper)
        self.assertRaises(ValueError, self._callFUT, 'static/foo.css', request)

    def test_abspath(self):
        from repoze.bfg.interfaces import IRoutesMapper
        request = _makeRequest()
        mapper = DummyRoutesMapper(result='/1/2/3')
        request.registry.registerUtility(mapper, IRoutesMapper)
        self.assertRaises(ValueError, self._callFUT, '/static/foo.css', request)

    def test_found_rel(self):
        from repoze.bfg.interfaces import IRoutesMapper
        from repoze.bfg.static import StaticRootFactory
        request = _makeRequest()
        factory = StaticRootFactory('repoze.bfg.tests:fixtures')
        routes = [DummyRoute('name', factory=factory)]
        mapper = DummyRoutesMapper(result='/1/2/3', routes = routes)
        request.registry.registerUtility(mapper, IRoutesMapper)
        url = self._callFUT('fixtures/minimal.pt', request)
        self.assertEqual(url, 'http://example.com:5432/1/2/3')

    def test_found_abs(self):
        from repoze.bfg.interfaces import IRoutesMapper
        from repoze.bfg.static import StaticRootFactory
        request = _makeRequest()
        factory = StaticRootFactory('repoze.bfg.tests:fixtures')
        routes = [DummyRoute('name', factory=factory)]
        mapper = DummyRoutesMapper(result='/1/2/3', routes = routes)
        request.registry.registerUtility(mapper, IRoutesMapper)
        url = self._callFUT('repoze.bfg.tests:fixtures/minimal.pt', request)
        self.assertEqual(url, 'http://example.com:5432/1/2/3')

    def test_found_abs_no_registry_on_request(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import IRoutesMapper
        from repoze.bfg.static import StaticRootFactory
        factory = StaticRootFactory('repoze.bfg.tests:fixtures')
        routes = [DummyRoute('name', factory=factory)]
        mapper = DummyRoutesMapper(result='/1/2/3', routes = routes)
        registry = get_current_registry()
        registry.registerUtility(mapper, IRoutesMapper)
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
        
    def generate(self, *route_args, **kw):
        self.kw = kw
        if self.raise_exc:
            raise self.raise_exc
        return self.result
    
class DummyRoute:
    def __init__(self, name, factory=None):
        self.name = name
        self.factory = factory

def _makeRequest(environ=None):
    from repoze.bfg.registry import Registry
    request = DummyRequest(environ)
    request.registry = Registry()
    return request

        
