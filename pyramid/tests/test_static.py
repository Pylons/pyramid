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

