import unittest
from repoze.bfg.testing import cleanUp

class RoutesRootFactoryTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _getEnviron(self, **kw):
        environ = {'SERVER_NAME':'localhost',
                   'wsgi.url_scheme':'http'}
        environ.update(kw)
        return environ

    def _getTargetClass(self):
        from repoze.bfg.urldispatch import RoutesRootFactory
        return RoutesRootFactory

    def _makeOne(self, get_root):
        klass = self._getTargetClass()
        return klass(get_root)

    def test_init_default_root_factory(self):
        mapper = self._makeOne(None)
        self.assertEqual(mapper.default_root_factory, None)

    def test_no_route_matches(self):
        get_root = make_get_root(123)
        mapper = self._makeOne(get_root)
        environ = self._getEnviron(PATH_INFO='/')
        result = mapper(environ)
        self.assertEqual(result, 123)
        self.assertEqual(mapper.environ, environ)

    def test_route_matches(self):
        get_root = make_get_root(123)
        mapper = self._makeOne(get_root)
        mapper.connect('foo', 'archives/:action/:article', foo='foo')
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        self.assertEqual(result, 123)
        routing_args = environ['wsgiorg.routing_args'][1]
        self.assertEqual(routing_args['foo'], 'foo')
        self.assertEqual(routing_args['action'], 'action1')
        self.assertEqual(routing_args['article'], 'article1')
        self.assertEqual(environ['bfg.routes.matchdict'], routing_args)
        self.assertEqual(environ['bfg.routes.route'].name, 'foo')

    def test_unnamed_root_route_matches(self):
        root_factory = make_get_root(123)
        mapper = self._makeOne(root_factory)
        mapper.connect('')
        environ = self._getEnviron(PATH_INFO='/')
        result = mapper(environ)
        self.assertEqual(result, 123)
        self.assertEqual(environ['bfg.routes.route'].name, None)
        self.assertEqual(environ['bfg.routes.matchdict'], {})
        self.assertEqual(environ['wsgiorg.routing_args'], ((), {}))

    def test_named_root_route_matches(self):
        root_factory = make_get_root(123)
        mapper = self._makeOne(root_factory)
        mapper.connect('root', '')
        environ = self._getEnviron(PATH_INFO='/')
        result = mapper(environ)
        self.assertEqual(result, 123)
        self.assertEqual(environ['bfg.routes.route'].name, 'root')
        self.assertEqual(environ['bfg.routes.matchdict'], {})
        self.assertEqual(environ['wsgiorg.routing_args'], ((), {}))

    def test_matches_with_path_info_no_scriptname(self):
        root_factory = make_get_root(123)
        mapper = self._makeOne(root_factory)
        mapper.connect('root', '/a/b/*path_info')
        environ = self._getEnviron(PATH_INFO='/a/b/c/d')
        result = mapper(environ)
        self.assertEqual(result, 123)
        self.assertEqual(environ['bfg.routes.route'].name, 'root')
        self.assertEqual(environ['bfg.routes.matchdict'], {'path_info':'c/d'})
        self.assertEqual(environ['PATH_INFO'], '/c/d')
        self.assertEqual(environ['SCRIPT_NAME'], '/a/b')

    def test_matches_with_path_info_with_scriptname(self):
        root_factory = make_get_root(123)
        mapper = self._makeOne(root_factory)
        mapper.connect('root', '/a/b/*path_info')
        environ = self._getEnviron(PATH_INFO='/a/b/c/d', SCRIPT_NAME='z')
        result = mapper(environ)
        self.assertEqual(result, 123)
        self.assertEqual(environ['bfg.routes.route'].name, 'root')
        self.assertEqual(environ['bfg.routes.matchdict'], {'path_info':'c/d'})
        self.assertEqual(environ['PATH_INFO'], '/c/d')
        self.assertEqual(environ['SCRIPT_NAME'], 'z/a/b')

    def test_matches_PATH_INFO_w_extra_slash(self):
        root_factory = make_get_root(123)
        mapper = self._makeOne(root_factory)
        mapper.connect('root', '/a/b/*path_info')
        environ = self._getEnviron(PATH_INFO='/a/b//c/d', SCRIPT_NAME='')
        result = mapper(environ)
        self.assertEqual(result, 123)
        self.assertEqual(environ['bfg.routes.route'].name, 'root')
        self.assertEqual(environ['bfg.routes.matchdict'], {'path_info':'/c/d'})
        self.assertEqual(environ['PATH_INFO'], '/c/d')
        self.assertEqual(environ['SCRIPT_NAME'], '/a/b')

    def test_matches_SCRIPT_NAME_endswith_slash(self):
        root_factory = make_get_root(123)
        mapper = self._makeOne(root_factory)
        mapper.connect('root', '/a/b//*path_info')
        environ = self._getEnviron(PATH_INFO='/a/b//c/d', SCRIPT_NAME='')
        result = mapper(environ)
        self.assertEqual(result, 123)
        self.assertEqual(environ['bfg.routes.route'].name, 'root')
        self.assertEqual(environ['bfg.routes.matchdict'], {'path_info':'c/d'})
        self.assertEqual(environ['PATH_INFO'], '/c/d')
        self.assertEqual(environ['SCRIPT_NAME'], '/a/b')

    def test_unicode_in_route_default(self):
        root_factory = make_get_root(123)
        mapper = self._makeOne(root_factory)
        class DummyRoute:
            routepath = ':id'
            _factory = None
        la = unicode('\xc3\xb1a', 'utf-8')
        mapper.routematch = lambda *arg: ({la:'id'}, DummyRoute)
        mapper.connect('whatever', ':la')
        environ = self._getEnviron(PATH_INFO='/foo')
        result = mapper(environ)
        self.assertEqual(result, 123)
        self.assertEqual(environ['bfg.routes.route'], DummyRoute)
        self.assertEqual(environ['bfg.routes.matchdict'], {u'\xf1a': 'id'})
        routing_args = environ['wsgiorg.routing_args'][1]
        self.assertEqual(routing_args[la], 'id')

    def test_fallback_to_default_root_factory(self):
        root_factory = make_get_root(123)
        mapper = self._makeOne(root_factory)
        mapper.connect('wont', 'wont/:be/:found')
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        self.assertEqual(result, 123)

    def test_has_routes(self):
        mapper = self._makeOne(None)
        self.assertEqual(mapper.has_routes(), False)
        mapper.connect('whatever', 'archives/:action/:article')
        self.assertEqual(mapper.has_routes(), True)

    def test_url_for(self):
        root_factory = make_get_root(None)
        mapper = self._makeOne(root_factory)
        mapper.connect('whatever', 'archives/:action/:article')
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        from routes import url_for
        result = url_for(action='action2', article='article2')
        self.assertEqual(result, '/archives/action2/article2')

def make_get_root(result):
    def dummy_get_root(environ):
        return result
    return dummy_get_root

class DummyContext(object):
    """ """
        
class DummyRequest(object):
    """ """
    
