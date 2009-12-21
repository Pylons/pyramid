import unittest

from repoze.bfg.testing import cleanUp
from repoze.bfg import testing

class TestTemplateRendererFactory(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, path, factory):
        from repoze.bfg.renderers import template_renderer_factory
        return template_renderer_factory(path, factory)

    def test_abspath_notfound(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        abspath = '/wont/exist'
        testing.registerUtility({}, ITemplateRenderer, name=abspath)
        self.assertRaises(ValueError, self._callFUT, abspath, None)

    def test_abspath_alreadyregistered(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        import os
        abspath = os.path.abspath(__file__)
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=abspath)
        result = self._callFUT(abspath, None)
        self.failUnless(result is renderer)

    def test_abspath_notyetregistered(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        import os
        abspath = os.path.abspath(__file__)
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=abspath)
        result = self._callFUT(abspath, None)
        self.failUnless(result is renderer)

    def test_relpath_path_registered(self):
        renderer = {}
        from repoze.bfg.interfaces import ITemplateRenderer
        testing.registerUtility(renderer, ITemplateRenderer, name='foo/bar')
        result = self._callFUT('foo/bar', None)
        self.failUnless(renderer is result)

    def test_relpath_is_package_registered(self):
        renderer = {}
        from repoze.bfg.interfaces import ITemplateRenderer
        testing.registerUtility(renderer, ITemplateRenderer, name='foo:bar/baz')
        result = self._callFUT('foo:bar/baz', None)
        self.failUnless(renderer is result)

    def test_spec_notfound(self):
        self.assertRaises(ValueError, self._callFUT,
                          'repoze.bfg.tests:wont/exist', None)

    def test_spec_alreadyregistered(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        from repoze.bfg import tests
        module_name = tests.__name__
        relpath = 'test_renderers.py'
        spec = '%s:%s' % (module_name, relpath)
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=spec)
        result = self._callFUT(spec, None)
        self.failUnless(result is renderer)

    def test_spec_notyetregistered(self):
        import os
        from repoze.bfg import tests
        module_name = tests.__name__
        relpath = 'test_renderers.py'
        renderer = {}
        factory = DummyFactory(renderer)
        spec = '%s:%s' % (module_name, relpath)
        result = self._callFUT(spec, factory)
        self.failUnless(result is renderer)
        path = os.path.abspath(__file__)
        if path.endswith('pyc'): # pragma: no cover
            path = path[:-1]
        self.assertEqual(factory.path, path)
        self.assertEqual(factory.kw, {})

    def test_reload_resources_true(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ITemplateRenderer
        settings = {'reload_resources':True}
        testing.registerUtility(settings, ISettings)
        renderer = {}
        factory = DummyFactory(renderer)
        result = self._callFUT('repoze.bfg.tests:test_renderers.py', factory)
        self.failUnless(result is renderer)
        spec = '%s:%s' % ('repoze.bfg.tests', 'test_renderers.py')
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, name=spec),
                         None)

    def test_reload_resources_false(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ITemplateRenderer
        settings = {'reload_resources':False}
        testing.registerUtility(settings, ISettings)
        renderer = {}
        factory = DummyFactory(renderer)
        result = self._callFUT('repoze.bfg.tests:test_renderers.py', factory)
        self.failUnless(result is renderer)
        spec = '%s:%s' % ('repoze.bfg.tests', 'test_renderers.py')
        reg = get_current_registry()
        self.assertNotEqual(reg.queryUtility(ITemplateRenderer, name=spec),
                            None)

class TestRendererFromName(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, path):
        from repoze.bfg.renderers import renderer_from_name
        return renderer_from_name(path)

    def test_it(self):
        from repoze.bfg.interfaces import IRendererFactory
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        fixture = os.path.join(here, 'fixtures/minimal.pt')
        renderer = {}
        def factory(path, **kw):
            return renderer
        testing.registerUtility(factory, IRendererFactory, name='.pt')
        result = self._callFUT(fixture)
        self.assertEqual(result, renderer)

    def test_it_no_renderer(self):
        self.assertRaises(ValueError, self._callFUT, 'foo')
        

class Test_json_renderer_factory(unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.renderers import json_renderer_factory
        return json_renderer_factory(name)

    def test_it(self):
        renderer = self._callFUT(None)
        result = renderer({'a':1}, {})
        self.assertEqual(result, '{"a": 1}')

    def test_with_request_content_type_notset(self):
        request = testing.DummyRequest()
        renderer = self._callFUT(None)
        renderer({'a':1}, {'request':request})
        self.assertEqual(request.response_content_type, 'application/json')

    def test_with_request_content_type_set(self):
        request = testing.DummyRequest()
        request.response_content_type = 'text/mishmash'
        renderer = self._callFUT(None)
        renderer({'a':1}, {'request':request})
        self.assertEqual(request.response_content_type, 'text/mishmash')

class Test_string_renderer_factory(unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.renderers import string_renderer_factory
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
        self.assertEqual(request.response_content_type, 'text/plain')

    def test_with_request_content_type_set(self):
        request = testing.DummyRequest()
        request.response_content_type = 'text/mishmash'
        renderer = self._callFUT(None)
        renderer(None, {'request':request})
        self.assertEqual(request.response_content_type, 'text/mishmash')

class DummyFactory:
    def __init__(self, renderer):
        self.renderer = renderer

    def __call__(self, path, **kw):
        self.path = path
        self.kw = kw
        return self.renderer
    

