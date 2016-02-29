import unittest
import transaction

from pyramid import testing


def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)


class BaseTest(unittest.TestCase):
    def setUp(self):
        from ..models import get_tm_session
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('..models')
        self.config.include('..routes')

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

    def makeUser(self, name, role, password='dummy'):
        from ..models import User
        user = User(name=name, role=role)
        user.set_password(password)
        return user

    def makePage(self, name, data, creator):
        from ..models import Page
        return Page(name=name, data=data, creator=creator)


class ViewWikiTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('..routes')

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
        from ..routes import PageResource

        # add a page to the db
        user = self.makeUser('foo', 'editor')
        page = self.makePage('IDoExist', 'Hello CruelWorld IDoExist', user)
        self.session.add_all([page, user])

        # create a request asking for the page we've created
        request = dummy_request(self.session)
        request.context = PageResource(page)

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

    def test_it_pageexists(self):
        from ..models import Page
        from ..routes import NewPage
        request = testing.DummyRequest({'form.submitted': True,
                                        'body': 'Hello yo!'},
                                       dbsession=self.session)
        request.user = self.makeUser('foo', 'editor')
        request.context = NewPage('AnotherPage')
        self._callFUT(request)
        pagecount = self.session.query(Page).filter_by(name='AnotherPage').count()
        self.assertGreater(pagecount, 0)

    def test_it_notsubmitted(self):
        from ..routes import NewPage
        request = dummy_request(self.session)
        request.user = self.makeUser('foo', 'editor')
        request.context = NewPage('AnotherPage')
        info = self._callFUT(request)
        self.assertEqual(info['pagedata'], '')
        self.assertEqual(info['save_url'],
                         'http://example.com/add_page/AnotherPage')

    def test_it_submitted(self):
        from ..models import Page
        from ..routes import NewPage
        request = testing.DummyRequest({'form.submitted': True,
                                        'body': 'Hello yo!'},
                                       dbsession=self.session)
        request.user = self.makeUser('foo', 'editor')
        request.context = NewPage('AnotherPage')
        self._callFUT(request)
        page = self.session.query(Page).filter_by(name='AnotherPage').one()
        self.assertEqual(page.data, 'Hello yo!')


class EditPageTests(BaseTest):
    def _callFUT(self, request):
        from tutorial.views.default import edit_page
        return edit_page(request)

    def makeContext(self, page):
        from ..routes import PageResource
        return PageResource(page)

    def test_it_notsubmitted(self):
        user = self.makeUser('foo', 'editor')
        page = self.makePage('abc', 'hello', user)
        self.session.add_all([page, user])

        request = dummy_request(self.session)
        request.context = self.makeContext(page)
        info = self._callFUT(request)
        self.assertEqual(info['pagename'], 'abc')
        self.assertEqual(info['save_url'],
                         'http://example.com/abc/edit_page')

    def test_it_submitted(self):
        user = self.makeUser('foo', 'editor')
        page = self.makePage('abc', 'hello', user)
        self.session.add_all([page, user])

        request = testing.DummyRequest({'form.submitted': True,
                                        'body': 'Hello yo!'},
                                       dbsession=self.session)
        request.context = self.makeContext(page)
        response = self._callFUT(request)
        self.assertEqual(response.location, 'http://example.com/abc')
        self.assertEqual(page.data, 'Hello yo!')
