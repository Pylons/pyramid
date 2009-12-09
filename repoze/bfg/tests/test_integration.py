import os
import unittest

from repoze.bfg.wsgi import wsgiapp
from repoze.bfg.view import bfg_view
from repoze.bfg.view import static

from zope.interface import Interface

from repoze.bfg import testing

class INothing(Interface):
    pass

@bfg_view(for_=INothing)
@wsgiapp
def wsgiapptest(environ, start_response):
    """ """
    return '123'

class WGSIAppPlusBFGViewTests(unittest.TestCase):
    def test_it(self):
        import types
        self.failUnless(wsgiapptest.__bfg_view_settings__)
        self.failUnless(type(wsgiapptest) is types.FunctionType)
        context = DummyContext()
        request = DummyRequest()
        result = wsgiapptest(context, request)
        self.assertEqual(result, '123')

    def test_scanned(self):
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.configuration import Configurator
        from repoze.bfg.tests import test_integration
        config = Configurator()
        config.scan(test_integration)
        reg = config.registry
        view = reg.adapters.lookup((INothing, IRequest), IView, name='')
        self.assertEqual(view, wsgiapptest)

here = os.path.dirname(__file__)
staticapp = static(os.path.join(here, 'fixtures'))

class TestStaticApp(unittest.TestCase):
    def test_it(self):
        from webob import Request
        context = DummyContext()
        from StringIO import StringIO
        request = Request({'PATH_INFO':'',
                           'SCRIPT_NAME':'',
                           'SERVER_NAME':'localhost',
                           'SERVER_PORT':'80',
                           'REQUEST_METHOD':'GET',
                           'wsgi.version':(1,0),
                           'wsgi.url_scheme':'http',
                           'wsgi.input':StringIO()})
        request.subpath = ['minimal.pt']
        result = staticapp(context, request)
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(
            result.body,
            open(os.path.join(here, 'fixtures/minimal.pt'), 'r').read())

class TestFixtureApp(unittest.TestCase):
    def setUp(self):
        import sys
        import twill
        from repoze.bfg.configuration import Configurator
        config = Configurator()
        config.load_zcml('repoze.bfg.tests.fixtureapp:configure.zcml')
        twill.add_wsgi_intercept('localhost', 6543, config.make_wsgi_app)
        if sys.platform is 'win32':
            out = open('nul:', 'wb')
        else:
            out = open('/dev/null', 'wb')
        twill.set_output(out)
        testing.setUp(registry=config.registry)

    def tearDown(self):
        import twill
        import twill.commands
        twill.commands.reset_browser()
        twill.remove_wsgi_intercept('localhost', 6543)
        twill.set_output(None)
        testing.tearDown()

    def test_it(self):
        import twill.commands
        browser = twill.commands.get_browser()
        browser.go('http://localhost:6543/another.html')
        self.assertEqual(browser.get_code(), 200)
        self.assertEqual(browser.get_html(), 'fixture')
        browser.go('http://localhost:6543')
        self.assertEqual(browser.get_code(), 200)
        self.assertEqual(browser.get_html(), 'fixture')
        browser.go('http://localhost:6543/dummyskin.html')
        self.assertEqual(browser.get_code(), 404)

class DummyContext(object):
    pass

class DummyRequest:
    subpath = ('__init__.py',)
    traversed = None
    environ = {'REQUEST_METHOD':'GET', 'wsgi.version':(1,0)}
    def get_response(self, application):
        return application(None, None)

