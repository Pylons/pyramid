import unittest

from pyramid import testing


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from cc_starter.views.default import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'cc_starter')

    def test_notfound_view(self):
        from cc_starter.views.notfound import notfound_view
        request = testing.DummyRequest()
        info = notfound_view(request)
        self.assertEqual(info, {})


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from cc_starter import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue(b'Pyramid' in res.body)

    def test_notfound(self):
        res = self.testapp.get('/badurl', status=404)
        self.assertTrue(res.status_code == 404)
