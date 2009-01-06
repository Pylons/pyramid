import unittest

class ModelURLTests(unittest.TestCase):
    def _callFUT(self, model, request, *elements, **kw):
        from repoze.bfg.url import model_url
        return model_url(model, request, *elements, **kw)

    def test_extra_args(self):
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyContext(foo)
        root.__parent__ = None
        root.__name__ = None
        foo.__parent__ = root
        foo.__name__ = 'foo '
        bar.__parent__ = foo
        bar.__name__ = 'bar'
        baz.__parent__ = bar
        baz.__name__ = 'baz'
        request = DummyRequest()
        result = self._callFUT(baz, request, 'this/theotherthing', 'that')

        self.assertEqual(
            result,
            'http://example.com:5432/foo%20/bar/baz/this/theotherthing/that')

    def test_root_default_app_url(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        request = DummyRequest()
        result = self._callFUT(root, request)
        self.assertEqual(result, 'http://example.com:5432/')

    def test_nonroot_default_app_url(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        other = DummyContext()
        other.__parent__ = root
        other.__name__ = 'nonroot object'
        request = DummyRequest()
        result = self._callFUT(other, request)
        self.assertEqual(result, 'http://example.com:5432/nonroot%20object/')

    def test_unicode_mixed_with_bytes_in_model_names(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        one = DummyContext()
        one.__parent__ = root
        one.__name__ = unicode('La Pe\xc3\xb1a', 'utf-8')
        two = DummyContext()
        two.__parent__ = one
        two.__name__ = 'La Pe\xc3\xb1a'
        request = DummyRequest()
        result = self._callFUT(two, request)
        self.assertEqual(result,
                     'http://example.com:5432/La%20Pe%C3%B1a/La%20Pe%C3%B1a/')

    def test_unicode_in_element_names(self):
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        one = DummyContext()
        one.__parent__ = root
        one.__name__ = uc
        request = DummyRequest()
        result = self._callFUT(one, request, uc)
        self.assertEqual(result,
                     'http://example.com:5432/La%20Pe%C3%B1a/La%20Pe%C3%B1a')

    def test_element_names_url_quoted(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        request = DummyRequest()
        result = self._callFUT(root, request, 'a b c')
        self.assertEqual(result, 'http://example.com:5432/a%20b%20c')

    def test_with_query_dict(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        request = DummyRequest()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        result = self._callFUT(root, request, 'a', query={'a':uc})
        self.assertEqual(result,
                         'http://example.com:5432/a?a=La+Pe%C3%B1a')

    def test_with_query_seq(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        request = DummyRequest()
        uc = unicode('La Pe\xc3\xb1a', 'utf-8')
        result = self._callFUT(root, request, 'a', query=[('a', 'hi there'),
                                                          ('b', uc)])
        self.assertEqual(result,
                         'http://example.com:5432/a?a=hi+there&b=La+Pe%C3%B1a')

class UrlEncodeTests(unittest.TestCase):
    def _callFUT(self, query, doseq=False):
        from repoze.bfg.url import urlencode
        return urlencode(query, doseq)

    def test_ascii_only(self):
        result = self._callFUT([('a',1), ('b',2)])
        self.assertEqual(result, 'a=1&b=2')

    def test_unicode_key(self):
        la = unicode('LaPe\xc3\xb1a', 'utf-8')
        result = self._callFUT([(la, 1), ('b',2)])
        self.assertEqual(result, 'LaPe%C3%B1a=1&b=2')

    def test_unicode_val_single(self):
        la = unicode('LaPe\xc3\xb1a', 'utf-8')
        result = self._callFUT([('a', la), ('b',2)])
        self.assertEqual(result, 'a=LaPe%C3%B1a&b=2')

    def test_unicode_val_multiple(self):
        la = [unicode('LaPe\xc3\xb1a', 'utf-8')] * 2
        result = self._callFUT([('a', la), ('b',2)], doseq=True)
        self.assertEqual(result, 'a=LaPe%C3%B1a&a=LaPe%C3%B1a&b=2')

    def test_dict(self):
        result = self._callFUT({'a':1})
        self.assertEqual(result, 'a=1')
        
class DummyContext(object):
    def __init__(self, next=None):
        self.next = next
        
    def __getitem__(self, name):
        if self.next is None:
            raise KeyError, name
        return self.next

class DummyRequest:
    application_url = 'http://example.com:5432' # app_url never ends with slash

class DummySettings:
    def __init__(self, **kw):
        self.__dict__.update(kw)
