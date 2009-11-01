import unittest
from repoze.bfg import testing

class TestRoute(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.urldispatch import Route
        return Route

    def _makeOne(self, *arg):
        return self._getTargetClass()(*arg)

    def test_ctor(self):
        import types
        route = self._makeOne(':path', 'name', 'factory')
        self.assertEqual(route.path, ':path')
        self.assertEqual(route.name, 'name')
        self.assertEqual(route.factory, 'factory')
        self.failUnless(route.generate.__class__ is types.FunctionType)
        self.failUnless(route.match.__class__ is types.FunctionType)

    def test_ctor_defaults(self):
        import types
        route = self._makeOne(':path')
        self.assertEqual(route.path, ':path')
        self.assertEqual(route.name, None)
        self.assertEqual(route.factory, None)
        self.failUnless(route.generate.__class__ is types.FunctionType)
        self.failUnless(route.match.__class__ is types.FunctionType)

    def test_match(self):
        route = self._makeOne(':path')
        self.assertEqual(route.match('/whatever'), {'path':'whatever'})
        
    def test_generate(self):
        route = self._makeOne(':path')
        self.assertEqual(route.generate({'path':'abc'}), '/abc')

class RoutesRootFactoryTests(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _getRequest(self, **kw):
        from zope.component import getSiteManager
        environ = {'SERVER_NAME':'localhost',
                   'wsgi.url_scheme':'http'}
        environ.update(kw)
        request = DummyRequest(environ)
        sm = getSiteManager()
        request.registry = sm
        return request

    def _registerRouteRequest(self, name):
        from repoze.bfg.interfaces import IRouteRequest
        from zope.interface import Interface
        from zope.component import getSiteManager
        class IRequest(Interface):
            """ """
        sm = getSiteManager()
        sm.registerUtility(IRequest, IRouteRequest, name=name)
        return IRequest

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
        root_factory = DummyRootFactory(123)
        mapper = self._makeOne(root_factory)
        request = self._getRequest(PATH_INFO='/')
        result = mapper(request)
        self.assertEqual(result, 123)

    def test_passed_environ_returns_default(self):
        root_factory = DummyRootFactory(123)
        mapper = self._makeOne(root_factory)
        request = self._getRequest(PATH_INFO='/')
        result = mapper(request.environ)
        self.assertEqual(result, 123)
        self.assertEqual(root_factory.request, request.environ)

    def test_route_matches(self):
        root_factory = DummyRootFactory(123)
        req_iface = self._registerRouteRequest('foo')
        mapper = self._makeOne(root_factory)
        mapper.connect('archives/:action/:article', 'foo')
        request = self._getRequest(PATH_INFO='/archives/action1/article1')
        result = mapper(request)
        self.assertEqual(result, 123)
        environ = request.environ
        routing_args = environ['wsgiorg.routing_args'][1]
        self.assertEqual(routing_args['action'], 'action1')
        self.assertEqual(routing_args['article'], 'article1')
        self.assertEqual(environ['bfg.routes.matchdict'], routing_args)
        self.assertEqual(environ['bfg.routes.route'].name, 'foo')
        self.assertEqual(request.matchdict, routing_args)
        self.failUnless(req_iface.providedBy(request))

    def test_route_matches_and_has_factory(self):
        root_factory = DummyRootFactory(123)
        req_iface = self._registerRouteRequest('foo')
        mapper = self._makeOne(root_factory)
        factory = DummyRootFactory(456)
        mapper.connect('archives/:action/:article', 'foo', factory)
        request = self._getRequest(PATH_INFO='/archives/action1/article1')
        result = mapper(request)
        self.assertEqual(result, 456)
        self.assertEqual(factory.request, request)
        environ = request.environ
        routing_args = environ['wsgiorg.routing_args'][1]
        self.assertEqual(routing_args['action'], 'action1')
        self.assertEqual(routing_args['article'], 'article1')
        self.assertEqual(environ['bfg.routes.matchdict'], routing_args)
        self.assertEqual(environ['bfg.routes.route'].name, 'foo')
        self.assertEqual(request.matchdict, routing_args)
        self.failUnless(req_iface.providedBy(request))

    def test_route_matches_with_predicates(self):
        root_factory = DummyRootFactory(123)
        req_iface = self._registerRouteRequest('foo')
        mapper = self._makeOne(root_factory)
        mapper.connect('archives/:action/:article', 'foo',
                       predicates=[lambda *arg: True])
        request = self._getRequest(PATH_INFO='/archives/action1/article1')
        result = mapper(request)
        self.assertEqual(result, 123)
        environ = request.environ
        routing_args = environ['wsgiorg.routing_args'][1]
        self.assertEqual(routing_args['action'], 'action1')
        self.assertEqual(routing_args['article'], 'article1')
        self.assertEqual(environ['bfg.routes.matchdict'], routing_args)
        self.assertEqual(environ['bfg.routes.route'].name, 'foo')
        self.assertEqual(request.matchdict, routing_args)
        self.failUnless(req_iface.providedBy(request))

    def test_route_fails_to_match_with_predicates(self):
        root_factory = DummyRootFactory(123)
        foo_iface = self._registerRouteRequest('foo')
        bar_iface = self._registerRouteRequest('bar')
        mapper = self._makeOne(root_factory)
        mapper.connect('archives/:action/article1', 'foo',
                       predicates=[lambda *arg: True, lambda *arg: False])
        mapper.connect('archives/:action/:article', 'bar')
        request = self._getRequest(PATH_INFO='/archives/action1/article1')
        result = mapper(request)
        self.assertEqual(result, 123)
        environ = request.environ
        routing_args = environ['wsgiorg.routing_args'][1]
        self.assertEqual(routing_args['action'], 'action1')
        self.assertEqual(routing_args['article'], 'article1')
        self.assertEqual(environ['bfg.routes.matchdict'], routing_args)
        self.assertEqual(environ['bfg.routes.route'].name, 'bar')
        self.assertEqual(request.matchdict, routing_args)
        self.failUnless(bar_iface.providedBy(request))
        self.failIf(foo_iface.providedBy(request))

    def test_root_route_matches(self):
        root_factory = DummyRootFactory(123)
        req_iface = self._registerRouteRequest('root')
        mapper = self._makeOne(root_factory)
        mapper.connect('', 'root')
        request = self._getRequest(PATH_INFO='/')
        result = mapper(request)
        environ = request.environ
        self.assertEqual(result, 123)
        self.assertEqual(environ['bfg.routes.route'].name, 'root')
        self.assertEqual(environ['bfg.routes.matchdict'], {})
        self.assertEqual(environ['wsgiorg.routing_args'], ((), {}))
        self.assertEqual(request.matchdict, {})
        self.failUnless(req_iface.providedBy(request))

    def test_root_route_matches2(self):
        root_factory = DummyRootFactory(123)
        req_iface = self._registerRouteRequest('root')
        mapper = self._makeOne(root_factory)
        mapper.connect('/', 'root')
        request = self._getRequest(PATH_INFO='/')
        result = mapper(request)
        environ = request.environ
        self.assertEqual(result, 123)
        self.assertEqual(environ['bfg.routes.route'].name, 'root')
        self.assertEqual(environ['bfg.routes.matchdict'], {})
        self.assertEqual(environ['wsgiorg.routing_args'], ((), {}))
        self.assertEqual(request.matchdict, {})
        self.failUnless(req_iface.providedBy(request))

    def test_root_route_when_path_info_empty(self):
        root_factory = DummyRootFactory(123)
        req_iface = self._registerRouteRequest('root')
        mapper = self._makeOne(root_factory)
        mapper.connect('/', 'root')
        request = self._getRequest(PATH_INFO='')
        result = mapper(request)
        environ = request.environ
        self.assertEqual(result, 123)
        self.assertEqual(environ['bfg.routes.route'].name, 'root')
        self.assertEqual(environ['bfg.routes.matchdict'], {})
        self.assertEqual(environ['wsgiorg.routing_args'], ((), {}))
        self.assertEqual(request.matchdict, {})
        self.failUnless(req_iface.providedBy(request))

    def test_fallback_to_default_root_factory(self):
        root_factory = DummyRootFactory(123)
        mapper = self._makeOne(root_factory)
        mapper.connect('wont/:be/:found', 'wont')
        request = self._getRequest(PATH_INFO='/archives/action1/article1')
        result = mapper(request)
        self.assertEqual(result, 123)
        self.assertEqual(root_factory.request, request)

    def test_no_path_info(self):
        root_factory = DummyRootFactory(123)
        mapper = self._makeOne(root_factory)
        mapper.connect('/', 'root')
        request = self._getRequest()
        result = mapper(request)
        self.assertEqual(result, 123)
        self.assertEqual(root_factory.request, request)

    def test_has_routes(self):
        mapper = self._makeOne(None)
        self.assertEqual(mapper.has_routes(), False)
        mapper.connect('whatever', 'archives/:action/:article')
        self.assertEqual(mapper.has_routes(), True)

    def test_get_routes(self):
        from repoze.bfg.urldispatch import Route
        mapper = self._makeOne(None)
        self.assertEqual(mapper.get_routes(), [])
        mapper.connect('whatever', 'archives/:action/:article')
        routes = mapper.get_routes()
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].__class__, Route)

    def test_generate(self):
        mapper = self._makeOne(None)
        def generator(kw):
            return 123
        route = DummyRoute(generator)
        mapper.routes['abc'] =  route
        self.assertEqual(mapper.generate('abc', {}), 123)

class TestCompileRoute(unittest.TestCase):
    def _callFUT(self, path):
        from repoze.bfg.urldispatch import _compile_route
        return _compile_route(path)

    def test_no_star(self):
        matcher, generator = self._callFUT('/foo/:baz/biz/:buz/bar')
        self.assertEqual(matcher('/foo/baz/biz/buz/bar'),
                         {'baz':'baz', 'buz':'buz'})
        self.assertEqual(matcher('foo/baz/biz/buz/bar'), None)
        self.assertEqual(generator({'baz':1, 'buz':2}), '/foo/1/biz/2/bar')

    def test_with_star(self):
        matcher, generator = self._callFUT('/foo/:baz/biz/:buz/bar*traverse')
        self.assertEqual(matcher('/foo/baz/biz/buz/bar'),
                         {'baz':'baz', 'buz':'buz', 'traverse':()})
        self.assertEqual(matcher('/foo/baz/biz/buz/bar/everything/else/here'),
                         {'baz':'baz', 'buz':'buz',
                          'traverse':('everything', 'else', 'here')})
        self.assertEqual(matcher('foo/baz/biz/buz/bar'), None)
        self.assertEqual(generator(
            {'baz':1, 'buz':2, 'traverse':u'/a/b'}), '/foo/1/biz/2/bar/a/b')

    def test_no_beginning_slash(self):
        matcher, generator = self._callFUT('foo/:baz/biz/:buz/bar')
        self.assertEqual(matcher('/foo/baz/biz/buz/bar'),
                         {'baz':'baz', 'buz':'buz'})
        self.assertEqual(matcher('foo/baz/biz/buz/bar'), None)
        self.assertEqual(generator({'baz':1, 'buz':2}), '/foo/1/biz/2/bar')

class TestCompileRouteMatchFunctional(unittest.TestCase):
    def matches(self, pattern, path, result):
        from repoze.bfg.urldispatch import _compile_route
        self.assertEqual(_compile_route(pattern)[0](path), result)

    def generates(self, pattern, dict, result):
        from repoze.bfg.urldispatch import _compile_route
        self.assertEqual(_compile_route(pattern)[1](dict), result)

    def test_matcher_functional(self):
        self.matches('/', '', None)
        self.matches('', '', None)
        self.matches('/', '/foo', None)
        self.matches('/foo/', '/foo', None)
        self.matches('/:x', '', None)
        self.matches('', '/', {})
        self.matches('/', '/', {})
        self.matches('/:x', '/', {'x':''})
        self.matches('/:x', '/a', {'x':'a'})
        self.matches('zzz/:x', '/zzz/abc', {'x':'abc'})
        self.matches('zzz/:x*traverse', '/zzz/abc', {'x':'abc', 'traverse':()})
        self.matches('zzz/:x*traverse', '/zzz/abc/def/g',
                     {'x':'abc', 'traverse':('def', 'g')})
        self.matches('*traverse', '/zzz/abc', {'traverse':('zzz', 'abc')})
        self.matches('*traverse', '/zzz/%20abc', {'traverse':('zzz', ' abc')})
        self.matches(':x', '/La%20Pe%C3%B1a', {'x':u'La Pe\xf1a'})
        self.matches('*traverse', '/La%20Pe%C3%B1a/x',
                     {'traverse':(u'La Pe\xf1a', 'x')})
        self.matches('/foo/:id.html', '/foo/bar.html', {'id':'bar'})
        
    def test_generator_functional(self):
        self.generates('', {}, '/')
        self.generates('/', {}, '/')
        self.generates('/:x', {'x':''}, '/')
        self.generates('/:x', {'x':'a'}, '/a')
        self.generates('zzz/:x', {'x':'abc'}, '/zzz/abc')
        self.generates('zzz/:x*traverse', {'x':'abc', 'traverse':''},
                       '/zzz/abc')
        self.generates('zzz/:x*traverse', {'x':'abc', 'traverse':'/def/g'},
                       '/zzz/abc/def/g')
        self.generates('/:x', {'x':unicode('/La Pe\xc3\xb1a', 'utf-8')},
                       '/%2FLa%20Pe%C3%B1a')
        self.generates('/:x*y', {'x':unicode('/La Pe\xc3\xb1a', 'utf-8'),
                                 'y':'/rest/of/path'},
                       '/%2FLa%20Pe%C3%B1a/rest/of/path')
        self.generates('*traverse', {'traverse':('a', u'La Pe\xf1a')},
                       '/a/La%20Pe%C3%B1a')
        self.generates('/foo/:id.html', {'id':'bar'}, '/foo/bar.html')

class DummyRootFactory(object):
    def __init__(self, result):
        self.result = result
    def __call__(self, request):
        self.request = request
        return self.result

class DummyContext(object):
    """ """
        
class DummyRequest(object):
    def __init__(self, environ):
        self.environ = environ
    
class DummyRoute(object):
    def __init__(self, generator):
        self.generate = generator
        
