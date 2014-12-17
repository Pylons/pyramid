import unittest

from pyramid import testing


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'MyProject')

class ViewIntegrationTests(unittest.TestCase):
    def setUp(self):
        """ This sets up the application registry with the
        registrations your application declares in its ``includeme``
        function.
        """
        self.config = testing.setUp()
        self.config.include('myproject')

    def tearDown(self):
        """ Clear out the application registry """
        testing.tearDown()

    def test_my_view(self):
        from myproject.views import my_view
        request = testing.DummyRequest()
        result = my_view(request)
        self.assertEqual(result.status, '200 OK')
        body = result.app_iter[0]
        self.assertTrue('Welcome to' in body)
        self.assertEqual(len(result.headerlist), 2)
        self.assertEqual(result.headerlist[0],
                         ('Content-Type', 'text/html; charset=UTF-8'))
        self.assertEqual(result.headerlist[1], ('Content-Length',
                                                str(len(body))))

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from myproject import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue('Pyramid' in res.body)
