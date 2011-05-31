import unittest

class TestIt(unittest.TestCase):
    def test_bwcompat_imports(self):
        from pyramid.httpexceptions import HTTPNotFound as one
        from pyramid.response import HTTPNotFound as two
        self.assertTrue(one is two)
        

