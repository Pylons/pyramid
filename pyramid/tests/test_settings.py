import unittest
from pyramid import testing

class TestSettings(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.settings import Settings
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
        self.assertEqual(settings['debug_routematch'], False)
        self.assertEqual(settings['reload_templates'], False)
        self.assertEqual(settings['reload_resources'], False)

    def test_reload_templates(self):
        settings = self._makeOne({})
        self.assertEqual(settings['reload_templates'], False)
        result = self._makeOne({'reload_templates':'false'})
        self.assertEqual(result['reload_templates'], False)
        result = self._makeOne({'reload_templates':'t'})
        self.assertEqual(result['reload_templates'], True)
        result = self._makeOne({'reload_templates':'1'})
        self.assertEqual(result['reload_templates'], True)
        result = self._makeOne({}, {'PYRAMID_RELOAD_TEMPLATES':'1'})
        self.assertEqual(result['reload_templates'], True)
        result = self._makeOne({'reload_templates':'false'},
                             {'PYRAMID_RELOAD_TEMPLATES':'1'})
        self.assertEqual(result['reload_templates'], True)

    def test_reload_resources(self):
        # alias for reload_assets
        result = self._makeOne({})
        self.assertEqual(result['reload_resources'], False)
        self.assertEqual(result['reload_assets'], False)
        result = self._makeOne({'reload_resources':'false'})
        self.assertEqual(result['reload_resources'], False)
        self.assertEqual(result['reload_assets'], False)
        result = self._makeOne({'reload_resources':'t'})
        self.assertEqual(result['reload_resources'], True)
        self.assertEqual(result['reload_assets'], True)
        result = self._makeOne({'reload_resources':'1'})
        self.assertEqual(result['reload_resources'], True)
        self.assertEqual(result['reload_assets'], True)
        result = self._makeOne({}, {'PYRAMID_RELOAD_RESOURCES':'1'})
        self.assertEqual(result['reload_resources'], True)
        self.assertEqual(result['reload_assets'], True)
        result = self._makeOne({'reload_resources':'false'},
                             {'PYRAMID_RELOAD_RESOURCES':'1'})
        self.assertEqual(result['reload_resources'], True)
        self.assertEqual(result['reload_assets'], True)

    def test_reload_assets(self):
        # alias for reload_resources
        result = self._makeOne({})
        self.assertEqual(result['reload_assets'], False)
        self.assertEqual(result['reload_resources'], False)
        result = self._makeOne({'reload_assets':'false'})
        self.assertEqual(result['reload_resources'], False)
        self.assertEqual(result['reload_assets'], False)
        result = self._makeOne({'reload_assets':'t'})
        self.assertEqual(result['reload_assets'], True)
        self.assertEqual(result['reload_resources'], True)
        result = self._makeOne({'reload_assets':'1'})
        self.assertEqual(result['reload_assets'], True)
        self.assertEqual(result['reload_resources'], True)
        result = self._makeOne({}, {'PYRAMID_RELOAD_ASSETS':'1'})
        self.assertEqual(result['reload_assets'], True)
        self.assertEqual(result['reload_resources'], True)
        result = self._makeOne({'reload_assets':'false'},
                             {'PYRAMID_RELOAD_ASSETS':'1'})
        self.assertEqual(result['reload_assets'], True)
        self.assertEqual(result['reload_resources'], True)


    def test_reload_all(self):
        result = self._makeOne({})
        self.assertEqual(result['reload_templates'], False)
        self.assertEqual(result['reload_resources'], False)
        self.assertEqual(result['reload_assets'], False)
        result = self._makeOne({'reload_all':'false'})
        self.assertEqual(result['reload_templates'], False)
        self.assertEqual(result['reload_resources'], False)
        self.assertEqual(result['reload_assets'], False)
        result = self._makeOne({'reload_all':'t'})
        self.assertEqual(result['reload_templates'], True)
        self.assertEqual(result['reload_resources'], True)
        self.assertEqual(result['reload_assets'], True)
        result = self._makeOne({'reload_all':'1'})
        self.assertEqual(result['reload_templates'], True)
        self.assertEqual(result['reload_resources'], True)
        self.assertEqual(result['reload_assets'], True)
        result = self._makeOne({}, {'PYRAMID_RELOAD_ALL':'1'})
        self.assertEqual(result['reload_templates'], True)
        self.assertEqual(result['reload_resources'], True)
        self.assertEqual(result['reload_assets'], True)
        result = self._makeOne({'reload_all':'false'},
                             {'PYRAMID_RELOAD_ALL':'1'})
        self.assertEqual(result['reload_templates'], True)
        self.assertEqual(result['reload_resources'], True)
        self.assertEqual(result['reload_assets'], True)

    def test_debug_authorization(self):
        result = self._makeOne({})
        self.assertEqual(result['debug_authorization'], False)
        result = self._makeOne({'debug_authorization':'false'})
        self.assertEqual(result['debug_authorization'], False)
        result = self._makeOne({'debug_authorization':'t'})
        self.assertEqual(result['debug_authorization'], True)
        result = self._makeOne({'debug_authorization':'1'})
        self.assertEqual(result['debug_authorization'], True)
        result = self._makeOne({}, {'PYRAMID_DEBUG_AUTHORIZATION':'1'})
        self.assertEqual(result['debug_authorization'], True)
        result = self._makeOne({'debug_authorization':'false'},
                             {'PYRAMID_DEBUG_AUTHORIZATION':'1'})
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
        result = self._makeOne({}, {'PYRAMID_DEBUG_NOTFOUND':'1'})
        self.assertEqual(result['debug_notfound'], True)
        result = self._makeOne({'debug_notfound':'false'},
                             {'PYRAMID_DEBUG_NOTFOUND':'1'})
        self.assertEqual(result['debug_notfound'], True)

    def test_debug_routematch(self):
        result = self._makeOne({})
        self.assertEqual(result['debug_routematch'], False)
        result = self._makeOne({'debug_routematch':'false'})
        self.assertEqual(result['debug_routematch'], False)
        result = self._makeOne({'debug_routematch':'t'})
        self.assertEqual(result['debug_routematch'], True)
        result = self._makeOne({'debug_routematch':'1'})
        self.assertEqual(result['debug_routematch'], True)
        result = self._makeOne({}, {'PYRAMID_DEBUG_ROUTEMATCH':'1'})
        self.assertEqual(result['debug_routematch'], True)
        result = self._makeOne({'debug_routematch':'false'},
                             {'PYRAMID_DEBUG_ROUTEMATCH':'1'})
        self.assertEqual(result['debug_routematch'], True)

    def test_debug_templates(self):
        result = self._makeOne({})
        self.assertEqual(result['debug_templates'], False)
        result = self._makeOne({'debug_templates':'false'})
        self.assertEqual(result['debug_templates'], False)
        result = self._makeOne({'debug_templates':'t'})
        self.assertEqual(result['debug_templates'], True)
        result = self._makeOne({'debug_templates':'1'})
        self.assertEqual(result['debug_templates'], True)
        result = self._makeOne({}, {'PYRAMID_DEBUG_TEMPLATES':'1'})
        self.assertEqual(result['debug_templates'], True)
        result = self._makeOne({'debug_templates':'false'},
                             {'PYRAMID_DEBUG_TEMPLATES':'1'})
        self.assertEqual(result['debug_templates'], True)

    def test_debug_all(self):
        result = self._makeOne({})
        self.assertEqual(result['debug_notfound'], False)
        self.assertEqual(result['debug_routematch'], False)
        self.assertEqual(result['debug_authorization'], False)
        self.assertEqual(result['debug_templates'], False)
        result = self._makeOne({'debug_all':'false'})
        self.assertEqual(result['debug_notfound'], False)
        self.assertEqual(result['debug_routematch'], False)
        self.assertEqual(result['debug_authorization'], False)
        self.assertEqual(result['debug_templates'], False)
        result = self._makeOne({'debug_all':'t'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_routematch'], True)
        self.assertEqual(result['debug_authorization'], True)
        self.assertEqual(result['debug_templates'], True)
        result = self._makeOne({'debug_all':'1'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_routematch'], True)
        self.assertEqual(result['debug_authorization'], True)
        self.assertEqual(result['debug_templates'], True)
        result = self._makeOne({}, {'PYRAMID_DEBUG_ALL':'1'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_routematch'], True)
        self.assertEqual(result['debug_authorization'], True)
        self.assertEqual(result['debug_templates'], True)
        result = self._makeOne({'debug_all':'false'},
                             {'PYRAMID_DEBUG_ALL':'1'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_routematch'], True)
        self.assertEqual(result['debug_authorization'], True)
        self.assertEqual(result['debug_templates'], True)

    def test_default_locale_name(self):
        result = self._makeOne({})
        self.assertEqual(result['default_locale_name'], 'en')
        result = self._makeOne({'default_locale_name':'abc'})
        self.assertEqual(result['default_locale_name'], 'abc')
        result = self._makeOne({}, {'PYRAMID_DEFAULT_LOCALE_NAME':'abc'})
        self.assertEqual(result['default_locale_name'], 'abc')
        result = self._makeOne({'default_locale_name':'def'},
                             {'PYRAMID_DEFAULT_LOCALE_NAME':'abc'})
        self.assertEqual(result['default_locale_name'], 'abc')

    def test_originals_kept(self):
        result = self._makeOne({'a':'i am so a'})
        self.assertEqual(result['a'], 'i am so a')


class TestGetSettings(unittest.TestCase):
    def setUp(self):
        from pyramid.registry import Registry
        registry = Registry('testing')
        self.config = testing.setUp(registry=registry)
        self.config.begin()
        from zope.deprecation import __show__
        __show__.off()

    def tearDown(self):
        self.config.end()
        from zope.deprecation import __show__
        __show__.on()
        
    def _callFUT(self):
        from pyramid.settings import get_settings
        return get_settings()

    def test_it_nosettings(self):
        self.assertEqual(self._callFUT()['reload_templates'], False)

    def test_it_withsettings(self):
        settings = {'a':1}
        self.config.registry.settings = settings
        self.assertEqual(self._callFUT(), settings)

class Test_asbool(unittest.TestCase):
    def _callFUT(self, s):
        from pyramid.settings import asbool
        return asbool(s)

    def test_s_is_None(self):
        result = self._callFUT(None)
        self.assertEqual(result, False)
        
    def test_s_is_True(self):
        result = self._callFUT(True)
        self.assertEqual(result, True)
        
    def test_s_is_False(self):
        result = self._callFUT(False)
        self.assertEqual(result, False)

    def test_s_is_true(self):
        result = self._callFUT('True')
        self.assertEqual(result, True)

    def test_s_is_false(self):
        result = self._callFUT('False')
        self.assertEqual(result, False)

    def test_s_is_yes(self):
        result = self._callFUT('yes')
        self.assertEqual(result, True)

    def test_s_is_on(self):
        result = self._callFUT('on')
        self.assertEqual(result, True)

    def test_s_is_1(self):
        result = self._callFUT(1)
        self.assertEqual(result, True)
