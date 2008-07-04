import unittest

class ZODBGetitemPolicyTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.zodb import ZODBGetitemPolicy
        return ZODBGetitemPolicy

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
        verifyObject(IPolicy, self._makeOne('dbname'))

    def test_call_noconn(self):
        mw = self._makeOne('dbname')
        environ = {}
        self.assertRaises(ValueError, mw, environ)

    def test_call_withconn_attributeerror(self):
        mw = self._makeOne('dbname')
        environ = {'repoze.zodbconn.dbname': DummyConnection(DummyNoGetitem()),
                   'PATH_INFO':''}
        self.assertRaises(AttributeError, mw, environ)

    def test_call_withconn_getitem_emptypath_nosubpath(self):
        mw = self._makeOne('dbname')
        context = DummyContext()
        environ = {'repoze.zodbconn.dbname': DummyConnection(context),
                   'PATH_INFO':''}
        ctx, name, subpath = mw(environ)
        self.assertEqual(context, ctx)
        self.assertEqual(name, '')
        self.assertEqual(subpath, [])

    def test_call_withconn_getitem_withpath_nosubpath(self):
        mw = self._makeOne('dbname')
        context = DummyContext()
        context2 = DummyContext(context)
        environ = {'repoze.zodbconn.dbname': DummyConnection(context2),
                   'PATH_INFO':'/foo/bar'}
        ctx, name, subpath = mw(environ)
        self.assertEqual(context, ctx)
        self.assertEqual(name, 'bar')
        self.assertEqual(subpath, [])

    def test_call_withconn_getitem_withpath_withsubpath(self):
        mw = self._makeOne('dbname')
        context = DummyContext()
        context2 = DummyContext(context)
        environ = {'repoze.zodbconn.dbname': DummyConnection(context2),
                   'PATH_INFO':'/foo/bar/baz/buz'}
        ctx, name, subpath = mw(environ)
        self.assertEqual(context, ctx)
        self.assertEqual(name, 'bar')
        self.assertEqual(subpath, ['baz', 'buz'])

    def test_call_withprefix(self):
        mw = self._makeOne('dbname', ['a', 'b'])
        context = DummyContext()
        context2 = DummyContext(context)
        context3 = DummyContext(context2)
        environ = {'repoze.zodbconn.dbname': DummyConnection(context3),
                   'PATH_INFO':'/foo/bar/baz/buz'}
        ctx, name, subpath = mw(environ)
        self.assertEqual(context, ctx)
        self.assertEqual(name, 'foo')
        self.assertEqual(subpath, ['bar', 'baz', 'buz'])

class DummyNoGetitem:
    pass

class DummyContext:
    def __init__(self, next=None):
        self.next = next
        
    def __getitem__(self, name):
        if self.next is None:
            raise KeyError, name
        return self.next
    
class DummyConnection:
    def __init__(self, result):
        self.result = result
    def open(self):
        return self.result

    
