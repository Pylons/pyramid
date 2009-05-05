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

    def test_relpath_found(self):
        renderer = {}
        from repoze.bfg.interfaces import ITemplateRenderer
        testing.registerUtility(renderer, ITemplateRenderer, name='foo/bar')
        result = self._callFUT('foo/bar', None)
        self.failUnless(renderer is result)

    def test_abspath_found(self):
        import os
        here = os.path.dirname(__file__)
        abspath = os.path.join(here, 'foo/bar')
        from repoze.bfg.interfaces import ITemplateRenderer
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=abspath)
        result = self._callFUT('foo/bar', None)
        self.failUnless(renderer is result)

    def test_notfound_missing(self):
        import os
        here = os.path.dirname(__file__)
        abspath = os.path.join(here, 'foo/bar')
        renderer = {}
        self.assertRaises(ValueError, self._callFUT, 'foo/bar', None)
        
    def test_withfactory(self):
        renderer = {}
        factory = DummyFactory(renderer)
        import os
        here = os.path.dirname(__file__)
        abspath = os.path.join(here, 'fixtures/pp.pt')
        from repoze.bfg.interfaces import ITemplateRenderer
        testing.registerUtility(renderer, ITemplateRenderer, name=abspath)
        result = self._callFUT('fixtures/pp.pt', factory)
        self.failUnless(renderer is result)
        
class DummyFactory:
    def __init__(self, renderer):
        self.renderer = renderer

