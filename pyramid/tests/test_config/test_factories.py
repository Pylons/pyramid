import unittest

from pyramid.tests.test_config import dummyfactory

class TestFactoriesMixin(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.config import Configurator
        config = Configurator(*arg, **kw)
        return config

    def test_set_request_factory(self):
        from pyramid.interfaces import IRequestFactory
        config = self._makeOne(autocommit=True)
        factory = object()
        config.set_request_factory(factory)
        self.assertEqual(config.registry.getUtility(IRequestFactory), factory)

    def test_set_request_factory_dottedname(self):
        from pyramid.interfaces import IRequestFactory
        config = self._makeOne(autocommit=True)
        config.set_request_factory(
            'pyramid.tests.test_config.dummyfactory')
        self.assertEqual(config.registry.getUtility(IRequestFactory),
                         dummyfactory)

    def test_set_root_factory(self):
        from pyramid.interfaces import IRootFactory
        config = self._makeOne()
        config.set_root_factory(dummyfactory)
        self.assertEqual(config.registry.queryUtility(IRootFactory), None)
        config.commit()
        self.assertEqual(config.registry.getUtility(IRootFactory), dummyfactory)

    def test_set_root_factory_as_None(self):
        from pyramid.interfaces import IRootFactory
        from pyramid.traversal import DefaultRootFactory
        config = self._makeOne()
        config.set_root_factory(None)
        self.assertEqual(config.registry.queryUtility(IRootFactory), None)
        config.commit()
        self.assertEqual(config.registry.getUtility(IRootFactory),
                         DefaultRootFactory)
        
    def test_set_root_factory_dottedname(self):
        from pyramid.interfaces import IRootFactory
        config = self._makeOne()
        config.set_root_factory('pyramid.tests.test_config.dummyfactory')
        self.assertEqual(config.registry.queryUtility(IRootFactory), None)
        config.commit()
        self.assertEqual(config.registry.getUtility(IRootFactory), dummyfactory)
        
    def test_set_session_factory(self):
        from pyramid.interfaces import ISessionFactory
        config = self._makeOne()
        config.set_session_factory(dummyfactory)
        self.assertEqual(config.registry.queryUtility(ISessionFactory), None)
        config.commit()
        self.assertEqual(config.registry.getUtility(ISessionFactory),
                         dummyfactory)

    def test_set_session_factory_dottedname(self):
        from pyramid.interfaces import ISessionFactory
        config = self._makeOne()
        config.set_session_factory('pyramid.tests.test_config.dummyfactory')
        self.assertEqual(config.registry.queryUtility(ISessionFactory), None)
        config.commit()
        self.assertEqual(config.registry.getUtility(ISessionFactory),
                         dummyfactory)


