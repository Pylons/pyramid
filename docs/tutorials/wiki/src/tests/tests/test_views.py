from pyramid import testing


class Test_view_wiki:
    def test_it_redirects_to_front_page(self):
        from tutorial.views.default import view_wiki
        context = testing.DummyResource()
        request = testing.DummyRequest()
        response = view_wiki(context, request)
        assert response.location == 'http://example.com/FrontPage'

class Test_view_page:
    def _callFUT(self, context, request):
        from tutorial.views.default import view_page
        return view_page(context, request)

    def test_it(self):
        wiki = testing.DummyResource()
        wiki['IDoExist'] = testing.DummyResource()
        context = testing.DummyResource(data='Hello CruelWorld IDoExist')
        context.__parent__ = wiki
        context.__name__ = 'thepage'
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        assert info['page'] == context
        assert info['page_text'] == (
            '<div class="document">\n'
            '<p>Hello <a href="http://example.com/add_page/CruelWorld">'
            'CruelWorld</a> '
            '<a href="http://example.com/IDoExist/">'
            'IDoExist</a>'
            '</p>\n</div>\n')
        assert info['edit_url'] == 'http://example.com/thepage/edit_page'


class Test_add_page:
    def _callFUT(self, context, request):
        from tutorial.views.default import add_page
        return add_page(context, request)

    def test_it_notsubmitted(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.subpath = ['AnotherPage']
        info = self._callFUT(context, request)
        assert info['page'].data == ''
        assert info['save_url'] == request.resource_url(
            context, 'add_page', 'AnotherPage')

    def test_it_submitted(self):
        context = testing.DummyResource()
        request = testing.DummyRequest({
            'form.submitted': True,
            'body': 'Hello yo!',
        })
        request.subpath = ['AnotherPage']
        self._callFUT(context, request)
        page = context['AnotherPage']
        assert page.data == 'Hello yo!'
        assert page.__name__ == 'AnotherPage'
        assert page.__parent__ == context

class Test_edit_page:
    def _callFUT(self, context, request):
        from tutorial.views.default import edit_page
        return edit_page(context, request)

    def test_it_notsubmitted(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        assert info['page'] == context
        assert info['save_url'] == request.resource_url(context, 'edit_page')

    def test_it_submitted(self):
        context = testing.DummyResource()
        request = testing.DummyRequest({
            'form.submitted': True,
            'body': 'Hello yo!',
        })
        response = self._callFUT(context, request)
        assert response.location == 'http://example.com/'
        assert context.data == 'Hello yo!'
