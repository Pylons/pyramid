import unittest
from pyramid.testing import cleanUp

class TestPackageURLParser(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.static import PackageURLParser
        return PackageURLParser

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)


    def _makeEnviron(self, **kw):
        environ = {
            'wsgi.url_scheme':'http',
            'wsgi.version':(1,0),
            'SERVER_NAME':'example.com',
            'SERVER_PORT':'6543',
            'PATH_INFO':'/',
            'SCRIPT_NAME':'',
            'REQUEST_METHOD':'GET',
            }
        environ.update(kw)
        return environ
    
    def test_ctor_allargs(self):
        import os.path
        inst = self._makeOne('package', 'resource/name', root_resource='root',
                             cache_max_age=100)
        self.assertEqual(inst.package_name, 'package')
        self.assertEqual(inst.resource_name, os.path.join('resource', 'name'))
        self.assertEqual(inst.root_resource, 'root')
        self.assertEqual(inst.cache_max_age, 100)
        
    def test_ctor_defaultargs(self):
        import os.path
        inst = self._makeOne('package', 'resource/name')
        self.assertEqual(inst.package_name, 'package')
        self.assertEqual(inst.resource_name, os.path.join('resource', 'name'))
        self.assertEqual(inst.root_resource, os.path.join('resource', 'name'))
        self.assertEqual(inst.cache_max_age, None)

    def test_call_adds_slash_path_info_empty(self):
        environ = self._makeEnviron(PATH_INFO='')
        inst = self._makeOne('pyramid.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.assertTrue('301 Moved Permanently' in body)
        self.assertTrue('http://example.com:6543/' in body)
        
    def test_path_info_slash_means_index_html(self):
        environ = self._makeEnviron()
        inst = self._makeOne('pyramid.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.assertTrue('<html>static</html>' in body)

    def test_resource_out_of_bounds(self):
        environ = self._makeEnviron()
        inst = self._makeOne('pyramid.tests', 'fixtures/static')
        inst.root_resource = 'abcdef'
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.assertTrue('404 Not Found' in body)
        self.assertTrue('http://example.com:6543/' in body)

    def test_resource_doesnt_exist(self):
        environ = self._makeEnviron(PATH_INFO='/notthere')
        inst = self._makeOne('pyramid.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.assertTrue('404 Not Found' in body)
        self.assertTrue('http://example.com:6543/' in body)

    def test_resource_isdir(self):
        environ = self._makeEnviron(PATH_INFO='/subdir/')
        inst = self._makeOne('pyramid.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.assertTrue('<html>subdir</html>' in body)

    def test_resource_is_file(self):
        environ = self._makeEnviron(PATH_INFO='/index.html')
        inst = self._makeOne('pyramid.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.assertTrue('<html>static</html>' in body)

    def test_resource_has_extra_path_info(self):
        environ = self._makeEnviron(PATH_INFO='/static/index.html/more')
        inst = self._makeOne('pyramid.tests', 'fixtures')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.assertTrue("The trailing path '/more' is not allowed" in body)

    def test_resource_is_file_with_cache_max_age(self):
        environ = self._makeEnviron(PATH_INFO='/index.html')
        inst = self._makeOne('pyramid.tests', 'fixtures/static',
                             cache_max_age=600)
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.assertTrue('<html>static</html>' in body)
        self.assertEqual(len(sr.headerlist), 8)
        header_names = [ x[0] for x in sr.headerlist ]
        header_names.sort()
        self.assertEqual(header_names,
                         ['Accept-Ranges', 'Cache-Control',
                          'Content-Length', 'Content-Range',
                          'Content-Type', 'ETag', 'Expires', 'Last-Modified'])

    def test_resource_is_file_with_no_cache_max_age(self):
        environ = self._makeEnviron(PATH_INFO='/index.html')
        inst = self._makeOne('pyramid.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.assertTrue('<html>static</html>' in body)
        self.assertEqual(len(sr.headerlist), 6)
        header_names = [ x[0] for x in sr.headerlist ]
        header_names.sort()
        self.assertEqual(header_names,
                         ['Accept-Ranges', 'Content-Length', 'Content-Range',
                          'Content-Type', 'ETag', 'Last-Modified'])

    def test_with_root_resource(self):
        environ = self._makeEnviron(PATH_INFO='/static/index.html')
        inst = self._makeOne('pyramid.tests', 'fixtures',
                             root_resource='fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.assertTrue('<html>static</html>' in body)

    def test_if_none_match(self):
        class DummyEq(object):
            def __eq__(self, other):
                return True
        dummy_eq = DummyEq()
        environ = self._makeEnviron(HTTP_IF_NONE_MATCH=dummy_eq)
        inst = self._makeOne('pyramid.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        self.assertEqual(len(sr.headerlist), 1)
        self.assertEqual(sr.status, '304 Not Modified')
        self.assertEqual(sr.headerlist[0][0], 'ETag')
        self.assertEqual(response[0], '')

    def test_if_none_match_miss(self):
        class DummyEq(object):
            def __eq__(self, other):
                return False
        dummy_eq = DummyEq()
        environ = self._makeEnviron(HTTP_IF_NONE_MATCH=dummy_eq)
        inst = self._makeOne('pyramid.tests', 'fixtures/static')
        sr = DummyStartResponse()
        inst(environ, sr)
        self.assertEqual(len(sr.headerlist), 6)
        self.assertEqual(sr.status, '200 OK')

    def test_repr(self):
        import os.path
        inst = self._makeOne('pyramid.tests', 'fixtures/static')
        self.assertTrue(
            repr(inst).startswith(
            '<PackageURLParser pyramid.tests:%s at'
                % os.path.join('fixtures', 'static')))

    def test_not_found(self):
        inst = self._makeOne('pyramid.tests', 'fixtures/static')
        environ = self._makeEnviron()
        sr = DummyStartResponse()
        response = inst.not_found(environ, sr, 'debug_message')
        body = response[0]
        self.assertTrue('404 Not Found' in body)
        self.assertEqual(sr.status, '404 Not Found')

class Test_static_view(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from pyramid.static import static_view
        return static_view

    def _makeOne(self, path, package_name=None, use_subpath=False):
        return self._getTargetClass()(path, package_name=package_name,
                                      use_subpath=use_subpath)
        
    def _makeEnviron(self, **extras):
        environ = {
            'wsgi.url_scheme':'http',
            'wsgi.version':(1,0),
            'SERVER_NAME':'localhost',
            'SERVER_PORT':'8080',
            'REQUEST_METHOD':'GET',
            }
        environ.update(extras)
        return environ

    def test_abspath_subpath(self):
        import os.path
        path = os.path.dirname(__file__)
        view = self._makeOne(path, use_subpath=True)
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ['__init__.py']
        request.environ = self._makeEnviron()
        response = view(context, request)
        self.assertEqual(request.copied, True)
        self.assertEqual(response.directory, os.path.normcase(path))

    def test_relpath_subpath(self):
        path = 'fixtures'
        view = self._makeOne(path, use_subpath=True)
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ['__init__.py']
        request.environ = self._makeEnviron()
        response = view(context, request)
        self.assertEqual(request.copied, True)
        self.assertEqual(response.root_resource, 'fixtures')
        self.assertEqual(response.resource_name, 'fixtures')
        self.assertEqual(response.package_name, 'pyramid.tests')
        self.assertEqual(response.cache_max_age, 3600)

    def test_relpath_notsubpath(self):
        path = 'fixtures'
        view = self._makeOne(path)
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ['__init__.py']
        request.environ = self._makeEnviron()
        response = view(context, request)
        self.assertTrue(not hasattr(request, 'copied'))
        self.assertEqual(response.root_resource, 'fixtures')
        self.assertEqual(response.resource_name, 'fixtures')
        self.assertEqual(response.package_name, 'pyramid.tests')
        self.assertEqual(response.cache_max_age, 3600)

    def test_relpath_withpackage_subpath(self):
        view = self._makeOne('another:fixtures', use_subpath=True)
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ['__init__.py']
        request.environ = self._makeEnviron()
        response = view(context, request)
        self.assertEqual(request.copied, True)
        self.assertEqual(response.root_resource, 'fixtures')
        self.assertEqual(response.resource_name, 'fixtures')
        self.assertEqual(response.package_name, 'another')
        self.assertEqual(response.cache_max_age, 3600)

    def test_relpath_withpackage_name_subpath(self):
        view = self._makeOne('fixtures', package_name='another',
                             use_subpath=True)
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ['__init__.py']
        request.environ = self._makeEnviron()
        response = view(context, request)
        self.assertEqual(request.copied, True)
        self.assertEqual(response.root_resource, 'fixtures')
        self.assertEqual(response.resource_name, 'fixtures')
        self.assertEqual(response.package_name, 'another')
        self.assertEqual(response.cache_max_age, 3600)

    def test_no_subpath_preserves_path_info_and_script_name_subpath(self):
        view = self._makeOne('fixtures', package_name='another',
                             use_subpath=True)
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ()
        request.environ = self._makeEnviron(PATH_INFO='/path_info', 
                                            SCRIPT_NAME='/script_name')
        view(context, request)
        self.assertEqual(request.copied, True)
        self.assertEqual(request.environ['PATH_INFO'], '/')
        self.assertEqual(request.environ['SCRIPT_NAME'],
                         '/script_name/path_info')

    def test_with_subpath_path_info_ends_with_slash_subpath(self):
        view = self._makeOne('fixtures', package_name='another',
                             use_subpath=True)
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ('subpath',)
        request.environ = self._makeEnviron(PATH_INFO='/path_info/subpath/')
        view(context, request)
        self.assertEqual(request.copied, True)
        self.assertEqual(request.environ['PATH_INFO'], '/subpath/')
        self.assertEqual(request.environ['SCRIPT_NAME'], '/path_info')

    def test_with_subpath_original_script_name_preserved(self):
        view = self._makeOne('fixtures', package_name='another',
                             use_subpath=True)
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ('subpath',)
        request.environ = self._makeEnviron(PATH_INFO='/path_info/subpath/',
                                            SCRIPT_NAME='/scriptname')
        view(context, request)
        self.assertEqual(request.copied, True)
        self.assertEqual(request.environ['PATH_INFO'], '/subpath/')
        self.assertEqual(request.environ['SCRIPT_NAME'], 
                         '/scriptname/path_info')

    def test_with_subpath_new_script_name_fixes_trailing_slashes(self):
        view = self._makeOne('fixtures', package_name='another',
                             use_subpath=True)
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ('sub', 'path')
        request.environ = self._makeEnviron(PATH_INFO='/path_info//sub//path//')
        view(context, request)
        self.assertEqual(request.copied, True)
        self.assertEqual(request.environ['PATH_INFO'], '/sub/path/')
        self.assertEqual(request.environ['SCRIPT_NAME'], '/path_info')

class TestStaticURLInfo(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.static import StaticURLInfo
        return StaticURLInfo
    
    def _makeOne(self, config):
        return self._getTargetClass()(config)

    def test_verifyClass(self):
        from pyramid.interfaces import IStaticURLInfo
        from zope.interface.verify import verifyClass
        verifyClass(IStaticURLInfo, self._getTargetClass())

    def test_verifyObject(self):
        from pyramid.interfaces import IStaticURLInfo
        from zope.interface.verify import verifyObject
        verifyObject(IStaticURLInfo, self._makeOne(None))

    def test_ctor(self):
        info = self._makeOne(None)
        self.assertEqual(info.registrations, [])
        self.assertEqual(info.config, None)

    def test_generate_missing(self):
        inst = self._makeOne(None)
        request = DummyRequest()
        self.assertRaises(ValueError, inst.generate, 'path', request)

    def test_generate_registration_miss(self):
        inst = self._makeOne(None)
        inst.registrations = [('name', 'spec', False),
                              ('http://example.com/foo/', 'package:path/',True)]
        request = DummyRequest()
        result = inst.generate('package:path/abc', request)
        self.assertEqual(result, 'http://example.com/foo/abc')

    def test_generate_slash_in_name1(self):
        inst = self._makeOne(None)
        inst.registrations = [('http://example.com/foo/', 'package:path/',True)]
        request = DummyRequest()
        result = inst.generate('package:path/abc', request)
        self.assertEqual(result, 'http://example.com/foo/abc')

    def test_generate_slash_in_name2(self):
        inst = self._makeOne(None)
        inst.registrations = [('http://example.com/foo/', 'package:path/',True)]
        request = DummyRequest()
        result = inst.generate('package:path/', request)
        self.assertEqual(result, 'http://example.com/foo/')

    def test_generate_route_url(self):
        inst = self._makeOne(None)
        inst.registrations = [('viewname/', 'package:path/', False)]
        def route_url(n, r, **kw):
            self.assertEqual(n, 'viewname/')
            self.assertEqual(r, request)
            self.assertEqual(kw, {'subpath':'abc', 'a':1})
            return 'url'
        request = DummyRequest()
        inst.route_url = route_url
        result = inst.generate('package:path/abc', request, a=1)
        self.assertEqual(result, 'url')

    def test_add_already_exists(self):
        inst = self._makeOne(None)
        inst.registrations = [('http://example.com/', 'package:path/', True)]
        inst.add('http://example.com', 'anotherpackage:path')
        expected = [('http://example.com/',  'anotherpackage:path/', True)]
        self.assertEqual(inst.registrations, expected)

    def test_add_url_withendslash(self):
        inst = self._makeOne(None)
        inst.add('http://example.com/', 'anotherpackage:path')
        expected = [('http://example.com/', 'anotherpackage:path/', True)]
        self.assertEqual(inst.registrations, expected)

    def test_add_url_noendslash(self):
        inst = self._makeOne(None)
        inst.add('http://example.com', 'anotherpackage:path')
        expected = [('http://example.com/', 'anotherpackage:path/', True)]
        self.assertEqual(inst.registrations, expected)

    def test_add_viewname(self):
        from pyramid.static import static_view
        config = DummyConfig()
        inst = self._makeOne(config)
        inst.add('view', 'anotherpackage:path', cache_max_age=1)
        expected = [('view/', 'anotherpackage:path/', False)]
        self.assertEqual(inst.registrations, expected)
        self.assertEqual(config.route_args, ('view/', 'view/*subpath'))
        self.assertEqual(config.view_kw['permission'],
                         '__no_permission_required__')
        self.assertEqual(config.view_kw['view'].__class__, static_view)
        self.assertEqual(config.view_kw['view'].app.cache_max_age, 1)

    def test_add_viewname_with_permission(self):
        config = DummyConfig()
        inst = self._makeOne(config)
        inst.add('view', 'anotherpackage:path', cache_max_age=1,
                 permission='abc')
        self.assertEqual(config.view_kw['permission'], 'abc')

    def test_add_viewname_with_view_permission(self):
        config = DummyConfig()
        inst = self._makeOne(config)
        inst.add('view', 'anotherpackage:path', cache_max_age=1,
                 view_permission='abc')
        self.assertEqual(config.view_kw['permission'], 'abc')

    def test_add_viewname_with_view_context(self):
        config = DummyConfig()
        inst = self._makeOne(config)
        inst.add('view', 'anotherpackage:path', cache_max_age=1,
                 view_context=DummyContext)
        self.assertEqual(config.view_kw['context'], DummyContext)

    def test_add_viewname_with_view_for(self):
        config = DummyConfig()
        inst = self._makeOne(config)
        inst.add('view', 'anotherpackage:path', cache_max_age=1,
                 view_for=DummyContext)
        self.assertEqual(config.view_kw['context'], DummyContext)

    def test_add_viewname_with_for_(self):
        config = DummyConfig()
        inst = self._makeOne(config)
        inst.add('view', 'anotherpackage:path', cache_max_age=1,
                 for_=DummyContext)
        self.assertEqual(config.view_kw['context'], DummyContext)

    def test_add_viewname_with_view_renderer(self):
        config = DummyConfig()
        inst = self._makeOne(config)
        inst.add('view', 'anotherpackage:path', cache_max_age=1,
                 view_renderer='mypackage:templates/index.pt')
        self.assertEqual(config.view_kw['renderer'],
                         'mypackage:templates/index.pt')

    def test_add_viewname_with_renderer(self):
        config = DummyConfig()
        inst = self._makeOne(config)
        inst.add('view', 'anotherpackage:path', cache_max_age=1,
                 renderer='mypackage:templates/index.pt')
        self.assertEqual(config.view_kw['renderer'],
                         'mypackage:templates/index.pt')

    def test_add_viewname_with_view_attr(self):
        config = DummyConfig()
        inst = self._makeOne(config)
        inst.add('view', 'anotherpackage:path', cache_max_age=1,
                 view_attr='attr')
        self.assertEqual(config.view_kw['attr'], 'attr')

class DummyConfig:
    def add_route(self, *args, **kw):
        self.route_args = args
        self.route_kw = kw

    def add_view(self, *args, **kw):
        self.view_args = args
        self.view_kw = kw

class DummyStartResponse:
    def __call__(self, status, headerlist, exc_info=None):
        self.status = status
        self.headerlist = headerlist
        self.exc_info = exc_info
    
class DummyContext:
    pass

class DummyRequest:
    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        
    def get_response(self, application):
        return application

    def copy(self):
        self.copied = True
        return self

