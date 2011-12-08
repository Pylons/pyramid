import unittest
from pyramid.compat import PY3

class Test_WeakOrderedSet(unittest.TestCase):
    def _makeOne(self):
        from pyramid.config import WeakOrderedSet
        return WeakOrderedSet()

    def test_ctor(self):
        wos = self._makeOne()
        self.assertEqual(len(wos), 0)
        self.assertEqual(wos.last, None)

    def test_add_item(self):
        wos = self._makeOne()
        reg = Dummy()
        wos.add(reg)
        self.assertEqual(list(wos), [reg])
        self.assertTrue(reg in wos)
        self.assertEqual(wos.last, reg)

    def test_add_multiple_items(self):
        wos = self._makeOne()
        reg1 = Dummy()
        reg2 = Dummy()
        wos.add(reg1)
        wos.add(reg2)
        self.assertEqual(len(wos), 2)
        self.assertEqual(list(wos), [reg1, reg2])
        self.assertTrue(reg1 in wos)
        self.assertTrue(reg2 in wos)
        self.assertEqual(wos.last, reg2)

    def test_add_duplicate_items(self):
        wos = self._makeOne()
        reg = Dummy()
        wos.add(reg)
        wos.add(reg)
        self.assertEqual(len(wos), 1)
        self.assertEqual(list(wos), [reg])
        self.assertTrue(reg in wos)
        self.assertEqual(wos.last, reg)

    def test_weakref_removal(self):
        wos = self._makeOne()
        reg = Dummy()
        wos.add(reg)
        wos.remove(reg)
        self.assertEqual(len(wos), 0)
        self.assertEqual(list(wos), [])
        self.assertEqual(wos.last, None)

    def test_last_updated(self):
        wos = self._makeOne()
        reg = Dummy()
        reg2 = Dummy()
        wos.add(reg)
        wos.add(reg2)
        wos.remove(reg2)
        self.assertEqual(len(wos), 1)
        self.assertEqual(list(wos), [reg])
        self.assertEqual(wos.last, reg)

    def test_empty(self):
        wos = self._makeOne()
        reg = Dummy()
        reg2 = Dummy()
        wos.add(reg)
        wos.add(reg2)
        wos.empty()
        self.assertEqual(len(wos), 0)
        self.assertEqual(list(wos), [])
        self.assertEqual(wos.last, None)

class Test_object_description(unittest.TestCase):
    def _callFUT(self, object):
        from pyramid.util import object_description
        return object_description(object)

    def test_string(self):
        self.assertEqual(self._callFUT('abc'), 'abc')

    def test_int(self):
        self.assertEqual(self._callFUT(1), '1')

    def test_bool(self):
        self.assertEqual(self._callFUT(True), 'True')

    def test_None(self):
        self.assertEqual(self._callFUT(None), 'None')

    def test_float(self):
        self.assertEqual(self._callFUT(1.2), '1.2')

    def test_tuple(self):
        self.assertEqual(self._callFUT(('a', 'b')), "('a', 'b')")

    def test_set(self):
        if PY3: # pragma: no cover
            self.assertEqual(self._callFUT(set(['a'])), "{'a'}")
        else: # pragma: no cover
            self.assertEqual(self._callFUT(set(['a'])), "set(['a'])")

    def test_list(self):
        self.assertEqual(self._callFUT(['a']), "['a']")

    def test_dict(self):
        self.assertEqual(self._callFUT({'a':1}), "{'a': 1}")

    def test_nomodule(self):
        o = object()
        self.assertEqual(self._callFUT(o), 'object %s' % str(o))

    def test_module(self):
        import pyramid
        self.assertEqual(self._callFUT(pyramid), 'module pyramid')

    def test_method(self):
        self.assertEqual(
            self._callFUT(self.test_method),
            'method test_method of class pyramid.tests.test_util.'
            'Test_object_description')

    def test_class(self):
        self.assertEqual(
            self._callFUT(self.__class__),
            'class pyramid.tests.test_util.Test_object_description')

    def test_function(self):
        self.assertEqual(
            self._callFUT(dummyfunc),
            'function pyramid.tests.test_util.dummyfunc')

    def test_instance(self):
        inst = Dummy()
        self.assertEqual(
            self._callFUT(inst),
            "object %s" % str(inst))
        
    def test_shortened_repr(self):
        inst = ['1'] * 1000
        self.assertEqual(
            self._callFUT(inst),
            str(inst)[:100] + ' ... ]')

def dummyfunc(): pass

class Dummy(object):
    pass
