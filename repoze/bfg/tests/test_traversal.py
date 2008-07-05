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

class NaivePolicyTests(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)
        
    def _getTargetClass(self):
        from repoze.bfg.traversal import NaiveTraversalPolicy
        return NaiveTraversalPolicy

    def _makeOne(self, *arg, **kw):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import ITraverser
        gsm.registerAdapter(DummyTraverser, (None,), ITraverser, '')
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_class_conforms_to_ITraversalPolicy(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ITraversalPolicy
        verifyClass(ITraversalPolicy, self._getTargetClass())

    def test_instance_conforms_to_ITraversalPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ITraversalPolicy
        verifyObject(ITraversalPolicy, self._makeOne())

    def test_call_nonkeyerror_raises(self):
        policy = self._makeOne()
        environ = {'PATH_INFO':'/foo'}
        root = None
        self.assertRaises(TypeError, policy, environ, root)

    def test_call_withconn_getitem_emptypath_nosubpath(self):
        policy = self._makeOne()
        context = DummyContext()
        environ = {'PATH_INFO':''}
        root = context
        ctx, name, subpath = policy(environ, root)
        self.assertEqual(context, ctx)
        self.assertEqual(name, '')
        self.assertEqual(subpath, [])

    def test_call_withconn_getitem_withpath_nosubpath(self):
        policy = self._makeOne()
        context = DummyContext()
        context2 = DummyContext(context)
        environ = {'PATH_INFO':'/foo/bar'}
        root = context
        ctx, name, subpath = policy(environ, root)
        self.assertEqual(context, ctx)
        self.assertEqual(name, 'bar')
        self.assertEqual(subpath, [])

    def test_call_withconn_getitem_withpath_withsubpath(self):
        policy = self._makeOne()
        context = DummyContext()
        context2 = DummyContext(context)
        environ = {'PATH_INFO':'/foo/bar/baz/buz'}
        root = context
        ctx, name, subpath = policy(environ, root)
        self.assertEqual(context, ctx)
        self.assertEqual(name, 'bar')
        self.assertEqual(subpath, ['baz', 'buz'])

class DummyContext:
    def __init__(self, next=None):
        self.next = next
        
    def __getitem__(self, name):
        if self.next is None:
            raise KeyError, name
        return self.next
    
class DummyTraverser:
    def __init__(self, context):
        self.context = context

    def __call__(self, environ, name):
        try:
            return self.context[name]
        except KeyError:
            return None
