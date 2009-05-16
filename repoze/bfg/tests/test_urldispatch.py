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

    def test_init_custom_default_context_factory_dont_decorate(self):
        from zope.component import getGlobalSiteManager
        from repoze.bfg.interfaces import IRoutesContextFactory
        class Dummy(object):
            pass
        gsm = getGlobalSiteManager()
        gsm.registerUtility(Dummy, IRoutesContextFactory)
        mapper = self._makeOne(None)
        self.assertEqual(mapper.default_context_factory,
                         Dummy)
        self.assertEqual(mapper.decorate_context, True)

    def test_init_custom_default_context_factory_decorate(self):
        from zope.component import getGlobalSiteManager
        from repoze.bfg.interfaces import IRoutesContextFactory
        from repoze.bfg.interfaces import IRoutesContext
        from zope.interface import implements
        class Dummy(object):
            implements(IRoutesContext)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(Dummy, IRoutesContextFactory)
        mapper = self._makeOne(None)
        self.assertEqual(mapper.default_context_factory,
                         Dummy)
        self.assertEqual(mapper.decorate_context, False)

    def test_no_route_matches(self):
        marker = ()
        get_root = make_get_root(marker)
        mapper = self._makeOne(get_root)
        environ = self._getEnviron(PATH_INFO='/')
        result = mapper(environ)
        self.assertEqual(result, marker)
        self.assertEqual(mapper.environ, environ)

    def test_route_matches(self):
        marker = ()
        get_root = make_get_root(marker)
        mapper = self._makeOne(get_root)
        mapper.connect('foo', 'archives/:action/:article', foo='foo')
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        from repoze.bfg.interfaces import IRoutesContext
        self.failUnless(IRoutesContext.providedBy(result))
        self.assertEqual(result.foo, 'foo')
        self.assertEqual(result.action, 'action1')
        self.assertEqual(result.article, 'article1')
        routing_args = environ['wsgiorg.routing_args'][1]
        self.assertEqual(routing_args['foo'], 'foo')
        self.assertEqual(routing_args['action'], 'action1')
        self.assertEqual(routing_args['article'], 'article1')
        self.assertEqual(environ['bfg.route'].name, 'foo')

    def test_unnamed_root_route_matches(self):
        mapper = self._makeOne(None)
        mapper.connect('')
        environ = self._getEnviron(PATH_INFO='/')
        result = mapper(environ)
        from repoze.bfg.interfaces import IRoutesContext
        self.failUnless(IRoutesContext.providedBy(result))
        self.assertEqual(environ['bfg.route'].name, None)

    def test_named_root_route_matches(self):
        mapper = self._makeOne(None)
        mapper.connect('root', '')
        environ = self._getEnviron(PATH_INFO='/')
        result = mapper(environ)
        from repoze.bfg.interfaces import IRoutesContext
        self.failUnless(IRoutesContext.providedBy(result))
        self.assertEqual(environ['bfg.route'].name, 'root')

    def test_unicode_in_route_default(self):
        marker = ()
        get_root = make_get_root(marker)
        mapper = self._makeOne(get_root)
        class DummyRoute2:
            routepath = ':id'
            _factory = None
            _provides = ()
        la = unicode('\xc3\xb1a', 'utf-8')
        mapper.routematch = lambda *arg: ({la:'id'}, DummyRoute2)
        mapper.connect('whatever', ':la')
        environ = self._getEnviron(PATH_INFO='/foo')
        result = mapper(environ)
        from repoze.bfg.interfaces import IRoutesContext
        self.failUnless(IRoutesContext.providedBy(result))
        self.assertEqual(getattr(result, la.encode('utf-8')), 'id')
        routing_args = environ['wsgiorg.routing_args'][1]
        self.assertEqual(routing_args[la.encode('utf-8')], 'id')

    def test_no_fallback_get_root(self):
        from repoze.bfg.urldispatch import RoutesContextNotFound
        marker = ()
        mapper = self._makeOne(None)
        mapper.connect('wont', 'wont/:be/:found')
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        self.failUnless(isinstance(result, RoutesContextNotFound))

    def test_custom_factory(self):
        marker = ()
        get_root = make_get_root(marker)
        mapper = self._makeOne(get_root)
        from zope.interface import implements, Interface
        class IDummy(Interface):
            pass
        class Dummy(object):
            implements(IDummy)
            def __init__(self, **kw):
                self.__dict__.update(kw)
        mapper.connect('article', 'archives/:action/:article',
                       _factory=Dummy)
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        self.assertEqual(result.action, 'action1')
        self.assertEqual(result.article, 'article1')
        from repoze.bfg.interfaces import IRoutesContext
        self.failUnless(IRoutesContext.providedBy(result))
        self.failUnless(isinstance(result, Dummy))
        self.failUnless(IDummy.providedBy(result))
        self.failIf(hasattr(result, '_factory'))

    def test_decorate_context_false(self):
        from repoze.bfg.interfaces import IRoutesContext
        class Dummy:
            def __init__(self, **kw):
                pass
        mapper = self._makeOne(None)
        mapper.connect('root', '')
        environ = self._getEnviron(PATH_INFO='/')
        mapper.decorate_context = False
        mapper.default_context_factory = Dummy
        result = mapper(environ)
        self.failIf(IRoutesContext.providedBy(result))

    def test_decorate_context_true(self):
        from repoze.bfg.interfaces import IRoutesContext
        class Dummy:
            def __init__(self, **kw):
                pass
        mapper = self._makeOne(None)
        mapper.connect('root', '')
        environ = self._getEnviron(PATH_INFO='/')
        mapper.decorate_context = True
        mapper.default_context_factory = Dummy
        result = mapper(environ)
        self.failUnless(IRoutesContext.providedBy(result))

    def test_has_routes(self):
        mapper = self._makeOne(None)
        self.assertEqual(mapper.has_routes(), False)
        mapper.connect('whatever', 'archives/:action/:article')
        self.assertEqual(mapper.has_routes(), True)

    def test_url_for(self):
        marker = ()
        get_root = make_get_root(marker)
        mapper = self._makeOne(get_root)
        mapper.connect('whatever', 'archives/:action/:article')
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        route = DummyRoute('yo')
        environ['bfg.route'] = route
        result = mapper(environ)
        from routes import url_for
        result = url_for(action='action2', article='article2')
        self.assertEqual(result, '/archives/action2/article2')

class TestRoutesContextNotFound(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.urldispatch import RoutesContextNotFound
        return RoutesContextNotFound

    def _makeOne(self, msg):
        return self._getTargetClass()(msg)

    def test_it(self):
        inst = self._makeOne('hi')
        self.assertEqual(inst.msg, 'hi')

def make_get_root(result):
    def dummy_get_root(environ):
        return result
    return dummy_get_root

class RoutesModelTraverserTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.urldispatch import RoutesModelTraverser
        return RoutesModelTraverser

    def _makeOne(self, model):
        klass = self._getTargetClass()
        return klass(model)

    def test_class_conforms_to_ITraverser(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ITraverser
        verifyClass(ITraverser, self._getTargetClass())

    def test_instance_conforms_to_ITraverser(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ITraverser
        verifyObject(ITraverser, self._makeOne(None))

    def test_it_nothingfancy(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        routing_args = ((), {})
        route = DummyRoute('yo')
        environ = {'wsgiorg.routing_args': routing_args, 'bfg.route': route}
        result = traverser(environ)
        self.assertEqual(result[0], model)
        self.assertEqual(result[1], 'yo')
        self.assertEqual(result[2], [])
        self.assertEqual(result[3], None)
        self.assertEqual(result[4], model)
        self.assertEqual(result[5], None)

    def test_call_with_subpath(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        routing_args = ((), {'subpath':'/a/b/c'})
        route = DummyRoute('yo')
        environ = {'wsgiorg.routing_args':routing_args, 'bfg.route': route}
        result = traverser(environ)
        self.assertEqual(result[0], model)
        self.assertEqual(result[1], 'yo')
        self.assertEqual(result[2], ['a', 'b','c'])
        self.assertEqual(result[3], None)
        self.assertEqual(result[4], model)
        self.assertEqual(result[5], None)

    def test_with_path_info(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        routing_args = ((), {'path_info':'foo/bar'})
        route = DummyRoute('yo')
        environ = {'wsgiorg.routing_args': routing_args, 'bfg.route': route,
                   'PATH_INFO':'/a/b/foo/bar', 'SCRIPT_NAME':''}
        result = traverser(environ)
        self.assertEqual(result[0], model)
        self.assertEqual(result[1], 'yo')
        self.assertEqual(result[2], [])
        self.assertEqual(result[3], None)
        self.assertEqual(result[4], model)
        self.assertEqual(result[5], None)
        self.assertEqual(environ['PATH_INFO'], '/foo/bar')
        self.assertEqual(environ['SCRIPT_NAME'], '/a/b')

    def test_with_path_info_PATH_INFO_w_extra_slash(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        routing_args = ((), {'path_info':'foo/bar'})
        route = DummyRoute('yo')
        environ = {'wsgiorg.routing_args': routing_args, 'bfg.route':route,
                   'PATH_INFO':'/a/b//foo/bar', 'SCRIPT_NAME':''}
        result = traverser(environ)
        self.assertEqual(environ['PATH_INFO'], '/foo/bar')
        self.assertEqual(environ['SCRIPT_NAME'], '/a/b')

class RoutesContextURLTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.urldispatch import RoutesContextURL
        return RoutesContextURL

    def _makeOne(self, context, request):
        return self._getTargetClass()(context, request)

    def test_class_conforms_to_IContextURL(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import IContextURL
        verifyClass(IContextURL, self._getTargetClass())

    def test_instance_conforms_to_IContextURL(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IContextURL
        verifyObject(IContextURL, self._makeOne(None, None))

    def test_get_virtual_root(self):
        context_url = self._makeOne(1,2)
        self.assertEqual(context_url.virtual_root(), 1)

    def test_call(self):
        from routes import Mapper
        mapper = Mapper(controller_scan=None, directory=None,
                        explicit=True, always_scan=False)
        args = {'a':'1', 'b':'2', 'c':'3'}
        mapper.connect(':a/:b/:c')
        mapper.create_regs([])
        environ = {'SERVER_NAME':'example.com', 'wsgi.url_scheme':'http',
                   'SERVER_PORT':'80', 'wsgiorg.routing_args':((), args)}
        mapper.environ = environ
        from routes import request_config
        config = request_config()
        config.environ = environ
        config.mapper = mapper
        config.mapper_dict = args
        config.host = 'www.example.com'
        config.protocol = 'https'
        config.redirect = None
        request = DummyRequest()
        request.environ = environ
        context_url = self._makeOne(None, request)
        result = context_url()
        self.assertEqual(result, '/1/2/3')

class DummyContext(object):
    """ """
        
class DummyRequest(object):
    """ """
    
class DummyRoute(object):
    def __init__(self, name):
        self.name = name
        
