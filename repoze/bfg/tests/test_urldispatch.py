import unittest

class RoutesMapperTests(unittest.TestCase):
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
        from zope.interface import implements, Interface
        class IDummy(Interface):
            pass
        class Dummy(object):
            implements(IDummy)
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
        self.failUnless(IDummy.providedBy(result))
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

class TestRoutesModelTraverser(unittest.TestCase):
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

    def test_call(self):
        model = DummyModel()
        traverser = self._makeOne(model)
        result = traverser({})
        self.assertEqual(result[0], model)
        self.assertEqual(result[1], 'controller')
        self.assertEqual(result[2], '')

class DummyModel:
    controller = 'controller'
    
def make_get_root(result):
    def dummy_get_root(environ):
        return result
    return dummy_get_root


        

