# -*- coding: utf-8 -*-

import datetime
import os
import unittest

from pyramid.wsgi import wsgiapp
from pyramid.view import view_config
from pyramid.static import static_view

from zope.interface import Interface

# 5 years from now (more or less)
fiveyrsfuture = datetime.datetime.utcnow() + datetime.timedelta(5*365)

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
        self.assertTrue(getattr(wsgiapptest, ATTACH_ATTR))
        self.assertTrue(type(wsgiapptest) is types.FunctionType)
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
        self.assertEqual(view.__original_view__, wsgiapptest)

class IntegrationBase(object):
    root_factory = None
    package = None
    def setUp(self):
        from pyramid.config import Configurator
        config = Configurator(root_factory=self.root_factory,
                              package=self.package)
        config.include(self.package)
        app = config.make_wsgi_app()
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.config = config

    def tearDown(self):
        self.config.end()

here = os.path.dirname(__file__)

class TestStaticAppBase(IntegrationBase):
    def _assertBody(self, body, filename):
        self.assertEqual(
            body.replace('\r', ''),
            open(filename, 'r').read()
            )

    def test_basic(self):
        res = self.testapp.get('/minimal.pt', status=200)
        self._assertBody(res.body, os.path.join(here, 'fixtures/minimal.pt'))

    def test_hidden(self):
        res = self.testapp.get('/static/.hiddenfile', status=200)
        self._assertBody(
            res.body,
            os.path.join(here, 'fixtures/static/.hiddenfile')
            )

    def test_highchars_in_pathelement(self):
        res = self.testapp.get('/static/héhé/index.html', status=200)
        self._assertBody(
            res.body, os.path.join(here, u'fixtures/static/héhé/index.html')
            )

    def test_highchars_in_filename(self):
        res = self.testapp.get('/static/héhé.html', status=200)
        self._assertBody(
            res.body, os.path.join(here, u'fixtures/static/héhé.html')
            )

    def test_not_modified(self):
        self.testapp.extra_environ = {
            'HTTP_IF_MODIFIED_SINCE':httpdate(fiveyrsfuture)}
        res = self.testapp.get('/minimal.pt', status=304)
        self.assertEqual(res.body, '')

    def test_file_in_subdir(self):
        fn = os.path.join(here, 'fixtures/static/index.html')
        res = self.testapp.get('/static/index.html', status=200)
        self._assertBody(res.body, fn)

    def test_directory_noslash_redir(self):
        res = self.testapp.get('/static', status=301)
        self.assertEqual(res.headers['Location'], 'http://localhost/static/')

    def test_directory_noslash_redir_preserves_qs(self):
        res = self.testapp.get('/static?a=1&b=2', status=301)
        self.assertEqual(res.headers['Location'],
                         'http://localhost/static/?a=1&b=2')

    def test_directory_noslash_redir_with_scriptname(self):
        self.testapp.extra_environ = {'SCRIPT_NAME':'/script_name'}
        res = self.testapp.get('/static', status=301)
        self.assertEqual(res.headers['Location'],
                         'http://localhost/script_name/static/')

    def test_directory_withslash(self):
        fn = os.path.join(here, 'fixtures/static/index.html')
        res = self.testapp.get('/static/', status=200)
        self._assertBody(res.body, fn)

    def test_range_inclusive(self):
        self.testapp.extra_environ = {'HTTP_RANGE':'bytes=1-2'}
        res = self.testapp.get('/static/index.html', status=206)
        self.assertEqual(res.body, 'ht')

    def test_range_tilend(self):
        self.testapp.extra_environ = {'HTTP_RANGE':'bytes=-5'}
        res = self.testapp.get('/static/index.html', status=206)
        self.assertEqual(res.body, 'tml>\n')

    def test_range_notbytes(self):
        self.testapp.extra_environ = {'HTTP_RANGE':'kHz=-5'}
        res = self.testapp.get('/static/index.html', status=200)
        self._assertBody(res.body,
                         os.path.join(here, 'fixtures/static/index.html'))

    def test_range_multiple(self):
        res = self.testapp.get('/static/index.html',
                               [('HTTP_RANGE', 'bytes=10-11,11-12')],
                               status=200)
        self._assertBody(res.body,
                         os.path.join(here, 'fixtures/static/index.html'))

    def test_range_oob(self):
        self.testapp.extra_environ = {'HTTP_RANGE':'bytes=1000-1002'}
        self.testapp.get('/static/index.html', status=416)

    def test_notfound(self):
        self.testapp.get('/static/wontbefound.html', status=404)

    def test_oob_dotdotslash(self):
        self.testapp.get('/static/../../test_integration.py', status=404)

    def test_oob_dotdotslash_encoded(self):
        self.testapp.get('/static/%2E%2E%2F/test_integration.py', status=404)

    def test_oob_slash(self):
        self.testapp.get('/%2F/test_integration.py', status=404)

class TestStaticAppUsingAbsPath(TestStaticAppBase, unittest.TestCase):
    package = 'pyramid.tests.pkgs.static_abspath'

class TestStaticAppUsingAssetSpec(TestStaticAppBase, unittest.TestCase):
    package = 'pyramid.tests.pkgs.static_assetspec'

class TestStaticAppNoSubpath(unittest.TestCase):
    staticapp = static_view(os.path.join(here, 'fixtures'), use_subpath=False)
    def _makeRequest(self, extra):
        from pyramid.request import Request
        from StringIO import StringIO
        kw = {'PATH_INFO':'',
              'SCRIPT_NAME':'',
              'SERVER_NAME':'localhost',
              'SERVER_PORT':'80',
              'REQUEST_METHOD':'GET',
              'wsgi.version':(1,0),
              'wsgi.url_scheme':'http',
              'wsgi.input':StringIO()}
        kw.update(extra)
        request = Request(kw)
        return request

    def _assertBody(self, body, filename):
        self.assertEqual(
            body.replace('\r', ''),
            open(filename, 'r').read()
            )

    def test_basic(self):
        request = self._makeRequest({'PATH_INFO':'/minimal.pt'})
        context = DummyContext()
        result = self.staticapp(context, request)
        self.assertEqual(result.status, '200 OK')
        self._assertBody(result.body, os.path.join(here, 'fixtures/minimal.pt'))

class TestStaticAppWithRoutePrefix(IntegrationBase, unittest.TestCase):
    package = 'pyramid.tests.pkgs.static_routeprefix'
    def _assertBody(self, body, filename):
        self.assertEqual(
            body.replace('\r', ''),
            open(filename, 'r').read()
            )

    def test_includelevel1(self):
        res = self.testapp.get('/static/minimal.pt', status=200)
        self._assertBody(res.body,
                         os.path.join(here, 'fixtures/minimal.pt'))

    def test_includelevel2(self):
        res = self.testapp.get('/prefix/static/index.html', status=200)
        self._assertBody(res.body,
                         os.path.join(here, 'fixtures/static/index.html'))


class TestFixtureApp(IntegrationBase, unittest.TestCase):
    package = 'pyramid.tests.pkgs.fixtureapp'
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

class TestStaticPermApp(IntegrationBase, unittest.TestCase):
    package = 'pyramid.tests.pkgs.staticpermapp'
    root_factory = 'pyramid.tests.pkgs.staticpermapp:RootFactory'
    def test_allowed(self):
        result = self.testapp.get('/allowed/index.html', status=200)
        self.assertEqual(
            result.body.replace('\r', ''),
            open(os.path.join(here, 'fixtures/static/index.html'), 'r').read())

    def test_denied_via_acl_global_root_factory(self):
        self.testapp.extra_environ = {'REMOTE_USER':'bob'}
        self.testapp.get('/protected/index.html', status=403)

    def test_allowed_via_acl_global_root_factory(self):
        self.testapp.extra_environ = {'REMOTE_USER':'fred'}
        result = self.testapp.get('/protected/index.html', status=200)
        self.assertEqual(
            result.body.replace('\r', ''),
            open(os.path.join(here, 'fixtures/static/index.html'), 'r').read())

    def test_denied_via_acl_local_root_factory(self):
        self.testapp.extra_environ = {'REMOTE_USER':'fred'}
        self.testapp.get('/factory_protected/index.html', status=403)

    def test_allowed_via_acl_local_root_factory(self):
        self.testapp.extra_environ = {'REMOTE_USER':'bob'}
        result = self.testapp.get('/factory_protected/index.html', status=200)
        self.assertEqual(
            result.body.replace('\r', ''),
            open(os.path.join(here, 'fixtures/static/index.html'), 'r').read())

class TestCCBug(IntegrationBase, unittest.TestCase):
    # "unordered" as reported in IRC by author of
    # http://labs.creativecommons.org/2010/01/13/cc-engine-and-web-non-frameworks/
    package = 'pyramid.tests.pkgs.ccbugapp'
    def test_rdf(self):
        res = self.testapp.get('/licenses/1/v1/rdf', status=200)
        self.assertEqual(res.body, 'rdf')

    def test_juri(self):
        res = self.testapp.get('/licenses/1/v1/juri', status=200)
        self.assertEqual(res.body, 'juri')

class TestHybridApp(IntegrationBase, unittest.TestCase):
    # make sure views registered for a route "win" over views registered
    # without one, even though the context of the non-route view may
    # be more specific than the route view.
    package = 'pyramid.tests.pkgs.hybridapp'
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

class TestRestBugApp(IntegrationBase, unittest.TestCase):
    # test bug reported by delijati 2010/2/3 (http://pastebin.com/d4cc15515)
    package = 'pyramid.tests.pkgs.restbugapp'
    def test_it(self):
        res = self.testapp.get('/pet', status=200)
        self.assertEqual(res.body, 'gotten')

class TestForbiddenAppHasResult(IntegrationBase, unittest.TestCase):
    # test that forbidden exception has ACLDenied result attached
    package = 'pyramid.tests.pkgs.forbiddenapp'
    def test_it(self):
        res = self.testapp.get('/x', status=403)
        message, result = [x.strip() for x in res.body.split('\n')]
        self.assertTrue(message.endswith('failed permission check'))
        self.assertTrue(
            result.startswith("ACLDenied permission 'private' via ACE "
                              "'<default deny>' in ACL "
                              "'<No ACL found on any object in resource "
                              "lineage>' on context"))
        self.assertTrue(
            result.endswith("for principals ['system.Everyone']"))

class TestViewDecoratorApp(IntegrationBase, unittest.TestCase):
    package = 'pyramid.tests.pkgs.viewdecoratorapp'
    def _configure_mako(self):
        tmpldir = os.path.join(os.path.dirname(__file__),
                               'pkgs',
                               'viewdecoratorapp',
                               'views')
        self.config.registry.settings['mako.directories'] = tmpldir

    def test_first(self):
        # we use mako here instead of chameleon because it works on Jython
        self._configure_mako()
        res = self.testapp.get('/first', status=200)
        self.assertTrue('OK' in res.body)

    def test_second(self):
        # we use mako here instead of chameleon because it works on Jython
        self._configure_mako()
        res = self.testapp.get('/second', status=200)
        self.assertTrue('OK2' in res.body)

class TestViewPermissionBug(IntegrationBase, unittest.TestCase):
    # view_execution_permitted bug as reported by Shane at http://lists.repoze.org/pipermail/repoze-dev/2010-October/003603.html
    package = 'pyramid.tests.pkgs.permbugapp'
    def test_test(self):
        res = self.testapp.get('/test', status=200)
        self.assertTrue('ACLDenied' in res.body)

    def test_x(self):
        self.testapp.get('/x', status=403)

class TestDefaultViewPermissionBug(IntegrationBase, unittest.TestCase):
    # default_view_permission bug as reported by Wiggy at http://lists.repoze.org/pipermail/repoze-dev/2010-October/003602.html
    package = 'pyramid.tests.pkgs.defpermbugapp'
    def test_x(self):
        res = self.testapp.get('/x', status=403)
        self.assertTrue('failed permission check' in res.body)

    def test_y(self):
        res = self.testapp.get('/y', status=403)
        self.assertTrue('failed permission check' in res.body)

    def test_z(self):
        res = self.testapp.get('/z', status=200)
        self.assertTrue('public' in res.body)

from pyramid.tests.pkgs.exceptionviewapp.models import \
     AnException, NotAnException
excroot = {'anexception':AnException(),
           'notanexception':NotAnException()}

class TestExceptionViewsApp(IntegrationBase, unittest.TestCase):
    package = 'pyramid.tests.pkgs.exceptionviewapp'
    root_factory = lambda *arg: excroot
    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue('maybe' in res.body)

    def test_notanexception(self):
        res = self.testapp.get('/notanexception', status=200)
        self.assertTrue('no' in res.body)

    def test_anexception(self):
        res = self.testapp.get('/anexception', status=200)
        self.assertTrue('yes' in res.body)

    def test_route_raise_exception(self):
        res = self.testapp.get('/route_raise_exception', status=200)
        self.assertTrue('yes' in res.body)

    def test_route_raise_exception2(self):
        res = self.testapp.get('/route_raise_exception2', status=200)
        self.assertTrue('yes' in res.body)

    def test_route_raise_exception3(self):
        res = self.testapp.get('/route_raise_exception3', status=200)
        self.assertTrue('whoa' in res.body)

    def test_route_raise_exception4(self):
        res = self.testapp.get('/route_raise_exception4', status=200)
        self.assertTrue('whoa' in res.body)

class TestConflictApp(unittest.TestCase):
    package = 'pyramid.tests.pkgs.conflictapp'
    def _makeConfig(self):
        from pyramid.config import Configurator
        config = Configurator()
        return config

    def test_autoresolved_view(self):
        config = self._makeConfig()
        config.include(self.package)
        app = config.make_wsgi_app()
        from webtest import TestApp
        self.testapp = TestApp(app)
        res = self.testapp.get('/')
        self.assertTrue('a view' in res.body)
        res = self.testapp.get('/route')
        self.assertTrue('route view' in res.body)

    def test_overridden_autoresolved_view(self):
        from pyramid.response import Response
        config = self._makeConfig()
        config.include(self.package)
        def thisview(request):
            return Response('this view')
        config.add_view(thisview)
        app = config.make_wsgi_app()
        from webtest import TestApp
        self.testapp = TestApp(app)
        res = self.testapp.get('/')
        self.assertTrue('this view' in res.body)

    def test_overridden_route_view(self):
        from pyramid.response import Response
        config = self._makeConfig()
        config.include(self.package)
        def thisview(request):
            return Response('this view')
        config.add_view(thisview, route_name='aroute')
        app = config.make_wsgi_app()
        from webtest import TestApp
        self.testapp = TestApp(app)
        res = self.testapp.get('/route')
        self.assertTrue('this view' in res.body)

    def test_nonoverridden_authorization_policy(self):
        config = self._makeConfig()
        config.include(self.package)
        app = config.make_wsgi_app()
        from webtest import TestApp
        self.testapp = TestApp(app)
        res = self.testapp.get('/protected', status=403)
        self.assertTrue('403 Forbidden' in res)

    def test_overridden_authorization_policy(self):
        config = self._makeConfig()
        config.include(self.package)
        from pyramid.testing import DummySecurityPolicy
        config.set_authorization_policy(DummySecurityPolicy('fred'))
        config.set_authentication_policy(DummySecurityPolicy(permissive=True))
        app = config.make_wsgi_app()
        from webtest import TestApp
        self.testapp = TestApp(app)
        res = self.testapp.get('/protected', status=200)
        self.assertTrue('protected view' in res)

class ImperativeIncludeConfigurationTest(unittest.TestCase):
    def setUp(self):
        from pyramid.config import Configurator
        config = Configurator()
        from pyramid.tests.pkgs.includeapp1.root import configure
        configure(config)
        app = config.make_wsgi_app()
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.config = config

    def tearDown(self):
        self.config.end()

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue('root' in res.body)

    def test_two(self):
        res = self.testapp.get('/two', status=200)
        self.assertTrue('two' in res.body)

    def test_three(self):
        res = self.testapp.get('/three', status=200)
        self.assertTrue('three' in res.body)

class SelfScanAppTest(unittest.TestCase):
    def setUp(self):
        from pyramid.tests.test_config.pkgs.selfscan import main
        config = main()
        app = config.make_wsgi_app()
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.config = config

    def tearDown(self):
        self.config.end()

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue('root' in res.body)

    def test_two(self):
        res = self.testapp.get('/two', status=200)
        self.assertTrue('two' in res.body)

class WSGIApp2AppTest(unittest.TestCase):
    def setUp(self):
        from pyramid.tests.pkgs.wsgiapp2app import main
        config = main()
        app = config.make_wsgi_app()
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.config = config

    def tearDown(self):
        self.config.end()

    def test_hello(self):
        res = self.testapp.get('/hello', status=200)
        self.assertTrue('Hello' in res.body)

if os.name != 'java': # uses chameleon
    class RendererScanAppTest(IntegrationBase, unittest.TestCase):
        package = 'pyramid.tests.pkgs.rendererscanapp'
        def test_root(self):
            res = self.testapp.get('/one', status=200)
            self.assertTrue('One!' in res.body)

        def test_two(self):
            res = self.testapp.get('/two', status=200)
            self.assertTrue('Two!' in res.body)

        def test_rescan(self):
            self.config.scan('pyramid.tests.pkgs.rendererscanapp')
            app = self.config.make_wsgi_app()
            from webtest import TestApp
            testapp = TestApp(app)
            res = testapp.get('/one', status=200)
            self.assertTrue('One!' in res.body)
            res = testapp.get('/two', status=200)
            self.assertTrue('Two!' in res.body)

class DummyContext(object):
    pass

class DummyRequest:
    subpath = ('__init__.py',)
    traversed = None
    environ = {'REQUEST_METHOD':'GET', 'wsgi.version':(1,0)}
    def get_response(self, application):
        return application(None, None)

def httpdate(ts):
    return ts.strftime("%a, %d %b %Y %H:%M:%S GMT")
