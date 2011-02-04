import os
import unittest

from pyramid.wsgi import wsgiapp
from pyramid.view import view_config
from pyramid.view import static

from zope.interface import Interface

class INothing(Interface):
    pass

@view_config(for_=INothing)
@wsgiapp
def wsgiapptest(environ, start_response):
    """ """
    return '123'

class WGSIAppPlusViewConfigTests(unittest.TestCase):
    def test_it(self):
        from venusian import ATTACH_ATTR
        import types
        self.failUnless(getattr(wsgiapptest, ATTACH_ATTR))
        self.failUnless(type(wsgiapptest) is types.FunctionType)
        context = DummyContext()
        request = DummyRequest()
        result = wsgiapptest(context, request)
        self.assertEqual(result, '123')

    def test_scanned(self):
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.config import Configurator
        from pyramid.tests import test_integration
        config = Configurator()
        config.scan(test_integration)
        config.commit()
        reg = config.registry
        view = reg.adapters.lookup(
            (IViewClassifier, IRequest, INothing), IView, name='')
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

class IntegrationBase(unittest.TestCase):
    root_factory = None
    package = None
    def setUp(self):
        from pyramid.config import Configurator
        config = Configurator(root_factory=self.root_factory,
                              package=self.package)
        config.begin()
        config.include(self.package)
        config.commit()
        app = config.make_wsgi_app()
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.config = config

    def tearDown(self):
        self.config.end()

class TestFixtureApp(IntegrationBase):
    package = 'pyramid.tests.fixtureapp'
    def test_another(self):
        res = self.testapp.get('/another.html', status=200)
        self.assertEqual(res.body, 'fixture')

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertEqual(res.body, 'fixture')

    def test_dummyskin(self):
        self.testapp.get('/dummyskin.html', status=404)

    def test_error(self):
        res = self.testapp.get('/error.html', status=200)
        self.assertEqual(res.body, 'supressed')

    def test_protected(self):
        self.testapp.get('/protected.html', status=403)

class TestCCBug(IntegrationBase):
    # "unordered" as reported in IRC by author of
    # http://labs.creativecommons.org/2010/01/13/cc-engine-and-web-non-frameworks/
    package = 'pyramid.tests.ccbugapp'
    def test_rdf(self):
        res = self.testapp.get('/licenses/1/v1/rdf', status=200)
        self.assertEqual(res.body, 'rdf')

    def test_juri(self):
        res = self.testapp.get('/licenses/1/v1/juri', status=200)
        self.assertEqual(res.body, 'juri')

class TestHybridApp(IntegrationBase):
    # make sure views registered for a route "win" over views registered
    # without one, even though the context of the non-route view may
    # be more specific than the route view.
    package = 'pyramid.tests.hybridapp'
    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertEqual(res.body, 'global')

    def test_abc(self):
        res = self.testapp.get('/abc', status=200)
        self.assertEqual(res.body, 'route')

    def test_def(self):
        res = self.testapp.get('/def', status=200)
        self.assertEqual(res.body, 'route2')

    def test_ghi(self):
        res = self.testapp.get('/ghi', status=200)
        self.assertEqual(res.body, 'global')

    def test_jkl(self):
        self.testapp.get('/jkl', status=404)

    def test_mno(self):
        self.testapp.get('/mno', status=404)

    def test_pqr_global2(self):
        res = self.testapp.get('/pqr/global2', status=200)
        self.assertEqual(res.body, 'global2')

    def test_error(self):
        res = self.testapp.get('/error', status=200)
        self.assertEqual(res.body, 'supressed')

    def test_error2(self):
        res = self.testapp.get('/error2', status=200)
        self.assertEqual(res.body, 'supressed2')

    def test_error_sub(self):
        res = self.testapp.get('/error_sub', status=200)
        self.assertEqual(res.body, 'supressed2')

class TestRestBugApp(IntegrationBase):
    # test bug reported by delijati 2010/2/3 (http://pastebin.com/d4cc15515)
    package = 'pyramid.tests.restbugapp'
    def test_it(self):
        res = self.testapp.get('/pet', status=200)
        self.assertEqual(res.body, 'gotten')

class TestViewDecoratorApp(IntegrationBase):
    package = 'pyramid.tests.viewdecoratorapp'
    def _configure_mako(self):
        tmpldir = os.path.join(os.path.dirname(__file__), 'viewdecoratorapp',
                               'views')
        self.config.registry.settings['mako.directories'] = tmpldir

    def test_first(self):
        # we use mako here instead of chameleon because it works on Jython
        self._configure_mako()
        res = self.testapp.get('/first', status=200)
        self.failUnless('OK' in res.body)

    def test_second(self):
        # we use mako here instead of chameleon because it works on Jython
        self._configure_mako()
        res = self.testapp.get('/second', status=200)
        self.failUnless('OK2' in res.body)

class TestViewPermissionBug(IntegrationBase):
    # view_execution_permitted bug as reported by Shane at http://lists.repoze.org/pipermail/repoze-dev/2010-October/003603.html
    package = 'pyramid.tests.permbugapp'
    def test_test(self):
        res = self.testapp.get('/test', status=200)
        self.failUnless('ACLDenied' in res.body)

    def test_x(self):
        self.testapp.get('/x', status=403)

class TestDefaultViewPermissionBug(IntegrationBase):
    # default_view_permission bug as reported by Wiggy at http://lists.repoze.org/pipermail/repoze-dev/2010-October/003602.html
    package = 'pyramid.tests.defpermbugapp'
    def test_x(self):
        res = self.testapp.get('/x', status=403)
        self.failUnless('failed permission check' in res.body)

    def test_y(self):
        res = self.testapp.get('/y', status=403)
        self.failUnless('failed permission check' in res.body)

    def test_z(self):
        res = self.testapp.get('/z', status=200)
        self.failUnless('public' in res.body)

from pyramid.tests.exceptionviewapp.models import AnException, NotAnException
excroot = {'anexception':AnException(),
           'notanexception':NotAnException()}

class TestExceptionViewsApp(IntegrationBase):
    package = 'pyramid.tests.exceptionviewapp'
    root_factory = lambda *arg: excroot
    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('maybe' in res.body)

    def test_notanexception(self):
        res = self.testapp.get('/notanexception', status=200)
        self.failUnless('no' in res.body)

    def test_anexception(self):
        res = self.testapp.get('/anexception', status=200)
        self.failUnless('yes' in res.body)

    def test_route_raise_exception(self):
        res = self.testapp.get('/route_raise_exception', status=200)
        self.failUnless('yes' in res.body)

    def test_route_raise_exception2(self):
        res = self.testapp.get('/route_raise_exception2', status=200)
        self.failUnless('yes' in res.body)

    def test_route_raise_exception3(self):
        res = self.testapp.get('/route_raise_exception3', status=200)
        self.failUnless('whoa' in res.body)

    def test_route_raise_exception4(self):
        res = self.testapp.get('/route_raise_exception4', status=200)
        self.failUnless('whoa' in res.body)

class ImperativeIncludeConfigurationTest(unittest.TestCase):
    def setUp(self):
        from pyramid.config import Configurator
        config = Configurator()
        from pyramid.tests.includeapp1.root import configure
        configure(config)
        app = config.make_wsgi_app()
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.config = config

    def tearDown(self):
        self.config.end()

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('root' in res.body)

    def test_two(self):
        res = self.testapp.get('/two', status=200)
        self.failUnless('two' in res.body)

    def test_three(self):
        res = self.testapp.get('/three', status=200)
        self.failUnless('three' in res.body)

class SelfScanAppTest(unittest.TestCase):
    def setUp(self):
        from pyramid.tests.selfscanapp import main
        config = main()
        app = config.make_wsgi_app()
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.config = config

    def tearDown(self):
        self.config.end()

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('root' in res.body)

    def test_two(self):
        res = self.testapp.get('/two', status=200)
        self.failUnless('two' in res.body)

class DummyContext(object):
    pass

class DummyRequest:
    subpath = ('__init__.py',)
    traversed = None
    environ = {'REQUEST_METHOD':'GET', 'wsgi.version':(1,0)}
    def get_response(self, application):
        return application(None, None)

