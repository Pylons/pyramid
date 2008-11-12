import unittest

from zope.component.testing import PlacelessSetup

class SplitPathTests(unittest.TestCase):
    def _callFUT(self, path):
        from repoze.bfg.traversal import split_path
        return split_path(path)
        
    def test_cleanPath_path_startswith_endswith(self):
        self.assertEqual(self._callFUT('/foo/'), ['foo'])

    def test_cleanPath_empty_elements(self):
        self.assertEqual(self._callFUT('foo///'), ['foo'])

    def test_cleanPath_onedot(self):
        self.assertEqual(self._callFUT('foo/./bar'), ['foo', 'bar'])

    def test_cleanPath_twodots(self):
        self.assertEqual(self._callFUT('foo/../bar'), ['bar'])

    def test_cleanPath_element_urllquoted(self):
        self.assertEqual(self._callFUT('/foo/space%20thing/bar'),
                         ['foo', 'space thing', 'bar'])

class ModelGraphTraverserTests(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)
        
    def _getTargetClass(self):
        from repoze.bfg.traversal import ModelGraphTraverser
        return ModelGraphTraverser

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def _getEnviron(self, **kw):
        environ = {}
        environ.update(kw)
        return environ

    def test_class_conforms_to_ITraverser(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ITraverser
        verifyClass(ITraverser, self._getTargetClass())

    def test_instance_conforms_to_ITraverser(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ITraverser
        context = DummyContext()
        verifyObject(ITraverser, self._makeOne(context))

    def test_call_pathel_with_no_getitem(self):
        policy = self._makeOne(None)
        environ = self._getEnviron(PATH_INFO='/foo/bar')
        ctx, name, subpath = policy(environ)
        self.assertEqual(ctx, None)
        self.assertEqual(name, 'foo')
        self.assertEqual(subpath, ['bar'])

    def test_call_withconn_getitem_emptypath_nosubpath(self):
        root = DummyContext()
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='')
        ctx, name, subpath = policy(environ)
        self.assertEqual(ctx, root)
        self.assertEqual(name, '')
        self.assertEqual(subpath, [])

    def test_call_withconn_getitem_withpath_nosubpath(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/foo/bar')
        ctx, name, subpath = policy(environ)
        self.assertEqual(ctx, foo)
        self.assertEqual(name, 'bar')
        self.assertEqual(subpath, [])

    def test_call_withconn_getitem_withpath_withsubpath(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/foo/bar/baz/buz')
        ctx, name, subpath = policy(environ)
        self.assertEqual(ctx, foo)
        self.assertEqual(name, 'bar')
        self.assertEqual(subpath, ['baz', 'buz'])

    def test_call_with_explicit_viewname(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/@@foo')
        ctx, name, subpath = policy(environ)
        self.assertEqual(ctx, root)
        self.assertEqual(name, 'foo')
        self.assertEqual(subpath, [])

    def test_call_with_ILocation_root(self):
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyContext(foo)
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import ILocation
        directlyProvides(root, ILocation)
        root.__name__ = None
        root.__parent__ = None
        # give bar a direct parent and name to mix things up a bit
        bar.__name__ = 'bar'
        bar.__parent__ = foo
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/foo/bar/baz')
        ctx, name, subpath = policy(environ)
        self.assertEqual(ctx, baz)
        self.assertEqual(name, '')
        self.assertEqual(subpath, [])
        self.assertEqual(ctx.__name__, 'baz')
        self.assertEqual(ctx.__parent__, bar)
        self.assertEqual(ctx.__parent__.__name__, 'bar')
        self.assertEqual(ctx.__parent__.__parent__, foo)
        self.assertEqual(ctx.__parent__.__parent__.__name__, 'foo')
        self.assertEqual(ctx.__parent__.__parent__.__parent__, root)
        self.assertEqual(ctx.__parent__.__parent__.__parent__.__name__, None)
        self.assertEqual(ctx.__parent__.__parent__.__parent__.__parent__, None)

class FindInterfaceTests(unittest.TestCase):
    def _callFUT(self, context, iface):
        from repoze.bfg.traversal import find_interface
        return find_interface(context, iface)

    def test_it(self):
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyContext(foo)
        root.__parent__ = None
        root.__name__ = 'root'
        foo.__parent__ = root
        foo.__name__ = 'foo'
        bar.__parent__ = foo
        bar.__name__ = 'bar'
        baz.__parent__ = bar
        baz.__name__ = 'baz'
        request = DummyRequest()
        from zope.interface import directlyProvides
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        directlyProvides(root, IFoo)
        result = self._callFUT(baz, IFoo)
        self.assertEqual(result.__name__, 'root')

class ModelURLTests(unittest.TestCase):
    def _callFUT(self, model, request, *elements):
        from repoze.bfg.traversal import model_url
        return model_url(model, request, *elements)

    def test_extra_args(self):
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyContext(foo)
        root.__parent__ = None
        root.__name__ = None
        foo.__parent__ = root
        foo.__name__ = 'foo '
        bar.__parent__ = foo
        bar.__name__ = 'bar'
        baz.__parent__ = bar
        baz.__name__ = 'baz'
        request = DummyRequest()
        result = self._callFUT(baz, request, 'this/theotherthing', 'that')

        self.assertEqual(
            result,
            'http://example.com:5432/foo%20/bar/baz/this/theotherthing/that')

    def test_root_default_app_url_endswith_slash(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        request = DummyRequest()
        request.application_url = 'http://example.com:5432/'
        result = self._callFUT(root, request)
        self.assertEqual(result, 'http://example.com:5432/')

    def test_root_default_app_url_endswith_nonslash(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        request = DummyRequest()
        request.application_url = 'http://example.com:5432'
        result = self._callFUT(root, request)
        self.assertEqual(result, 'http://example.com:5432/')

    def test_nonroot_default_app_url_endswith_slash(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        other = DummyContext()
        other.__parent__ = root
        other.__name__ = 'nonroot object'
        request = DummyRequest()
        request.application_url = 'http://example.com:5432/'
        result = self._callFUT(other, request)
        self.assertEqual(result, 'http://example.com:5432/nonroot%20object/')

    def test_nonroot_default_app_url_endswith_nonslash(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        other = DummyContext()
        other.__parent__ = root
        other.__name__ = 'nonroot object'
        request = DummyRequest()
        request.application_url = 'http://example.com:5432'
        result = self._callFUT(other, request)
        self.assertEqual(result, 'http://example.com:5432/nonroot%20object/')

class FindRootTests(unittest.TestCase):
    def _callFUT(self, context):
        from repoze.bfg.traversal import find_root
        return find_root(context)

    def test_it(self):
        dummy = DummyContext()
        baz = DummyContext()
        baz.__parent__ = dummy
        baz.__name__ = 'baz'
        dummy.__parent__ = None
        dummy.__name__ = None
        result = self._callFUT(baz)
        self.assertEqual(result, dummy)

class FindModelTests(unittest.TestCase):
    def _callFUT(self, context, name):
        from repoze.bfg.traversal import find_model
        return find_model(context, name)

    def _registerTraverserFactory(self, traverser):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import ITraverserFactory
        from zope.interface import Interface
        gsm.registerAdapter(traverser, (Interface,), ITraverserFactory)

    def test_relative_found(self):
        dummy = DummyContext()
        baz = DummyContext()
        traverser = make_traverser(baz, '', [])
        self._registerTraverserFactory(traverser)
        result = self._callFUT(dummy, 'baz')
        self.assertEqual(result, baz)

    def test_relative_notfound(self):
        dummy = DummyContext()
        baz = DummyContext()
        traverser = make_traverser(baz, 'bar', [])
        self._registerTraverserFactory(traverser)
        self.assertRaises(KeyError, self._callFUT, dummy, 'baz')

    def test_absolute_found(self):
        dummy = DummyContext()
        baz = DummyContext()
        baz.__parent__ = dummy
        baz.__name__ = 'baz'
        dummy.__parent__ = None
        dummy.__name__ = None
        traverser = make_traverser(dummy, '', [])
        self._registerTraverserFactory(traverser)
        result = self._callFUT(baz, '/')
        self.assertEqual(result, dummy)
        self.assertEqual(dummy.wascontext, True)

    def test_absolute_notfound(self):
        dummy = DummyContext()
        baz = DummyContext()
        baz.__parent__ = dummy
        baz.__name__ = 'baz'
        dummy.__parent__ = None
        dummy.__name__ = None
        traverser = make_traverser(dummy, 'fuz', [])
        self._registerTraverserFactory(traverser)
        self.assertRaises(KeyError, self._callFUT, baz, '/')
        self.assertEqual(dummy.wascontext, True)

class ModelPathTests(unittest.TestCase):
    def _callFUT(self, model, *elements):
        from repoze.bfg.traversal import model_path
        return model_path(model, *elements)

    def test_it(self):
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyContext(foo)
        root.__parent__ = None
        root.__name__ = None
        foo.__parent__ = root
        foo.__name__ = 'foo '
        bar.__parent__ = foo
        bar.__name__ = 'bar'
        baz.__parent__ = bar
        baz.__name__ = 'baz'
        result = self._callFUT(baz, 'this/theotherthing', 'that')
        self.assertEqual(result, '/foo /bar/baz/this/theotherthing/that')

    def test_root_default(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        request = DummyRequest()
        result = self._callFUT(root)
        self.assertEqual(result, '/')
        
    def test_nonroot_default(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        other = DummyContext()
        other.__parent__ = root
        other.__name__ = 'other'
        request = DummyRequest()
        result = self._callFUT(other)
        self.assertEqual(result, '/other')

def make_traverser(*args):
    class DummyTraverser(object):
        def __init__(self, context):
            context.wascontext = True
        def __call__(self, environ):
            return args
    return DummyTraverser
        
class DummyContext(object):
    def __init__(self, next=None):
        self.next = next
        
    def __getitem__(self, name):
        if self.next is None:
            raise KeyError, name
        return self.next

class DummyRequest:
    application_url = 'http://example.com:5432/'

