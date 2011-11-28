import unittest

class Test_get_app(unittest.TestCase):
    def _callFUT(self, config_file, section_name, loadapp):
        from pyramid.paster import get_app
        return get_app(config_file, section_name, loadapp)

    def test_it(self):
        import os
        app = DummyApp()
        loadapp = DummyLoadWSGI(app)
        result = self._callFUT('/foo/bar/myapp.ini', 'myapp', loadapp)
        self.assertEqual(loadapp.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(loadapp.section_name, 'myapp')
        self.assertEqual(loadapp.relative_to, os.getcwd())
        self.assertEqual(result, app)

    def test_it_with_hash(self):
        import os
        app = DummyApp()
        loadapp = DummyLoadWSGI(app)
        result = self._callFUT('/foo/bar/myapp.ini#myapp', None, loadapp)
        self.assertEqual(loadapp.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(loadapp.section_name, 'myapp')
        self.assertEqual(loadapp.relative_to, os.getcwd())
        self.assertEqual(result, app)

    def test_it_with_hash_and_name_override(self):
        import os
        app = DummyApp()
        loadapp = DummyLoadWSGI(app)
        result = self._callFUT('/foo/bar/myapp.ini#myapp', 'yourapp', loadapp)
        self.assertEqual(loadapp.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(loadapp.section_name, 'yourapp')
        self.assertEqual(loadapp.relative_to, os.getcwd())
        self.assertEqual(result, app)

class Test_get_appsettings(unittest.TestCase):
    def _callFUT(self, config_file, section_name, appconfig):
        from pyramid.paster import get_appsettings
        return get_appsettings(config_file, section_name, appconfig)

    def test_it(self):
        import os
        values = {'a':1}
        appconfig = DummyLoadWSGI(values)
        result = self._callFUT('/foo/bar/myapp.ini', 'myapp', appconfig)
        self.assertEqual(appconfig.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(appconfig.section_name, 'myapp')
        self.assertEqual(appconfig.relative_to, os.getcwd())
        self.assertEqual(result, values)

    def test_it_with_hash(self):
        import os
        values = {'a':1}
        appconfig = DummyLoadWSGI(values)
        result = self._callFUT('/foo/bar/myapp.ini#myapp', None, appconfig)
        self.assertEqual(appconfig.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(appconfig.section_name, 'myapp')
        self.assertEqual(appconfig.relative_to, os.getcwd())
        self.assertEqual(result, values)

    def test_it_with_hash_and_name_override(self):
        import os
        values = {'a':1}
        appconfig = DummyLoadWSGI(values)
        result = self._callFUT('/foo/bar/myapp.ini#myapp', 'yourapp', appconfig)
        self.assertEqual(appconfig.config_name, 'config:/foo/bar/myapp.ini')
        self.assertEqual(appconfig.section_name, 'yourapp')
        self.assertEqual(appconfig.relative_to, os.getcwd())
        self.assertEqual(result, values)

class Test_setup_logging(unittest.TestCase):
    def _callFUT(self, config_file):
        from pyramid.paster import setup_logging
        dummy_cp = DummyConfigParserModule
        return setup_logging(config_file, self.fileConfig, dummy_cp)

    def test_it(self):
        config_file, dict = self._callFUT('/abc')
        self.assertEqual(config_file, '/abc')
        self.assertEqual(dict['__file__'], '/abc')
        self.assertEqual(dict['here'], '/')

    def fileConfig(self, config_file, dict):
        return config_file, dict

class Test_bootstrap(unittest.TestCase):
    def _callFUT(self, config_uri, request=None):
        from pyramid.paster import bootstrap
        return bootstrap(config_uri, request)

    def setUp(self):
        import pyramid.paster
        self.original_get_app = pyramid.paster.get_app
        self.original_prepare = pyramid.paster.prepare
        self.app = app = DummyApp()
        self.root = root = Dummy()

        class DummyGetApp(object):
            def __call__(self, *a, **kw):
                self.a = a
                self.kw = kw
                return app
        self.get_app = pyramid.paster.get_app = DummyGetApp()

        class DummyPrepare(object):
            def __call__(self, *a, **kw):
                self.a = a
                self.kw = kw
                return {'root':root, 'closer':lambda: None}
        self.getroot = pyramid.paster.prepare = DummyPrepare()

    def tearDown(self):
        import pyramid.paster
        pyramid.paster.get_app = self.original_get_app
        pyramid.paster.prepare = self.original_prepare

    def test_it_request_with_registry(self):
        request = DummyRequest({})
        request.registry = dummy_registry
        result = self._callFUT('/foo/bar/myapp.ini', request)
        self.assertEqual(result['app'], self.app)
        self.assertEqual(result['root'], self.root)
        self.assertTrue('closer' in result)

class Dummy:
    pass

class DummyRegistry(object):
    settings = {}

dummy_registry = DummyRegistry()

class DummyLoadWSGI:
    def __init__(self, result):
        self.result = result

    def __call__(self, config_name, name=None, relative_to=None):
        self.config_name = config_name
        self.section_name = name
        self.relative_to = relative_to
        return self.result

class DummyApp:
    def __init__(self):
        self.registry = dummy_registry

class DummyRequest:
    application_url = 'http://example.com:5432'
    script_name = ''
    def __init__(self, environ):
        self.environ = environ
        self.matchdict = {}

class DummyConfigParser(object):
    def read(self, x):
        pass

    def has_section(self, name):
        return True

class DummyConfigParserModule(object):
    ConfigParser = DummyConfigParser



