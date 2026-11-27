import unittest


class Test_resource(unittest.TestCase):
    def test_import(self):
        with self.assertWarns(DeprecationWarning):
            import pyramid.resource  # noqa: F401
