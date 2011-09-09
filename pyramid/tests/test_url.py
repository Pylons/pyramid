import unittest

from pyramid.testing import setUp
from pyramid.testing import tearDown

class TestURLMethodsMixin(unittest.TestCase):
    def setUp(self):
        self.config = setUp()

    def tearDown(self):
        tearDown()
        
    def _makeOne(self):
        from pyramid.url import URLMethodsMixin
        class Request(URLMethodsMixin):
            application_url = 'http://example.com:5432'
        request = Request()
        request.registry = self.config.registry
        return request

    def _registerContextURL(self, reg):
        from pyramid.interfaces import IContextURL
        from zope.interface import Interface
        class DummyContextURL(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'http://example.com/context/'
        reg.registerAdapter(DummyContextURL, (Interface, Interface),
                            IContextURL)

    def test_resource_url_root_default(self):
        request = self._makeOne()
        self._registerContextURL(request.registry)
        root = DummyContext()
        result = request.resource_url(root)
        self.assertEqual(result, 'http://example.com/context/')

    def test_resource_url_extra_args(self):
        request = self._makeOne()
        self._registerContextURL(request.registry)
        context = DummyContext()
        result = request.resource_url(context, 'this/theotherthing', 'that')
        self.assertEqual(
            result,
            'http://example.com/context/this%2Ftheotherthing/that')

    def test_resource_url_unicode_in_element_names(self):
        request = self._makeOne()
        self._registerContextURL(request.registry)
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        context = DummyContext()
        result = request.resource_url(context, uc)
        self.assertEqual(result,
                     'http://example.com/context/La%20Pe%C3%B1a')

    def test_resource_url_at_sign_in_element_names(self):
        request = self._makeOne()
        self._registerContextURL(request.registry)
        context = DummyContext()
        result = request.resource_url(context, '@@myview')
        self.assertEqual(result,
                     'http://example.com/context/@@myview')

    def test_resource_url_element_names_url_quoted(self):
        request = self._makeOne()
        self._registerContextURL(request.registry)
        context = DummyContext()
        result = request.resource_url(context, 'a b c')
        self.assertEqual(result, 'http://example.com/context/a%20b%20c')

    def test_resource_url_with_query_dict(self):
        request = self._makeOne()
        self._registerContextURL(request.registry)
        context = DummyContext()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        result = request.resource_url(context, 'a', query={'a':uc})
        self.assertEqual(result,
                         'http://example.com/context/a?a=La+Pe%C3%B1a')

    def test_resource_url_with_query_seq(self):
        request = self._makeOne()
        self._registerContextURL(request.registry)
        context = DummyContext()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        result = request.resource_url(context, 'a', query=[('a', 'hi there'),
                                                             ('b', uc)])
        self.assertEqual(result,
                     'http://example.com/context/a?a=hi+there&b=La+Pe%C3%B1a')

    def test_resource_url_anchor_is_after_root_when_no_elements(self):
        request = self._makeOne()
        self._registerContextURL(request.registry)
        context = DummyContext()
        result = request.resource_url(context, anchor='a')
        self.assertEqual(result,
                         'http://example.com/context/#a')

    def test_resource_url_anchor_is_after_elements_when_no_qs(self):
        request = self._makeOne()
        self._registerContextURL(request.registry)
        context = DummyContext()
        result = request.resource_url(context, 'a', anchor='b')
        self.assertEqual(result,
                         'http://example.com/context/a#b')

    def test_resource_url_anchor_is_after_qs_when_qs_is_present(self):
        request = self._makeOne()
        self._registerContextURL(request.registry)
        context = DummyContext()
        result = request.resource_url(context, 'a', 
                                      query={'b':'c'}, anchor='d')
        self.assertEqual(result,
                         'http://example.com/context/a?b=c#d')

    def test_resource_url_anchor_is_encoded_utf8_if_unicode(self):
        request = self._makeOne()
        self._registerContextURL(request.registry)
        context = DummyContext()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8') 
        result = request.resource_url(context, anchor=uc)
        self.assertEqual(result,
                         'http://example.com/context/#La Pe\xc3\xb1a')

    def test_resource_url_anchor_is_not_urlencoded(self):
        request = self._makeOne()
        self._registerContextURL(request.registry)
        context = DummyContext()
        result = request.resource_url(context, anchor=' /#')
        self.assertEqual(result,
                         'http://example.com/context/# /#')

    def test_resource_url_no_IContextURL_registered(self):
        # falls back to TraversalContextURL
        root = DummyContext()
        root.__name__ = ''
        root.__parent__ = None
        request = self._makeOne()
        request.environ = {}
        result = request.resource_url(root)
        self.assertEqual(result, 'http://example.com:5432/')

    def test_resource_url_no_registry_on_request(self):
        request = self._makeOne()
        self._registerContextURL(request.registry)
        del request.registry
        root = DummyContext()
        result = request.resource_url(root)
        self.assertEqual(result, 'http://example.com/context/')

    def test_route_url_with_elements(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        mapper = DummyRoutesMapper(route=DummyRoute('/1/2/3'))
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.route_url('flub', 'extra1', 'extra2')
        self.assertEqual(result,
                         'http://example.com:5432/1/2/3/extra1/extra2')

    def test_route_url_with_elements_path_endswith_slash(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        mapper = DummyRoutesMapper(route=DummyRoute('/1/2/3/'))
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.route_url('flub', 'extra1', 'extra2')
        self.assertEqual(result,
                         'http://example.com:5432/1/2/3/extra1/extra2')

    def test_route_url_no_elements(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        mapper = DummyRoutesMapper(route=DummyRoute('/1/2/3'))
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.route_url('flub', a=1, b=2, c=3, _query={'a':1},
                                   _anchor=u"foo")
        self.assertEqual(result,
                         'http://example.com:5432/1/2/3?a=1#foo')

    def test_route_url_with_anchor_string(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        mapper = DummyRoutesMapper(route=DummyRoute('/1/2/3'))
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.route_url('flub', _anchor="La Pe\xc3\xb1a")
        self.assertEqual(result,
                         'http://example.com:5432/1/2/3#La Pe\xc3\xb1a')

    def test_route_url_with_anchor_unicode(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        mapper = DummyRoutesMapper(route=DummyRoute('/1/2/3'))
        request.registry.registerUtility(mapper, IRoutesMapper)
        anchor = unicode('La Pe\xc3\xb1a', 'utf-8')
        result = request.route_url('flub', _anchor=anchor)
        self.assertEqual(result,
                         'http://example.com:5432/1/2/3#La Pe\xc3\xb1a')

    def test_route_url_with_query(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        mapper = DummyRoutesMapper(route=DummyRoute('/1/2/3'))
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.route_url('flub', _query={'q':'1'})
        self.assertEqual(result,
                         'http://example.com:5432/1/2/3?q=1')

    def test_route_url_with_app_url(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        mapper = DummyRoutesMapper(route=DummyRoute('/1/2/3'))
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.route_url('flub', _app_url='http://example2.com')
        self.assertEqual(result,
                         'http://example2.com/1/2/3')

    def test_route_url_generation_error(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        mapper = DummyRoutesMapper(raise_exc=KeyError)
        request.registry.registerUtility(mapper, IRoutesMapper)
        mapper.raise_exc = KeyError
        self.assertRaises(KeyError, request.route_url, 'flub', request, a=1)

    def test_route_url_generate_doesnt_receive_query_or_anchor(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        route = DummyRoute(result='')
        mapper = DummyRoutesMapper(route=route)
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.route_url('flub', _query=dict(name='some_name'))
        self.assertEqual(route.kw, {}) # shouldnt have anchor/query
        self.assertEqual(result, 'http://example.com:5432?name=some_name')

    def test_route_url_with_pregenerator(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        route = DummyRoute(result='/1/2/3')
        def pregenerator(request, elements, kw):
            return ('a',), {'_app_url':'http://example2.com'}
        route.pregenerator = pregenerator
        mapper = DummyRoutesMapper(route=route)
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.route_url('flub')
        self.assertEqual(result,  'http://example2.com/1/2/3/a')
        self.assertEqual(route.kw, {}) # shouldnt have anchor/query

    def test_route_url_with_anchor_app_url_elements_and_query(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        mapper = DummyRoutesMapper(route=DummyRoute(result='/1/2/3'))
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.route_url('flub', 'element1',
                                   _app_url='http://example2.com',
                                   _anchor='anchor', _query={'q':'1'})
        self.assertEqual(result,
                         'http://example2.com/1/2/3/element1?q=1#anchor')

    def test_route_url_integration_with_real_request(self):
        # to try to replicate https://github.com/Pylons/pyramid/issues/213
        from pyramid.interfaces import IRoutesMapper
        from pyramid.request import Request
        request = Request.blank('/')
        request.registry = self.config.registry
        mapper = DummyRoutesMapper(route=DummyRoute('/1/2/3'))
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.route_url('flub', 'extra1', 'extra2')
        self.assertEqual(result,
                         'http://localhost/1/2/3/extra1/extra2')
        

    def test_current_route_url_current_request_has_no_route(self):
        request = self._makeOne()
        self.assertRaises(ValueError, request.current_route_url)

    def test_current_route_url_with_elements_query_and_anchor(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        route = DummyRoute('/1/2/3')
        mapper = DummyRoutesMapper(route=route)
        request.matched_route = route
        request.matchdict = {}
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.current_route_url('extra1', 'extra2', _query={'a':1},
                                           _anchor=u"foo")
        self.assertEqual(result,
                         'http://example.com:5432/1/2/3/extra1/extra2?a=1#foo')

    def test_current_route_url_with_route_name(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        route = DummyRoute('/1/2/3')
        mapper = DummyRoutesMapper(route=route)
        request.matched_route = route
        request.matchdict = {}
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.current_route_url('extra1', 'extra2', _query={'a':1},
                                           _anchor=u"foo", _route_name='bar')
        self.assertEqual(result,
                         'http://example.com:5432/1/2/3/extra1/extra2?a=1#foo')

    def test_current_route_path(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        route = DummyRoute('/1/2/3')
        mapper = DummyRoutesMapper(route=route)
        request.matched_route = route
        request.matchdict = {}
        request.script_name = '/script_name'
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.current_route_path('extra1', 'extra2', _query={'a':1},
                                            _anchor=u"foo")
        self.assertEqual(result, '/script_name/1/2/3/extra1/extra2?a=1#foo')
        
    def test_route_path_with_elements(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        mapper = DummyRoutesMapper(route=DummyRoute('/1/2/3'))
        request.registry.registerUtility(mapper, IRoutesMapper)
        request.script_name = ''
        result = request.route_path('flub', 'extra1', 'extra2',
                                    a=1, b=2, c=3, _query={'a':1},
                                    _anchor=u"foo")
        self.assertEqual(result, '/1/2/3/extra1/extra2?a=1#foo')

    def test_route_path_with_script_name(self):
        from pyramid.interfaces import IRoutesMapper
        request = self._makeOne()
        request.script_name = '/foo'
        mapper = DummyRoutesMapper(route=DummyRoute('/1/2/3'))
        request.registry.registerUtility(mapper, IRoutesMapper)
        result = request.route_path('flub', 'extra1', 'extra2',
                                    a=1, b=2, c=3, _query={'a':1},
                                    _anchor=u"foo")
        self.assertEqual(result, '/foo/1/2/3/extra1/extra2?a=1#foo')
        
    def test_static_url_staticurlinfo_notfound(self):
        request = self._makeOne()
        self.assertRaises(ValueError, request.static_url, 'static/foo.css')

    def test_static_url_abspath(self):
        from pyramid.interfaces import IStaticURLInfo
        request = self._makeOne()
        info = DummyStaticURLInfo('abc')
        registry = request.registry
        registry.registerUtility(info, IStaticURLInfo)
        abspath = makeabs('static', 'foo.css')
        result = request.static_url(abspath)
        self.assertEqual(result, 'abc')
        self.assertEqual(info.args, ('/static/foo.css', request, {}))
        request = self._makeOne()

    def test_static_url_found_rel(self):
        from pyramid.interfaces import IStaticURLInfo
        request = self._makeOne()
        info = DummyStaticURLInfo('abc')
        request.registry.registerUtility(info, IStaticURLInfo)
        result = request.static_url('static/foo.css')
        self.assertEqual(result, 'abc')
        self.assertEqual(info.args,
                         ('pyramid.tests:static/foo.css', request, {}) )

    def test_static_url_abs(self):
        from pyramid.interfaces import IStaticURLInfo
        request = self._makeOne()
        info = DummyStaticURLInfo('abc')
        request.registry.registerUtility(info, IStaticURLInfo)
        result = request.static_url('pyramid.tests:static/foo.css')
        self.assertEqual(result, 'abc')
        self.assertEqual(info.args,
                         ('pyramid.tests:static/foo.css', request, {}) )

    def test_static_url_found_abs_no_registry_on_request(self):
        from pyramid.interfaces import IStaticURLInfo
        request = self._makeOne()
        registry = request.registry
        info = DummyStaticURLInfo('abc')
        registry.registerUtility(info, IStaticURLInfo)
        del request.registry
        result = request.static_url('pyramid.tests:static/foo.css')
        self.assertEqual(result, 'abc')
        self.assertEqual(info.args,
                         ('pyramid.tests:static/foo.css', request, {}) )

    def test_static_url_abspath_integration_with_staticurlinfo(self):
        import os
        from pyramid.interfaces import IStaticURLInfo
        from pyramid.config.views import StaticURLInfo
        info = StaticURLInfo()
        here = os.path.abspath(os.path.dirname(__file__))
        info.add(self.config, 'absstatic', here)
        request = self._makeOne()
        registry = request.registry
        registry.registerUtility(info, IStaticURLInfo)
        abspath = os.path.join(here, 'test_url.py')
        result = request.static_url(abspath)
        self.assertEqual(result,
                         'http://example.com:5432/absstatic/test_url.py')

    def test_static_path_abspath(self):
        from pyramid.interfaces import IStaticURLInfo
        request = self._makeOne()
        request.script_name = '/foo'
        info = DummyStaticURLInfo('abc')
        registry = request.registry
        registry.registerUtility(info, IStaticURLInfo)
        abspath = makeabs('static', 'foo.css')
        result = request.static_path(abspath)
        self.assertEqual(result, 'abc')
        self.assertEqual(info.args, ('/static/foo.css', request,
                                     {'_app_url':'/foo'})
                         )

    def test_static_path_found_rel(self):
        from pyramid.interfaces import IStaticURLInfo
        request = self._makeOne()
        request.script_name = '/foo'
        info = DummyStaticURLInfo('abc')
        request.registry.registerUtility(info, IStaticURLInfo)
        result = request.static_path('static/foo.css')
        self.assertEqual(result, 'abc')
        self.assertEqual(info.args,
                         ('pyramid.tests:static/foo.css', request,
                          {'_app_url':'/foo'})
                         )

    def test_static_path_abs(self):
        from pyramid.interfaces import IStaticURLInfo
        request = self._makeOne()
        request.script_name = '/foo'
        info = DummyStaticURLInfo('abc')
        request.registry.registerUtility(info, IStaticURLInfo)
        result = request.static_path('pyramid.tests:static/foo.css')
        self.assertEqual(result, 'abc')
        self.assertEqual(info.args,
                         ('pyramid.tests:static/foo.css', request,
                          {'_app_url':'/foo'})
                         )

    def test_static_path(self):
        from pyramid.interfaces import IStaticURLInfo
        request = self._makeOne()
        request.script_name = '/foo'
        info = DummyStaticURLInfo('abc')
        request.registry.registerUtility(info, IStaticURLInfo)
        result = request.static_path('static/foo.css')
        self.assertEqual(result, 'abc')
        self.assertEqual(info.args,
                         ('pyramid.tests:static/foo.css', request,
                          {'_app_url':'/foo'})
                         )

class Test_route_url(unittest.TestCase):
    def _callFUT(self, route_name, request, *elements, **kw):
        from pyramid.url import route_url
        return route_url(route_name, request, *elements, **kw)

    def _makeRequest(self):
        class Request(object):
            def route_url(self, route_name, *elements, **kw):
                self.route_name = route_name
                self.elements = elements
                self.kw = kw
                return 'route url'
        return Request()

    def test_it(self):
        request = self._makeRequest()
        result = self._callFUT('abc', request, 'a', _app_url='')
        self.assertEqual(result, 'route url')
        self.assertEqual(request.route_name, 'abc')
        self.assertEqual(request.elements, ('a',))
        self.assertEqual(request.kw, {'_app_url':''})

class Test_route_path(unittest.TestCase):
    def _callFUT(self, route_name, request, *elements, **kw):
        from pyramid.url import route_path
        return route_path(route_name, request, *elements, **kw)

    def _makeRequest(self):
        class Request(object):
            def route_path(self, route_name, *elements, **kw):
                self.route_name = route_name
                self.elements = elements
                self.kw = kw
                return 'route path'
        return Request()

    def test_it(self):
        request = self._makeRequest()
        result = self._callFUT('abc', request, 'a', _app_url='')
        self.assertEqual(result, 'route path')
        self.assertEqual(request.route_name, 'abc')
        self.assertEqual(request.elements, ('a',))
        self.assertEqual(request.kw, {'_app_url':''})

class Test_resource_url(unittest.TestCase):
    def _callFUT(self, resource, request, *elements, **kw):
        from pyramid.url import resource_url
        return resource_url(resource, request, *elements, **kw)

    def _makeRequest(self):
        class Request(object):
            def resource_url(self, resource, *elements, **kw):
                self.resource = resource
                self.elements = elements
                self.kw = kw
                return 'resource url'
        return Request()

    def test_it(self):
        request = self._makeRequest()
        result = self._callFUT('abc', request, 'a', _app_url='')
        self.assertEqual(result, 'resource url')
        self.assertEqual(request.resource, 'abc')
        self.assertEqual(request.elements, ('a',))
        self.assertEqual(request.kw, {'_app_url':''})

class Test_static_url(unittest.TestCase):
    def _callFUT(self, path, request, **kw):
        from pyramid.url import static_url
        return static_url(path, request, **kw)

    def _makeRequest(self):
        class Request(object):
            def static_url(self, path, **kw):
                self.path = path
                self.kw = kw
                return 'static url'
        return Request()

    def test_it_abs(self):
        request = self._makeRequest()
        result = self._callFUT('/foo/bar/abc', request, _app_url='')
        self.assertEqual(result, 'static url')
        self.assertEqual(request.path, '/foo/bar/abc')
        self.assertEqual(request.kw, {'_app_url':''})

    def test_it_absspec(self):
        request = self._makeRequest()
        result = self._callFUT('foo:abc', request, _anchor='anchor')
        self.assertEqual(result, 'static url')
        self.assertEqual(request.path, 'foo:abc')
        self.assertEqual(request.kw, {'_anchor':'anchor'})

    def test_it_rel(self):
        request = self._makeRequest()
        result = self._callFUT('abc', request, _app_url='')
        self.assertEqual(result, 'static url')
        self.assertEqual(request.path, 'pyramid.tests:abc')
        self.assertEqual(request.kw, {'_app_url':''})

class Test_static_path(unittest.TestCase):
    def _callFUT(self, path, request, **kw):
        from pyramid.url import static_path
        return static_path(path, request, **kw)

    def _makeRequest(self):
        class Request(object):
            def static_path(self, path, **kw):
                self.path = path
                self.kw = kw
                return 'static path'
        return Request()

    def test_it_abs(self):
        request = self._makeRequest()
        result = self._callFUT('/foo/bar/abc', request, _anchor='anchor')
        self.assertEqual(result, 'static path')
        self.assertEqual(request.path, '/foo/bar/abc')
        self.assertEqual(request.kw, {'_anchor':'anchor'})

    def test_it_absspec(self):
        request = self._makeRequest()
        result = self._callFUT('foo:abc', request, _anchor='anchor')
        self.assertEqual(result, 'static path')
        self.assertEqual(request.path, 'foo:abc')
        self.assertEqual(request.kw, {'_anchor':'anchor'})

    def test_it_rel(self):
        request = self._makeRequest()
        result = self._callFUT('abc', request, _app_url='')
        self.assertEqual(result, 'static path')
        self.assertEqual(request.path, 'pyramid.tests:abc')
        self.assertEqual(request.kw, {'_app_url':''})

class Test_current_route_url(unittest.TestCase):
    def _callFUT(self, request, *elements, **kw):
        from pyramid.url import current_route_url
        return current_route_url(request, *elements, **kw)

    def _makeRequest(self):
        class Request(object):
            def current_route_url(self, *elements, **kw):
                self.elements = elements
                self.kw = kw
                return 'current route url'
        return Request()

    def test_it(self):
        request = self._makeRequest()
        result = self._callFUT(request, 'abc', _app_url='')
        self.assertEqual(result, 'current route url')
        self.assertEqual(request.elements, ('abc',))
        self.assertEqual(request.kw, {'_app_url':''})

class Test_current_route_path(unittest.TestCase):
    def _callFUT(self, request, *elements, **kw):
        from pyramid.url import current_route_path
        return current_route_path(request, *elements, **kw)

    def _makeRequest(self):
        class Request(object):
            def current_route_path(self, *elements, **kw):
                self.elements = elements
                self.kw = kw
                return 'current route path'
        return Request()

    def test_it(self):
        request = self._makeRequest()
        result = self._callFUT(request, 'abc', _anchor='abc')
        self.assertEqual(result, 'current route path')
        self.assertEqual(request.elements, ('abc',))
        self.assertEqual(request.kw, {'_anchor':'abc'})

class DummyContext(object):
    def __init__(self, next=None):
        self.next = next
        
class DummyRoutesMapper:
    raise_exc = None
    def __init__(self, route=None, raise_exc=False):
        self.route = route

    def get_route(self, route_name):
        return self.route

class DummyRoute:
    pregenerator = None
    name = 'route'
    def __init__(self, result='/1/2/3'):
        self.result = result

    def generate(self, kw):
        self.kw = kw
        return self.result
    
class DummyStaticURLInfo:
    def __init__(self, result):
        self.result = result

    def generate(self, path, request, **kw):
        self.args = path, request, kw
        return self.result
    
def makeabs(*elements):
    import os
    return os.path.sep + os.path.sep.join(elements)
