import datetime
import gc
import locale
import os
import unittest
from urllib.parse import quote
from webtest import TestApp
from zope.interface import Interface

from pyramid.static import static_view
from pyramid.testing import skip_on
from pyramid.util import text_
from pyramid.view import view_config
from pyramid.wsgi import wsgiapp

from .pkgs.exceptionviewapp.models import AnException, NotAnException

# 5 years from now (more or less)
fiveyrsfuture = datetime.datetime.utcnow() + datetime.timedelta(5 * 365)

defaultlocale = locale.getdefaultlocale()[1]


class INothing(Interface):
    pass


@view_config(for_=INothing)
@wsgiapp
def wsgiapptest(environ, start_response):
    """ """
    return '123'


class WGSIAppPlusViewConfigTests(unittest.TestCase):
    def test_it(self):
        import types
        from venusian import ATTACH_ATTR

        self.assertTrue(getattr(wsgiapptest, ATTACH_ATTR))
        self.assertIsInstance(wsgiapptest, types.FunctionType)
        context = DummyContext()
        request = DummyRequest()
        result = wsgiapptest(context, request)
        self.assertEqual(result, '123')

    def test_scanned(self):
        from pyramid.config import Configurator
        from pyramid.interfaces import IRequest, IView, IViewClassifier

        from . import test_integration

        config = Configurator()
        config.scan(test_integration)
        config.commit()
        reg = config.registry
        view = reg.adapters.lookup(
            (IViewClassifier, IRequest, INothing), IView, name=''
        )
        self.assertEqual(view.__original_view__, wsgiapptest)


class IntegrationBase:
    root_factory = None
    package = None

    def setUp(self):
        from pyramid.config import Configurator

        config = Configurator(
            root_factory=self.root_factory, package=self.package
        )
        config.include(self.package)
        self.app = config.make_wsgi_app()
        self.testapp = TestApp(self.app)
        self.config = config

    def tearDown(self):
        self.config.end()


here = os.path.dirname(__file__)


class StaticAppBase(IntegrationBase):
    def test_basic(self):
        res = self.testapp.get('/minimal.txt', status=200)
        _assertBody(res.body, os.path.join(here, 'fixtures/minimal.txt'))

    def test_hidden(self):
        res = self.testapp.get('/static/.hiddenfile', status=200)
        _assertBody(
            res.body, os.path.join(here, 'fixtures/static/.hiddenfile')
        )

    if defaultlocale is not None:  # pragma: no cover
        # These tests are expected to fail on LANG=C systems due to decode
        # errors and on non-Linux systems due to git highchar handling
        # vagaries
        def test_highchars_in_pathelement(self):
            path = os.path.join(
                here, text_('fixtures/static/héhé/index.html', 'utf-8')
            )
            pathdir = os.path.dirname(path)
            body = b'<html>hehe</html>\n'
            try:
                os.makedirs(pathdir)
                with open(path, 'wb') as fp:
                    fp.write(body)
                url = quote('/static/héhé/index.html')
                res = self.testapp.get(url, status=200)
                self.assertEqual(res.body, body)
            finally:
                os.unlink(path)
                os.rmdir(pathdir)

        def test_highchars_in_filename(self):
            path = os.path.join(
                here, text_('fixtures/static/héhé.html', 'utf-8')
            )
            body = b'<html>hehe file</html>\n'
            with open(path, 'wb') as fp:
                fp.write(body)
            try:
                url = quote('/static/héhé.html')
                res = self.testapp.get(url, status=200)
                self.assertEqual(res.body, body)
            finally:
                os.unlink(path)

    def test_not_modified(self):
        self.testapp.extra_environ = {
            'HTTP_IF_MODIFIED_SINCE': httpdate(fiveyrsfuture)
        }
        res = self.testapp.get('/minimal.txt', status=304)
        self.assertEqual(res.body, b'')

    def test_file_in_subdir(self):
        fn = os.path.join(here, 'fixtures/static/index.html')
        res = self.testapp.get('/static/index.html', status=200)
        _assertBody(res.body, fn)

    def test_directory_noslash_redir(self):
        res = self.testapp.get('/static', status=301)
        self.assertEqual(res.headers['Location'], 'http://localhost/static/')

    def test_directory_noslash_redir_preserves_qs(self):
        res = self.testapp.get('/static?a=1&b=2', status=301)
        self.assertEqual(
            res.headers['Location'], 'http://localhost/static/?a=1&b=2'
        )

    def test_directory_noslash_redir_with_scriptname(self):
        self.testapp.extra_environ = {'SCRIPT_NAME': '/script_name'}
        res = self.testapp.get('/static', status=301)
        self.assertEqual(
            res.headers['Location'], 'http://localhost/script_name/static/'
        )

    def test_directory_withslash(self):
        fn = os.path.join(here, 'fixtures/static/index.html')
        res = self.testapp.get('/static/', status=200)
        _assertBody(res.body, fn)

    def test_range_inclusive(self):
        self.testapp.extra_environ = {'HTTP_RANGE': 'bytes=1-2'}
        res = self.testapp.get('/static/index.html', status=206)
        self.assertEqual(res.body, b'ht')

    def test_range_tilend(self):
        self.testapp.extra_environ = {'HTTP_RANGE': 'bytes=-5'}
        res = self.testapp.get('/static/index.html', status=206)
        self.assertEqual(res.body, b'html>')

    def test_range_notbytes(self):
        self.testapp.extra_environ = {'HTTP_RANGE': 'kHz=-5'}
        res = self.testapp.get('/static/index.html', status=200)
        _assertBody(res.body, os.path.join(here, 'fixtures/static/index.html'))

    def test_range_multiple(self):
        res = self.testapp.get(
            '/static/index.html',
            [('HTTP_RANGE', 'bytes=10-11,11-12')],
            status=200,
        )
        _assertBody(res.body, os.path.join(here, 'fixtures/static/index.html'))

    def test_range_oob(self):
        self.testapp.extra_environ = {'HTTP_RANGE': 'bytes=1000-1002'}
        self.testapp.get('/static/index.html', status=416)

    def test_notfound(self):
        self.testapp.get('/static/wontbefound.html', status=404)

    def test_oob_dotdotslash(self):
        self.testapp.get('/static/../../test_integration.py', status=404)

    def test_oob_dotdotslash_encoded(self):
        self.testapp.get('/static/%2E%2E%2F/test_integration.py', status=404)

    def test_oob_slash(self):
        self.testapp.get('/%2F/test_integration.py', status=404)


class TestEventOnlySubscribers(IntegrationBase, unittest.TestCase):
    package = 'tests.pkgs.eventonly'

    def test_sendfoo(self):
        res = self.testapp.get('/sendfoo', status=200)
        self.assertEqual(sorted(res.body.split()), [b'foo', b'fooyup'])

    def test_sendfoobar(self):
        res = self.testapp.get('/sendfoobar', status=200)
        self.assertEqual(
            sorted(res.body.split()),
            [b'foobar', b'foobar2', b'foobaryup', b'foobaryup2'],
        )


class TestStaticAppUsingAbsPath(StaticAppBase, unittest.TestCase):
    package = 'tests.pkgs.static_abspath'


class TestStaticAppUsingAssetSpec(StaticAppBase, unittest.TestCase):
    package = 'tests.pkgs.static_assetspec'


class TestStaticAppWithEncodings(IntegrationBase, unittest.TestCase):
    package = 'tests.pkgs.static_encodings'

    # XXX webtest actually runs response.decode_content() and so we can't
    # use it to test gzip- or deflate-encoded responses to see if they
    # were transferred correctly
    def _getResponse(self, *args, **kwargs):
        from pyramid.request import Request

        req = Request.blank(*args, **kwargs)
        return req.get_response(self.app)

    def test_no_accept(self):
        res = self._getResponse('/static/encoded.html')
        self.assertEqual(res.headers['Vary'], 'Accept-Encoding')
        self.assertNotIn('Content-Encoding', res.headers)
        _assertBody(
            res.body, os.path.join(here, 'fixtures/static/encoded.html')
        )

    def test_unsupported_accept(self):
        res = self._getResponse(
            '/static/encoded.html',
            headers={'Accept-Encoding': 'br, foo, bar'},
        )
        self.assertEqual(res.headers['Vary'], 'Accept-Encoding')
        self.assertNotIn('Content-Encoding', res.headers)
        _assertBody(
            res.body, os.path.join(here, 'fixtures/static/encoded.html')
        )

    def test_accept_gzip(self):
        res = self._getResponse(
            '/static/encoded.html',
            headers={'Accept-Encoding': 'br, foo, gzip'},
        )
        self.assertEqual(res.headers['Vary'], 'Accept-Encoding')
        self.assertEqual(res.headers['Content-Encoding'], 'gzip')
        _assertBody(
            res.body, os.path.join(here, 'fixtures/static/encoded.html.gz')
        )

    def test_accept_gzip_returns_identity(self):
        res = self._getResponse(
            '/static/index.html', headers={'Accept-Encoding': 'gzip'}
        )
        self.assertNotIn('Vary', res.headers)
        self.assertNotIn('Content-Encoding', res.headers)
        _assertBody(res.body, os.path.join(here, 'fixtures/static/index.html'))


class TestStaticAppNoSubpath(unittest.TestCase):
    staticapp = static_view(os.path.join(here, 'fixtures'), use_subpath=False)

    def _makeRequest(self, extra):
        from io import BytesIO

        from pyramid.request import Request

        kw = {
            'PATH_INFO': '',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
            'REQUEST_METHOD': 'GET',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': BytesIO(),
        }
        kw.update(extra)
        request = Request(kw)
        return request

    def test_basic(self):
        request = self._makeRequest({'PATH_INFO': '/minimal.txt'})
        context = DummyContext()
        result = self.staticapp(context, request)
        self.assertEqual(result.status, '200 OK')
        _assertBody(result.body, os.path.join(here, 'fixtures/minimal.txt'))


class TestStaticAppWithRoutePrefix(IntegrationBase, unittest.TestCase):
    package = 'tests.pkgs.static_routeprefix'

    def test_includelevel1(self):
        res = self.testapp.get('/static/minimal.txt', status=200)
        _assertBody(res.body, os.path.join(here, 'fixtures/minimal.txt'))

    def test_includelevel2(self):
        res = self.testapp.get('/prefix/static/index.html', status=200)
        _assertBody(res.body, os.path.join(here, 'fixtures/static/index.html'))


class TestFixtureApp(IntegrationBase, unittest.TestCase):
    package = 'tests.pkgs.fixtureapp'

    def test_another(self):
        res = self.testapp.get('/another.html', status=200)
        self.assertEqual(res.body, b'fixture')

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertEqual(res.body, b'fixture')

    def test_dummyskin(self):
        self.testapp.get('/dummyskin.html', status=404)

    def test_error(self):
        res = self.testapp.get('/error.html', status=200)
        self.assertEqual(res.body, b'supressed')

    def test_protected(self):
        self.testapp.get('/protected.html', status=403)


class TestStaticPermApp(IntegrationBase, unittest.TestCase):
    package = 'tests.pkgs.staticpermapp'
    root_factory = 'tests.pkgs.staticpermapp:RootFactory'

    def test_allowed(self):
        result = self.testapp.get('/allowed/index.html', status=200)
        _assertBody(
            result.body, os.path.join(here, 'fixtures/static/index.html')
        )

    def test_denied_via_acl_global_root_factory(self):
        self.testapp.extra_environ = {'REMOTE_USER': 'bob'}
        self.testapp.get('/protected/index.html', status=403)

    def test_allowed_via_acl_global_root_factory(self):
        self.testapp.extra_environ = {'REMOTE_USER': 'fred'}
        result = self.testapp.get('/protected/index.html', status=200)
        _assertBody(
            result.body, os.path.join(here, 'fixtures/static/index.html')
        )

    def test_denied_via_acl_local_root_factory(self):
        self.testapp.extra_environ = {'REMOTE_USER': 'fred'}
        self.testapp.get('/factory_protected/index.html', status=403)

    def test_allowed_via_acl_local_root_factory(self):
        self.testapp.extra_environ = {'REMOTE_USER': 'bob'}
        result = self.testapp.get('/factory_protected/index.html', status=200)
        _assertBody(
            result.body, os.path.join(here, 'fixtures/static/index.html')
        )


class TestCCBug(IntegrationBase, unittest.TestCase):
    # "unordered" as reported in IRC by author of
    # http://labs.creativecommons.org/2010/01/13/cc-engine-and-web-non-frameworks/
    package = 'tests.pkgs.ccbugapp'

    def test_rdf(self):
        res = self.testapp.get('/licenses/1/v1/rdf', status=200)
        self.assertEqual(res.body, b'rdf')

    def test_juri(self):
        res = self.testapp.get('/licenses/1/v1/juri', status=200)
        self.assertEqual(res.body, b'juri')


class TestHybridApp(IntegrationBase, unittest.TestCase):
    # make sure views registered for a route "win" over views registered
    # without one, even though the context of the non-route view may
    # be more specific than the route view.
    package = 'tests.pkgs.hybridapp'

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertEqual(res.body, b'global')

    def test_abc(self):
        res = self.testapp.get('/abc', status=200)
        self.assertEqual(res.body, b'route')

    def test_def(self):
        res = self.testapp.get('/def', status=200)
        self.assertEqual(res.body, b'route2')

    def test_ghi(self):
        res = self.testapp.get('/ghi', status=200)
        self.assertEqual(res.body, b'global')

    def test_jkl(self):
        self.testapp.get('/jkl', status=404)

    def test_mno(self):
        self.testapp.get('/mno', status=404)

    def test_pqr_global2(self):
        res = self.testapp.get('/pqr/global2', status=200)
        self.assertEqual(res.body, b'global2')

    def test_error(self):
        res = self.testapp.get('/error', status=200)
        self.assertEqual(res.body, b'supressed')

    def test_error2(self):
        res = self.testapp.get('/error2', status=200)
        self.assertEqual(res.body, b'supressed2')

    def test_error_sub(self):
        res = self.testapp.get('/error_sub', status=200)
        self.assertEqual(res.body, b'supressed2')


class TestRestBugApp(IntegrationBase, unittest.TestCase):
    # test bug reported by delijati 2010/2/3 (http://pastebin.com/d4cc15515)
    package = 'tests.pkgs.restbugapp'

    def test_it(self):
        res = self.testapp.get('/pet', status=200)
        self.assertEqual(res.body, b'gotten')


class TestForbiddenAppHasResult(IntegrationBase, unittest.TestCase):
    # test that forbidden exception has ACLDenied result attached
    package = 'tests.pkgs.forbiddenapp'

    def test_it(self):
        res = self.testapp.get('/x', status=403)
        message, result = (x.strip() for x in res.body.split(b'\n'))
        self.assertTrue(message.endswith(b'failed permission check'))
        self.assertTrue(
            result.startswith(
                b"ACLDenied permission 'private' via ACE "
                b"'<default deny>' in ACL "
                b"'<No ACL found on any object in resource "
                b"lineage>' on context"
            )
        )
        self.assertTrue(result.endswith(b"for principals ['system.Everyone']"))


class TestViewDecoratorApp(IntegrationBase, unittest.TestCase):
    package = 'tests.pkgs.viewdecoratorapp'

    def test_first(self):
        res = self.testapp.get('/first', status=200)
        self.assertTrue(b'OK' in res.body)

    def test_second(self):
        res = self.testapp.get('/second', status=200)
        self.assertTrue(b'OK2' in res.body)


class TestNotFoundView(IntegrationBase, unittest.TestCase):
    package = 'tests.pkgs.notfoundview'

    def test_it(self):
        res = self.testapp.get('/wontbefound', status=200)
        self.assertTrue(b'generic_notfound' in res.body)
        res = self.testapp.get('/bar', status=307)
        self.assertEqual(res.location, 'http://localhost/bar/')
        res = self.testapp.get('/bar/', status=200)
        self.assertTrue(b'OK bar' in res.body)
        res = self.testapp.get('/foo', status=307)
        self.assertEqual(res.location, 'http://localhost/foo/')
        res = self.testapp.get('/foo/', status=200)
        self.assertTrue(b'OK foo2' in res.body)
        res = self.testapp.get('/baz', status=200)
        self.assertTrue(b'baz_notfound' in res.body)


class TestForbiddenView(IntegrationBase, unittest.TestCase):
    package = 'tests.pkgs.forbiddenview'

    def test_it(self):
        res = self.testapp.get('/foo', status=200)
        self.assertTrue(b'foo_forbidden' in res.body)
        res = self.testapp.get('/bar', status=200)
        self.assertTrue(b'generic_forbidden' in res.body)


class TestViewPermissionBug(IntegrationBase, unittest.TestCase):
    # view_execution_permitted bug as reported by Shane at
    # http://lists.repoze.org/pipermail/repoze-dev/2010-October/003603.html
    package = 'tests.pkgs.permbugapp'

    def test_test(self):
        res = self.testapp.get('/test', status=200)
        self.assertTrue(b'ACLDenied' in res.body)

    def test_x(self):
        self.testapp.get('/x', status=403)


class TestDefaultViewPermissionBug(IntegrationBase, unittest.TestCase):
    # default_view_permission bug as reported by Wiggy at
    # http://lists.repoze.org/pipermail/repoze-dev/2010-October/003602.html
    package = 'tests.pkgs.defpermbugapp'

    def test_x(self):
        res = self.testapp.get('/x', status=403)
        self.assertTrue(b'failed permission check' in res.body)

    def test_y(self):
        res = self.testapp.get('/y', status=403)
        self.assertTrue(b'failed permission check' in res.body)

    def test_z(self):
        res = self.testapp.get('/z', status=200)
        self.assertTrue(b'public' in res.body)


excroot = {'anexception': AnException(), 'notanexception': NotAnException()}


class TestExceptionViewsApp(IntegrationBase, unittest.TestCase):
    package = 'tests.pkgs.exceptionviewapp'
    root_factory = lambda *arg: excroot

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue(b'maybe' in res.body)

    def test_notanexception(self):
        res = self.testapp.get('/notanexception', status=200)
        self.assertTrue(b'no' in res.body)

    def test_anexception(self):
        res = self.testapp.get('/anexception', status=200)
        self.assertTrue(b'yes' in res.body)

    def test_route_raise_exception(self):
        res = self.testapp.get('/route_raise_exception', status=200)
        self.assertTrue(b'yes' in res.body)

    def test_route_raise_exception2(self):
        res = self.testapp.get('/route_raise_exception2', status=200)
        self.assertTrue(b'yes' in res.body)

    def test_route_raise_exception3(self):
        res = self.testapp.get('/route_raise_exception3', status=200)
        self.assertTrue(b'whoa' in res.body)

    def test_route_raise_exception4(self):
        res = self.testapp.get('/route_raise_exception4', status=200)
        self.assertTrue(b'whoa' in res.body)

    def test_raise_httpexception(self):
        res = self.testapp.get('/route_raise_httpexception', status=200)
        self.assertTrue(b'caught' in res.body)


class TestSecurityApp(IntegrationBase, unittest.TestCase):
    package = 'tests.pkgs.securityapp'

    def test_public(self):
        res = self.testapp.get('/public', status=200)
        self.assertEqual(res.body, b'Hello')

    def test_private_denied(self):
        self.testapp.get('/private', status=403)

    def test_private_allowed(self):
        self.testapp.extra_environ = {'REMOTE_USER': 'bob'}
        res = self.testapp.get('/private', status=200)
        self.assertEqual(res.body, b'Secret')

    def test_inaccessible(self):
        self.testapp.get('/inaccessible', status=403)
        self.testapp.extra_environ = {'REMOTE_USER': 'bob'}
        self.testapp.get('/inaccessible', status=403)


class TestLegacySecurityApp(IntegrationBase, unittest.TestCase):
    package = 'tests.pkgs.legacysecurityapp'

    def test_public(self):
        res = self.testapp.get('/public', status=200)
        self.assertEqual(res.body, b'Hello')

    def test_private_denied(self):
        self.testapp.get('/private', status=403)

    def test_private_allowed(self):
        self.testapp.extra_environ = {'REMOTE_USER': 'bob'}
        res = self.testapp.get('/private', status=200)
        self.assertEqual(res.body, b'Secret')

    def test_inaccessible(self):
        self.testapp.get('/inaccessible', status=403)
        self.testapp.extra_environ = {'REMOTE_USER': 'bob'}
        self.testapp.get('/inaccessible', status=403)


class TestConflictApp(unittest.TestCase):
    package = 'tests.pkgs.conflictapp'

    def _makeConfig(self):
        from pyramid.config import Configurator

        config = Configurator()
        return config

    def test_autoresolved_view(self):
        config = self._makeConfig()
        config.include(self.package)
        app = config.make_wsgi_app()
        self.testapp = TestApp(app)
        res = self.testapp.get('/')
        self.assertTrue(b'a view' in res.body)
        res = self.testapp.get('/route')
        self.assertTrue(b'route view' in res.body)

    def test_overridden_autoresolved_view(self):
        from pyramid.response import Response

        config = self._makeConfig()
        config.include(self.package)

        def thisview(request):
            return Response('this view')

        config.add_view(thisview)
        app = config.make_wsgi_app()
        self.testapp = TestApp(app)
        res = self.testapp.get('/')
        self.assertTrue(b'this view' in res.body)

    def test_overridden_route_view(self):
        from pyramid.response import Response

        config = self._makeConfig()
        config.include(self.package)

        def thisview(request):
            return Response('this view')

        config.add_view(thisview, route_name='aroute')
        app = config.make_wsgi_app()
        self.testapp = TestApp(app)
        res = self.testapp.get('/route')
        self.assertTrue(b'this view' in res.body)

    def test_nonoverridden_authorization_policy(self):
        config = self._makeConfig()
        config.include(self.package)
        app = config.make_wsgi_app()
        self.testapp = TestApp(app)
        res = self.testapp.get('/protected', status=403)
        self.assertTrue(b'403 Forbidden' in res.body)

    def test_overridden_authorization_policy(self):
        config = self._makeConfig()
        config.include(self.package)

        class DummySecurityPolicy:
            def permits(self, context, principals, permission):
                return True

        config.set_authorization_policy(DummySecurityPolicy())
        app = config.make_wsgi_app()
        self.testapp = TestApp(app)
        res = self.testapp.get('/protected', status=200)
        self.assertTrue('protected view' in res)


class ImperativeIncludeConfigurationTest(unittest.TestCase):
    def setUp(self):
        from pyramid.config import Configurator

        config = Configurator()
        from .pkgs.includeapp1.root import configure

        configure(config)
        app = config.make_wsgi_app()
        self.testapp = TestApp(app)
        self.config = config

    def tearDown(self):
        self.config.end()

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue(b'root' in res.body)

    def test_two(self):
        res = self.testapp.get('/two', status=200)
        self.assertTrue(b'two' in res.body)

    def test_three(self):
        res = self.testapp.get('/three', status=200)
        self.assertTrue(b'three' in res.body)


class SelfScanAppTest(unittest.TestCase):
    def setUp(self):
        from .test_config.pkgs.selfscan import main

        config = main()
        app = config.make_wsgi_app()
        self.testapp = TestApp(app)
        self.config = config

    def tearDown(self):
        self.config.end()

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue(b'root' in res.body)

    def test_two(self):
        res = self.testapp.get('/two', status=200)
        self.assertTrue(b'two' in res.body)


class WSGIApp2AppTest(unittest.TestCase):
    def setUp(self):
        from .pkgs.wsgiapp2app import main

        config = main()
        app = config.make_wsgi_app()
        self.testapp = TestApp(app)
        self.config = config

    def tearDown(self):
        self.config.end()

    def test_hello(self):
        res = self.testapp.get('/hello', status=200)
        self.assertTrue(b'Hello' in res.body)


class SubrequestAppTest(unittest.TestCase):
    def setUp(self):
        from .pkgs.subrequestapp import main

        config = main()
        app = config.make_wsgi_app()
        self.testapp = TestApp(app)
        self.config = config

    def tearDown(self):
        self.config.end()

    def test_one(self):
        res = self.testapp.get('/view_one', status=200)
        self.assertTrue(b'This came from view_two, foo=bar' in res.body)

    def test_three(self):
        res = self.testapp.get('/view_three', status=500)
        self.assertTrue(b'Bad stuff happened' in res.body)

    def test_five(self):
        res = self.testapp.get('/view_five', status=200)
        self.assertTrue(b'Value error raised' in res.body)


class RendererScanAppTest(IntegrationBase, unittest.TestCase):
    package = 'tests.pkgs.rendererscanapp'

    def test_root(self):
        res = self.testapp.get('/one', status=200)
        self.assertTrue(b'One!' in res.body)

    def test_two(self):
        res = self.testapp.get('/two', status=200)
        self.assertTrue(b'Two!' in res.body)

    def test_rescan(self):
        self.config.scan('tests.pkgs.rendererscanapp')
        app = self.config.make_wsgi_app()
        testapp = TestApp(app)
        res = testapp.get('/one', status=200)
        self.assertTrue(b'One!' in res.body)
        res = testapp.get('/two', status=200)
        self.assertTrue(b'Two!' in res.body)


class UnicodeInURLTest(unittest.TestCase):
    def _makeConfig(self):
        from pyramid.config import Configurator

        config = Configurator()
        return config

    def _makeTestApp(self, config):
        app = config.make_wsgi_app()
        return TestApp(app)

    def test_unicode_in_url_404(self):
        request_path = '/avalia%C3%A7%C3%A3o_participante'
        request_path_unicode = b'/avalia\xc3\xa7\xc3\xa3o_participante'.decode(
            'utf-8'
        )

        config = self._makeConfig()
        testapp = self._makeTestApp(config)

        res = testapp.get(request_path, status=404)

        # Pyramid default 404 handler outputs:
        # '404 Not Found\n\nThe resource could not be found.\n\n\n'
        # '/avalia\xe7\xe3o_participante\n\n'
        self.assertTrue(request_path_unicode in res.text)

    def test_unicode_in_url_200(self):
        request_path = '/avalia%C3%A7%C3%A3o_participante'
        request_path_unicode = b'/avalia\xc3\xa7\xc3\xa3o_participante'.decode(
            'utf-8'
        )

        def myview(request):
            return 'XXX'

        config = self._makeConfig()
        config.add_route('myroute', request_path_unicode)
        config.add_view(myview, route_name='myroute', renderer='json')
        testapp = self._makeTestApp(config)

        res = testapp.get(request_path, status=200)

        self.assertEqual(res.text, '"XXX"')


class AcceptContentTypeTest(unittest.TestCase):
    def _makeConfig(self):
        def hello_view(request):
            return {'message': 'Hello!'}

        from pyramid.config import Configurator

        config = Configurator()
        config.add_route('hello', '/hello')
        config.add_view(
            hello_view,
            route_name='hello',
            accept='text/plain',
            renderer='string',
        )
        config.add_view(
            hello_view,
            route_name='hello',
            accept='application/json',
            renderer='json',
        )

        def hello_fallback_view(request):
            request.response.content_type = 'text/x-fallback'
            return 'hello fallback'

        config.add_view(
            hello_fallback_view, route_name='hello', renderer='string'
        )
        return config

    def _makeTestApp(self, config):
        app = config.make_wsgi_app()
        return TestApp(app)

    def tearDown(self):
        import pyramid.config

        pyramid.config.global_registries.empty()

    def test_client_side_ordering(self):
        config = self._makeConfig()
        app = self._makeTestApp(config)
        res = app.get(
            '/hello',
            headers={'Accept': 'application/json; q=1.0, text/plain; q=0.9'},
            status=200,
        )
        self.assertEqual(res.content_type, 'application/json')
        res = app.get(
            '/hello',
            headers={'Accept': 'text/plain; q=0.9, application/json; q=1.0'},
            status=200,
        )
        self.assertEqual(res.content_type, 'application/json')
        res = app.get(
            '/hello', headers={'Accept': 'application/*'}, status=200
        )
        self.assertEqual(res.content_type, 'application/json')
        res = app.get('/hello', headers={'Accept': 'text/*'}, status=200)
        self.assertEqual(res.content_type, 'text/plain')
        res = app.get(
            '/hello', headers={'Accept': 'something/else'}, status=200
        )
        self.assertEqual(res.content_type, 'text/x-fallback')

    def test_default_server_side_ordering(self):
        config = self._makeConfig()
        app = self._makeTestApp(config)
        res = app.get(
            '/hello',
            headers={'Accept': 'application/json, text/plain'},
            status=200,
        )
        self.assertEqual(res.content_type, 'text/plain')
        res = app.get(
            '/hello',
            headers={'Accept': 'text/plain, application/json'},
            status=200,
        )
        self.assertEqual(res.content_type, 'text/plain')
        res = app.get('/hello', headers={'Accept': '*/*'}, status=200)
        self.assertEqual(res.content_type, 'text/plain')
        res = app.get('/hello', status=200)
        self.assertEqual(res.content_type, 'text/plain')
        res = app.get('/hello', headers={'Accept': 'invalid'}, status=200)
        self.assertEqual(res.content_type, 'text/plain')
        res = app.get(
            '/hello', headers={'Accept': 'something/else'}, status=200
        )
        self.assertEqual(res.content_type, 'text/x-fallback')

    def test_custom_server_side_ordering(self):
        config = self._makeConfig()
        config.add_accept_view_order(
            'application/json', weighs_more_than='text/plain'
        )
        app = self._makeTestApp(config)
        res = app.get(
            '/hello',
            headers={'Accept': 'application/json, text/plain'},
            status=200,
        )
        self.assertEqual(res.content_type, 'application/json')
        res = app.get(
            '/hello',
            headers={'Accept': 'text/plain, application/json'},
            status=200,
        )
        self.assertEqual(res.content_type, 'application/json')
        res = app.get('/hello', headers={'Accept': '*/*'}, status=200)
        self.assertEqual(res.content_type, 'application/json')
        res = app.get('/hello', status=200)
        self.assertEqual(res.content_type, 'application/json')
        res = app.get('/hello', headers={'Accept': 'invalid'}, status=200)
        self.assertEqual(res.content_type, 'application/json')
        res = app.get(
            '/hello', headers={'Accept': 'something/else'}, status=200
        )
        self.assertEqual(res.content_type, 'text/x-fallback')


class DummyContext:
    pass


class DummyRequest:
    subpath = ('__init__.py',)
    traversed = None
    environ = {'REQUEST_METHOD': 'GET', 'wsgi.version': (1, 0)}

    def get_response(self, application):
        return application(None, None)


def httpdate(ts):
    return ts.strftime("%a, %d %b %Y %H:%M:%S GMT")


def read_(filename):
    with open(filename, 'rb') as fp:
        val = fp.read()
        return val


def _assertBody(body, filename):
    if defaultlocale is None:  # pragma: no cover
        # If system locale does not have an encoding then default to utf-8
        filename = filename.encode('utf-8')
    # strip both \n and \r for windows
    body = body.replace(b'\r', b'')
    body = body.replace(b'\n', b'')
    data = read_(filename)
    data = data.replace(b'\r', b'')
    data = data.replace(b'\n', b'')
    assert body == data


class MemoryLeaksTest(unittest.TestCase):
    def tearDown(self):
        import pyramid.config

        pyramid.config.global_registries.empty()

    def get_gc_count(self):
        last_collected = 0
        while True:
            collected = gc.collect()
            if collected == last_collected:
                break
            last_collected = collected
        return len(gc.get_objects())

    @skip_on('pypy')
    def test_memory_leaks(self):
        from pyramid.config import Configurator

        Configurator().make_wsgi_app()  # Initialize all global objects

        initial_count = self.get_gc_count()
        Configurator().make_wsgi_app()
        current_count = self.get_gc_count()
        self.assertEqual(current_count, initial_count)
