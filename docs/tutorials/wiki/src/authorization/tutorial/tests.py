import unittest

from pyramid import testing

class PageModelTests(unittest.TestCase):

    def _getTargetClass(self):
        from .models import Page
        return Page

    def _makeOne(self, data=u'some data'):
        return self._getTargetClass()(data=data)

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.data, u'some data')

class WikiModelTests(unittest.TestCase):

    def _getTargetClass(self):
        from .models import Wiki
        return Wiki

    def _makeOne(self):
        return self._getTargetClass()()

    def test_it(self):
        wiki = self._makeOne()
        self.assertEqual(wiki.__parent__, None)
        self.assertEqual(wiki.__name__, None)

class AppmakerTests(unittest.TestCase):
    def _callFUT(self, zodb_root):
        from .models import appmaker
        return appmaker(zodb_root)

    def test_it(self):
        root = {}
        self._callFUT(root)
        self.assertEqual(root['app_root']['FrontPage'].data,
                         'This is the front page')

class ViewWikiTests(unittest.TestCase):
    def test_it(self):
        from .views import view_wiki
        context = testing.DummyResource()
        request = testing.DummyRequest()
        response = view_wiki(context, request)
        self.assertEqual(response.location, 'http://example.com/FrontPage')

class ViewPageTests(unittest.TestCase):
    def _callFUT(self, context, request):
        from .views import view_page
        return view_page(context, request)

    def test_it(self):
        wiki = testing.DummyResource()
        wiki['IDoExist'] = testing.DummyResource()
        context = testing.DummyResource(data='Hello CruelWorld IDoExist')
        context.__parent__ = wiki
        context.__name__ = 'thepage'
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['page'], context)
        self.assertEqual(
            info['content'], 
            '<div class="document">\n'
            '<p>Hello <a href="http://example.com/add_page/CruelWorld">'
            'CruelWorld</a> '
            '<a href="http://example.com/IDoExist/">'
            'IDoExist</a>'
            '</p>\n</div>\n')
        self.assertEqual(info['edit_url'],
                         'http://example.com/thepage/edit_page')


class AddPageTests(unittest.TestCase):
    def _callFUT(self, context, request):
        from .views import add_page
        return add_page(context, request)

    def test_it_notsubmitted(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.subpath = ['AnotherPage']
        info = self._callFUT(context, request)
        self.assertEqual(info['page'].data,'')
        self.assertEqual(info['save_url'],
                         request.resource_url(
                             context, 'add_page', 'AnotherPage'))

    def test_it_submitted(self):
        context = testing.DummyResource()
        request = testing.DummyRequest({'form.submitted':True,
                                        'body':'Hello yo!'})
        request.subpath = ['AnotherPage']
        self._callFUT(context, request)
        page = context['AnotherPage']
        self.assertEqual(page.data, 'Hello yo!')
        self.assertEqual(page.__name__, 'AnotherPage')
        self.assertEqual(page.__parent__, context)

class EditPageTests(unittest.TestCase):
    def _callFUT(self, context, request):
        from .views import edit_page
        return edit_page(context, request)

    def test_it_notsubmitted(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['page'], context)
        self.assertEqual(info['save_url'],
                         request.resource_url(context, 'edit_page'))

    def test_it_submitted(self):
        context = testing.DummyResource()
        request = testing.DummyRequest({'form.submitted':True,
                                        'body':'Hello yo!'})
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')
        self.assertEqual(context.data, 'Hello yo!')
