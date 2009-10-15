import unittest

from repoze.bfg.testing import cleanUp

class MakeRegistryTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.router import make_registry
        return make_registry(*arg, **kw)

    def test_fixtureapp_default_filename_withpackage(self):
        manager = DummyRegistryManager()
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        registry = self._callFUT(rootfactory, fixtureapp)
        self.assertEqual(registry.__name__, 'repoze.bfg.tests.fixtureapp')
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failUnless(registry.queryUtility(IFixture)) # only in c.zcml

    def test_fixtureapp_explicit_filename(self):
        manager = DummyRegistryManager()
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        registry = self._callFUT(
            rootfactory, fixtureapp, filename='another.zcml',
            manager=manager)
        self.assertEqual(registry.__name__, 'repoze.bfg.tests.fixtureapp')
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failIf(registry.queryUtility(IFixture)) # only in c.zcml

    def test_fixtureapp_explicit_filename_in_options(self):
        import os
        manager = DummyRegistryManager()
        rootfactory = DummyRootFactory(None)
        from repoze.bfg.tests import fixtureapp
        zcmlfile = os.path.join(os.path.dirname(fixtureapp.__file__),
                                'another.zcml')
        registry = self._callFUT(
            rootfactory, fixtureapp, filename='configure.zcml',
            options={'configure_zcml':zcmlfile},
            manager=manager)
        self.assertEqual(registry.__name__, 'repoze.bfg.tests.fixtureapp')
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failIf(registry.queryUtility(IFixture)) # only in c.zcml

    def test_fixtureapp_explicit_specification_in_options(self):
        manager = DummyRegistryManager()
        rootfactory = DummyRootFactory(None)
        from repoze.bfg.tests import fixtureapp
        zcmlfile = 'repoze.bfg.tests.fixtureapp.subpackage:yetanother.zcml'
        registry = self._callFUT(
            rootfactory, fixtureapp, filename='configure.zcml',
            options={'configure_zcml':zcmlfile},
            manager=manager)
        self.assertEqual(registry.__name__,
                         'repoze.bfg.tests.fixtureapp.subpackage')
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failIf(registry.queryUtility(IFixture)) # only in c.zcml

    def test_fixtureapp_filename_hascolon_isabs(self):
        manager = DummyRegistryManager()
        rootfactory = DummyRootFactory(None)
        from repoze.bfg.tests import fixtureapp
        zcmlfile = 'repoze.bfg.tests.fixtureapp.subpackage:yetanother.zcml'
        class Dummy:
            def isabs(self, name):
                return True
        os = Dummy()
        os.path = Dummy()
        self.assertRaises(IOError, self._callFUT,
                          rootfactory,
                          fixtureapp,
                          filename='configure.zcml',
                          options={'configure_zcml':zcmlfile},
                          manager=manager,
                          os=os)
        
    def test_custom_settings(self):
        manager = DummyRegistryManager()
        options= {'mysetting':True}
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        registry = self._callFUT(rootfactory, fixtureapp, options=options,
                                 manager=manager)
        from repoze.bfg.interfaces import ISettings
        settings = registry.getUtility(ISettings)
        self.assertEqual(settings.reload_templates, False)
        self.assertEqual(settings.debug_authorization, False)
        self.assertEqual(settings.mysetting, True)

    def test_registrations(self):
        manager = DummyRegistryManager()
        options= {'reload_templates':True,
                  'debug_authorization':True}
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        registry = self._callFUT(rootfactory, fixtureapp, options=options,
                                 manager=manager)
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ILogger
        from repoze.bfg.interfaces import IRootFactory
        settings = registry.getUtility(ISettings)
        logger = registry.getUtility(ILogger, name='repoze.bfg.debug')
        rootfactory = registry.getUtility(IRootFactory)
        self.assertEqual(logger.name, 'repoze.bfg.debug')
        self.assertEqual(settings.reload_templates, True)
        self.assertEqual(settings.debug_authorization, True)
        self.assertEqual(rootfactory, rootfactory)
        self.failUnless(manager.pushed and manager.popped)

    def test_routes_in_config_with_rootfactory(self):
        options= {'reload_templates':True,
                  'debug_authorization':True}
        from repoze.bfg.urldispatch import RoutesRootFactory
        from repoze.bfg.tests import routesapp
        rootfactory = DummyRootFactory(None)
        registry = self._callFUT(rootfactory, routesapp, options=options)
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ILogger
        from repoze.bfg.interfaces import IRootFactory
        settings = registry.getUtility(ISettings)
        logger = registry.getUtility(ILogger, name='repoze.bfg.debug')
        effective_rootfactory = registry.getUtility(IRootFactory)
        self.assertEqual(logger.name, 'repoze.bfg.debug')
        self.assertEqual(settings.reload_templates, True)
        self.assertEqual(settings.debug_authorization, True)
        self.failUnless(isinstance(effective_rootfactory, RoutesRootFactory))
        self.assertEqual(effective_rootfactory.default_root_factory,
                         rootfactory)

    def test_routes_in_config_no_rootfactory(self):
        options= {'reload_templates':True,
                  'debug_authorization':True}
        from repoze.bfg.urldispatch import RoutesRootFactory
        from repoze.bfg.router import DefaultRootFactory
        from repoze.bfg.tests import routesapp
        registry = self._callFUT(None, routesapp, options=options)
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ILogger
        from repoze.bfg.interfaces import IRootFactory
        settings = registry.getUtility(ISettings)
        logger = registry.getUtility(ILogger, name='repoze.bfg.debug')
        rootfactory = registry.getUtility(IRootFactory)
        self.assertEqual(logger.name, 'repoze.bfg.debug')
        self.assertEqual(settings.reload_templates, True)
        self.assertEqual(settings.debug_authorization, True)
        self.failUnless(isinstance(rootfactory, RoutesRootFactory))
        self.assertEqual(rootfactory.default_root_factory, DefaultRootFactory)
        
    def test_no_routes_in_config_no_rootfactory(self):
        from repoze.bfg.router import DefaultRootFactory
        from repoze.bfg.interfaces import IRootFactory
        options= {'reload_templates':True,
                  'debug_authorization':True}
        from repoze.bfg.tests import fixtureapp
        registry = self._callFUT(None, fixtureapp, options=options)
        rootfactory = registry.getUtility(IRootFactory)
        self.assertEqual(rootfactory, DefaultRootFactory)

    def test_authorization_policy_no_authentication_policy(self):
        from repoze.bfg.interfaces import IAuthorizationPolicy
        authzpolicy = DummyContext()
        from repoze.bfg.tests import routesapp
        logger = DummyLogger()
        registry = self._callFUT(
            None, routesapp, authorization_policy=authzpolicy,
            debug_logger=logger)
        self.failIf(registry.queryUtility(IAuthorizationPolicy))
        self.assertEqual(logger.messages, [])
        
    def test_authentication_policy_no_authorization_policy(self):
        from repoze.bfg.interfaces import IAuthorizationPolicy
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.authorization import ACLAuthorizationPolicy
        authnpolicy = DummyContext()
        from repoze.bfg.tests import routesapp
        logger = DummyLogger()
        registry = self._callFUT(
            None, routesapp, authentication_policy=authnpolicy,
            debug_logger=logger)
        self.assertEqual(registry.getUtility(IAuthenticationPolicy),
                         authnpolicy)
        self.assertEqual(
            registry.getUtility(IAuthorizationPolicy).__class__,
            ACLAuthorizationPolicy)
        self.assertEqual(len(logger.messages), 1) # deprecation warning
                        
    def test_authentication_policy_and_authorization_policy(self):
        from repoze.bfg.interfaces import IAuthorizationPolicy
        from repoze.bfg.interfaces import IAuthenticationPolicy
        authnpolicy = DummyContext()
        authzpolicy = DummyContext()
        from repoze.bfg.tests import routesapp
        logger = DummyLogger()
        registry = self._callFUT(
           None, routesapp, authentication_policy=authnpolicy,
           authorization_policy = authzpolicy,
           debug_logger=logger)
        self.assertEqual(registry.getUtility(IAuthenticationPolicy),
                         authnpolicy)
        self.assertEqual(registry.getUtility(IAuthorizationPolicy),
                         authzpolicy)
        self.assertEqual(len(logger.messages), 1) # deprecation warning

    def test_lock_and_unlock(self):
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        dummylock = DummyLock()
        registry = self._callFUT(
            rootfactory, fixtureapp, filename='configure.zcml',
            lock=dummylock)
        self.assertEqual(dummylock.acquired, True)
        self.assertEqual(dummylock.released, True)

class DummyRegistryManager:
    def push(self, registry):
        from repoze.bfg.threadlocal import manager
        manager.push(registry)
        self.pushed = True

    def pop(self):
        from repoze.bfg.threadlocal import manager
        manager.pop()
        self.popped = True

class DummyRootFactory:
    def __init__(self, root):
        self.root = root

class DummyLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(msg)
    warn = info
    debug = info

class DummyContext:
    pass

class DummyLock:
    def acquire(self):
        self.acquired = True

    def release(self):
        self.released = True
        
