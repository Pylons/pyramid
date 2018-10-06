import unittest

from pyramid import testing


class TutorialViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_hello_world(self):
        from tutorial.views import TutorialViews

        request = testing.DummyRequest()
        response = TutorialViews.hello(request)
        self.assertEqual(response, {'name': 'Hello View'})


class TutorialFunctionalTests(unittest.TestCase):
    def setUp(self):
        from tutorial import main
        app = main(None, **{'tutorial.secret': '98zd'})
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_home(self):
        res = self.testapp.get('/', status=200)
        self.assertIn(b'<title>Quick Tutorial: Home View</title>', res.body)

    def test_hello_without_authetication(self):
        res = self.testapp.get('/howdy', status=200)
        self.assertIn(b'<title>Quick Tutorial: Login</title>', res.body)

    def test_editor(self):

        res = self.testapp.post(
            '/login',
            {'login': 'editor', 'password': 'editor', 'form.submitted': True},
            status=302)

        res = self.testapp.get('/howdy', status=200)
        self.assertIn(b'<title>Quick Tutorial: Hello View</title>', res.body)

    def test_viewer(self):

        res = self.testapp.post(
            '/login',
            {'login': 'viewer', 'password': 'viewer', 'form.submitted': True},
            status=302
        )

        res = self.testapp.get('/howdy', status=200)
        self.assertIn(b'<title>Quick Tutorial: Login</title>', res.body)
