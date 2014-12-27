import unittest

class TestUnboundMethods(unittest.TestCase):
    def test_old_style_bound(self):
        from pyramid.compat import is_unbound_method

        class OldStyle:
            def run(self):
                return 'OK'

        self.assertFalse(is_unbound_method(OldStyle().run))

    def test_new_style_bound(self):
        from pyramid.compat import is_unbound_method

        class NewStyle(object):
            def run(self):
                return 'OK'

        self.assertFalse(is_unbound_method(NewStyle().run))

    def test_old_style_unbound(self):
        from pyramid.compat import is_unbound_method

        class OldStyle:
            def run(self):
                return 'OK'

        self.assertTrue(is_unbound_method(OldStyle.run))

    def test_new_style_unbound(self):
        from pyramid.compat import is_unbound_method

        class NewStyle(object):
            def run(self):
                return 'OK'

        self.assertTrue(is_unbound_method(NewStyle.run))

    def test_normal_func_unbound(self):
        from pyramid.compat import is_unbound_method

        def func():
            return 'OK'

        self.assertFalse(is_unbound_method(func))
