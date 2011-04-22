import unittest

class WSGIAppTests(unittest.TestCase):
    def _callFUT(self, app):
        from pyramid.wsgi import wsgiapp
        return wsgiapp(app)

    def test_decorator(self):
        context = DummyContext()
        request = DummyRequest()
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)

class WSGIApp2Tests(unittest.TestCase):
    def _callFUT(self, app):
        from pyramid.wsgi import wsgiapp2
        return wsgiapp2(app)

    def test_decorator_with_subpath_and_view_name(self):
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ('subpath',)
        request.environ = {'SCRIPT_NAME':'/foo',
                           'PATH_INFO':'/b/view_name/subpath'}
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)
        self.assertEqual(request.environ['PATH_INFO'], '/subpath')
        self.assertEqual(request.environ['SCRIPT_NAME'], '/foo/b/view_name')

    def test_decorator_with_subpath_no_view_name(self):
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ('subpath',)
        request.environ = {'SCRIPT_NAME':'/foo', 'PATH_INFO':'/b/subpath'}
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)
        self.assertEqual(request.environ['PATH_INFO'], '/subpath')
        self.assertEqual(request.environ['SCRIPT_NAME'], '/foo/b')

    def test_decorator_no_subpath_with_view_name(self):
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ()
        request.environ = {'SCRIPT_NAME':'/foo', 'PATH_INFO':'/b/view_name'}
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)
        self.assertEqual(request.environ['PATH_INFO'], '/')
        self.assertEqual(request.environ['SCRIPT_NAME'], '/foo/b/view_name')

    def test_decorator_traversed_empty_with_view_name(self):
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ()
        request.environ = {'SCRIPT_NAME':'/foo', 'PATH_INFO':'/view_name'}
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)
        self.assertEqual(request.environ['PATH_INFO'], '/')
        self.assertEqual(request.environ['SCRIPT_NAME'], '/foo/view_name')

    def test_decorator_traversed_empty_no_view_name(self):
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ()
        request.environ = {'SCRIPT_NAME':'/foo', 'PATH_INFO':'/'}
        decorator = self._callFUT(dummyapp)
        response = decorator(context, request)
        self.assertEqual(response, dummyapp)
        self.assertEqual(request.environ['PATH_INFO'], '/')
        self.assertEqual(request.environ['SCRIPT_NAME'], '/foo')

    def test_decorator_traversed_empty_no_view_name_no_script_name(self):
        context = DummyContext()
        request = DummyRequest()
        request.subpath = ()
        request.environ = {'SCRIPT_NAME':'', 'PATH_INFO':'/'}
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

    def copy(self):
        self.copied = True
        return self

