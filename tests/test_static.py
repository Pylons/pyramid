import datetime
import os.path
import unittest

here = os.path.dirname(__file__)

# 5 years from now (more or less)
fiveyrsfuture = datetime.datetime.utcnow() + datetime.timedelta(5 * 365)


class Test_static_view_use_subpath_False(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.static import static_view

        return static_view

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def _makeRequest(self, kw=None):
        from pyramid.request import Request

        environ = {
            'wsgi.url_scheme': 'http',
            'wsgi.version': (1, 0),
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '6543',
            'PATH_INFO': '/',
            'SCRIPT_NAME': '',
            'REQUEST_METHOD': 'GET',
        }
        if kw is not None:
            environ.update(kw)
        return Request(environ=environ)

    def test_ctor_defaultargs(self):
        inst = self._makeOne('package:resource_name')
        self.assertEqual(inst.package_name, 'package')
        self.assertEqual(inst.docroot, 'resource_name')
        self.assertEqual(inst.cache_max_age, 3600)
        self.assertEqual(inst.index, 'index.html')
        self.assertEqual(inst.reload, False)
        self.assertEqual(inst.content_encodings, {})

    def test_call_adds_slash_path_info_empty(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest({'PATH_INFO': ''})
        context = DummyContext()
        from pyramid.httpexceptions import HTTPMovedPermanently

        self.assertRaises(HTTPMovedPermanently, inst, context, request)

    def test_path_info_slash_means_index_html(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest()
        context = DummyContext()
        response = inst(context, request)
        self.assertTrue(b'<html>static</html>' in response.body)

    def test_oob_singledot(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest({'PATH_INFO': '/./index.html'})
        context = DummyContext()
        response = inst(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertTrue(b'<html>static</html>' in response.body)

    def test_oob_emptyelement(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest({'PATH_INFO': '//index.html'})
        context = DummyContext()
        response = inst(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertTrue(b'<html>static</html>' in response.body)

    def test_oob_dotdotslash(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest({'PATH_INFO': '/subdir/../../minimal.pt'})
        context = DummyContext()
        from pyramid.httpexceptions import HTTPNotFound

        self.assertRaises(HTTPNotFound, inst, context, request)

    def test_oob_dotdotslash_encoded(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest(
            {'PATH_INFO': '/subdir/%2E%2E%2F%2E%2E/minimal.pt'}
        )
        context = DummyContext()
        from pyramid.httpexceptions import HTTPNotFound

        self.assertRaises(HTTPNotFound, inst, context, request)

    def test_oob_os_sep(self):
        import os

        inst = self._makeOne('tests:fixtures/static')
        dds = '..' + os.sep
        request = self._makeRequest(
            {'PATH_INFO': '/subdir/%s%sminimal.pt' % (dds, dds)}
        )
        context = DummyContext()
        from pyramid.httpexceptions import HTTPNotFound

        self.assertRaises(HTTPNotFound, inst, context, request)

    def test_oob_nul_char(self):
        import os

        inst = self._makeOne(f'{os.getcwd()}/tests/fixtures/static')
        dds = '..\x00/'
        request = self._makeRequest(
            {'PATH_INFO': f'/{dds}'}
        )
        context = DummyContext()
        from pyramid.httpexceptions import HTTPNotFound

        self.assertRaises(HTTPNotFound, inst, context, request)

    def test_resource_doesnt_exist(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest({'PATH_INFO': '/notthere'})
        context = DummyContext()
        from pyramid.httpexceptions import HTTPNotFound

        self.assertRaises(HTTPNotFound, inst, context, request)

    def test_resource_isdir(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest({'PATH_INFO': '/subdir/'})
        context = DummyContext()
        response = inst(context, request)
        self.assertTrue(b'<html>subdir</html>' in response.body)

    def test_resource_is_file(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest({'PATH_INFO': '/index.html'})
        context = DummyContext()
        response = inst(context, request)
        self.assertTrue(b'<html>static</html>' in response.body)

    def test_resource_is_file_with_wsgi_file_wrapper(self):
        from pyramid.response import _BLOCK_SIZE

        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest({'PATH_INFO': '/index.html'})

        class _Wrapper:
            def __init__(self, file, block_size=None):
                self.file = file
                self.block_size = block_size

        request.environ['wsgi.file_wrapper'] = _Wrapper
        context = DummyContext()
        response = inst(context, request)
        app_iter = response.app_iter
        self.assertTrue(isinstance(app_iter, _Wrapper))
        self.assertTrue(b'<html>static</html>' in app_iter.file.read())
        self.assertEqual(app_iter.block_size, _BLOCK_SIZE)
        app_iter.file.close()

    def test_resource_is_file_with_cache_max_age(self):
        inst = self._makeOne('tests:fixtures/static', cache_max_age=600)
        request = self._makeRequest({'PATH_INFO': '/index.html'})
        context = DummyContext()
        response = inst(context, request)
        self.assertTrue(b'<html>static</html>' in response.body)
        self.assertEqual(len(response.headerlist), 5)
        header_names = [x[0] for x in response.headerlist]
        header_names.sort()
        self.assertEqual(
            header_names,
            [
                'Cache-Control',
                'Content-Length',
                'Content-Type',
                'Expires',
                'Last-Modified',
            ],
        )

    def test_resource_is_file_with_no_cache_max_age(self):
        inst = self._makeOne('tests:fixtures/static', cache_max_age=None)
        request = self._makeRequest({'PATH_INFO': '/index.html'})
        context = DummyContext()
        response = inst(context, request)
        self.assertTrue(b'<html>static</html>' in response.body)
        self.assertEqual(len(response.headerlist), 3)
        header_names = [x[0] for x in response.headerlist]
        header_names.sort()
        self.assertEqual(
            header_names, ['Content-Length', 'Content-Type', 'Last-Modified']
        )

    def test_resource_notmodified(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest({'PATH_INFO': '/index.html'})
        request.if_modified_since = fiveyrsfuture
        context = DummyContext()
        response = inst(context, request)
        start_response = DummyStartResponse()
        app_iter = response(request.environ, start_response)
        try:
            self.assertEqual(start_response.status, '304 Not Modified')
            self.assertEqual(list(app_iter), [])
        finally:
            app_iter.close()

    def test_not_found(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest({'PATH_INFO': '/notthere.html'})
        context = DummyContext()
        from pyramid.httpexceptions import HTTPNotFound

        self.assertRaises(HTTPNotFound, inst, context, request)

    def test_gz_resource_no_content_encoding(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest({'PATH_INFO': '/arcs.svg.tgz'})
        context = DummyContext()
        response = inst(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/x-tar')
        self.assertEqual(response.content_encoding, None)
        response.app_iter.close()

    def test_resource_no_content_encoding(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest({'PATH_INFO': '/index.html'})
        context = DummyContext()
        response = inst(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'text/html')
        self.assertEqual(response.content_encoding, None)
        response.app_iter.close()


class Test_static_view_use_subpath_True(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.static import static_view

        return static_view

    def _makeOne(self, *arg, **kw):
        kw['use_subpath'] = True
        return self._getTargetClass()(*arg, **kw)

    def _makeRequest(self, kw=None):
        from pyramid.request import Request

        environ = {
            'wsgi.url_scheme': 'http',
            'wsgi.version': (1, 0),
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '6543',
            'PATH_INFO': '/',
            'SCRIPT_NAME': '',
            'REQUEST_METHOD': 'GET',
        }
        if kw is not None:
            environ.update(kw)
        return Request(environ=environ)

    def test_ctor_defaultargs(self):
        inst = self._makeOne('package:resource_name')
        self.assertEqual(inst.package_name, 'package')
        self.assertEqual(inst.docroot, 'resource_name')
        self.assertEqual(inst.cache_max_age, 3600)
        self.assertEqual(inst.index, 'index.html')
        self.assertEqual(inst.reload, False)
        self.assertEqual(inst.content_encodings, {})

    def test_call_adds_slash_path_info_empty(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest({'PATH_INFO': ''})
        request.subpath = ()
        context = DummyContext()
        from pyramid.httpexceptions import HTTPMovedPermanently

        self.assertRaises(HTTPMovedPermanently, inst, context, request)

    def test_path_info_slash_means_index_html(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest()
        request.subpath = ()
        context = DummyContext()
        response = inst(context, request)
        self.assertTrue(b'<html>static</html>' in response.body)

    def test_oob_singledot(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest()
        request.subpath = ('.', 'index.html')
        context = DummyContext()
        from pyramid.httpexceptions import HTTPNotFound

        self.assertRaises(HTTPNotFound, inst, context, request)

    def test_oob_emptyelement(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest()
        request.subpath = ('', 'index.html')
        context = DummyContext()
        from pyramid.httpexceptions import HTTPNotFound

        self.assertRaises(HTTPNotFound, inst, context, request)

    def test_oob_dotdotslash(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest()
        request.subpath = ('subdir', '..', '..', 'minimal.pt')
        context = DummyContext()
        from pyramid.httpexceptions import HTTPNotFound

        self.assertRaises(HTTPNotFound, inst, context, request)

    def test_oob_dotdotslash_encoded(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest()
        request.subpath = ('subdir', '%2E%2E', '%2E%2E', 'minimal.pt')
        context = DummyContext()
        from pyramid.httpexceptions import HTTPNotFound

        self.assertRaises(HTTPNotFound, inst, context, request)

    def test_oob_os_sep(self):
        import os

        inst = self._makeOne('tests:fixtures/static')
        dds = '..' + os.sep
        request = self._makeRequest()
        request.subpath = ('subdir', dds, dds, 'minimal.pt')
        context = DummyContext()
        from pyramid.httpexceptions import HTTPNotFound

        self.assertRaises(HTTPNotFound, inst, context, request)

    def test_resource_doesnt_exist(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest()
        request.subpath = 'notthere,'
        context = DummyContext()
        from pyramid.httpexceptions import HTTPNotFound

        self.assertRaises(HTTPNotFound, inst, context, request)

    def test_resource_isdir(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest()
        request.subpath = ('subdir',)
        context = DummyContext()
        response = inst(context, request)
        self.assertTrue(b'<html>subdir</html>' in response.body)

    def test_resource_is_file(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest()
        request.subpath = ('index.html',)
        context = DummyContext()
        response = inst(context, request)
        self.assertTrue(b'<html>static</html>' in response.body)

    def test_resource_is_file_with_cache_max_age(self):
        inst = self._makeOne('tests:fixtures/static', cache_max_age=600)
        request = self._makeRequest()
        request.subpath = ('index.html',)
        context = DummyContext()
        response = inst(context, request)
        self.assertTrue(b'<html>static</html>' in response.body)
        self.assertEqual(len(response.headerlist), 5)
        header_names = [x[0] for x in response.headerlist]
        header_names.sort()
        self.assertEqual(
            header_names,
            [
                'Cache-Control',
                'Content-Length',
                'Content-Type',
                'Expires',
                'Last-Modified',
            ],
        )

    def test_resource_is_file_with_no_cache_max_age(self):
        inst = self._makeOne('tests:fixtures/static', cache_max_age=None)
        request = self._makeRequest()
        request.subpath = ('index.html',)
        context = DummyContext()
        response = inst(context, request)
        self.assertTrue(b'<html>static</html>' in response.body)
        self.assertEqual(len(response.headerlist), 3)
        header_names = [x[0] for x in response.headerlist]
        header_names.sort()
        self.assertEqual(
            header_names, ['Content-Length', 'Content-Type', 'Last-Modified']
        )

    def test_resource_notmodified(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest()
        request.if_modified_since = fiveyrsfuture
        request.subpath = ('index.html',)
        context = DummyContext()
        response = inst(context, request)
        start_response = DummyStartResponse()
        app_iter = response(request.environ, start_response)
        try:
            self.assertEqual(start_response.status, '304 Not Modified')
            self.assertEqual(list(app_iter), [])
        finally:
            app_iter.close()

    def test_not_found(self):
        inst = self._makeOne('tests:fixtures/static')
        request = self._makeRequest()
        request.subpath = ('notthere.html',)
        context = DummyContext()
        from pyramid.httpexceptions import HTTPNotFound

        self.assertRaises(HTTPNotFound, inst, context, request)


class Test_static_view_content_encodings(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.static import static_view

        return static_view

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def _makeRequest(self, kw=None):
        from pyramid.request import Request

        environ = {
            'wsgi.url_scheme': 'http',
            'wsgi.version': (1, 0),
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '6543',
            'PATH_INFO': '/',
            'SCRIPT_NAME': '',
            'REQUEST_METHOD': 'GET',
        }
        if kw is not None:
            environ.update(kw)
        return Request(environ=environ)

    def test_call_without_accept(self):
        inst = self._makeOne(
            'tests:fixtures/static', content_encodings=['gzip']
        )
        request = self._makeRequest({'PATH_INFO': '/encoded.html'})
        context = DummyContext()

        res = inst(context, request)
        self.assertEqual(res.headers['Vary'], 'Accept-Encoding')
        self.assertNotIn('Content-Encoding', res.headers)
        self.assertEqual(len(res.body), 221)

    def test_call_with_accept_gzip(self):
        inst = self._makeOne(
            'tests:fixtures/static', content_encodings=['gzip']
        )
        request = self._makeRequest(
            {'PATH_INFO': '/encoded.html', 'HTTP_ACCEPT_ENCODING': 'gzip'}
        )
        context = DummyContext()

        res = inst(context, request)
        self.assertEqual(res.headers['Vary'], 'Accept-Encoding')
        self.assertEqual(res.headers['Content-Encoding'], 'gzip')
        self.assertEqual(len(res.body), 187)

    def test_call_for_encoded_variant_without_unencoded_variant_no_accept(
        self,
    ):
        inst = self._makeOne(
            'tests:fixtures/static', content_encodings=['gzip']
        )
        request = self._makeRequest({'PATH_INFO': '/only_encoded.html.gz'})
        context = DummyContext()

        res = inst(context, request)
        self.assertNotIn('Vary', res.headers)
        self.assertNotIn('Content-Encoding', res.headers)
        self.assertEqual(len(res.body), 187)

    def test_call_for_encoded_variant_without_unencoded_variant_with_accept(
        self,
    ):
        inst = self._makeOne(
            'tests:fixtures/static', content_encodings=['gzip']
        )
        request = self._makeRequest(
            {
                'PATH_INFO': '/only_encoded.html.gz',
                'HTTP_ACCEPT_ENCODING': 'gzip',
            }
        )
        context = DummyContext()

        res = inst(context, request)
        self.assertNotIn('Vary', res.headers)
        self.assertNotIn('Content-Encoding', res.headers)
        self.assertEqual(len(res.body), 187)

    def test_call_for_unencoded_variant_with_only_encoded_variant_no_accept(
        self,
    ):
        from pyramid.httpexceptions import HTTPNotFound

        inst = self._makeOne(
            'tests:fixtures/static', content_encodings=['gzip']
        )
        request = self._makeRequest({'PATH_INFO': '/only_encoded.html'})
        context = DummyContext()

        self.assertRaises(HTTPNotFound, lambda: inst(context, request))

    def test_call_for_unencoded_variant_with_only_encoded_variant_with_accept(
        self,
    ):
        inst = self._makeOne(
            'tests:fixtures/static', content_encodings=['gzip']
        )
        request = self._makeRequest(
            {
                'PATH_INFO': '/only_encoded.html',
                'HTTP_ACCEPT_ENCODING': 'gzip',
            }
        )
        context = DummyContext()

        res = inst(context, request)
        self.assertNotIn('Vary', res.headers)
        self.assertEqual(res.headers['Content-Encoding'], 'gzip')
        self.assertEqual(len(res.body), 187)

    def test_call_for_unencoded_variant_with_only_encoded_variant_bad_accept(
        self,
    ):
        from pyramid.httpexceptions import HTTPNotFound

        inst = self._makeOne(
            'tests:fixtures/static', content_encodings=['gzip']
        )
        request = self._makeRequest(
            {'PATH_INFO': '/only_encoded.html', 'HTTP_ACCEPT_ENCODING': 'br'}
        )
        context = DummyContext()

        self.assertRaises(HTTPNotFound, lambda: inst(context, request))

    def test_call_get_possible_files_is_cached(self):
        inst = self._makeOne('tests:fixtures/static')
        result1 = inst.get_possible_files('tests:fixtures/static/encoded.html')
        result2 = inst.get_possible_files('tests:fixtures/static/encoded.html')
        self.assertIs(result1, result2)

    def test_call_get_possible_files_is_not_cached(self):
        inst = self._makeOne('tests:fixtures/static', reload=True)
        result1 = inst.get_possible_files('tests:fixtures/static/encoded.html')
        result2 = inst.get_possible_files('tests:fixtures/static/encoded.html')
        self.assertIsNot(result1, result2)


class TestQueryStringConstantCacheBuster(unittest.TestCase):
    def _makeOne(self, param=None):
        from pyramid.static import QueryStringConstantCacheBuster as cls

        if param:
            inst = cls('foo', param)
        else:
            inst = cls('foo')
        return inst

    def test_token(self):
        fut = self._makeOne().tokenize
        self.assertEqual(fut(None, 'whatever', None), 'foo')

    def test_it(self):
        fut = self._makeOne()
        self.assertEqual(
            fut('foo', 'bar', {}), ('bar', {'_query': {'x': 'foo'}})
        )

    def test_change_param(self):
        fut = self._makeOne('y')
        self.assertEqual(
            fut('foo', 'bar', {}), ('bar', {'_query': {'y': 'foo'}})
        )

    def test_query_is_already_tuples(self):
        fut = self._makeOne()
        self.assertEqual(
            fut('foo', 'bar', {'_query': [('a', 'b')]}),
            ('bar', {'_query': (('a', 'b'), ('x', 'foo'))}),
        )

    def test_query_is_tuple_of_tuples(self):
        fut = self._makeOne()
        self.assertEqual(
            fut('foo', 'bar', {'_query': (('a', 'b'),)}),
            ('bar', {'_query': (('a', 'b'), ('x', 'foo'))}),
        )


class TestManifestCacheBuster(unittest.TestCase):
    def _makeOne(self, path, **kw):
        from pyramid.static import ManifestCacheBuster as cls

        return cls(path, **kw)

    def test_it(self):
        manifest_path = os.path.join(here, 'fixtures', 'manifest.json')
        fut = self._makeOne(manifest_path)
        self.assertEqual(fut('foo', 'bar', {}), ('bar', {}))
        self.assertEqual(
            fut('foo', 'css/main.css', {}), ('css/main-test.css', {})
        )

    def test_it_with_relspec(self):
        fut = self._makeOne('fixtures/manifest.json')
        self.assertEqual(fut('foo', 'bar', {}), ('bar', {}))
        self.assertEqual(
            fut('foo', 'css/main.css', {}), ('css/main-test.css', {})
        )

    def test_it_with_absspec(self):
        fut = self._makeOne('tests:fixtures/manifest.json')
        self.assertEqual(fut('foo', 'bar', {}), ('bar', {}))
        self.assertEqual(
            fut('foo', 'css/main.css', {}), ('css/main-test.css', {})
        )

    def test_reload(self):
        manifest_path = os.path.join(here, 'fixtures', 'manifest.json')
        new_manifest_path = os.path.join(here, 'fixtures', 'manifest2.json')
        inst = self._makeOne('foo', reload=True)
        inst.getmtime = lambda *args, **kwargs: 0
        fut = inst

        # test without a valid manifest
        self.assertEqual(fut('foo', 'css/main.css', {}), ('css/main.css', {}))

        # swap to a real manifest, setting mtime to 0
        inst.manifest_path = manifest_path
        self.assertEqual(
            fut('foo', 'css/main.css', {}), ('css/main-test.css', {})
        )

        # ensure switching the path doesn't change the result
        inst.manifest_path = new_manifest_path
        self.assertEqual(
            fut('foo', 'css/main.css', {}), ('css/main-test.css', {})
        )

        # update mtime, should cause a reload
        inst.getmtime = lambda *args, **kwargs: 1
        self.assertEqual(
            fut('foo', 'css/main.css', {}), ('css/main-678b7c80.css', {})
        )

    def test_invalid_manifest(self):
        self.assertRaises(IOError, lambda: self._makeOne('foo'))

    def test_invalid_manifest_with_reload(self):
        inst = self._makeOne('foo', reload=True)
        self.assertEqual(inst.manifest, {})


class DummyContext:
    pass


class DummyStartResponse:
    status = ()
    headers = ()

    def __call__(self, status, headers):
        self.status = status
        self.headers = headers
