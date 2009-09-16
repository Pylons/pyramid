import unittest

from repoze.bfg.testing import cleanUp
from repoze.bfg import testing

class TestTemplateRendererFactory(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, path, factory, level=3):
        from repoze.bfg.renderers import template_renderer_factory
        return template_renderer_factory(path, factory, level)

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

    def test_relpath_notfound(self):
        self.assertRaises(ValueError, self._callFUT, 'wont/exist', None)

    def test_relpath_is_package_notfound(self):
        from repoze.bfg import tests
        module_name = tests.__name__
        self.assertRaises(ValueError, self._callFUT,
                          '%s:wont/exist' % module_name, None)

    def test_relpath_alreadyregistered(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        from repoze.bfg import tests
        module_name = tests.__name__
        relpath = 'test_renderers.py'
        spec = '%s:%s' % (module_name, relpath)
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=spec)
        result = self._callFUT('test_renderers.py', None)
        self.failUnless(result is renderer)

    def test_relpath_is_package_alreadyregistered(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        from repoze.bfg import tests
        module_name = tests.__name__
        relpath = 'test_renderers.py'
        spec = '%s:%s' % (module_name, relpath)
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=spec)
        result = self._callFUT(spec, None)
        self.failUnless(result is renderer)

    def test_relpath_notyetregistered(self):
        import os
        from repoze.bfg.tests import test_renderers
        module_name = test_renderers.__name__
        relpath = 'test_renderers.py'
        renderer = {}
        factory = DummyFactory(renderer)
        result = self._callFUT('test_renderers.py', factory)
        self.failUnless(result is renderer)
        path = os.path.abspath(__file__)
        if path.endswith('pyc'): # pragma: no cover
            path = path[:-1]
        self.assertEqual(factory.path, path)
        self.assertEqual(factory.kw, {})

    def test_relpath_is_package_notyetregistered(self):
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
        from zope.component import queryUtility
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ITemplateRenderer
        settings = {'reload_resources':True}
        testing.registerUtility(settings, ISettings)
        renderer = {}
        factory = DummyFactory(renderer)
        result = self._callFUT('test_renderers.py', factory)
        self.failUnless(result is renderer)
        spec = '%s:%s' % ('repoze.bfg.tests', 'test_renderers.py')
        self.assertEqual(queryUtility(ITemplateRenderer, name=spec),
                         None)

    def test_reload_resources_false(self):
        from zope.component import queryUtility
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ITemplateRenderer
        settings = {'reload_resources':False}
        testing.registerUtility(settings, ISettings)
        renderer = {}
        factory = DummyFactory(renderer)
        result = self._callFUT('test_renderers.py', factory)
        self.failUnless(result is renderer)
        spec = '%s:%s' % ('repoze.bfg.tests', 'test_renderers.py')
        self.assertNotEqual(queryUtility(ITemplateRenderer, name=spec),
                            None)

class TestRendererFromName(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, path, level=4):
        from repoze.bfg.renderers import renderer_from_name
        return renderer_from_name(path, level)

    def test_it(self):
        from repoze.bfg.interfaces import ITemplateRendererFactory
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        fixture = os.path.join(here, 'fixtures/minimal.pt')
        renderer = {}
        def factory(path, **kw):
            return renderer
        testing.registerUtility(factory, ITemplateRendererFactory, name='.pt')
        result = self._callFUT(fixture)
        self.assertEqual(result, renderer)

class DummyFactory:
    def __init__(self, renderer):
        self.renderer = renderer

    def __call__(self, path, **kw):
        self.path = path
        self.kw = kw
        return self.renderer
    

