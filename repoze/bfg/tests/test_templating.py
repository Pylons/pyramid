import unittest

from repoze.bfg.testing import cleanUp
from repoze.bfg import testing

class TestRendererFromCache(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, path, factory, level=3, **kw):
        from repoze.bfg.templating import renderer_from_cache
        return renderer_from_cache(path, factory, level, **kw)

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

    def test_relpath_notfound(self):
        import os
        here = os.path.dirname(__file__)
        abspath = os.path.join(here, 'wont/exist')
        renderer = {}
        self.assertRaises(ValueError, self._callFUT, 'wont/exist', None)

    def test_relpath_alreadyregistered(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        from repoze.bfg.tests import test_templating
        module_name = test_templating.__name__
        relpath = 'test_templating.py'
        spec = '%s\t%s' % (module_name, relpath)
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=spec)
        result = self._callFUT('test_templating.py', None)
        self.failUnless(result is renderer)

    def test_relpath_notyetregistered(self):
        from repoze.bfg import resource
        import os
        from repoze.bfg.tests import test_templating
        module_name = test_templating.__name__
        relpath = 'test_templating.py'
        spec = '%s\t%s' % (module_name, relpath)
        renderer = {}
        factory = DummyFactory(renderer)
        result = self._callFUT('test_templating.py', factory)
        self.failUnless(result is renderer)
        path = os.path.abspath(__file__)
        if path.endswith('pyc'): # pragma: no cover
            path = path[:-1]
        self.assertEqual(factory.path, path)
        self.assertEqual(factory.kw, {})

class DummyFactory:
    def __init__(self, renderer):
        self.renderer = renderer

    def __call__(self, path, **kw):
        self.path = path
        self.kw = kw
        return self.renderer
    

