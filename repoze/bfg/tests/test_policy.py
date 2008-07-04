import unittest

class SplitPathTests(unittest.TestCase):
    def _getFUT(self):
        from repoze.bfg.policy import split_path
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
   
class NaivePolicyTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.policy import NaivePolicy
        return NaivePolicy

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_class_conforms_to_IPolicy(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import IPolicy
        verifyClass(IPolicy, self._getTargetClass())

    def test_instance_conforms_to_IPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IPolicy
        verifyObject(IPolicy, self._makeOne())

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
    
