import unittest

from pyramid.config import Configurator
from pyramid import testing

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = Configurator(autocommit=True)
        self.config.begin()

    def tearDown(self):
        self.config.end()

    def test_my_view(self):
        from tutorial.views import my_view
        context = testing.DummyModel()
        request = testing.DummyRequest()
        info = my_view(context, request)
        self.assertEqual(info['project'], 'tutorial')
