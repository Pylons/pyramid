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
        
    def test_package_is_not_None(self):
        import pyramid
        config = self._makeOne(package='pyramid')
        self.assertEqual(config.package, pyramid)

    def test_with_package(self):
        import pyramid
        config = self._makeOne()
        newconfig = config.with_package('pyramid')
        self.assertEqual(newconfig.package, pyramid)


