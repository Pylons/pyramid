import unittest

from repoze.bfg.configuration import Configurator
from repoze.bfg import testing

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = Configurator()
        self.config.begin()

    def tearDown(self):
        self.config.end()

    def test_my_view(self):
        from tutorial.views import my_view
        context = testing.DummyModel()
        request = testing.DummyRequest()
        info = my_view(context, request)
        self.assertEqual(info['project'], 'tutorial')
