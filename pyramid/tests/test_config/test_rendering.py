import unittest
import warnings

from pyramid.tests.test_config import dummyfactory

class TestRenderingConfiguratorMixin(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.config import Configurator
        config = Configurator(*arg, **kw)
        return config

    def test_set_renderer_globals_factory(self):
        from pyramid.interfaces import IRendererGlobalsFactory
        config = self._makeOne(autocommit=True)
        factory = object()
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            config.set_renderer_globals_factory(factory)
        self.assertEqual(
            config.registry.getUtility(IRendererGlobalsFactory),
            factory)

    def test_set_renderer_globals_factory_dottedname(self):
        from pyramid.interfaces import IRendererGlobalsFactory
        config = self._makeOne(autocommit=True)
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            config.set_renderer_globals_factory(
                'pyramid.tests.test_config.dummyfactory')
        self.assertEqual(
            config.registry.getUtility(IRendererGlobalsFactory),
            dummyfactory)

    def test_add_renderer(self):
        from pyramid.interfaces import IRendererFactory
        config = self._makeOne(autocommit=True)
        renderer = object()
        config.add_renderer('name', renderer)
        self.assertEqual(config.registry.getUtility(IRendererFactory, 'name'),
                         renderer)

    def test_add_renderer_dottedname_factory(self):
        from pyramid.interfaces import IRendererFactory
        config = self._makeOne(autocommit=True)
        import pyramid.tests.test_config
        config.add_renderer('name', 'pyramid.tests.test_config')
        self.assertEqual(config.registry.getUtility(IRendererFactory, 'name'),
                         pyramid.tests.test_config)

