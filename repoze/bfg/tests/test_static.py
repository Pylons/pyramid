import unittest

class TestPackageURLParser(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.static import PackageURLParser
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
        inst = self._makeOne('package', 'resource/name', root_resource='root',
                             cache_max_age=100)
        self.assertEqual(inst.package_name, 'package')
        self.assertEqual(inst.resource_name, 'resource/name')
        self.assertEqual(inst.root_resource, 'root')
        self.assertEqual(inst.cache_max_age, 100)
        
    def test_ctor_defaultargs(self):
        inst = self._makeOne('package', 'resource/name')
        self.assertEqual(inst.package_name, 'package')
        self.assertEqual(inst.resource_name, 'resource/name')
        self.assertEqual(inst.root_resource, 'resource/name')
        self.assertEqual(inst.cache_max_age, None)

    def test_call_adds_slash_path_info_empty(self):
        environ = self._makeEnviron(PATH_INFO='')
        inst = self._makeOne('repoze.bfg.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.failUnless('301 Moved Permanently' in body)
        self.failUnless('http://example.com:6543/' in body)
        
    def test_path_info_slash_means_index_html(self):
        environ = self._makeEnviron()
        inst = self._makeOne('repoze.bfg.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.failUnless('<html>static</html>' in body)

    def test_resource_out_of_bounds(self):
        environ = self._makeEnviron()
        inst = self._makeOne('repoze.bfg.tests', 'fixtures/static')
        inst.root_resource = 'abcdef'
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.failUnless('404 Not Found' in body)
        self.failUnless('http://example.com:6543/' in body)

    def test_resource_doesnt_exist(self):
        environ = self._makeEnviron(PATH_INFO='/notthere')
        inst = self._makeOne('repoze.bfg.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.failUnless('404 Not Found' in body)
        self.failUnless('http://example.com:6543/' in body)

    def test_resource_isdir(self):
        environ = self._makeEnviron(PATH_INFO='/subdir/')
        inst = self._makeOne('repoze.bfg.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.failUnless('<html>subdir</html>' in body)

    def test_resource_is_file(self):
        environ = self._makeEnviron(PATH_INFO='/index.html')
        inst = self._makeOne('repoze.bfg.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.failUnless('<html>static</html>' in body)

    def test_resource_is_file_with_cache_max_age(self):
        environ = self._makeEnviron(PATH_INFO='/index.html')
        inst = self._makeOne('repoze.bfg.tests', 'fixtures/static',
                             cache_max_age=600)
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.failUnless('<html>static</html>' in body)
        self.assertEqual(len(sr.headerlist), 8)
        header_names = [ x[0] for x in sr.headerlist ]
        header_names.sort()
        self.assertEqual(header_names,
                         ['Accept-Ranges', 'Cache-Control',
                          'Content-Length', 'Content-Range',
                          'Content-Type', 'ETag', 'Expires', 'Last-Modified'])

    def test_resource_is_file_with_no_cache_max_age(self):
        environ = self._makeEnviron(PATH_INFO='/index.html')
        inst = self._makeOne('repoze.bfg.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        body = response[0]
        self.failUnless('<html>static</html>' in body)
        self.assertEqual(len(sr.headerlist), 6)
        header_names = [ x[0] for x in sr.headerlist ]
        header_names.sort()
        self.assertEqual(header_names,
                         ['Accept-Ranges', 'Content-Length', 'Content-Range',
                          'Content-Type', 'ETag', 'Last-Modified'])

    def test_if_none_match(self):
        class DummyEq(object):
            def __eq__(self, other):
                return True
        dummy_eq = DummyEq()
        environ = self._makeEnviron(HTTP_IF_NONE_MATCH=dummy_eq)
        inst = self._makeOne('repoze.bfg.tests', 'fixtures/static')
        sr = DummyStartResponse()
        response = inst(environ, sr)
        self.assertEqual(len(sr.headerlist), 1)
        self.assertEqual(sr.status, '304 Not Modified')
        self.assertEqual(sr.headerlist[0][0], 'ETag')
        self.assertEqual(response[0], '')

    def test_repr(self):
        inst = self._makeOne('repoze.bfg.tests', 'fixtures/static')
        self.failUnless(
            repr(inst).startswith(
            '<PackageURLParser repoze.bfg.tests:fixtures/static at'))

    def test_not_found(self):
        inst = self._makeOne('repoze.bfg.tests', 'fixtures/static')
        environ = self._makeEnviron()
        sr = DummyStartResponse()
        response = inst.not_found(environ, sr, 'debug_message')
        body = response[0]
        self.failUnless('404 Not Found' in body)
        self.assertEqual(sr.status, '404 Not Found')

class TestStaticRootFactory(unittest.TestCase):
    def test_it(self):
        from repoze.bfg.static import StaticRootFactory
        factory = StaticRootFactory('abc') 
        self.assertEqual(factory.spec, 'abc')
        self.assertEqual(factory({}), factory)

class DummyStartResponse:
    def __call__(self, status, headerlist, exc_info=None):
        self.status = status
        self.headerlist = headerlist
        self.exc_info = exc_info
        
    
