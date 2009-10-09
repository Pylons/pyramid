import unittest

from repoze.bfg import testing

class ViewTests(unittest.TestCase):
    def test_my_view(self):
        from myproject.views import my_view
        context = testing.DummyModel()
        request = testing.DummyRequest()
        self.assertEqual(my_view(context, request), {'project':'MyProject'})

