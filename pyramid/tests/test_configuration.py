import unittest

class ConfiguratorTests(unittest.TestCase):
    def setUp(self):
        from zope.deprecation import __show__
        __show__.off()

    def tearDown(self):
        from zope.deprecation import __show__
        __show__.on()
        
    def _makeOne(self, *arg, **kw):
        from pyramid.configuration import Configurator
        return Configurator(*arg, **kw)

    def test_autocommit_true(self):
        config = self._makeOne()
        self.assertEqual(config.autocommit, True)
        


