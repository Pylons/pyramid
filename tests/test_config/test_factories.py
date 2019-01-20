import unittest

from . import dummyfactory


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
        config.set_request_factory('tests.test_config.dummyfactory')
        self.assertEqual(
            config.registry.getUtility(IRequestFactory), dummyfactory
        )

    def test_set_response_factory(self):
        from pyramid.interfaces import IResponseFactory

        config = self._makeOne(autocommit=True)
        factory = lambda r: object()
        config.set_response_factory(factory)
        self.assertEqual(config.registry.getUtility(IResponseFactory), factory)

    def test_set_response_factory_dottedname(self):
        from pyramid.interfaces import IResponseFactory

        config = self._makeOne(autocommit=True)
        config.set_response_factory('tests.test_config.dummyfactory')
        self.assertEqual(
            config.registry.getUtility(IResponseFactory), dummyfactory
        )

    def test_set_root_factory(self):
        from pyramid.interfaces import IRootFactory

        config = self._makeOne()
        config.set_root_factory(dummyfactory)
        self.assertEqual(config.registry.queryUtility(IRootFactory), None)
        config.commit()
        self.assertEqual(
            config.registry.getUtility(IRootFactory), dummyfactory
        )

    def test_set_root_factory_as_None(self):
        from pyramid.interfaces import IRootFactory
        from pyramid.traversal import DefaultRootFactory

        config = self._makeOne()
        config.set_root_factory(None)
        self.assertEqual(config.registry.queryUtility(IRootFactory), None)
        config.commit()
        self.assertEqual(
            config.registry.getUtility(IRootFactory), DefaultRootFactory
        )

    def test_set_root_factory_dottedname(self):
        from pyramid.interfaces import IRootFactory

        config = self._makeOne()
        config.set_root_factory('tests.test_config.dummyfactory')
        self.assertEqual(config.registry.queryUtility(IRootFactory), None)
        config.commit()
        self.assertEqual(
            config.registry.getUtility(IRootFactory), dummyfactory
        )

    def test_set_session_factory(self):
        from pyramid.interfaces import ISessionFactory

        config = self._makeOne()
        config.set_session_factory(dummyfactory)
        self.assertEqual(config.registry.queryUtility(ISessionFactory), None)
        config.commit()
        self.assertEqual(
            config.registry.getUtility(ISessionFactory), dummyfactory
        )

    def test_set_session_factory_dottedname(self):
        from pyramid.interfaces import ISessionFactory

        config = self._makeOne()
        config.set_session_factory('tests.test_config.dummyfactory')
        self.assertEqual(config.registry.queryUtility(ISessionFactory), None)
        config.commit()
        self.assertEqual(
            config.registry.getUtility(ISessionFactory), dummyfactory
        )

    def test_add_request_method_with_callable(self):
        from pyramid.interfaces import IRequestExtensions

        config = self._makeOne(autocommit=True)
        callable = lambda x: None
        config.add_request_method(callable, name='foo')
        exts = config.registry.getUtility(IRequestExtensions)
        self.assertTrue('foo' in exts.methods)

    def test_add_request_method_with_unnamed_callable(self):
        from pyramid.interfaces import IRequestExtensions

        config = self._makeOne(autocommit=True)

        def foo(self):  # pragma: no cover
            pass

        config.add_request_method(foo)
        exts = config.registry.getUtility(IRequestExtensions)
        self.assertTrue('foo' in exts.methods)

    def test_set_multiple_request_methods_conflict(self):
        from pyramid.exceptions import ConfigurationConflictError

        config = self._makeOne()

        def foo(self):  # pragma: no cover
            pass

        def bar(self):  # pragma: no cover
            pass

        config.add_request_method(foo, name='bar')
        config.add_request_method(bar, name='bar')
        self.assertRaises(ConfigurationConflictError, config.commit)

    def test_add_request_method_with_None_callable(self):
        from pyramid.interfaces import IRequestExtensions

        config = self._makeOne(autocommit=True)
        config.add_request_method(name='foo')
        exts = config.registry.queryUtility(IRequestExtensions)
        self.assertTrue(exts is None)

    def test_add_request_method_with_None_callable_conflict(self):
        from pyramid.exceptions import ConfigurationConflictError

        config = self._makeOne()

        def bar(self):  # pragma: no cover
            pass

        config.add_request_method(name='foo')
        config.add_request_method(bar, name='foo')
        self.assertRaises(ConfigurationConflictError, config.commit)

    def test_add_request_method_with_None_callable_and_no_name(self):
        config = self._makeOne(autocommit=True)
        self.assertRaises(AttributeError, config.add_request_method)

    def test_add_request_method_with_text_name(self):
        from pyramid.exceptions import ConfigurationError

        config = self._makeOne(autocommit=True)

        def boomshaka(r):  # pragma: no cover
            pass

        def get_bad_name():
            name = b'La Pe\xc3\xb1a'
            config.add_request_method(boomshaka, name=name)

        self.assertRaises(ConfigurationError, get_bad_name)

    def test_set_execution_policy(self):
        from pyramid.interfaces import IExecutionPolicy

        config = self._makeOne(autocommit=True)

        def dummy_policy(environ, router):  # pragma: no cover
            pass

        config.set_execution_policy(dummy_policy)
        registry = config.registry
        result = registry.queryUtility(IExecutionPolicy)
        self.assertEqual(result, dummy_policy)

    def test_set_execution_policy_to_None(self):
        from pyramid.interfaces import IExecutionPolicy
        from pyramid.router import default_execution_policy

        config = self._makeOne(autocommit=True)
        config.set_execution_policy(None)
        registry = config.registry
        result = registry.queryUtility(IExecutionPolicy)
        self.assertEqual(result, default_execution_policy)
