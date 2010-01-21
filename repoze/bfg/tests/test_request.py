import unittest

class TestMakeRequestASCII(unittest.TestCase):
    def _callFUT(self, event):
        from repoze.bfg.request import make_request_ascii
        return make_request_ascii(event)

    def test_it(self):
        request = DummyRequest()
        event = DummyNewRequestEvent(request)
        self._callFUT(event)
        self.assertEqual(request.default_charset, None)

class TestRequest(unittest.TestCase):
    def _makeOne(self, environ):
        return self._getTargetClass()(environ)

    def _getTargetClass(self):
        from repoze.bfg.request import Request
        return Request

    def test_charset_defaults_to_utf8(self):
        r = self._makeOne({'PATH_INFO':'/'})
        self.assertEqual(r.charset, 'utf-8')

    def test_params_decoded_from_utf_8_by_default(self):
        environ = {
            'PATH_INFO':'/',
            'QUERY_STRING':'la=La%20Pe%C3%B1a'
            }
        request = self._makeOne(environ)
        self.assertEqual(request.GET['la'], u'La Pe\xf1a')

    def test_params_bystring_when_default_charset_is_None(self):
        environ = {
            'PATH_INFO':'/',
            'QUERY_STRING':'la=La%20Pe%C3%B1a'
            }
        request = self._makeOne(environ)
        request.default_charset = None
        self.assertEqual(request.GET['la'], 'La Pe\xc3\xb1a')

    def test_class_implements(self):
        from repoze.bfg.interfaces import IRequest
        klass = self._getTargetClass()
        self.assertTrue(IRequest.implementedBy(klass))

    def test_instance_provides(self):
        from repoze.bfg.interfaces import IRequest
        inst = self._makeOne({})
        self.assertTrue(IRequest.providedBy(inst))

    def test_setattr_and_getattr_dotnotation(self):
        inst = self._makeOne({})
        inst.foo = 1
        self.assertEqual(inst.foo, 1)

    def test_setattr_and_getattr(self):
        inst = self._makeOne({})
        setattr(inst, 'bar', 1)
        self.assertEqual(getattr(inst, 'bar'), 1)

    def test___contains__(self):
        environ ={'zooma':1}
        inst = self._makeOne(environ)
        self.failUnless('zooma' in inst)

    def test___delitem__(self):
        environ = {'zooma':1}
        inst = self._makeOne(environ)
        del inst['zooma']
        self.failIf('zooma' in environ)

    def test___getitem__(self):
        environ = {'zooma':1}
        inst = self._makeOne(environ)
        self.assertEqual(inst['zooma'], 1)

    def test___iter__(self):
        environ = {'zooma':1}
        inst = self._makeOne(environ)
        iterator = iter(inst)
        self.assertEqual(list(iterator), list(iter(environ)))

    def test___setitem__(self):
        environ = {}
        inst = self._makeOne(environ)
        inst['zooma'] = 1
        self.assertEqual(environ, {'zooma':1})

    def test_get(self):
        environ = {'zooma':1}
        inst = self._makeOne(environ)
        self.assertEqual(inst.get('zooma'), 1)
        
    def test_has_key(self):
        environ = {'zooma':1}
        inst = self._makeOne(environ)
        self.assertEqual(inst.has_key('zooma'), True)

    def test_items(self):
        environ = {'zooma':1}
        inst = self._makeOne(environ)
        self.assertEqual(inst.items(), environ.items())

    def test_iteritems(self):
        environ = {'zooma':1}
        inst = self._makeOne(environ)
        self.assertEqual(list(inst.iteritems()), list(environ.iteritems()))

    def test_iterkeys(self):
        environ = {'zooma':1}
        inst = self._makeOne(environ)
        self.assertEqual(list(inst.iterkeys()), list(environ.iterkeys()))

    def test_itervalues(self):
        environ = {'zooma':1}
        inst = self._makeOne(environ)
        self.assertEqual(list(inst.itervalues()), list(environ.itervalues()))

    def test_keys(self):
        environ = {'zooma':1}
        inst = self._makeOne(environ)
        self.assertEqual(inst.keys(), environ.keys())

    def test_pop(self):
        environ = {'zooma':1}
        inst = self._makeOne(environ)
        popped = inst.pop('zooma')
        self.assertEqual(environ, {})
        self.assertEqual(popped, 1)

    def test_popitem(self):
        environ = {'zooma':1}
        inst = self._makeOne(environ)
        popped = inst.popitem()
        self.assertEqual(environ, {})
        self.assertEqual(popped, ('zooma', 1))

    def test_setdefault(self):
        environ = {}
        inst = self._makeOne(environ)
        marker = []
        result = inst.setdefault('a', marker)
        self.assertEqual(environ, {'a':marker})
        self.assertEqual(result, marker)

    def test_update(self):
        environ = {}
        inst = self._makeOne(environ)
        inst.update({'a':1}, b=2)
        self.assertEqual(environ, {'a':1, 'b':2})

    def test_values(self):
        environ = {'zooma':1}
        inst = self._makeOne(environ)
        result = inst.values()
        self.assertEqual(result, environ.values())

class Test_route_request_iface(unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.request import route_request_iface
        return route_request_iface(name)

    def test_it(self):
        iface = self._callFUT('routename')
        self.assertEqual(iface.__name__, 'routename_IRequest')

class Test_add_global_response_headers(unittest.TestCase):
    def _callFUT(self, request, headerlist):
        from repoze.bfg.request import add_global_response_headers
        return add_global_response_headers(request, headerlist)

    def test_it(self):
        request = DummyRequest()
        headers = [('a', 1), ('b', 2)]
        request.global_response_headers = headers[:]
        self._callFUT(request, [('c', 1)])
        self.assertEqual(request.global_response_headers, headers + [('c', 1)])

class DummyRequest:
    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ

class DummyNewRequestEvent:
    def __init__(self, request):
        self.request = request
        



