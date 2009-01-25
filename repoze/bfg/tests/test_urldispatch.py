import unittest

class RoutesMapperTests(unittest.TestCase):
    def setUp(self):
        from zope.deprecation import __show__
        __show__.off()

    def tearDown(self):
        from zope.deprecation import __show__
        __show__.on()

    def _getEnviron(self, **kw):
        environ = {'SERVER_NAME':'localhost',
                   'wsgi.url_scheme':'http'}
        environ.update(kw)
        return environ

    def _getTargetClass(self):
        from repoze.bfg.urldispatch import RoutesMapper
        return RoutesMapper

    def _makeOne(self, get_root):
        klass = self._getTargetClass()
        return klass(get_root)

    def test_routes_mapper_no_route_matches(self):
        marker = ()
        get_root = make_get_root(marker)
        mapper = self._makeOne(get_root)
        environ = self._getEnviron(PATH_INFO='/')
        result = mapper(environ)
        self.assertEqual(result, marker)
        self.assertEqual(mapper.mapper.environ, environ)

    def test_routes_mapper_route_matches(self):
        marker = ()
        get_root = make_get_root(marker)
        mapper = self._makeOne(get_root)
        mapper.connect('archives/:action/:article', controller='foo')
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        from repoze.bfg.interfaces import IRoutesContext
        self.failUnless(IRoutesContext.providedBy(result))
        self.assertEqual(result.controller, 'foo')
        self.assertEqual(result.action, 'action1')
        self.assertEqual(result.article, 'article1')

    def test_routes_mapper_custom_context_factory(self):
        marker = ()
        get_root = make_get_root(marker)
        mapper = self._makeOne(get_root)
        class Dummy(object):
            def __init__(self, **kw):
                self.__dict__.update(kw)
        mapper.connect('archives/:action/:article', controller='foo',
                       context_factory=Dummy)
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        self.assertEqual(result.controller, 'foo')
        self.assertEqual(result.action, 'action1')
        self.assertEqual(result.article, 'article1')
        from repoze.bfg.interfaces import IRoutesContext
        self.failUnless(IRoutesContext.providedBy(result))
        self.failUnless(isinstance(result, Dummy))
        self.failIf(hasattr(result, 'context_factory'))

    def test_url_for(self):
        marker = ()
        get_root = make_get_root(marker)
        mapper = self._makeOne(get_root)
        mapper.connect('archives/:action/:article', controller='foo')
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        from routes import url_for
        result = url_for(controller='foo', action='action2', article='article2')
        self.assertEqual(result, '/archives/action2/article2')

class RoutesRootFactoryTests(unittest.TestCase):
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
        mapper.connect('archives/:action/:article', view_name='foo')
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        from repoze.bfg.interfaces import IRoutesContext
        self.failUnless(IRoutesContext.providedBy(result))
        self.assertEqual(result.view_name, 'foo')
        self.assertEqual(result.action, 'action1')
        self.assertEqual(result.article, 'article1')
        routing_args = environ['wsgiorg.routing_args'][1]
        self.assertEqual(routing_args['view_name'], 'foo')
        self.assertEqual(routing_args['action'], 'action1')
        self.assertEqual(routing_args['article'], 'article1')

    def test_unicode_in_route_default(self):
        marker = ()
        get_root = make_get_root(marker)
        mapper = self._makeOne(get_root)
        class DummyRoute:
            routepath = ':id'
            _factory = None
            _provides = ()
        la = unicode('\xc3\xb1a', 'utf-8')
        mapper.routematch = lambda *arg: ({la:'id'}, DummyRoute)
        mapper.connect(':la')
        environ = self._getEnviron(PATH_INFO='/foo')
        result = mapper(environ)
        from repoze.bfg.interfaces import IRoutesContext
        self.failUnless(IRoutesContext.providedBy(result))
        self.assertEqual(getattr(result, la.encode('utf-8')), 'id')
        routing_args = environ['wsgiorg.routing_args'][1]
        self.assertEqual(routing_args[la.encode('utf-8')], 'id')

    def test_no_fallback_get_root(self):
        marker = ()
        mapper = self._makeOne(None)
        mapper.connect('wont/:be/:found', view_name='foo')
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        from repoze.bfg.urldispatch import RoutesContextNotFound
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
        mapper.connect('archives/:action/:article', view_name='foo',
                       _factory=Dummy)
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        self.assertEqual(result.view_name, 'foo')
        self.assertEqual(result.action, 'action1')
        self.assertEqual(result.article, 'article1')
        from repoze.bfg.interfaces import IRoutesContext
        self.failUnless(IRoutesContext.providedBy(result))
        self.failUnless(isinstance(result, Dummy))
        self.failUnless(IDummy.providedBy(result))
        self.failIf(hasattr(result, '_factory'))

    def test_custom_provides(self):
        marker = ()
        get_root = make_get_root(marker)
        mapper = self._makeOne(get_root)
        from zope.interface import Interface
        class IDummy(Interface):
            pass
        mapper.connect('archives/:action/:article', view_name='foo',
                       _provides = [IDummy])
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        self.assertEqual(result.view_name, 'foo')
        self.assertEqual(result.action, 'action1')
        self.assertEqual(result.article, 'article1')
        from repoze.bfg.interfaces import IRoutesContext
        self.failUnless(IRoutesContext.providedBy(result))
        self.failUnless(IDummy.providedBy(result))
        self.failIf(hasattr(result, '_provides'))

    def test_has_routes(self):
        mapper = self._makeOne(None)
        self.assertEqual(mapper.has_routes(), False)
        mapper.connect('archives/:action/:article', view_name='foo')
        self.assertEqual(mapper.has_routes(), True)

    def test_url_for(self):
        marker = ()
        get_root = make_get_root(marker)
        mapper = self._makeOne(get_root)
        mapper.connect('archives/:action/:article', view_name='foo')
        environ = self._getEnviron(PATH_INFO='/archives/action1/article1')
        result = mapper(environ)
        from routes import url_for
        result = url_for(view_name='foo', action='action2', article='article2')
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


        

