from tutorial import models


def makeUser(name, role):
    return models.User(name=name, role=role)

def makePage(name, data, creator):
    return models.Page(name=name, data=data, creator=creator)

class Test_view_wiki:
    def _callFUT(self, request):
        from tutorial.views.default import view_wiki
        return view_wiki(request)

    def test_it(self, dummy_request):
        response = self._callFUT(dummy_request)
        assert response.location == 'http://example.com/FrontPage'

class Test_view_page:
    def _callFUT(self, request):
        from tutorial.views.default import view_page
        return view_page(request)

    def _makeContext(self, page):
        from tutorial.routes import PageResource
        return PageResource(page)

    def test_it(self, dummy_request, dbsession):
        # add a page to the db
        user = makeUser('foo', 'editor')
        page = makePage('IDoExist', 'Hello CruelWorld IDoExist', user)
        dbsession.add_all([page, user])

        # create a request asking for the page we've created
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

    def test_get(self, dummy_request, dbsession):
        dummy_request.user = makeUser('foo', 'editor')
        dummy_request.context = self._makeContext('AnotherPage')
        info = self._callFUT(dummy_request)
        assert info['pagedata'] == ''
        assert info['save_url'] == 'http://example.com/add_page/AnotherPage'

    def test_submit_works(self, dummy_request, dbsession):
        dummy_request.method = 'POST'
        dummy_request.POST['body'] = 'Hello yo!'
        dummy_request.context = self._makeContext('AnotherPage')
        dummy_request.user = makeUser('foo', 'editor')
        self._callFUT(dummy_request)
        page = (
            dbsession.query(models.Page)
            .filter_by(name='AnotherPage')
            .one()
        )
        assert page.data == 'Hello yo!'

class Test_edit_page:
    def _callFUT(self, request):
        from tutorial.views.default import edit_page
        return edit_page(request)

    def _makeContext(self, page):
        from tutorial.routes import PageResource
        return PageResource(page)

    def test_get(self, dummy_request, dbsession):
        user = makeUser('foo', 'editor')
        page = makePage('abc', 'hello', user)
        dbsession.add_all([page, user])

        dummy_request.context = self._makeContext(page)
        info = self._callFUT(dummy_request)
        assert info['pagename'] == 'abc'
        assert info['save_url'] == 'http://example.com/abc/edit_page'

    def test_submit_works(self, dummy_request, dbsession):
        user = makeUser('foo', 'editor')
        page = makePage('abc', 'hello', user)
        dbsession.add_all([page, user])

        dummy_request.method = 'POST'
        dummy_request.POST['body'] = 'Hello yo!'
        dummy_request.user = user
        dummy_request.context = self._makeContext(page)
        response = self._callFUT(dummy_request)
        assert response.location == 'http://example.com/abc'
        assert page.data == 'Hello yo!'
