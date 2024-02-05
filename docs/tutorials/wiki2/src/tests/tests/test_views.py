from pyramid.testing import DummySecurityPolicy
import sqlalchemy as sa

from tutorial import models


def makeUser(name, role):
    return models.User(name=name, role=role)


def setUser(config, user):
    config.set_security_policy(
        DummySecurityPolicy(identity=user)
    )

def makePage(name, data, creator):
    return models.Page(name=name, data=data, creator=creator)

class Test_view_wiki:
    def _callFUT(self, request):
        from tutorial.views.default import view_wiki
        return view_wiki(request)

    def _addRoutes(self, config):
        config.add_route('view_page', '/{pagename}')

    def test_it(self, dummy_config, dummy_request):
        self._addRoutes(dummy_config)
        response = self._callFUT(dummy_request)
        assert response.location == 'http://example.com/FrontPage'

class Test_view_page:
    def _callFUT(self, request):
        from tutorial.views.default import view_page
        return view_page(request)

    def _makeContext(self, page):
        from tutorial.routes import PageResource
        return PageResource(page)

    def _addRoutes(self, config):
        config.add_route('edit_page', '/{pagename}/edit_page')
        config.add_route('add_page', '/add_page/{pagename}')
        config.add_route('view_page', '/{pagename}')

    def test_it(self, dummy_config, dummy_request, dbsession):
        # add a page to the db
        user = makeUser('foo', 'editor')
        page = makePage('IDoExist', 'Hello CruelWorld IDoExist', user)
        dbsession.add_all([page, user])

        # create a request asking for the page we've created
        self._addRoutes(dummy_config)
        dummy_request.context = self._makeContext(page)

        # call the view we're testing and check its behavior
        info = self._callFUT(dummy_request)
        assert info['page'] is page
        assert info['content'] == (
            '<div class="document">\n'
            '<p>Hello <a href="http://example.com/add_page/CruelWorld">'
            'CruelWorld</a> '
            '<a href="http://example.com/IDoExist">'
            'IDoExist</a>'
            '</p>\n</div>\n'
        )
        assert info['edit_url'] == 'http://example.com/IDoExist/edit_page'

class Test_add_page:
    def _callFUT(self, request):
        from tutorial.views.default import add_page
        return add_page(request)

    def _makeContext(self, pagename):
        from tutorial.routes import NewPage
        return NewPage(pagename)

    def _addRoutes(self, config):
        config.add_route('add_page', '/add_page/{pagename}')
        config.add_route('view_page', '/{pagename}')

    def test_get(self, dummy_config, dummy_request, dbsession):
        setUser(dummy_config, makeUser('foo', 'editor'))
        self._addRoutes(dummy_config)
        dummy_request.context = self._makeContext('AnotherPage')
        info = self._callFUT(dummy_request)
        assert info['pagedata'] == ''
        assert info['save_url'] == 'http://example.com/add_page/AnotherPage'

    def test_submit_works(self, dummy_config, dummy_request, dbsession):
        dummy_request.method = 'POST'
        dummy_request.POST['body'] = 'Hello yo!'
        dummy_request.context = self._makeContext('AnotherPage')
        setUser(dummy_config, makeUser('foo', 'editor'))
        self._addRoutes(dummy_config)
        self._callFUT(dummy_request)
        page = dbsession.scalars(
            sa.select(models.Page).where(models.Page.name == 'AnotherPage')
        ).one()
        assert page.data == 'Hello yo!'

class Test_edit_page:
    def _callFUT(self, request):
        from tutorial.views.default import edit_page
        return edit_page(request)

    def _makeContext(self, page):
        from tutorial.routes import PageResource
        return PageResource(page)

    def _addRoutes(self, config):
        config.add_route('edit_page', '/{pagename}/edit_page')
        config.add_route('view_page', '/{pagename}')

    def test_get(self, dummy_config, dummy_request, dbsession):
        user = makeUser('foo', 'editor')
        page = makePage('abc', 'hello', user)
        dbsession.add_all([page, user])

        self._addRoutes(dummy_config)
        dummy_request.context = self._makeContext(page)
        info = self._callFUT(dummy_request)
        assert info['pagename'] == 'abc'
        assert info['save_url'] == 'http://example.com/abc/edit_page'

    def test_submit_works(self, dummy_config, dummy_request, dbsession):
        user = makeUser('foo', 'editor')
        page = makePage('abc', 'hello', user)
        dbsession.add_all([page, user])

        self._addRoutes(dummy_config)
        dummy_request.method = 'POST'
        dummy_request.POST['body'] = 'Hello yo!'
        setUser(dummy_config, user)
        dummy_request.context = self._makeContext(page)
        response = self._callFUT(dummy_request)
        assert response.location == 'http://example.com/abc'
        assert page.data == 'Hello yo!'
