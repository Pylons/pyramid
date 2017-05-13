import os
import unittest
from pyramid.tests.test_scripts.dummy import DummyLoader

here = os.path.dirname(__file__)

class Test_get_app(unittest.TestCase):
    def _callFUT(self, config_file, section_name, options=None, _loader=None):
        import pyramid.paster
        old_loader = pyramid.paster.get_config_loader
        try:
            if _loader is not None:
                pyramid.paster.get_config_loader = _loader
            return pyramid.paster.get_app(config_file, section_name,
                                          options=options)
        finally:
            pyramid.paster.get_config_loader = old_loader

    def test_it(self):
        app = DummyApp()
        loader = DummyLoader(app=app)
        result = self._callFUT(
            '/foo/bar/myapp.ini', 'myapp', options={'a': 'b'},
            _loader=loader)
        self.assertEqual(loader.uri.path, '/foo/bar/myapp.ini')
        self.assertEqual(len(loader.calls), 1)
        self.assertEqual(loader.calls[0]['op'], 'app')
        self.assertEqual(loader.calls[0]['name'], 'myapp')
        self.assertEqual(loader.calls[0]['defaults'], {'a': 'b'})
        self.assertEqual(result, app)

    def test_it_with_dummyapp_requiring_options(self):
        options = {'bar': 'baz'}
        app = self._callFUT(
            os.path.join(here, 'fixtures', 'dummy.ini'),
            'myapp', options=options)
        self.assertEqual(app.settings['foo'], 'baz')

class Test_get_appsettings(unittest.TestCase):
    def _callFUT(self, config_file, section_name, options=None, _loader=None):
        import pyramid.paster
        old_loader = pyramid.paster.get_config_loader
        try:
            if _loader is not None:
                pyramid.paster.get_config_loader = _loader
            return pyramid.paster.get_appsettings(config_file, section_name,
                                                  options=options)
        finally:
            pyramid.paster.get_config_loader = old_loader

    def test_it(self):
        values = {'a': 1}
        loader = DummyLoader(app_settings=values)
        result = self._callFUT(
            '/foo/bar/myapp.ini', 'myapp', options={'a': 'b'},
            _loader=loader)
        self.assertEqual(loader.uri.path, '/foo/bar/myapp.ini')
        self.assertEqual(len(loader.calls), 1)
        self.assertEqual(loader.calls[0]['op'], 'app_settings')
        self.assertEqual(loader.calls[0]['name'], 'myapp')
        self.assertEqual(loader.calls[0]['defaults'], {'a': 'b'})
        self.assertEqual(result, values)

    def test_it_with_dummyapp_requiring_options(self):
        options = {'bar': 'baz'}
        result = self._callFUT(
            os.path.join(here, 'fixtures', 'dummy.ini'),
            'myapp', options=options)
        self.assertEqual(result['foo'], 'baz')

class Test_setup_logging(unittest.TestCase):
    def _callFUT(self, config_file, global_conf=None, _loader=None):
        import pyramid.paster
        old_loader = pyramid.paster.get_config_loader
        try:
            if _loader is not None:
                pyramid.paster.get_config_loader = _loader
            return pyramid.paster.setup_logging(config_file, global_conf)
        finally:
            pyramid.paster.get_config_loader = old_loader

    def test_it_no_global_conf(self):
        loader = DummyLoader()
        self._callFUT('/abc.ini', _loader=loader)
        self.assertEqual(loader.uri.path, '/abc.ini')
        self.assertEqual(len(loader.calls), 1)
        self.assertEqual(loader.calls[0]['op'], 'logging')
        self.assertEqual(loader.calls[0]['defaults'], None)

    def test_it_global_conf_empty(self):
        loader = DummyLoader()
        self._callFUT('/abc.ini', global_conf={}, _loader=loader)
        self.assertEqual(loader.uri.path, '/abc.ini')
        self.assertEqual(len(loader.calls), 1)
        self.assertEqual(loader.calls[0]['op'], 'logging')
        self.assertEqual(loader.calls[0]['defaults'], {})

    def test_it_global_conf_not_empty(self):
        loader = DummyLoader()
        self._callFUT('/abc.ini', global_conf={'key': 'val'}, _loader=loader)
        self.assertEqual(loader.uri.path, '/abc.ini')
        self.assertEqual(len(loader.calls), 1)
        self.assertEqual(loader.calls[0]['op'], 'logging')
        self.assertEqual(loader.calls[0]['defaults'], {'key': 'val'})

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

class DummyApp:
    def __init__(self):
        self.registry = dummy_registry

def make_dummyapp(global_conf, **settings):
    app = DummyApp()
    app.settings = settings
    app.global_conf = global_conf
    return app

class DummyRequest:
    application_url = 'http://example.com:5432'
    script_name = ''
    def __init__(self, environ):
        self.environ = environ
        self.matchdict = {}
