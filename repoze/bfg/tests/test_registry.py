import unittest

from zope.component.testing import PlacelessSetup

class TestMakeRegistry(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getFUT(self):
        from repoze.bfg.registry import makeRegistry
        return makeRegistry

    def test_it(self):
        from repoze.bfg.tests import fixtureapp
        makeRegistry = self._getFUT()
        dummylock = DummyLock()
        dummyregmgr = DummyRegistrationManager()
        import repoze.bfg.registry
        try:
            old = repoze.bfg.registry.setRegistryManager(dummyregmgr)
            registry = makeRegistry('configure.zcml',
                                    fixtureapp,
                                    options={'reload_templates':True,
                                             'debug_authorization':True},
                                    lock=dummylock)
            from zope.component.registry import Components
            self.failUnless(isinstance(registry, Components))
            self.assertEqual(dummylock.acquired, True)
            self.assertEqual(dummylock.released, True)
            self.assertEqual(dummyregmgr.registry, registry)
            from zope.component import getUtility
            from repoze.bfg.interfaces import ISettings
            from repoze.bfg.interfaces import ILogger
            settings = getUtility(ISettings)
            logger = getUtility(ILogger, name='repoze.bfg.debug')
            self.assertEqual(logger.name, 'repoze.bfg.debug')
            self.assertEqual(settings.reload_templates, True)
            self.assertEqual(settings.debug_authorization, True)
        finally:
            repoze.bfg.registry.setRegistryManager(old)

class TestGetOptions(unittest.TestCase):
    def _getFUT(self):
        from repoze.bfg.registry import get_options
        return get_options

    def test_reload_templates(self):
        get_options = self._getFUT()
        result = get_options({})
        self.assertEqual(result['reload_templates'], False)
        result = get_options({'reload_templates':'false'})
        self.assertEqual(result['reload_templates'], False)
        result = get_options({'reload_templates':'t'})
        self.assertEqual(result['reload_templates'], True)
        result = get_options({'reload_templates':'1'})
        self.assertEqual(result['reload_templates'], True)
        result = get_options({}, {'BFG_RELOAD_TEMPLATES':'1'})
        self.assertEqual(result['reload_templates'], True)
        result = get_options({'reload_templates':'false'},
                             {'BFG_RELOAD_TEMPLATES':'1'})
        self.assertEqual(result['reload_templates'], True)

    def test_debug_authorization(self):
        get_options = self._getFUT()
        result = get_options({})
        self.assertEqual(result['debug_authorization'], False)
        result = get_options({'debug_authorization':'false'})
        self.assertEqual(result['debug_authorization'], False)
        result = get_options({'debug_authorization':'t'})
        self.assertEqual(result['debug_authorization'], True)
        result = get_options({'debug_authorization':'1'})
        self.assertEqual(result['debug_authorization'], True)
        result = get_options({}, {'BFG_DEBUG_AUTHORIZATION':'1'})
        self.assertEqual(result['debug_authorization'], True)
        result = get_options({'debug_authorization':'false'},
                             {'BFG_DEBUG_AUTHORIZATION':'1'})
        self.assertEqual(result['debug_authorization'], True)

    def test_debug_notfound(self):
        get_options = self._getFUT()
        result = get_options({})
        self.assertEqual(result['debug_notfound'], False)
        result = get_options({'debug_notfound':'false'})
        self.assertEqual(result['debug_notfound'], False)
        result = get_options({'debug_notfound':'t'})
        self.assertEqual(result['debug_notfound'], True)
        result = get_options({'debug_notfound':'1'})
        self.assertEqual(result['debug_notfound'], True)
        result = get_options({}, {'BFG_DEBUG_NOTFOUND':'1'})
        self.assertEqual(result['debug_notfound'], True)
        result = get_options({'debug_notfound':'false'},
                             {'BFG_DEBUG_NOTFOUND':'1'})
        self.assertEqual(result['debug_notfound'], True)
        
    def test_debug_all(self):
        get_options = self._getFUT()
        result = get_options({})
        self.assertEqual(result['debug_notfound'], False)
        self.assertEqual(result['debug_authorization'], False)
        result = get_options({'debug_all':'false'})
        self.assertEqual(result['debug_notfound'], False)
        self.assertEqual(result['debug_authorization'], False)
        result = get_options({'debug_all':'t'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_authorization'], True)
        result = get_options({'debug_all':'1'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_authorization'], True)
        result = get_options({}, {'BFG_DEBUG_ALL':'1'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_authorization'], True)
        result = get_options({'debug_all':'false'},
                             {'BFG_DEBUG_ALL':'1'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_authorization'], True)

class TestSettings(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.registry import Settings
        return Settings

    def _makeOne(self, **options):
        klass = self._getTargetClass()
        return klass(options)

    def test_no_options(self):
        settings = self._makeOne()
        self.assertEqual(settings.reload_templates, False)
        self.assertEqual(settings.debug_notfound, False)
        self.assertEqual(settings.debug_authorization, False)

    def test_with_option(self):
        settings = self._makeOne(reload_templates=True)
        self.assertEqual(settings.reload_templates, True)
        self.assertEqual(settings.debug_notfound, False)
        self.assertEqual(settings.debug_authorization, False)

class TestThreadLocalRegistryManager(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getTargetClass(self):
        from repoze.bfg.registry import ThreadLocalRegistryManager
        return ThreadLocalRegistryManager

    def _makeOne(self):
        return self._getTargetClass()()

    def test_init(self):
        local = self._makeOne()
        from zope.component import getGlobalSiteManager
        self.assertEqual(local.registry, getGlobalSiteManager())

    def test_set_get_and_clear(self):
        local = self._makeOne()
        from zope.component import getGlobalSiteManager
        local.set(None)
        self.failIfEqual(local.registry, getGlobalSiteManager())
        self.assertEqual(local.get(), None)
        local.clear()
        self.assertEqual(local.registry, getGlobalSiteManager())

class GetSiteManagerTests(unittest.TestCase):
    def _getFUT(self):
        from repoze.bfg.registry import getSiteManager
        return getSiteManager

    def test_no_context(self):
        gsm = self._getFUT()
        from zope.component import getGlobalSiteManager
        self.assertEqual(gsm(), getGlobalSiteManager())
    
    def test_with_context(self):
        gsm = self._getFUT()
        from zope.component.interfaces import ComponentLookupError
        self.assertRaises(ComponentLookupError, gsm, object)
        
class DummyRegistrationManager:
    registry = None
    def set(self, registry):
        self.registry = registry

    def get(self):
        return self.registry

    def clear(self):
        self.cleared = True

class DummyLock:
    def acquire(self):
        self.acquired = True

    def release(self):
        self.released = True
        
