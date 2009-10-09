import unittest

from repoze.bfg import testing

class ViewTests(unittest.TestCase):
    """ These tests are unit tests for the view.  They test the
    functionality of *only* the view.  They register and use dummy
    implementations of repoze.bfg functionality to allow you to avoid
    testing 'too much'"""
    def test_my_view(self):
        from myproject.views import my_view
        context = testing.DummyModel()
        request = testing.DummyRequest()
        self.assertEqual(my_view(context, request), {'project':'MyProject'})

