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
        view = reg.adapters.lookup((IRequest, INothing), IView, name='')
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

class TwillBase(unittest.TestCase):
    def setUp(self):
        import sys
        import twill
        from repoze.bfg.configuration import Configurator
        config = Configurator()
        config.load_zcml(self.config)
        twill.add_wsgi_intercept('localhost', 6543, config.make_wsgi_app)
        if sys.platform is 'win32': # pragma: no cover
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

class TestFixtureApp(TwillBase):
    config = 'repoze.bfg.tests.fixtureapp:configure.zcml'
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

class TestCCBug(TwillBase):
    # "unordered" as reported in IRC by author of
    # http://labs.creativecommons.org/2010/01/13/cc-engine-and-web-non-frameworks/
    config = 'repoze.bfg.tests.ccbugapp:configure.zcml'
    def test_it(self):
        import twill.commands
        browser = twill.commands.get_browser()
        browser.go('http://localhost:6543/licenses/1/v1/rdf')
        self.assertEqual(browser.get_code(), 200)
        self.assertEqual(browser.get_html(), 'rdf')
        browser.go('http://localhost:6543/licenses/1/v1/juri')
        self.assertEqual(browser.get_code(), 200)
        self.assertEqual(browser.get_html(), 'juri')

class TestHybridApp(TwillBase):
    # make sure views registered for a route "win" over views registered
    # without one, even though the context of the non-route view may
    # be more specific than the route view.
    config = 'repoze.bfg.tests.hybridapp:configure.zcml'
    def test_it(self):
        import twill.commands
        browser = twill.commands.get_browser()
        browser.go('http://localhost:6543/')
        self.assertEqual(browser.get_code(), 200)
        self.assertEqual(browser.get_html(), 'global')
        browser.go('http://localhost:6543/abc')
        self.assertEqual(browser.get_code(), 200)
        self.assertEqual(browser.get_html(), 'route')
        browser.go('http://localhost:6543/def')
        self.assertEqual(browser.get_code(), 200)
        self.assertEqual(browser.get_html(), 'route2')
        browser.go('http://localhost:6543/ghi')
        self.assertEqual(browser.get_code(), 200)
        self.assertEqual(browser.get_html(), 'global')
        browser.go('http://localhost:6543/jkl')
        self.assertEqual(browser.get_code(), 404)
        browser.go('http://localhost:6543/mno/global2')
        self.assertEqual(browser.get_code(), 404)
        browser.go('http://localhost:6543/pqr/global2')
        self.assertEqual(browser.get_code(), 200)
        self.assertEqual(browser.get_html(), 'global2')

class TestRestBugApp(TwillBase):
    # test bug reported by delijati 2010/2/3 (http://pastebin.com/d4cc15515)
    config = 'repoze.bfg.tests.restbugapp:configure.zcml'
    def test_it(self):
        import twill.commands
        browser = twill.commands.get_browser()
        browser.go('http://localhost:6543/pet')
        self.assertEqual(browser.get_code(), 200)
        self.assertEqual(browser.get_html(), 'gotten')

class TestViewDecoratorApp(TwillBase):
    config = 'repoze.bfg.tests.viewdecoratorapp:configure.zcml'
    def test_it(self):
        import twill.commands
        browser = twill.commands.get_browser()
        browser.go('http://localhost:6543/first')
        self.assertEqual(browser.get_code(), 200)
        self.failUnless('OK' in browser.get_html())

        browser.go('http://localhost:6543/second')
        self.assertEqual(browser.get_code(), 200)
        self.failUnless('OK2' in browser.get_html())

        browser.go('http://localhost:6543/third')
        self.assertEqual(browser.get_code(), 200)
        self.failUnless('OK3' in browser.get_html())

class DummyContext(object):
    pass

class DummyRequest:
    subpath = ('__init__.py',)
    traversed = None
    environ = {'REQUEST_METHOD':'GET', 'wsgi.version':(1,0)}
    def get_response(self, application):
        return application(None, None)

