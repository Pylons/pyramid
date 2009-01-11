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
        self.assertEqual(settings.unicode_path_segments, True)

    def test_with_option(self):
        settings = self._makeOne(reload_templates=True)
        self.assertEqual(settings.reload_templates, True)
        self.assertEqual(settings.debug_notfound, False)
        self.assertEqual(settings.debug_authorization, False)
        self.assertEqual(settings.unicode_path_segments, True)

class TestGetOptions(unittest.TestCase):
    def _getFUT(self):
        from repoze.bfg.settings import get_options
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

    def test_unicode_path_segments(self):
        get_options = self._getFUT()
        result = get_options({})
        self.assertEqual(result['unicode_path_segments'], True)
        result = get_options({'unicode_path_segments':'false'})
        self.assertEqual(result['unicode_path_segments'], False)
        result = get_options({'unicode_path_segments':'t'})
        self.assertEqual(result['unicode_path_segments'], True)
        result = get_options({'unicode_path_segments':'1'})
        self.assertEqual(result['unicode_path_segments'], True)
        result = get_options({}, {'BFG_UNICODE_PATH_SEGMENTS':'1'})
        self.assertEqual(result['unicode_path_segments'], True)
        result = get_options({'unicode_path_segments':'false'},
                             {'BFG_UNICODE_PATH_SEGMENTS':'1'})
        self.assertEqual(result['unicode_path_segments'], True)

    def test_originals_kept(self):
        get_options = self._getFUT()
        result = get_options({'a':'i am so a'})
        self.assertEqual(result['a'], 'i am so a')

