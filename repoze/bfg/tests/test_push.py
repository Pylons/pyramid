import unittest

from zope.testing.cleanup import cleanUp

class Test_pushpage(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _zcmlConfigure(self):
        import repoze.bfg.includes
        import zope.configuration.xmlconfig
        zope.configuration.xmlconfig.file('configure.zcml',
                                          package=repoze.bfg.includes)

    def _getTargetClass(self):
        from repoze.bfg.push import pushpage
        return pushpage

    def _makeOne(self, template):
        return self._getTargetClass()(template)

    def test_decorated_has_same_name_as_wrapped(self):
        pp = self._makeOne('pp.pt')
        wrapped = pp(to_wrap)
        self.assertEqual(wrapped.__name__, 'to_wrap')
        self.assertEqual(wrapped.__module__, to_wrap.__module__)

    def test___call___passes_names_from_wrapped(self):
        self._zcmlConfigure()
        pp = self._makeOne('pp.pt')
        wrapped = pp(to_wrap)
        response = wrapped(object(), object())
        self.assertEqual(response.body,
                     '<p xmlns="http://www.w3.org/1999/xhtml">WRAPPED</p>')

def to_wrap(context, request):
    return {'wrapped': 'WRAPPED'}
