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

class NaivePublishTraverserTests(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)
        
    def _getTargetClass(self):
        from repoze.bfg.traversal import NaivePublishTraverser
        return NaivePublishTraverser

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_class_conforms_to_IPublishTraverser(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import IPublishTraverser
        verifyClass(IPublishTraverser, self._getTargetClass())

    def test_instance_conforms_to_IPublishTraverser(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IPublishTraverser
        context = DummyContext()
        request = DummyRequest()
        verifyObject(IPublishTraverser, self._makeOne(context, request))

    def test_call_pathel_with_no_getitem(self):
        request = DummyRequest()
        policy = self._makeOne(None, request)
        ctx, name, subpath = policy('/foo/bar')
        self.assertEqual(ctx, None)
        self.assertEqual(name, 'foo')
        self.assertEqual(subpath, ['bar'])

    def test_call_withconn_getitem_emptypath_nosubpath(self):
        root = DummyContext()
        request = DummyRequest()
        policy = self._makeOne(root, request)
        ctx, name, subpath = policy('')
        self.assertEqual(ctx, root)
        self.assertEqual(name, '')
        self.assertEqual(subpath, [])

    def test_call_withconn_getitem_withpath_nosubpath(self):
        foo = DummyContext()
        root = DummyContext(foo)
        request = DummyRequest()
        policy = self._makeOne(root, request)
        ctx, name, subpath = policy('/foo/bar')
        self.assertEqual(ctx, foo)
        self.assertEqual(name, 'bar')
        self.assertEqual(subpath, [])

    def test_call_withconn_getitem_withpath_withsubpath(self):
        foo = DummyContext()
        request = DummyRequest()
        root = DummyContext(foo)
        policy = self._makeOne(root, request)
        ctx, name, subpath = policy('/foo/bar/baz/buz')
        self.assertEqual(ctx, foo)
        self.assertEqual(name, 'bar')
        self.assertEqual(subpath, ['baz', 'buz'])

    def test_call_with_explicit_viewname(self):
        foo = DummyContext()
        request = DummyRequest()
        root = DummyContext(foo)
        policy = self._makeOne(root, request)
        ctx, name, subpath = policy('/@@foo')
        self.assertEqual(ctx, root)
        self.assertEqual(name, 'foo')
        self.assertEqual(subpath, [])

class DummyContext:
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
