import unittest
from pyramid.compat import is_unbound_method


class TestUnboundMethods(unittest.TestCase):
    def test_old_style_bound(self):
        self.assertFalse(is_unbound_method(OldStyle().run))

    def test_new_style_bound(self):
        self.assertFalse(is_unbound_method(NewStyle().run))

    def test_old_style_unbound(self):
        self.assertTrue(is_unbound_method(OldStyle.run))

    def test_new_style_unbound(self):
        self.assertTrue(is_unbound_method(NewStyle.run))

    def test_normal_func_unbound(self):
        def func():  # pragma: no cover
            return 'OK'

        self.assertFalse(is_unbound_method(func))


class OldStyle:
    def run(self):  # pragma: no cover
        return 'OK'


class NewStyle(object):
    def run(self):  # pragma: no cover
        return 'OK'
