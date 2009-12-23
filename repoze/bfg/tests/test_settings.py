import unittest

class TestSettings(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.settings import Settings
        return Settings

    def _makeOne(self, d=None, environ=None):
        if environ is None:
            environ = {}
        klass = self._getTargetClass()
        return klass(d, _environ_=environ)

    def test_getattr(self):
        settings = self._makeOne({'reload_templates':False})
        self.assertEqual(settings.reload_templates, False)

    def test_getattr_raises_attribute_error(self):
        settings = self._makeOne()
        self.assertRaises(AttributeError, settings.__getattr__, 'mykey')

    def test_noargs(self):
        settings = self._makeOne()
        self.assertEqual(settings['debug_authorization'], False)
        self.assertEqual(settings['debug_notfound'], False)
        self.assertEqual(settings['reload_templates'], False)
        self.assertEqual(settings['reload_resources'], False)
        self.assertEqual(settings['configure_zcml'], '')

    def test_reload_templates(self):
        settings = self._makeOne({})
        self.assertEqual(settings['reload_templates'], False)
        result = self._makeOne({'reload_templates':'false'})
        self.assertEqual(result['reload_templates'], False)
        result = self._makeOne({'reload_templates':'t'})
        self.assertEqual(result['reload_templates'], True)
        result = self._makeOne({'reload_templates':'1'})
        self.assertEqual(result['reload_templates'], True)
        result = self._makeOne({}, {'BFG_RELOAD_TEMPLATES':'1'})
        self.assertEqual(result['reload_templates'], True)
        result = self._makeOne({'reload_templates':'false'},
                             {'BFG_RELOAD_TEMPLATES':'1'})
        self.assertEqual(result['reload_templates'], True)

    def test_reload_resources(self):
        result = self._makeOne({})
        self.assertEqual(result['reload_resources'], False)
        result = self._makeOne({'reload_resources':'false'})
        self.assertEqual(result['reload_resources'], False)
        result = self._makeOne({'reload_resources':'t'})
        self.assertEqual(result['reload_resources'], True)
        result = self._makeOne({'reload_resources':'1'})
        self.assertEqual(result['reload_resources'], True)
        result = self._makeOne({}, {'BFG_RELOAD_RESOURCES':'1'})
        self.assertEqual(result['reload_resources'], True)
        result = self._makeOne({'reload_resources':'false'},
                             {'BFG_RELOAD_RESOURCES':'1'})
        self.assertEqual(result['reload_resources'], True)

    def test_reload_all(self):
        result = self._makeOne({})
        self.assertEqual(result['reload_templates'], False)
        self.assertEqual(result['reload_resources'], False)
        result = self._makeOne({'reload_all':'false'})
        self.assertEqual(result['reload_templates'], False)
        self.assertEqual(result['reload_resources'], False)
        result = self._makeOne({'reload_all':'t'})
        self.assertEqual(result['reload_templates'], True)
        self.assertEqual(result['reload_resources'], True)
        result = self._makeOne({'reload_all':'1'})
        self.assertEqual(result['reload_templates'], True)
        self.assertEqual(result['reload_resources'], True)
        result = self._makeOne({}, {'BFG_RELOAD_ALL':'1'})
        self.assertEqual(result['reload_templates'], True)
        self.assertEqual(result['reload_resources'], True)
        result = self._makeOne({'reload_all':'false'},
                             {'BFG_RELOAD_ALL':'1'})
        self.assertEqual(result['reload_templates'], True)
        self.assertEqual(result['reload_resources'], True)

    def test_debug_authorization(self):
        result = self._makeOne({})
        self.assertEqual(result['debug_authorization'], False)
        result = self._makeOne({'debug_authorization':'false'})
        self.assertEqual(result['debug_authorization'], False)
        result = self._makeOne({'debug_authorization':'t'})
        self.assertEqual(result['debug_authorization'], True)
        result = self._makeOne({'debug_authorization':'1'})
        self.assertEqual(result['debug_authorization'], True)
        result = self._makeOne({}, {'BFG_DEBUG_AUTHORIZATION':'1'})
        self.assertEqual(result['debug_authorization'], True)
        result = self._makeOne({'debug_authorization':'false'},
                             {'BFG_DEBUG_AUTHORIZATION':'1'})
        self.assertEqual(result['debug_authorization'], True)

    def test_debug_notfound(self):
        result = self._makeOne({})
        self.assertEqual(result['debug_notfound'], False)
        result = self._makeOne({'debug_notfound':'false'})
        self.assertEqual(result['debug_notfound'], False)
        result = self._makeOne({'debug_notfound':'t'})
        self.assertEqual(result['debug_notfound'], True)
        result = self._makeOne({'debug_notfound':'1'})
        self.assertEqual(result['debug_notfound'], True)
        result = self._makeOne({}, {'BFG_DEBUG_NOTFOUND':'1'})
        self.assertEqual(result['debug_notfound'], True)
        result = self._makeOne({'debug_notfound':'false'},
                             {'BFG_DEBUG_NOTFOUND':'1'})
        self.assertEqual(result['debug_notfound'], True)
        
    def test_debug_all(self):
        result = self._makeOne({})
        self.assertEqual(result['debug_notfound'], False)
        self.assertEqual(result['debug_authorization'], False)
        result = self._makeOne({'debug_all':'false'})
        self.assertEqual(result['debug_notfound'], False)
        self.assertEqual(result['debug_authorization'], False)
        result = self._makeOne({'debug_all':'t'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_authorization'], True)
        result = self._makeOne({'debug_all':'1'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_authorization'], True)
        result = self._makeOne({}, {'BFG_DEBUG_ALL':'1'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_authorization'], True)
        result = self._makeOne({'debug_all':'false'},
                             {'BFG_DEBUG_ALL':'1'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_authorization'], True)

    def test_configure_zcml(self):
        result = self._makeOne({})
        self.assertEqual(result['configure_zcml'], '')
        result = self._makeOne({'configure_zcml':'abc'})
        self.assertEqual(result['configure_zcml'], 'abc')
        result = self._makeOne({}, {'BFG_CONFIGURE_ZCML':'abc'})
        self.assertEqual(result['configure_zcml'], 'abc')
        result = self._makeOne({'configure_zcml':'def'},
                             {'BFG_CONFIGURE_ZCML':'abc'})
        self.assertEqual(result['configure_zcml'], 'abc')

    def test_originals_kept(self):
        result = self._makeOne({'a':'i am so a'})
        self.assertEqual(result['a'], 'i am so a')


class TestGetSettings(unittest.TestCase):
    def setUp(self):
        from repoze.bfg.configuration import Configurator
        from repoze.bfg.registry import Registry
        registry = Registry('testing')
        self.config = Configurator(registry=registry)
        self.config.begin()

    def tearDown(self):
        self.config.end()
        
    def _callFUT(self):
        from repoze.bfg.settings import get_settings
        return get_settings()

    def test_it_nosettings(self):
        self.assertEqual(self._callFUT(), None)

    def test_it_withsettings(self):
        from repoze.bfg.interfaces import ISettings
        settings = {'a':1}
        self.config.registry.registerUtility(settings, ISettings)
        self.assertEqual(self._callFUT(), settings)

