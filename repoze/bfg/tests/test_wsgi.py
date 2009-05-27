import unittest

class WSGIAppTests(unittest.TestCase):
    def _callFUT(self, app):
        from repoze.bfg.wsgi import wsgiapp
        return wsgiapp(app)

    def test_decorator(self):
        context = DummyContext()
        request = DummyRequest()
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)

class WSGIApp2Tests(unittest.TestCase):
    def _callFUT(self, app):
        from repoze.bfg.wsgi import wsgiapp2
        return wsgiapp2(app)

    def test_decorator_traversed_is_None(self):
        context = DummyContext()
        request = DummyRequest()
        request.traversed = None
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)

    def test_decorator_traversed_not_None_with_subpath_and_view_name(self):
        context = DummyContext()
        request = DummyRequest()
        request.traversed = ['a', 'b']
        request.virtual_root_path = ['a']
        request.subpath = ['subpath']
        request.view_name = 'view_name'
        request.environ = {'SCRIPT_NAME':'/foo'}
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)
        self.assertEqual(request.environ['PATH_INFO'], '/subpath')
        self.assertEqual(request.environ['SCRIPT_NAME'], '/foo/b/view_name')
        
    def test_decorator_traversed_not_None_with_subpath_no_view_name(self):
        context = DummyContext()
        request = DummyRequest()
        request.traversed = ['a', 'b']
        request.virtual_root_path = ['a']
        request.subpath = ['subpath']
        request.view_name = ''
        request.environ = {'SCRIPT_NAME':'/foo'}
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)
        self.assertEqual(request.environ['PATH_INFO'], '/subpath')
        self.assertEqual(request.environ['SCRIPT_NAME'], '/foo/b')

    def test_decorator_traversed_not_None_no_subpath_with_view_name(self):
        context = DummyContext()
        request = DummyRequest()
        request.traversed = ['a', 'b']
        request.virtual_root_path = ['a']
        request.subpath = []
        request.view_name = 'view_name'
        request.environ = {'SCRIPT_NAME':'/foo'}
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)
        self.assertEqual(request.environ['PATH_INFO'], '/')
        self.assertEqual(request.environ['SCRIPT_NAME'], '/foo/b/view_name')

    def test_decorator_traversed_empty_with_view_name(self):
        context = DummyContext()
        request = DummyRequest()
        request.traversed = []
        request.virtual_root_path = []
        request.subpath = []
        request.view_name = 'view_name'
        request.environ = {'SCRIPT_NAME':'/foo'}
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)
        self.assertEqual(request.environ['PATH_INFO'], '/')
        self.assertEqual(request.environ['SCRIPT_NAME'], '/foo/view_name')

    def test_decorator_traversed_empty_no_view_name(self):
        context = DummyContext()
        request = DummyRequest()
        request.traversed = []
        request.virtual_root_path = []
        request.subpath = []
        request.view_name = ''
        request.environ = {'SCRIPT_NAME':'/foo'}
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)
        self.assertEqual(request.environ['PATH_INFO'], '/')
        self.assertEqual(request.environ['SCRIPT_NAME'], '/foo')

    def test_decorator_traversed_empty_no_view_name_no_script_name(self):
        context = DummyContext()
        request = DummyRequest()
        request.traversed = []
        request.virtual_root_path = []
        request.subpath = []
        request.view_name = ''
        request.environ = {'SCRIPT_NAME':''}
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)
        self.assertEqual(request.environ['PATH_INFO'], '/')
        self.assertEqual(request.environ['SCRIPT_NAME'], '')

class TestNotFound(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.wsgi import NotFound
        return NotFound

    def _makeOne(self):
        return self._getTargetClass()()

    def test_no_message(self):
        environ = {}
        L = []
        def start_response(status, headers):
            L.append((status, headers))
        app = self._makeOne()
        result = app(environ, start_response)
        self.assertEqual(len(result), 1)
        self.failUnless('404 Not Found' in result[0])
        self.assertEqual(L[0][0], '404 Not Found')
        self.assertEqual(L[0][1], [('Content-Length', str(len(result[0]))),
                                   ('Content-Type', 'text/html')])
        
    def test_with_message(self):
        environ = {'repoze.bfg.message':'<hi!>'}
        L = []
        def start_response(status, headers):
            L.append((status, headers))
        app = self._makeOne()
        result = app(environ, start_response)
        self.assertEqual(len(result), 1)
        self.failUnless('404 Not Found' in result[0])
        self.failUnless('&lt;hi!&gt;' in result[0])
        self.assertEqual(L[0][0], '404 Not Found')
        self.assertEqual(L[0][1], [('Content-Length', str(len(result[0]))),
                                   ('Content-Type', 'text/html')])

class TestUnauthorized(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.wsgi import Unauthorized
        return Unauthorized

    def _makeOne(self):
        return self._getTargetClass()()

    def test_no_message(self):
        environ = {}
        L = []
        def start_response(status, headers):
            L.append((status, headers))
        app = self._makeOne()
        result = app(environ, start_response)
        self.assertEqual(len(result), 1)
        self.failUnless('401 Unauthorized' in result[0])
        self.assertEqual(L[0][0], '401 Unauthorized')
        self.assertEqual(L[0][1], [('Content-Length', str(len(result[0]))),
                                   ('Content-Type', 'text/html')])
        
    def test_with_message(self):
        environ = {'repoze.bfg.message':'<hi!>'}
        L = []
        def start_response(status, headers):
            L.append((status, headers))
        app = self._makeOne()
        result = app(environ, start_response)
        self.assertEqual(len(result), 1)
        self.failUnless('401 Unauthorized' in result[0])
        self.failUnless('&lt;hi!&gt;' in result[0])
        self.assertEqual(L[0][0], '401 Unauthorized')
        self.assertEqual(L[0][1], [('Content-Length', str(len(result[0]))),
                                   ('Content-Type', 'text/html')])

def dummyapp(environ, start_response):
    """ """

class DummyContext:
    pass

class DummyRequest:
    def get_response(self, application):
        return application


        
      

    

