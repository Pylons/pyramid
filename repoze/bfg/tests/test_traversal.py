import unittest

from zope.testing.cleanup import cleanUp

class TraversalPathTests(unittest.TestCase):
    def _callFUT(self, path):
        from repoze.bfg.traversal import traversal_path
        return traversal_path(path)
        
    def test_path_startswith_endswith(self):
        self.assertEqual(self._callFUT('/foo/'), (u'foo',))

    def test_empty_elements(self):
        self.assertEqual(self._callFUT('foo///'), (u'foo',))

    def test_onedot(self):
        self.assertEqual(self._callFUT('foo/./bar'), (u'foo', u'bar'))

    def test_twodots(self):
        self.assertEqual(self._callFUT('foo/../bar'), (u'bar',))

    def test_element_urllquoted(self):
        self.assertEqual(self._callFUT('/foo/space%20thing/bar'),
                         (u'foo', u'space thing', u'bar'))

    def test_segments_are_unicode(self):
        result = self._callFUT('/foo/bar')
        self.assertEqual(type(result[0]), unicode)
        self.assertEqual(type(result[1]), unicode)

    def test_same_value_returned_if_cached(self):
        result1 = self._callFUT('/foo/bar')
        result2 = self._callFUT('/foo/bar')
        self.assertEqual(result1, (u'foo', u'bar'))
        self.assertEqual(result2, (u'foo', u'bar'))

    def test_utf8(self):
        import urllib
        la = 'La Pe\xc3\xb1a'
        encoded = urllib.quote(la)
        decoded = unicode(la, 'utf-8')
        path = '/'.join([encoded, encoded])
        self.assertEqual(self._callFUT(path), (decoded, decoded))
        
    def test_utf16(self):
        import urllib
        la = unicode('La Pe\xc3\xb1a', 'utf-8').encode('utf-16')
        encoded = urllib.quote(la)
        path = '/'.join([encoded, encoded])
        self.assertRaises(TypeError, self._callFUT, path)

class ModelGraphTraverserTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _getTargetClass(self):
        from repoze.bfg.traversal import ModelGraphTraverser
        return ModelGraphTraverser

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def _getEnviron(self, **kw):
        environ = {}
        environ.update(kw)
        return environ

    def test_class_conforms_to_ITraverser(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ITraverser
        verifyClass(ITraverser, self._getTargetClass())

    def test_instance_conforms_to_ITraverser(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ITraverser
        context = DummyContext()
        verifyObject(ITraverser, self._makeOne(context))

    def test_call_with_no_pathinfo(self):
        policy = self._makeOne(None)
        environ = self._getEnviron()
        ctx, name, subpath, traversed, vroot, vroot_path = policy(environ)
        self.assertEqual(ctx, None)
        self.assertEqual(name, '')
        self.assertEqual(subpath, [])
        self.assertEqual(traversed, [])
        self.assertEqual(vroot, policy.root)
        self.assertEqual(vroot_path, [])

    def test_call_pathel_with_no_getitem(self):
        policy = self._makeOne(None)
        environ = self._getEnviron(PATH_INFO='/foo/bar')
        ctx, name, subpath, traversed, vroot, vroot_path = policy(environ)
        self.assertEqual(ctx, None)
        self.assertEqual(name, 'foo')
        self.assertEqual(subpath, ['bar'])
        self.assertEqual(traversed, [])
        self.assertEqual(vroot, policy.root)
        self.assertEqual(vroot_path, [])

    def test_call_withconn_getitem_emptypath_nosubpath(self):
        root = DummyContext()
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='')
        ctx, name, subpath, traversed, vroot, vroot_path = policy(environ)
        self.assertEqual(ctx, root)
        self.assertEqual(name, '')
        self.assertEqual(subpath, [])
        self.assertEqual(traversed, [])
        self.assertEqual(vroot, root)
        self.assertEqual(vroot_path, [])

    def test_call_withconn_getitem_withpath_nosubpath(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/foo/bar')
        ctx, name, subpath, traversed, vroot, vroot_path = policy(environ)
        self.assertEqual(ctx, foo)
        self.assertEqual(name, 'bar')
        self.assertEqual(subpath, [])
        self.assertEqual(traversed, [u'foo'])
        self.assertEqual(vroot, root)
        self.assertEqual(vroot_path, [])

    def test_call_withconn_getitem_withpath_withsubpath(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/foo/bar/baz/buz')
        ctx, name, subpath, traversed, vroot, vroot_path = policy(environ)
        self.assertEqual(ctx, foo)
        self.assertEqual(name, 'bar')
        self.assertEqual(subpath, ['baz', 'buz'])
        self.assertEqual(traversed, [u'foo'])
        self.assertEqual(vroot, root)
        self.assertEqual(vroot_path, [])

    def test_call_with_explicit_viewname(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/@@foo')
        ctx, name, subpath, traversed, vroot, vroot_path = policy(environ)
        self.assertEqual(ctx, root)
        self.assertEqual(name, 'foo')
        self.assertEqual(subpath, [])
        self.assertEqual(traversed, [])
        self.assertEqual(vroot, root)
        self.assertEqual(vroot_path, [])

    def test_call_with_vh_root(self):
        environ = self._getEnviron(PATH_INFO='/baz',
                                   HTTP_X_VHM_ROOT='/foo/bar')
        baz = DummyContext()
        baz.name = 'baz'
        bar = DummyContext(baz)
        bar.name = 'bar'
        foo = DummyContext(bar)
        foo.name = 'foo'
        root = DummyContext(foo)
        root.name = 'root'
        policy = self._makeOne(root)
        ctx, name, subpath, traversed, vroot, vroot_path = policy(environ)
        self.assertEqual(ctx, baz)
        self.assertEqual(name, '')
        self.assertEqual(subpath, [])
        self.assertEqual(traversed, [u'foo', u'bar', u'baz'])
        self.assertEqual(vroot, bar)
        self.assertEqual(vroot_path, [u'foo', u'bar'])

    def test_call_with_ILocation_root_proxies(self):
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyContext(foo)
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import ILocation
        from zope.proxy import isProxy
        directlyProvides(root, ILocation)
        root.__name__ = None
        root.__parent__ = None
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/foo/bar/baz')
        ctx, name, subpath, traversed, vroot, vroot_path = policy(environ)
        self.assertEqual(name, '')
        self.assertEqual(subpath, [])
        self.assertEqual(ctx, baz)
        self.failUnless(isProxy(ctx))
        self.assertEqual(ctx.__name__, 'baz')
        self.assertEqual(ctx.__parent__, bar)
        self.failUnless(isProxy(ctx.__parent__))
        self.assertEqual(ctx.__parent__.__name__, 'bar')
        self.assertEqual(ctx.__parent__.__parent__, foo)
        self.failUnless(isProxy(ctx.__parent__.__parent__))
        self.assertEqual(ctx.__parent__.__parent__.__name__, 'foo')
        self.assertEqual(ctx.__parent__.__parent__.__parent__, root)
        self.failIf(isProxy(ctx.__parent__.__parent__.__parent__))
        self.assertEqual(ctx.__parent__.__parent__.__parent__.__name__, None)
        self.assertEqual(ctx.__parent__.__parent__.__parent__.__parent__, None)
        self.assertEqual(traversed, [u'foo', u'bar', u'baz'])
        self.assertEqual(vroot, root)
        self.assertEqual(vroot_path, [])

    def test_call_with_ILocation_root_proxies_til_next_ILocation(self):
        # This is a test of an insane setup; it tests the case where
        # intermediate objects (foo and bar) do not implement
        # ILocation, and so are returned as proxies to the traverser,
        # but when we reach the "baz" object, it *does* implement
        # ILocation, and its parent should be the *real* "bar" object
        # rather than the proxied bar.
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import ILocation
        baz = DummyContext()
        directlyProvides(baz, ILocation)
        baz.__name__ = 'baz'
        bar = DummyContext(baz)
        baz.__parent__ = bar
        foo = DummyContext(bar)
        root = DummyContext(foo)
        from zope.proxy import isProxy
        directlyProvides(root, ILocation)
        root.__name__ = None
        root.__parent__ = None
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/foo/bar/baz')
        ctx, name, subpath, traversed, vroot, vroot_path = policy(environ)
        self.assertEqual(name, '')
        self.assertEqual(subpath, [])
        self.assertEqual(ctx, baz)
        self.failIf(isProxy(ctx))
        self.assertEqual(ctx.__name__, 'baz')
        self.assertEqual(ctx.__parent__, bar)
        self.failIf(isProxy(ctx.__parent__))
        self.assertEqual(traversed, [u'foo', u'bar', u'baz'])
        self.assertEqual(vroot, root)
        self.assertEqual(vroot_path, [])

    def test_non_utf8_path_segment_unicode_path_segments_fails(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        segment = unicode('LaPe\xc3\xb1a', 'utf-8').encode('utf-16')
        environ = self._getEnviron(PATH_INFO='/%s' % segment)
        self.assertRaises(TypeError, policy, environ)

    def test_non_utf8_path_segment_settings_unicode_path_segments_fails(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        segment = unicode('LaPe\xc3\xb1a', 'utf-8').encode('utf-16')
        environ = self._getEnviron(PATH_INFO='/%s' % segment)
        self.assertRaises(TypeError, policy, environ)

class FindInterfaceTests(unittest.TestCase):
    def _callFUT(self, context, iface):
        from repoze.bfg.traversal import find_interface
        return find_interface(context, iface)

    def test_it(self):
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyContext(foo)
        root.__parent__ = None
        root.__name__ = 'root'
        foo.__parent__ = root
        foo.__name__ = 'foo'
        bar.__parent__ = foo
        bar.__name__ = 'bar'
        baz.__parent__ = bar
        baz.__name__ = 'baz'
        request = DummyRequest()
        from zope.interface import directlyProvides
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        directlyProvides(root, IFoo)
        result = self._callFUT(baz, IFoo)
        self.assertEqual(result.__name__, 'root')

class FindRootTests(unittest.TestCase):
    def _callFUT(self, context):
        from repoze.bfg.traversal import find_root
        return find_root(context)

    def test_it(self):
        dummy = DummyContext()
        baz = DummyContext()
        baz.__parent__ = dummy
        baz.__name__ = 'baz'
        dummy.__parent__ = None
        dummy.__name__ = None
        result = self._callFUT(baz)
        self.assertEqual(result, dummy)

class FindModelTests(unittest.TestCase):
    def _callFUT(self, context, name):
        from repoze.bfg.traversal import find_model
        return find_model(context, name)

    def _registerTraverserFactory(self, traverser):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import ITraverserFactory
        from zope.interface import Interface
        gsm.registerAdapter(traverser, (Interface,), ITraverserFactory)

    def test_list(self):
        model = DummyContext()
        traverser = make_traverser(model, '', [])
        self._registerTraverserFactory(traverser)
        result = self._callFUT(model, [''])
        self.assertEqual(result, model)
        self.assertEqual(model.environ['PATH_INFO'], '/')

    def test_generator(self):
        model = DummyContext()
        traverser = make_traverser(model, '', [])
        self._registerTraverserFactory(traverser)
        def foo():
            yield ''
        result = self._callFUT(model, foo())
        self.assertEqual(result, model)
        self.assertEqual(model.environ['PATH_INFO'], '/')

    def test_self_string_found(self):
        model = DummyContext()
        traverser = make_traverser(model, '', [])
        self._registerTraverserFactory(traverser)
        result = self._callFUT(model, '')
        self.assertEqual(result, model)
        self.assertEqual(model.environ['PATH_INFO'], '')

    def test_self_tuple_found(self):
        model = DummyContext()
        traverser = make_traverser(model, '', [])
        self._registerTraverserFactory(traverser)
        result = self._callFUT(model, ())
        self.assertEqual(result, model)
        self.assertEqual(model.environ['PATH_INFO'], '')

    def test_relative_string_found(self):
        model = DummyContext()
        baz = DummyContext()
        traverser = make_traverser(baz, '', [])
        self._registerTraverserFactory(traverser)
        result = self._callFUT(model, 'baz')
        self.assertEqual(result, baz)
        self.assertEqual(model.environ['PATH_INFO'], 'baz')

    def test_relative_tuple_found(self):
        model = DummyContext()
        baz = DummyContext()
        traverser = make_traverser(baz, '', [])
        self._registerTraverserFactory(traverser)
        result = self._callFUT(model, ('baz',))
        self.assertEqual(result, baz)
        self.assertEqual(model.environ['PATH_INFO'], 'baz')

    def test_relative_string_notfound(self):
        model = DummyContext()
        baz = DummyContext()
        traverser = make_traverser(baz, 'bar', [])
        self._registerTraverserFactory(traverser)
        self.assertRaises(KeyError, self._callFUT, model, 'baz')
        self.assertEqual(model.environ['PATH_INFO'], 'baz')

    def test_relative_tuple_notfound(self):
        model = DummyContext()
        baz = DummyContext()
        traverser = make_traverser(baz, 'bar', [])
        self._registerTraverserFactory(traverser)
        self.assertRaises(KeyError, self._callFUT, model, ('baz',))
        self.assertEqual(model.environ['PATH_INFO'], 'baz')

    def test_absolute_string_found(self):
        root = DummyContext()
        model = DummyContext()
        model.__parent__ = root
        model.__name__ = 'baz'
        traverser = make_traverser(root, '', [])
        self._registerTraverserFactory(traverser)
        result = self._callFUT(model, '/')
        self.assertEqual(result, root)
        self.assertEqual(root.wascontext, True)
        self.assertEqual(root.environ['PATH_INFO'], '/')

    def test_absolute_tuple_found(self):
        root = DummyContext()
        model = DummyContext()
        model.__parent__ = root
        model.__name__ = 'baz'
        traverser = make_traverser(root, '', [])
        self._registerTraverserFactory(traverser)
        result = self._callFUT(model, ('',))
        self.assertEqual(result, root)
        self.assertEqual(root.wascontext, True)
        self.assertEqual(root.environ['PATH_INFO'], '/')

    def test_absolute_string_notfound(self):
        root = DummyContext()
        model = DummyContext()
        model.__parent__ = root
        model.__name__ = 'baz'
        traverser = make_traverser(root, 'fuz', [])
        self._registerTraverserFactory(traverser)
        self.assertRaises(KeyError, self._callFUT, model, '/')
        self.assertEqual(root.wascontext, True)
        self.assertEqual(root.environ['PATH_INFO'], '/')

    def test_absolute_tuple_notfound(self):
        root = DummyContext()
        model = DummyContext()
        model.__parent__ = root
        model.__name__ = 'baz'
        traverser = make_traverser(root, 'fuz', [])
        self._registerTraverserFactory(traverser)
        self.assertRaises(KeyError, self._callFUT, model, ('',))
        self.assertEqual(root.wascontext, True)
        self.assertEqual(root.environ['PATH_INFO'], '/')

class ModelPathTests(unittest.TestCase):
    def _callFUT(self, model, *elements):
        from repoze.bfg.traversal import model_path
        return model_path(model, *elements)

    def test_it(self):
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
        result = self._callFUT(baz, 'this/theotherthing', 'that')
        self.assertEqual(result, '/foo%20/bar/baz/this%2Ftheotherthing/that')

    def test_root_default(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        result = self._callFUT(root)
        self.assertEqual(result, '/')
        
    def test_nonroot_default(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        other = DummyContext()
        other.__parent__ = root
        other.__name__ = 'other'
        result = self._callFUT(other)
        self.assertEqual(result, '/other')

    def test_path_with_None_itermediate_names(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        other = DummyContext()
        other.__parent__ = root
        other.__name__ = None
        other2 = DummyContext()
        other2.__parent__ = other
        other2.__name__ = 'other2'
        result = self._callFUT(other2)
        self.assertEqual(result, '//other2')

class ModelPathTupleTests(unittest.TestCase):
    def _callFUT(self, model, *elements):
        from repoze.bfg.traversal import model_path_tuple
        return model_path_tuple(model, *elements)

    def test_it(self):
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
        result = self._callFUT(baz, 'this/theotherthing', 'that')
        self.assertEqual(result, ('','foo ', 'bar', 'baz', 'this/theotherthing',
                                  'that'))

    def test_root_default(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        result = self._callFUT(root)
        self.assertEqual(result, ('',))
        
    def test_nonroot_default(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        other = DummyContext()
        other.__parent__ = root
        other.__name__ = 'other'
        result = self._callFUT(other)
        self.assertEqual(result, ('', 'other'))

    def test_path_with_None_itermediate_names(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        other = DummyContext()
        other.__parent__ = root
        other.__name__ = None
        other2 = DummyContext()
        other2.__parent__ = other
        other2.__name__ = 'other2'
        result = self._callFUT(other2)
        self.assertEqual(result, ('', '', 'other2'))

class QuotePathSegmentTests(unittest.TestCase):
    def _callFUT(self, s):
        from repoze.bfg.traversal import quote_path_segment
        return quote_path_segment(s)

    def test_unicode(self):
        la = unicode('/La Pe\xc3\xb1a', 'utf-8')
        result = self._callFUT(la)
        self.assertEqual(result, '%2FLa%20Pe%C3%B1a')

    def test_string(self):
        s = '/ hello!'
        result = self._callFUT(s)
        self.assertEqual(result, '%2F%20hello%21')

class TraversalContextURLTests(unittest.TestCase):
    def _makeOne(self, context, url):
        return self._getTargetClass()(context, url)

    def _getTargetClass(self):
        from repoze.bfg.traversal import TraversalContextURL
        return TraversalContextURL

    def _registerTraverserFactory(self, traverser):
        import zope.component
        gsm = zope.component.getGlobalSiteManager()
        from repoze.bfg.interfaces import ITraverserFactory
        from zope.interface import Interface
        gsm.registerAdapter(traverser, (Interface,), ITraverserFactory)

    def test_class_conforms_to_IContextURL(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import IContextURL
        verifyClass(IContextURL, self._getTargetClass())

    def test_instance_conforms_to_IContextURL(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IContextURL
        context = DummyContext()
        request = DummyRequest()
        verifyObject(IContextURL, self._makeOne(context, request))

    def test_call_withlineage(self):
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
        context_url = self._makeOne(baz, request)
        result = context_url()
        self.assertEqual(result, 'http://example.com:5432/foo%20/bar/baz/')

    def test_call_nolineage(self):
        context = DummyContext()
        context.__name__ = ''
        context.__parent__ = None
        request = DummyRequest()
        context_url = self._makeOne(context, request)
        result = context_url()
        self.assertEqual(result, 'http://example.com:5432/')

    def test_call_unicode_mixed_with_bytes_in_model_names(self):
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
        context_url = self._makeOne(two, request)
        result = context_url()
        self.assertEqual(result,
                     'http://example.com:5432/La%20Pe%C3%B1a/La%20Pe%C3%B1a/')

    def test_call_with_vroot_path(self):
        from repoze.bfg.interfaces import VH_ROOT_KEY
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = None
        one = DummyContext()
        one.__parent__ = root
        one.__name__ = 'one'
        two = DummyContext()
        two.__parent__ = one
        two.__name__ = 'two'
        request = DummyRequest({VH_ROOT_KEY:'/one'})
        context_url = self._makeOne(two, request)
        result = context_url()
        self.assertEqual(result, 'http://example.com:5432/two/')
        
        request = DummyRequest({VH_ROOT_KEY:'/one/two'})
        context_url = self._makeOne(two, request)
        result = context_url()
        self.assertEqual(result, 'http://example.com:5432/')

    def test_virtual_root_no_vroot_path(self):
        root = DummyContext()
        root.__name__ = None
        root.__parent__ = None
        one = DummyContext()
        one.__name__ = 'one'
        one.__parent__ = root
        request = DummyRequest()
        context_url = self._makeOne(one, request)
        self.assertEqual(context_url.virtual_root(), root)

    def test_virtual_root_no_vroot_path_with_root_on_request(self):
        context = DummyContext()
        context.__parent__ = None
        request = DummyRequest()
        request.root = DummyContext()
        context_url = self._makeOne(context, request)
        self.assertEqual(context_url.virtual_root(), request.root)

    def test_virtual_root_with_vroot_path(self):
        from repoze.bfg.interfaces import VH_ROOT_KEY
        context = DummyContext()
        context.__parent__ = None
        traversed_to = DummyContext()
        environ = {VH_ROOT_KEY:'/one'}
        request = DummyRequest(environ)
        traverser = make_traverser(traversed_to, '', [])
        self._registerTraverserFactory(traverser)
        context_url = self._makeOne(context, request)
        self.assertEqual(context_url.virtual_root(), traversed_to)
        self.assertEqual(context.environ['PATH_INFO'], '/one')

    def test_empty_names_not_ignored(self):
        bar = DummyContext()
        empty = DummyContext(bar)
        root = DummyContext(empty)
        root.__parent__ = None
        root.__name__ = None
        empty.__parent__ = root
        empty.__name__ = ''
        bar.__parent__ = empty
        bar.__name__ = 'bar'
        request = DummyRequest()
        context_url = self._makeOne(bar, request)
        result = context_url()
        self.assertEqual(result, 'http://example.com:5432//bar/')
        

class TestVirtualRoot(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, model, request):
        from repoze.bfg.traversal import virtual_root
        return virtual_root(model, request)

    def test_it(self):
        from zope.component import getGlobalSiteManager
        from repoze.bfg.interfaces import IContextURL
        from zope.interface import Interface
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(DummyContextURL, (Interface,Interface),
                            IContextURL)
        context = DummyContext()
        request = DummyRequest()
        result = self._callFUT(context, request)
        self.assertEqual(result, '123')

def make_traverser(*args):
    class DummyTraverser(object):
        def __init__(self, context):
            self.context = context
            context.wascontext = True
        def __call__(self, environ):
            self.context.environ = environ
            return args
    return DummyTraverser
        
class DummyContext(object):
    __parent__ = None
    __name__ = None
    def __init__(self, next=None):
        self.next = next
        
    def __getitem__(self, name):
        if self.next is None:
            raise KeyError, name
        return self.next

class DummyRequest:
    application_url = 'http://example.com:5432' # app_url never ends with slash
    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        
class DummyContextURL:
    def __init__(self, context, request):
        pass

    def virtual_root(self):
        return '123'
