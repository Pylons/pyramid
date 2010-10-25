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

    def test_decorator_with_subpath_and_view_name(self):
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
        
    def test_decorator_with_subpath_no_view_name(self):
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

    def test_decorator_no_subpath_with_view_name(self):
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

def dummyapp(environ, start_response):
    """ """

class DummyContext:
    pass

class DummyRequest:
    def get_response(self, application):
        return application
