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

    def test_set_request_property_with_callable(self):
        from pyramid.interfaces import IRequestProperties
        config = self._makeOne(autocommit=True)
        callable = lambda x: None
        config.set_request_property(callable, name='foo')
        plist = config.registry.getUtility(IRequestProperties)
        self.assertEqual(plist, [('foo', callable, False)])

    def test_set_request_property_with_unnamed_callable(self):
        from pyramid.interfaces import IRequestProperties
        config = self._makeOne(autocommit=True)
        def foo(self): pass
        config.set_request_property(foo, reify=True)
        plist = config.registry.getUtility(IRequestProperties)
        self.assertEqual(plist, [('foo', foo, True)])

    def test_set_request_property_with_property(self):
        from pyramid.interfaces import IRequestProperties
        config = self._makeOne(autocommit=True)
        callable = property(lambda x: None)
        config.set_request_property(callable, name='foo')
        plist = config.registry.getUtility(IRequestProperties)
        self.assertEqual(plist, [('foo', callable, False)])

    def test_set_multiple_request_properties(self):
        from pyramid.interfaces import IRequestProperties
        config = self._makeOne()
        def foo(self): pass
        bar = property(lambda x: None)
        config.set_request_property(foo, reify=True)
        config.set_request_property(bar, name='bar')
        config.commit()
        plist = config.registry.getUtility(IRequestProperties)
        self.assertEqual(plist, [('foo', foo, True),
                                 ('bar', bar, False)])

    def test_set_multiple_request_properties_conflict(self):
        from pyramid.exceptions import ConfigurationConflictError
        config = self._makeOne()
        def foo(self): pass
        bar = property(lambda x: None)
        config.set_request_property(foo, name='bar', reify=True)
        config.set_request_property(bar, name='bar')
        self.assertRaises(ConfigurationConflictError, config.commit)

    def test_set_request_property_subscriber(self):
        from zope.interface import implementer
        from pyramid.interfaces import INewRequest
        config = self._makeOne()
        def foo(r): pass
        config.set_request_property(foo, name='foo')
        config.set_request_property(foo, name='bar', reify=True)
        config.commit()
        @implementer(INewRequest)
        class Event(object):
            request = DummyRequest(config.registry)
        event = Event()
        config.registry.notify(event)
        callables = event.request.callables
        self.assertEqual(callables, [('foo', foo, False),
                                     ('bar', foo, True)])


        
class DummyRequest(object):
    callables = None

    def __init__(self, registry):
        self.registry = registry

    def set_property(self, callable, name, reify):
        if self.callables is None:
            self.callables = []
        self.callables.append((name, callable, reify))

