import unittest

class TestSettings(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.settings import Settings
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

class TestGetOptions(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.settings import get_options
        return get_options(*arg, **kw)

    def test_reload_templates(self):
        result = self._callFUT({})
        self.assertEqual(result['reload_templates'], False)
        result = self._callFUT({'reload_templates':'false'})
        self.assertEqual(result['reload_templates'], False)
        result = self._callFUT({'reload_templates':'t'})
        self.assertEqual(result['reload_templates'], True)
        result = self._callFUT({'reload_templates':'1'})
        self.assertEqual(result['reload_templates'], True)
        result = self._callFUT({}, {'BFG_RELOAD_TEMPLATES':'1'})
        self.assertEqual(result['reload_templates'], True)
        result = self._callFUT({'reload_templates':'false'},
                             {'BFG_RELOAD_TEMPLATES':'1'})
        self.assertEqual(result['reload_templates'], True)

    def test_debug_authorization(self):
        result = self._callFUT({})
        self.assertEqual(result['debug_authorization'], False)
        result = self._callFUT({'debug_authorization':'false'})
        self.assertEqual(result['debug_authorization'], False)
        result = self._callFUT({'debug_authorization':'t'})
        self.assertEqual(result['debug_authorization'], True)
        result = self._callFUT({'debug_authorization':'1'})
        self.assertEqual(result['debug_authorization'], True)
        result = self._callFUT({}, {'BFG_DEBUG_AUTHORIZATION':'1'})
        self.assertEqual(result['debug_authorization'], True)
        result = self._callFUT({'debug_authorization':'false'},
                             {'BFG_DEBUG_AUTHORIZATION':'1'})
        self.assertEqual(result['debug_authorization'], True)

    def test_debug_notfound(self):
        result = self._callFUT({})
        self.assertEqual(result['debug_notfound'], False)
        result = self._callFUT({'debug_notfound':'false'})
        self.assertEqual(result['debug_notfound'], False)
        result = self._callFUT({'debug_notfound':'t'})
        self.assertEqual(result['debug_notfound'], True)
        result = self._callFUT({'debug_notfound':'1'})
        self.assertEqual(result['debug_notfound'], True)
        result = self._callFUT({}, {'BFG_DEBUG_NOTFOUND':'1'})
        self.assertEqual(result['debug_notfound'], True)
        result = self._callFUT({'debug_notfound':'false'},
                             {'BFG_DEBUG_NOTFOUND':'1'})
        self.assertEqual(result['debug_notfound'], True)
        
    def test_debug_all(self):
        result = self._callFUT({})
        self.assertEqual(result['debug_notfound'], False)
        self.assertEqual(result['debug_authorization'], False)
        result = self._callFUT({'debug_all':'false'})
        self.assertEqual(result['debug_notfound'], False)
        self.assertEqual(result['debug_authorization'], False)
        result = self._callFUT({'debug_all':'t'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_authorization'], True)
        result = self._callFUT({'debug_all':'1'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_authorization'], True)
        result = self._callFUT({}, {'BFG_DEBUG_ALL':'1'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_authorization'], True)
        result = self._callFUT({'debug_all':'false'},
                             {'BFG_DEBUG_ALL':'1'})
        self.assertEqual(result['debug_notfound'], True)
        self.assertEqual(result['debug_authorization'], True)

    def test_originals_kept(self):
        result = self._callFUT({'a':'i am so a'})
        self.assertEqual(result['a'], 'i am so a')

