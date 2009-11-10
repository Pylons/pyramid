import unittest

from repoze.bfg import testing

class ViewTests(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from tutorial.views import my_view
        context = testing.DummyModel()
        request = testing.DummyRequest()
        info = my_view(context, request)
        self.assertEqual(info['project'], 'tutorial')
