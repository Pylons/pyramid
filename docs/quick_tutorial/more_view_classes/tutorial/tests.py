import unittest

from pyramid import testing


class TutorialViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_full_name(self):
        from .views import TutorialViews

        request = testing.DummyRequest()
        request.matchdict['first'] = 'jane'
        request.matchdict['last'] = 'doe'
        inst = TutorialViews(request)
        self.assertEqual('jane doe', inst.full_name)

    def test_home(self):
        from .views import TutorialViews

        request = testing.DummyRequest()
        inst = TutorialViews(request)
        response = inst.home()
        self.assertEqual('Home View', response['page_title'])

    def test_hello(self):
        from .views import TutorialViews

        request = testing.DummyRequest()
        inst = TutorialViews(request)
        response = inst.hello()
        self.assertEqual('Hello View', response['page_title'])

    def test_edit(self):
        from .views import TutorialViews

        request = testing.DummyRequest(params={'new_name': 'John Doe'})
        inst = TutorialViews(request)
        response = inst.edit()
        self.assertEqual('Edit View', response['page_title'])
        self.assertEqual('John Doe', response['new_name'])

    def test_delete(self):
        from .views import TutorialViews

        request = testing.DummyRequest()
        inst = TutorialViews(request)
        response = inst.delete()
        self.assertEqual('Delete View', response['page_title'])


class TutorialFunctionalTests(unittest.TestCase):
    def setUp(self):
        from tutorial import main
        app = main({})
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_home(self):
        res = self.testapp.get('/', status=200)
        self.assertIn(b'TutorialViews - Home View', res.body)

    def test_hello(self):
        res = self.testapp.get('/howdy/jane/doe', status=200)
        self.assertIn(b'TutorialViews - Hello View', res.body)

    def test_edit(self):
        res = self.testapp.post(
                '/howdy/jane/doe', params={'new_name': 'John Doe'}, status=200)
        self.assertIn(b'TutorialViews - Edit View', res.body)
        self.assertIn(b'John Doe', res.body)

    def test_delete(self):
        res = self.testapp.post(
                '/howdy/jane/doe', params={'form.delete': 'Jane Doe'}, status=200)
        self.assertIn(b'TutorialViews - Delete View', res.body)
