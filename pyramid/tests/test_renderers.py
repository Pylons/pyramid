import unittest

from pyramid.testing import cleanUp
from pyramid import testing

class TestTemplateRendererFactory(unittest.TestCase):
    def setUp(self):
        self.config = cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, info, impl):
        from pyramid.renderers import template_renderer_factory
        return template_renderer_factory(info, impl)

    def test_lookup_found(self):
        from pyramid.interfaces import IChameleonLookup
        L = []
        def dummy(info):
            L.append(info)
            return True
        self.config.registry.registerUtility(dummy, IChameleonLookup,
                                             name='abc')
        class DummyInfo(object):
            pass
        info = DummyInfo()
        info.registry = self.config.registry
        info.type = 'abc'
        result = self._callFUT(info, None)
        self.assertEqual(result, True)
        self.assertEqual(L, [info])

    def test_lookup_miss(self):
        from pyramid.interfaces import ITemplateRenderer
        import os
        abspath = os.path.abspath(__file__)
        renderer = {}
        self.config.registry.registerUtility(
            renderer, ITemplateRenderer, name=abspath)
        info = DummyRendererInfo({
            'name':abspath,
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            'type':'type',
            })
        result = self._callFUT(info, None)
        self.assertTrue(result is renderer)

class TestChameleonRendererLookup(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self, impl):
        from pyramid.renderers import ChameleonRendererLookup
        return ChameleonRendererLookup(impl, self.config.registry)

    def _registerTemplateRenderer(self, renderer, name):
        from pyramid.interfaces import ITemplateRenderer
        self.config.registry.registerUtility(
            renderer, ITemplateRenderer, name=name)

    def test_get_spec_not_abspath_no_colon_no_package(self):
        lookup = self._makeOne(None)
        result = lookup.get_spec('foo', None)
        self.assertEqual(result, 'foo')

    def test_get_spec_not_abspath_no_colon_with_package(self):
        from pyramid import tests
        lookup = self._makeOne(None)
        result = lookup.get_spec('foo', tests)
        self.assertEqual(result, 'pyramid.tests:foo')

    def test_get_spec_not_abspath_with_colon_no_package(self):
        lookup = self._makeOne(None)
        result = lookup.get_spec('fudge:foo', None)
        self.assertEqual(result, 'fudge:foo')

    def test_get_spec_not_abspath_with_colon_with_package(self):
        from pyramid import tests
        lookup = self._makeOne(None)
        result = lookup.get_spec('fudge:foo', tests)
        self.assertEqual(result, 'fudge:foo')

    def test_get_spec_is_abspath_no_colon_no_package(self):
        import os
        lookup = self._makeOne(None)
        spec = os.path.abspath(__file__)
        result = lookup.get_spec(spec, None)
        self.assertEqual(result, spec)

    def test_get_spec_is_abspath_no_colon_with_path_in_package(self):
        from pyramid import tests
        import os
        lookup = self._makeOne(None)
        f = __file__
        spec = os.path.abspath(f)
        result = lookup.get_spec(spec, tests)
        self.assertEqual(result, 'pyramid.tests:%s' % os.path.split(f)[-1])

    def test_get_spec_is_abspath_no_colon_with_path_outside_package(self):
        import venusian # used only because it's outside of pyramid.tests
        import os
        lookup = self._makeOne(None)
        f = __file__
        spec = os.path.abspath(f)
        result = lookup.get_spec(spec, venusian)
        self.assertEqual(result, spec)

    def test_get_spec_is_abspath_with_colon_no_package(self):
        import os
        lookup = self._makeOne(None)
        spec = os.path.join(os.path.abspath(__file__), ':foo')
        result = lookup.get_spec(spec, None)
        self.assertEqual(result, spec)

    def test_get_spec_is_abspath_with_colon_with_path_in_package(self):
        from pyramid import tests
        import os
        lookup = self._makeOne(None)
        f = os.path.abspath(__file__)
        spec = os.path.join(f, ':foo')
        result = lookup.get_spec(spec, tests)
        tail = spec.split(os.sep)[-2:]
        self.assertEqual(result, 'pyramid.tests:%s/%s' % tuple(tail))

    def test_get_spec_is_abspath_with_colon_with_path_outside_package(self):
        import venusian # used only because it's outside of pyramid.tests
        import os
        lookup = self._makeOne(None)
        spec = os.path.join(os.path.abspath(__file__), ':foo')
        result = lookup.get_spec(spec, venusian)
        self.assertEqual(result, spec)

    def test_translate(self):
        from pyramid.interfaces import IChameleonTranslate
        def t(): pass
        self.config.registry.registerUtility(t, IChameleonTranslate)
        lookup = self._makeOne(None)
        self.assertEqual(lookup.translate, t)

    def test_debug_settings_None(self):
        self.config.registry.settings = None
        lookup = self._makeOne(None)
        self.assertEqual(lookup.debug, False)

    def test_debug_settings_not_None(self):
        self.config.registry.settings = {'debug_templates':True}
        lookup = self._makeOne(None)
        self.assertEqual(lookup.debug, True)

    def test_auto_reload_settings_None(self):
        self.config.registry.settings = None
        lookup = self._makeOne(None)
        self.assertEqual(lookup.auto_reload, False)

    def test_auto_reload_settings_not_None(self):
        self.config.registry.settings = {'reload_templates':True}
        lookup = self._makeOne(None)
        self.assertEqual(lookup.auto_reload, True)

    def test___call__abspath_path_notexists(self):
        abspath = '/wont/exist'
        self._registerTemplateRenderer({}, abspath)
        info = DummyRendererInfo({
            'name':abspath,
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            'type':'type',
            })
        lookup = self._makeOne(None)
        self.assertRaises(ValueError, lookup.__call__, info)

    def test___call__abspath_alreadyregistered(self):
        import os
        abspath = os.path.abspath(__file__)
        renderer = {}
        self._registerTemplateRenderer(renderer, abspath)
        info = DummyRendererInfo({
            'name':abspath,
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            'type':'type',
            })
        lookup = self._makeOne(None)
        result = lookup(info)
        self.assertTrue(result is renderer)

    def test___call__abspath_notyetregistered(self):
        import os
        abspath = os.path.abspath(__file__)
        renderer = {}
        factory = DummyFactory(renderer)
        info = DummyRendererInfo({
            'name':abspath,
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            'type':'type',
            })
        lookup = self._makeOne(factory)
        result = lookup(info)
        self.assertEqual(result, renderer)

    def test___call__relpath_path_registered(self):
        renderer = {}
        spec = 'foo/bar'
        self._registerTemplateRenderer(renderer, spec)
        info = DummyRendererInfo({
            'name':spec,
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            'type':'type',
            })
        lookup = self._makeOne(None)
        result = lookup(info)
        self.assertTrue(renderer is result)

    def test___call__relpath_has_package_registered(self):
        renderer = {}
        import pyramid.tests
        spec = 'bar/baz'
        self._registerTemplateRenderer(renderer, 'pyramid.tests:bar/baz')
        info = DummyRendererInfo({
            'name':spec,
            'package':pyramid.tests,
            'registry':self.config.registry,
            'settings':{},
            'type':'type',
            })
        lookup = self._makeOne(None)
        result = lookup(info)
        self.assertTrue(renderer is result)

    def test___call__spec_notfound(self):
        spec = 'pyramid.tests:wont/exist'
        info = DummyRendererInfo({
            'name':spec,
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            'type':'type',
            })
        lookup = self._makeOne(None)
        self.assertRaises(ValueError, lookup.__call__, info)

    def test___call__spec_alreadyregistered(self):
        from pyramid import tests
        module_name = tests.__name__
        relpath = 'test_renderers.py'
        spec = '%s:%s' % (module_name, relpath)
        info = DummyRendererInfo({
            'name':spec,
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            'type':'type',
            })
        renderer = {}
        self._registerTemplateRenderer(renderer, spec)
        lookup = self._makeOne(None)
        result = lookup(info)
        self.assertTrue(result is renderer)

    def test___call__spec_notyetregistered(self):
        import os
        from pyramid import tests
        module_name = tests.__name__
        relpath = 'test_renderers.py'
        renderer = {}
        factory = DummyFactory(renderer)
        spec = '%s:%s' % (module_name, relpath)
        info = DummyRendererInfo({
            'name':spec,
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            'type':'type',
            })
        lookup = self._makeOne(factory)
        result = lookup(info)
        self.assertTrue(result is renderer)
        path = os.path.abspath(__file__).split('$')[0] # jython
        if path.endswith('.pyc'): # pragma: no cover
            path = path[:-1]
        self.assertTrue(factory.path.startswith(path))
        self.assertEqual(factory.kw, {})

    def test___call__reload_assets_true(self):
        import pyramid.tests
        from pyramid.interfaces import ISettings
        from pyramid.interfaces import ITemplateRenderer
        settings = {'reload_assets':True}
        self.config.registry.registerUtility(settings, ISettings)
        renderer = {}
        factory = DummyFactory(renderer)
        spec = 'test_renderers.py'
        reg = self.config.registry
        info = DummyRendererInfo({
            'name':spec,
            'package':pyramid.tests,
            'registry':reg,
            'settings':settings,
            'type':'type',
            })
        lookup = self._makeOne(factory)
        result = lookup(info)
        self.assertTrue(result is renderer)
        spec = '%s:%s' % ('pyramid.tests', 'test_renderers.py')
        self.assertEqual(reg.queryUtility(ITemplateRenderer, name=spec),
                         None)

    def test___call__reload_assets_false(self):
        import pyramid.tests
        from pyramid.interfaces import ITemplateRenderer
        settings = {'reload_assets':False}
        renderer = {}
        factory = DummyFactory(renderer)
        spec = 'test_renderers.py'
        reg = self.config.registry
        info = DummyRendererInfo({
            'name':spec,
            'package':pyramid.tests,
            'registry':reg,
            'settings':settings,
            'type':'type',
            })
        lookup = self._makeOne(factory)
        result = lookup(info)
        self.assertTrue(result is renderer)
        spec = '%s:%s' % ('pyramid.tests', 'test_renderers.py')
        self.assertNotEqual(reg.queryUtility(ITemplateRenderer, name=spec),
                            None)

class TestRendererFromName(unittest.TestCase):
    def setUp(self):
        from zope.deprecation import __show__
        __show__.off()
        self.config = cleanUp()

    def tearDown(self):
        cleanUp()
        from zope.deprecation import __show__
        __show__.on()

    def _callFUT(self, path, package=None):
        from pyramid.renderers import renderer_from_name
        return renderer_from_name(path, package)

    def test_it(self):
        registry = self.config.registry
        settings = {}
        registry.settings = settings
        from pyramid.interfaces import IRendererFactory
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        fixture = os.path.join(here, 'fixtures/minimal.pt')
        def factory(info, **kw):
            return info
        self.config.registry.registerUtility(
            factory, IRendererFactory, name='.pt')
        result = self._callFUT(fixture)
        self.assertEqual(result.registry, registry)
        self.assertEqual(result.type, '.pt')
        self.assertEqual(result.package, None)
        self.assertEqual(result.name, fixture)
        self.assertEqual(result.settings, settings)

    def test_it_with_package(self):
        import pyramid
        registry = self.config.registry
        settings = {}
        registry.settings = settings
        from pyramid.interfaces import IRendererFactory
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        fixture = os.path.join(here, 'fixtures/minimal.pt')
        def factory(info, **kw):
            return info
        self.config.registry.registerUtility(
            factory, IRendererFactory, name='.pt')
        result = self._callFUT(fixture, pyramid)
        self.assertEqual(result.registry, registry)
        self.assertEqual(result.type, '.pt')
        self.assertEqual(result.package, pyramid)
        self.assertEqual(result.name, fixture)
        self.assertEqual(result.settings, settings)

    def test_it_no_renderer(self):
        self.assertRaises(ValueError, self._callFUT, 'foo')
        

class Test_json_renderer_factory(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _callFUT(self, name):
        from pyramid.renderers import json_renderer_factory
        return json_renderer_factory(name)

    def test_it(self):
        renderer = self._callFUT(None)
        result = renderer({'a':1}, {})
        self.assertEqual(result, '{"a": 1}')

    def test_with_request_content_type_notset(self):
        request = testing.DummyRequest()
        renderer = self._callFUT(None)
        renderer({'a':1}, {'request':request})
        self.assertEqual(request.response.content_type, 'application/json')

    def test_with_request_content_type_set(self):
        request = testing.DummyRequest()
        request.response.content_type = 'text/mishmash'
        renderer = self._callFUT(None)
        renderer({'a':1}, {'request':request})
        self.assertEqual(request.response.content_type, 'text/mishmash')

class Test_string_renderer_factory(unittest.TestCase):
    def _callFUT(self, name):
        from pyramid.renderers import string_renderer_factory
        return string_renderer_factory(name)

    def test_it_unicode(self):
        renderer = self._callFUT(None)
        value = unicode('La Pe\xc3\xb1a', 'utf-8')
        result = renderer(value, {})
        self.assertEqual(result, value)
                          
    def test_it_str(self):
        renderer = self._callFUT(None)
        value = 'La Pe\xc3\xb1a'
        result = renderer(value, {})
        self.assertEqual(result, value)

    def test_it_other(self):
        renderer = self._callFUT(None)
        value = None
        result = renderer(value, {})
        self.assertEqual(result, 'None')

    def test_with_request_content_type_notset(self):
        request = testing.DummyRequest()
        renderer = self._callFUT(None)
        renderer(None, {'request':request})
        self.assertEqual(request.response.content_type, 'text/plain')

    def test_with_request_content_type_set(self):
        request = testing.DummyRequest()
        request.response.content_type = 'text/mishmash'
        renderer = self._callFUT(None)
        renderer(None, {'request':request})
        self.assertEqual(request.response.content_type, 'text/mishmash')


class TestRendererHelper(unittest.TestCase):
    def setUp(self):
        self.config = cleanUp()

    def tearDown(self):
        cleanUp()

    def _makeOne(self, *arg, **kw):
        from pyramid.renderers import RendererHelper
        return RendererHelper(*arg, **kw)

    def test_instance_conforms(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IRendererInfo
        helper = self._makeOne()
        verifyObject(IRendererInfo, helper)

    def test_settings_registry_settings_is_None(self):
        class Dummy(object):
            settings = None
        helper = self._makeOne(registry=Dummy)
        self.assertEqual(helper.settings, {})

    def test_settings_registry_name_is_None(self):
        class Dummy(object):
            settings = None
        helper = self._makeOne(registry=Dummy)
        self.assertEqual(helper.name, None)
        self.assertEqual(helper.type, '')

    def test_settings_registry_settings_is_not_None(self):
        class Dummy(object):
            settings = {'a':1}
        helper = self._makeOne(registry=Dummy)
        self.assertEqual(helper.settings, {'a':1})

    def _registerRendererFactory(self):
        from pyramid.interfaces import IRendererFactory
        def renderer(*arg):
            def respond(*arg):
                return arg
            return respond
        self.config.registry.registerUtility(renderer, IRendererFactory,
                                             name='.foo')
        return renderer

    def _registerResponseFactory(self):
        from pyramid.interfaces import IResponseFactory
        class ResponseFactory(object):
            pass
        self.config.registry.registerUtility(ResponseFactory, IResponseFactory)

    def test_render_to_response(self):
        self._registerRendererFactory()
        self._registerResponseFactory()
        request = Dummy()
        helper = self._makeOne('loo.foo')
        response = helper.render_to_response('values', {},
                                             request=request)
        self.assertEqual(response.body[0], 'values')
        self.assertEqual(response.body[1], {})

    def test_render_view(self):
        self._registerRendererFactory()
        self._registerResponseFactory()
        request = Dummy()
        helper = self._makeOne('loo.foo')
        view = 'view'
        context = 'context'
        request = testing.DummyRequest()
        response = 'response'
        response = helper.render_view(request, response, view, context)
        self.assertEqual(response.body[0], 'response')
        self.assertEqual(response.body[1],
                          {'renderer_info': helper,
                           'renderer_name': 'loo.foo',
                           'request': request,
                           'context': 'context',
                           'view': 'view'}
                         )

    def test_render_explicit_registry(self):
        factory = self._registerRendererFactory()
        class DummyRegistry(object):
            def __init__(self):
                self.responses = [factory, lambda *arg: {}, None]
            def queryUtility(self, iface, name=None):
                self.queried = True
                return self.responses.pop(0)
            def notify(self, event):
                self.event = event
        reg = DummyRegistry()
        helper = self._makeOne('loo.foo', registry=reg)
        result = helper.render('value', {})
        self.assertEqual(result[0], 'value')
        self.assertEqual(result[1], {})
        self.assertTrue(reg.queried)
        self.assertEqual(reg.event, {})
        self.assertEqual(reg.event.__class__.__name__, 'BeforeRender')

    def test_render_system_values_is_None(self):
        self._registerRendererFactory()
        request = Dummy()
        context = Dummy()
        request.context = context
        helper = self._makeOne('loo.foo')
        result = helper.render('values', None, request=request)
        system = {'request':request,
                  'context':context,
                  'renderer_name':'loo.foo',
                  'view':None,
                  'renderer_info':helper
                  }
        self.assertEqual(result[0], 'values')
        self.assertEqual(result[1], system)

    def test_render_renderer_globals_factory_active(self):
        self._registerRendererFactory()
        from pyramid.interfaces import IRendererGlobalsFactory
        def rg(system):
            return {'a':1}
        self.config.registry.registerUtility(rg, IRendererGlobalsFactory)
        helper = self._makeOne('loo.foo')
        result = helper.render('values', None)
        self.assertEqual(result[1]['a'], 1)

    def test__make_response_request_is_None(self):
        request = None
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.body, 'abc')

    def test__make_response_request_is_None_response_factory_exists(self):
        self._registerResponseFactory()
        request = None
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.__class__.__name__, 'ResponseFactory')
        self.assertEqual(response.body, 'abc')

    def test__make_response_result_is_unicode(self):
        from pyramid.response import Response
        request = testing.DummyRequest()
        request.response = Response()
        helper = self._makeOne('loo.foo')
        la = unicode('/La Pe\xc3\xb1a', 'utf-8')
        response = helper._make_response(la, request)
        self.assertEqual(response.body, la.encode('utf-8'))

    def test__make_response_result_is_str(self):
        from pyramid.response import Response
        request = testing.DummyRequest()
        request.response = Response()
        helper = self._makeOne('loo.foo')
        la = unicode('/La Pe\xc3\xb1a', 'utf-8')
        response = helper._make_response(la.encode('utf-8'), request)
        self.assertEqual(response.body, la.encode('utf-8'))

    def test__make_response_with_content_type(self):
        from pyramid.response import Response
        request = testing.DummyRequest()
        request.response = Response()
        attrs = {'_response_content_type':'text/nonsense'}
        request.__dict__.update(attrs)
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.content_type, 'text/nonsense')
        self.assertEqual(response.body, 'abc')

    def test__make_response_with_headerlist(self):
        from pyramid.response import Response
        request = testing.DummyRequest()
        request.response = Response()
        attrs = {'_response_headerlist':[('a', '1'), ('b', '2')]}
        request.__dict__.update(attrs)
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.headerlist,
                         [('Content-Type', 'text/html; charset=UTF-8'),
                          ('Content-Length', '3'),
                          ('a', '1'),
                          ('b', '2')])
        self.assertEqual(response.body, 'abc')

    def test__make_response_with_status(self):
        from pyramid.response import Response
        request = testing.DummyRequest()
        request.response = Response()
        attrs = {'_response_status':'406 You Lose'}
        request.__dict__.update(attrs)
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.status, '406 You Lose')
        self.assertEqual(response.body, 'abc')

    def test__make_response_with_charset(self):
        from pyramid.response import Response
        request = testing.DummyRequest()
        request.response = Response()
        attrs = {'_response_charset':'UTF-16'}
        request.__dict__.update(attrs)
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.charset, 'UTF-16')

    def test__make_response_with_cache_for(self):
        from pyramid.response import Response
        request = testing.DummyRequest()
        request.response = Response()
        attrs = {'_response_cache_for':100}
        request.__dict__.update(attrs)
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.cache_control.max_age, 100)

    def test_with_alternate_response_factory(self):
        from pyramid.interfaces import IResponseFactory
        class ResponseFactory(object):
            def __init__(self):
                pass
        self.config.registry.registerUtility(ResponseFactory, IResponseFactory)
        request = testing.DummyRequest()
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.__class__, ResponseFactory)
        self.assertEqual(response.body, 'abc')

    def test__make_response_with_real_request(self):
        # functional
        from pyramid.request import Request
        request = Request({})
        request.registry = self.config.registry
        request.response.status = '406 You Lose'
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.status, '406 You Lose')
        self.assertEqual(response.body, 'abc')

    def test_clone_noargs(self):
        helper = self._makeOne('name', 'package', 'registry')
        cloned_helper = helper.clone()
        self.assertEqual(cloned_helper.name, 'name')
        self.assertEqual(cloned_helper.package, 'package')
        self.assertEqual(cloned_helper.registry, 'registry')
        self.assertFalse(helper is cloned_helper)

    def test_clone_allargs(self):
        helper = self._makeOne('name', 'package', 'registry')
        cloned_helper = helper.clone(name='name2', package='package2',
                                     registry='registry2')
        self.assertEqual(cloned_helper.name, 'name2')
        self.assertEqual(cloned_helper.package, 'package2')
        self.assertEqual(cloned_helper.registry, 'registry2')
        self.assertFalse(helper is cloned_helper)

class TestNullRendererHelper(unittest.TestCase):
    def setUp(self):
        self.config = cleanUp()

    def tearDown(self):
        cleanUp()

    def _makeOne(self, *arg, **kw):
        from pyramid.renderers import NullRendererHelper
        return NullRendererHelper(*arg, **kw)

    def test_instance_conforms(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IRendererInfo
        helper = self._makeOne()
        verifyObject(IRendererInfo, helper)

    def test_render_view(self):
        helper = self._makeOne()
        self.assertEqual(helper.render_view(None, True, None, None), True)

    def test_render(self):
        helper = self._makeOne()
        self.assertEqual(helper.render(True, None, None), True)

    def test_render_to_response(self):
        helper = self._makeOne()
        self.assertEqual(helper.render_to_response(True, None, None), True)

    def test_clone(self):
        helper = self._makeOne()
        self.assertTrue(helper.clone() is helper)

class Test_render(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, renderer_name, value, request=None, package=None):
        from pyramid.renderers import render
        return render(renderer_name, value, request=request, package=package)

    def test_it_no_request(self):
        renderer = self.config.testing_add_renderer(
            'pyramid.tests:abc/def.pt')
        renderer.string_response = 'abc'
        result = self._callFUT('abc/def.pt', dict(a=1))
        self.assertEqual(result, 'abc')
        renderer.assert_(a=1)
        renderer.assert_(request=None)
        
    def test_it_with_request(self):
        renderer = self.config.testing_add_renderer(
            'pyramid.tests:abc/def.pt')
        renderer.string_response = 'abc'
        request = testing.DummyRequest()
        result = self._callFUT('abc/def.pt',
                               dict(a=1), request=request)
        self.assertEqual(result, 'abc')
        renderer.assert_(a=1)
        renderer.assert_(request=request)

    def test_it_with_package(self):
        import pyramid.tests
        renderer = self.config.testing_add_renderer(
            'pyramid.tests:abc/def.pt')
        renderer.string_response = 'abc'
        request = testing.DummyRequest()
        result = self._callFUT('abc/def.pt', dict(a=1), request=request,
                               package=pyramid.tests)
        self.assertEqual(result, 'abc')
        renderer.assert_(a=1)
        renderer.assert_(request=request)

class Test_render_to_response(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, renderer_name, value, request=None, package=None):
        from pyramid.renderers import render_to_response
        return render_to_response(renderer_name, value, request=request,
                                  package=package)

    def test_it_no_request(self):
        renderer = self.config.testing_add_renderer(
            'pyramid.tests:abc/def.pt')
        renderer.string_response = 'abc'
        response = self._callFUT('abc/def.pt', dict(a=1))
        self.assertEqual(response.body, 'abc')
        renderer.assert_(a=1)
        renderer.assert_(request=None)
        
    def test_it_with_request(self):
        renderer = self.config.testing_add_renderer(
            'pyramid.tests:abc/def.pt')
        renderer.string_response = 'abc'
        request = testing.DummyRequest()
        response = self._callFUT('abc/def.pt',
                                 dict(a=1), request=request)
        self.assertEqual(response.body, 'abc')
        renderer.assert_(a=1)
        renderer.assert_(request=request)

    def test_it_with_package(self):
        import pyramid.tests
        renderer = self.config.testing_add_renderer(
            'pyramid.tests:abc/def.pt')
        renderer.string_response = 'abc'
        request = testing.DummyRequest()
        response = self._callFUT('abc/def.pt', dict(a=1), request=request,
                                 package=pyramid.tests)
        self.assertEqual(response.body, 'abc')
        renderer.assert_(a=1)
        renderer.assert_(request=request)

class Test_get_renderer(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, renderer_name, **kw):
        from pyramid.renderers import get_renderer
        return get_renderer(renderer_name, **kw)

    def test_it_no_package(self):
        renderer = self.config.testing_add_renderer(
            'pyramid.tests:abc/def.pt')
        result = self._callFUT('abc/def.pt')
        self.assertEqual(result, renderer)

    def test_it_with_package(self):
        import pyramid.tests
        renderer = self.config.testing_add_renderer(
            'pyramid.tests:abc/def.pt')
        result = self._callFUT('abc/def.pt', package=pyramid.tests)
        self.assertEqual(result, renderer)

class TestJSONP(unittest.TestCase):
    def _makeOne(self, param_name='callback'):
        from pyramid.renderers import JSONP
        return JSONP(param_name)

    def test_render_to_jsonp(self):
        renderer_factory = self._makeOne()
        renderer = renderer_factory(None)
        request = testing.DummyRequest()
        request.GET['callback'] = 'callback'
        result = renderer({'a':'1'}, {'request':request})
        self.assertEqual(result, 'callback({"a": "1"})')
        self.assertEqual(request.response.content_type,
                         'application/javascript')

    def test_render_to_json(self):
        renderer_factory = self._makeOne()
        renderer = renderer_factory(None)
        request = testing.DummyRequest()
        result = renderer({'a':'1'}, {'request':request})
        self.assertEqual(result, '{"a": "1"}')
        self.assertEqual(request.response.content_type,
                         'application/json')


class Dummy:
    pass

class DummyResponse:
    status = '200 OK'
    headerlist = ()
    app_iter = ()
    body = ''

class DummyFactory:
    def __init__(self, renderer):
        self.renderer = renderer

    def __call__(self, path, lookup, **kw):
        self.path = path
        self.kw = kw
        return self.renderer
    

class DummyRendererInfo(object):
    def __init__(self, kw):
        self.__dict__.update(kw)
        
