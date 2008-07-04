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



    
