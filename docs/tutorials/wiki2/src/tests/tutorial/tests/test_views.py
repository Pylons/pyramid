import unittest
import transaction

from pyramid import testing


def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)


def _register_routes(config):
    config.add_route('view_page', '{pagename}')
    config.add_route('add_page', 'add_page/{pagename}')
    config.add_route('edit_page', '{pagename}/edit_page')


class BaseTest(unittest.TestCase):
    def setUp(self):
        from ..models import get_tm_session
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('..models')
        self.config.include(_register_routes)

        session_factory = self.config.registry['dbsession_factory']
        self.session = get_tm_session(session_factory, transaction.manager)

        self.init_database()

    def init_database(self):
        from ..models.meta import Base
        session_factory = self.config.registry['dbsession_factory']
        engine = session_factory.kw['bind']
        Base.metadata.create_all(engine)

    def tearDown(self):
        testing.tearDown()
        transaction.abort()


class ViewWikiTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        _register_routes(self.config)

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from tutorial.views.default import view_wiki
        return view_wiki(request)

    def test_it(self):
        request = testing.DummyRequest()
        response = self._callFUT(request)
        self.assertEqual(response.location, 'http://example.com/FrontPage')


class ViewPageTests(BaseTest):
    def _callFUT(self, request):
        from tutorial.views.default import view_page
        return view_page(request)

    def test_it(self):
        # add a page to the db
        from ..models.mymodel import Page
        page = Page(name='IDoExist', data='Hello CruelWorld IDoExist')
        self.session.add(page)

        # create a request asking for the page we've created
        request = dummy_request(self.session)
        request.matchdict['pagename'] = 'IDoExist'

        # call the view we're testing and check its behavior
        info = self._callFUT(request)
        self.assertEqual(info['page'], page)
        self.assertEqual(
            info['content'],
            '<div class="document">\n'
            '<p>Hello <a href="http://example.com/add_page/CruelWorld">'
            'CruelWorld</a> '
            '<a href="http://example.com/IDoExist">'
            'IDoExist</a>'
            '</p>\n</div>\n')
        self.assertEqual(info['edit_url'],
                         'http://example.com/IDoExist/edit_page')


class AddPageTests(BaseTest):
    def _callFUT(self, request):
        from tutorial.views.default import add_page
        return add_page(request)

    def test_it_notsubmitted(self):
        request = dummy_request(self.session)
        request.matchdict = {'pagename': 'AnotherPage'}
        info = self._callFUT(request)
        self.assertEqual(info['page'].data, '')
        self.assertEqual(info['save_url'],
                         'http://example.com/add_page/AnotherPage')

    def test_it_submitted(self):
        from ..models.mymodel import Page
        request = testing.DummyRequest({'form.submitted': True,
                                        'body': 'Hello yo!'},
                                       dbsession=self.session)
        request.matchdict = {'pagename': 'AnotherPage'}
        self._callFUT(request)
        page = self.session.query(Page).filter_by(name='AnotherPage').one()
        self.assertEqual(page.data, 'Hello yo!')


class EditPageTests(BaseTest):
    def _callFUT(self, request):
        from tutorial.views.default import edit_page
        return edit_page(request)

    def test_it_notsubmitted(self):
        from ..models.mymodel import Page
        request = dummy_request(self.session)
        request.matchdict = {'pagename': 'abc'}
        page = Page(name='abc', data='hello')
        self.session.add(page)
        info = self._callFUT(request)
        self.assertEqual(info['page'], page)
        self.assertEqual(info['save_url'],
                         'http://example.com/abc/edit_page')

    def test_it_submitted(self):
        from ..models.mymodel import Page
        request = testing.DummyRequest({'form.submitted': True,
                                        'body': 'Hello yo!'},
                                       dbsession=self.session)
        request.matchdict = {'pagename': 'abc'}
        page = Page(name='abc', data='hello')
        self.session.add(page)
        response = self._callFUT(request)
        self.assertEqual(response.location, 'http://example.com/abc')
        self.assertEqual(page.data, 'Hello yo!')
