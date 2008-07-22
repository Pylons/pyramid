import unittest

from zope.component.testing import PlacelessSetup

class SplitPathTests(unittest.TestCase):
    def _getFUT(self):
        from repoze.bfg.traversal import split_path
        return split_path
        
    def test_cleanPath_path_startswith_endswith(self):
        f = self._getFUT()
        self.assertEqual(f('/foo/'), ['foo'])

    def test_cleanPath_empty_elements(self):
        f = self._getFUT()
        self.assertEqual(f('foo///'), ['foo'])

    def test_cleanPath_onedot(self):
        f = self._getFUT()
        self.assertEqual(f('foo/./bar'), ['foo', 'bar'])

    def test_cleanPath_twodots(self):
        f = self._getFUT()
        self.assertEqual(f('foo/../bar'), ['bar'])

    def test_cleanPath_element_urllquoted(self):
        f = self._getFUT()
        self.assertEqual(f('/foo/space%20thing/bar'), ['foo', 'space thing',
                                                       'bar'])

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
        request = DummyRequest()
        verifyObject(ITraverser, self._makeOne(context, request))

    def test_call_pathel_with_no_getitem(self):
        request = DummyRequest()
        policy = self._makeOne(None, request)
        environ = self._getEnviron(PATH_INFO='/foo/bar')
        ctx, name, subpath = policy(environ)
        self.assertEqual(ctx, None)
        self.assertEqual(name, 'foo')
        self.assertEqual(subpath, ['bar'])

    def test_call_withconn_getitem_emptypath_nosubpath(self):
        root = DummyContext()
        request = DummyRequest()
        policy = self._makeOne(root, request)
        environ = self._getEnviron(PATH_INFO='')
        ctx, name, subpath = policy(environ)
        self.assertEqual(ctx, root)
        self.assertEqual(name, '')
        self.assertEqual(subpath, [])

    def test_call_withconn_getitem_withpath_nosubpath(self):
        foo = DummyContext()
        root = DummyContext(foo)
        request = DummyRequest()
        policy = self._makeOne(root, request)
        environ = self._getEnviron(PATH_INFO='/foo/bar')
        ctx, name, subpath = policy(environ)
        self.assertEqual(ctx, foo)
        self.assertEqual(name, 'bar')
        self.assertEqual(subpath, [])

    def test_call_withconn_getitem_withpath_withsubpath(self):
        foo = DummyContext()
        request = DummyRequest()
        root = DummyContext(foo)
        policy = self._makeOne(root, request)
        environ = self._getEnviron(PATH_INFO='/foo/bar/baz/buz')
        ctx, name, subpath = policy(environ)
        self.assertEqual(ctx, foo)
        self.assertEqual(name, 'bar')
        self.assertEqual(subpath, ['baz', 'buz'])

    def test_call_with_explicit_viewname(self):
        foo = DummyContext()
        request = DummyRequest()
        root = DummyContext(foo)
        policy = self._makeOne(root, request)
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
        request = DummyRequest()
        from zope.interface import directlyProvides
        from zope.location.interfaces import ILocation
        directlyProvides(root, ILocation)
        root.__name__ = None
        root.__parent__ = None
        # give bar a direct parent and name to mix things up a bit
        bar.__name__ = 'bar'
        bar.__parent__ = foo
        policy = self._makeOne(root, request)
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
    def _getFUT(self):
        from repoze.bfg.traversal import find_interface
        return find_interface

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
        finder = self._getFUT()
        result = finder(baz, IFoo)
        self.assertEqual(result.__name__, 'root')

class DummyContext(object):
    def __init__(self, next=None):
        self.next = next
        
    def __getitem__(self, name):
        if self.next is None:
            raise KeyError, name
        return self.next

class DummyRequest:
    pass
    
class DummyTraverser:
    def __init__(self, context):
        self.context = context

    def __call__(self, environ, name):
        try:
            return name, self.context[name]
        except KeyError:
            return name, None
