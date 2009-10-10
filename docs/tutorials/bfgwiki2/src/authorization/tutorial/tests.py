import unittest
from repoze.bfg import testing

def _initTestingDB():
    from tutorial.models import DBSession
    from tutorial.models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession

def _registerRoutes():
    testing.registerRoute(':pagename', 'view_page')
    testing.registerRoute(':pagename/edit_page', 'edit_page')
    testing.registerRoute('add_page/:pagename', 'add_page')

class ViewWikiTests(unittest.TestCase):
    def test_it(self):
        from tutorial.views import view_wiki
        testing.registerRoute(':pagename', 'view_page')
        request = testing.DummyRequest()
        response = view_wiki(request)
        self.assertEqual(response.location, 'http://example.com/FrontPage')

class ViewPageTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        self.session.remove()
        
    def _callFUT(self, request):
        from tutorial.views import view_page
        return view_page(request)

    def test_it(self):
        from tutorial.models import Page
        request = testing.DummyRequest()
        request.matchdict['pagename'] = 'IDoExist'
        page = Page('IDoExist', 'Hello CruelWorld IDoExist')
        self.session.add(page)
        _registerRoutes()
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
        
    
class AddPageTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        self.session.remove()

    def _callFUT(self, request):
        from tutorial.views import add_page
        return add_page(request)

    def test_it_notsubmitted(self):
        _registerRoutes()
        request = testing.DummyRequest()
        request.matchdict = {'pagename':'AnotherPage'}
        info = self._callFUT(request)
        self.assertEqual(info['page'].data,'')
        self.assertEqual(info['save_url'],
                         'http://example.com/add_page/AnotherPage')
        
    def test_it_submitted(self):
        from tutorial.models import Page
        _registerRoutes()
        request = testing.DummyRequest({'form.submitted':True,
                                        'body':'Hello yo!'})
        request.matchdict = {'pagename':'AnotherPage'}
        response = self._callFUT(request)
        page = self.session.query(Page).filter_by(name='AnotherPage').one()
        self.assertEqual(page.data, 'Hello yo!')

class EditPageTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        self.session.remove()

    def _callFUT(self, request):
        from tutorial.views import edit_page
        return edit_page(request)

    def test_it_notsubmitted(self):
        from tutorial.models import Page
        _registerRoutes()
        request = testing.DummyRequest()
        request.matchdict = {'pagename':'abc'}
        page = Page('abc', 'hello')
        self.session.add(page)
        info = self._callFUT(request)
        self.assertEqual(info['page'], page)
        self.assertEqual(info['save_url'], 'http://example.com/abc/edit_page')
        
    def test_it_submitted(self):
        from tutorial.models import Page
        _registerRoutes()
        request = testing.DummyRequest({'form.submitted':True,
                                        'body':'Hello yo!'})
        request.matchdict = {'pagename':'abc'}
        page = Page('abc', 'hello')
        self.session.add(page)
        response = self._callFUT(request)
        self.assertEqual(response.location, 'http://example.com/abc')
        self.assertEqual(page.data, 'Hello yo!')
