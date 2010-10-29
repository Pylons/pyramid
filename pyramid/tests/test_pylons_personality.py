import unittest


class Test_pylons_renderer_globals_factory_config(unittest.TestCase):
    def setUp(self):
        from pyramid.configuration import Configurator
        self.config = Configurator()
        request = DummyRequest()
        self.config.begin(request)

    def tearDown(self):
        self.config.end()

    def _makeOne(self, helpers):
        from pyramid.personality import pylons
        return pylons.renderer_globals_factory_config(helpers)

    def test_with_request(self):
        request = DummyRequest()
        from pyramid.url import route_url
        system = {'request':request}
        factory = self._makeOne('helpers')
        result = factory(system)
        self.assertEqual(result['url'], route_url)
        self.assertEqual(result['h'], 'helpers')
        self.assertEqual(result['c'], request.tmpl_context)
        self.assertEqual(result['tmpl_context'], request.tmpl_context)

    def test_without_request(self):
        from pyramid.url import route_url
        from pyramid.threadlocal import get_current_request
        system = {'request':None}
        factory = self._makeOne('helpers')
        result = factory(system)
        self.assertEqual(result['url'], route_url)
        self.assertEqual(result['h'], 'helpers')
        request = get_current_request()
        self.assertEqual(result['c'], request.tmpl_context)
        self.assertEqual(result['tmpl_context'], request.tmpl_context)
        self.assertEqual(result['request'], request)

    def test_with_session(self):
        request = DummyRequest()
        request.session = 'session'
        system = {'request':request}
        factory = self._makeOne('helpers')
        result = factory(system)
        self.assertEqual(result['session'], 'session')

class DummyRequest(object):
    def __init__(self):
        self.tmpl_context = object()
        
    
