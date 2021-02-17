import inspect
import unittest


class TestReify(unittest.TestCase):
    def _makeOne(self, wrapped):
        from pyramid.decorator import reify

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
        def wrapped(inst):
            return 'a'  # pragma: no cover

        decorator = self._makeOne(wrapped)
        result = decorator.__get__(None)
        self.assertEqual(result, decorator)

    def test_copy_docstring(self):
        def wrapped(inst):
            """Test doc"""
            return 'a'  # pragma: no cover

        decorator = self._makeOne(wrapped)
        assert decorator.__doc__ == 'Test doc'

    def test_not_function(self):
        """
        Because reify'd methods act as attributes, it's important that they
        aren't recognized as a function.  Otherwise tools like Sphinx may
        misbehave, like in https://github.com/Pylons/pyramid/issues/3655

        """

        def wrapped(inst):
            return 'a'  # pragma: no cover

        decorator = self._makeOne(wrapped)
        assert not inspect.isfunction(decorator)


class Dummy(object):
    pass
