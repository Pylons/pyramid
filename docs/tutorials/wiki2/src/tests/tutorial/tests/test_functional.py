import unittest

from pyramid import testing


def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)


def _register_routes(config):
    config.add_route('view_page', '{pagename}')
    config.add_route('edit_page', '{pagename}/edit_page')
    config.add_route('add_page', 'add_page/{pagename}')


class FunctionalTests(unittest.TestCase):

    viewer_login = '/login?login=viewer&password=viewer' \
                   '&came_from=FrontPage&form.submitted=Login'
    viewer_wrong_login = '/login?login=viewer&password=incorrect' \
                   '&came_from=FrontPage&form.submitted=Login'
    editor_login = '/login?login=editor&password=editor' \
                   '&came_from=FrontPage&form.submitted=Login'

    engine = None

    @staticmethod
    def setup_database():
        import transaction
        from tutorial.models.mymodel import Page
        from tutorial.models.meta import (
            Base,
            )
        import tutorial.models.meta


        def initialize_db(dbsession, engine):
            Base.metadata.create_all(engine)
            with transaction.manager:
                model = Page(name='FrontPage', data='This is the front page')
                dbsession.add(model)

        def wrap_get_session(transaction_manager, dbmaker):
            dbsession = get_session(transaction_manager, dbmaker)
            initialize_db(dbsession, engine)
            tutorial.models.meta.get_session = get_session
            tutorial.models.meta.get_engine = get_engine
            return dbsession

        def wrap_get_engine(settings):
            global engine
            engine = get_engine(settings)
            return engine

        get_session = tutorial.models.meta.get_session
        tutorial.models.meta.get_session = wrap_get_session

        get_engine = tutorial.models.meta.get_engine
        tutorial.models.meta.get_engine = wrap_get_engine

    @classmethod
    def setUpClass(cls):
        cls.setup_database()

        from webtest import TestApp
        from tutorial import main
        settings = {'sqlalchemy.url': 'sqlite://'}
        app = main({}, **settings)
        cls.testapp = TestApp(app)

    @classmethod
    def tearDownClass(cls):
        from tutorial.models.meta import Base
        Base.metadata.drop_all(engine)

    def tearDown(self):
        import transaction
        transaction.abort()

    def test_root(self):
        res = self.testapp.get('/', status=302)
        self.assertEqual(res.location, 'http://localhost/FrontPage')

    def test_FrontPage(self):
        res = self.testapp.get('/FrontPage', status=200)
        self.assertTrue(b'FrontPage' in res.body)

    def test_unexisting_page(self):
        self.testapp.get('/SomePage', status=404)

    def test_successful_log_in(self):
        res = self.testapp.get(self.viewer_login, status=302)
        self.assertEqual(res.location, 'http://localhost/FrontPage')

    def test_failed_log_in(self):
        res = self.testapp.get(self.viewer_wrong_login, status=200)
        self.assertTrue(b'login' in res.body)

    def test_logout_link_present_when_logged_in(self):
        self.testapp.get(self.viewer_login, status=302)
        res = self.testapp.get('/FrontPage', status=200)
        self.assertTrue(b'Logout' in res.body)

    def test_logout_link_not_present_after_logged_out(self):
        self.testapp.get(self.viewer_login, status=302)
        self.testapp.get('/FrontPage', status=200)
        res = self.testapp.get('/logout', status=302)
        self.assertTrue(b'Logout' not in res.body)

    def test_anonymous_user_cannot_edit(self):
        res = self.testapp.get('/FrontPage/edit_page', status=200)
        self.assertTrue(b'Login' in res.body)

    def test_anonymous_user_cannot_add(self):
        res = self.testapp.get('/add_page/NewPage', status=200)
        self.assertTrue(b'Login' in res.body)

    def test_viewer_user_cannot_edit(self):
        self.testapp.get(self.viewer_login, status=302)
        res = self.testapp.get('/FrontPage/edit_page', status=200)
        self.assertTrue(b'Login' in res.body)

    def test_viewer_user_cannot_add(self):
        self.testapp.get(self.viewer_login, status=302)
        res = self.testapp.get('/add_page/NewPage', status=200)
        self.assertTrue(b'Login' in res.body)

    def test_editors_member_user_can_edit(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/FrontPage/edit_page', status=200)
        self.assertTrue(b'Editing' in res.body)

    def test_editors_member_user_can_add(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/add_page/NewPage', status=200)
        self.assertTrue(b'Editing' in res.body)

    def test_editors_member_user_can_view(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/FrontPage', status=200)
        self.assertTrue(b'FrontPage' in res.body)
