import unittest

class TestReify(unittest.TestCase):
    def _makeOne(self, wrapped):
        from repoze.bfg.decorator import reify
        return reify(wrapped)

    def test___get__withinst(self):
        def wrapped(inst):
            return 'a'
        decorator = self._makeOne(wrapped)
        inst = Dummy()
        result = decorator.__get__(inst)
        self.assertEqual(result, 'a')
        self.assertEqual(inst.__dict__['wrapped'], 'a')

    def test___get__noinst(self):
        decorator = self._makeOne(None)
        result = decorator.__get__(None)
        self.assertEqual(result, decorator)

class Dummy(object):
    pass
