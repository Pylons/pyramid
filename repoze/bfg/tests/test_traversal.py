import unittest

from repoze.bfg.testing import cleanUp

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
        result = policy(environ)
        self.assertEqual(result['context'], None)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], policy.root)
        self.assertEqual(result['virtual_root'], policy.root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_pathel_with_no_getitem(self):
        policy = self._makeOne(None)
        environ = self._getEnviron(PATH_INFO='/foo/bar')
        result = policy(environ)
        self.assertEqual(result['context'], None)
        self.assertEqual(result['view_name'], 'foo')
        self.assertEqual(result['subpath'], ('bar',))
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], policy.root)
        self.assertEqual(result['virtual_root'], policy.root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_withconn_getitem_emptypath_nosubpath(self):
        root = DummyContext()
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='')
        result = policy(environ)
        self.assertEqual(result['context'], root)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_withconn_getitem_withpath_nosubpath(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/foo/bar')
        result = policy(environ)
        self.assertEqual(result['context'], foo)
        self.assertEqual(result['view_name'], 'bar')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo',))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_withconn_getitem_withpath_withsubpath(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/foo/bar/baz/buz')
        result = policy(environ)
        self.assertEqual(result['context'], foo)
        self.assertEqual(result['view_name'], 'bar')
        self.assertEqual(result['subpath'], ('baz', 'buz'))
        self.assertEqual(result['traversed'], (u'foo',))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_with_explicit_viewname(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron(PATH_INFO='/@@foo')
        result = policy(environ)
        self.assertEqual(result['context'], root)
        self.assertEqual(result['view_name'], 'foo')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_with_vh_root(self):
        environ = self._getEnviron(PATH_INFO='/baz',
                                   HTTP_X_VHM_ROOT='/foo/bar')
        baz = DummyContext(None, 'baz')
        bar = DummyContext(baz, 'bar')
        foo = DummyContext(bar, 'foo')
        root = DummyContext(foo, 'root')
        policy = self._makeOne(root)
        result = policy(environ)
        self.assertEqual(result['context'], baz)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo', u'bar', u'baz'))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], bar)
        self.assertEqual(result['virtual_root_path'], (u'foo', u'bar'))

    def test_call_with_vh_root2(self):
        environ = self._getEnviron(PATH_INFO='/bar/baz',
                                   HTTP_X_VHM_ROOT='/foo')
        baz = DummyContext(None, 'baz')
        bar = DummyContext(baz, 'bar')
        foo = DummyContext(bar, 'foo')
        root = DummyContext(foo, 'root')
        policy = self._makeOne(root)
        result = policy(environ)
        self.assertEqual(result['context'], baz)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo', u'bar', u'baz'))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], foo)
        self.assertEqual(result['virtual_root_path'], (u'foo',))

    def test_call_with_vh_root3(self):
        environ = self._getEnviron(PATH_INFO='/foo/bar/baz',
                                   HTTP_X_VHM_ROOT='/')
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyContext(foo)
        policy = self._makeOne(root)
        result = policy(environ)
        self.assertEqual(result['context'], baz)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo', u'bar', u'baz'))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_with_vh_root4(self):
        environ = self._getEnviron(PATH_INFO='/',
                                   HTTP_X_VHM_ROOT='/foo/bar/baz')
        baz = DummyContext(None, 'baz')
        bar = DummyContext(baz, 'bar')
        foo = DummyContext(bar, 'foo')
        root = DummyContext(foo, 'root')
        policy = self._makeOne(root)
        result = policy(environ)
        self.assertEqual(result['context'], baz)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo', u'bar', u'baz'))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], baz)
        self.assertEqual(result['virtual_root_path'], (u'foo', u'bar', u'baz'))

    def test_call_with_vh_root_path_root(self):
        policy = self._makeOne(None)
        environ = self._getEnviron(HTTP_X_VHM_ROOT='/',
                                   PATH_INFO='/')
        result = policy(environ)
        self.assertEqual(result['context'], None)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], policy.root)
        self.assertEqual(result['virtual_root'], policy.root)
        self.assertEqual(result['virtual_root_path'], ())

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

    def test_withroute_nothingfancy(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        environ = {'bfg.routes.matchdict': {}}
        result = traverser(environ)
        self.assertEqual(result['context'], model)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], model)
        self.assertEqual(result['virtual_root'], model)
        self.assertEqual(result['virtual_root_path'], ())

    def test_withroute_with_subpath_string(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        environ = {'bfg.routes.matchdict': {'subpath':'/a/b/c'}}
        result = traverser(environ)
        self.assertEqual(result['context'], model)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ('a', 'b','c'))
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], model)
        self.assertEqual(result['virtual_root'], model)
        self.assertEqual(result['virtual_root_path'], ())

    def test_withroute_with_subpath_tuple(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        environ = {'bfg.routes.matchdict': {'subpath':('a', 'b', 'c')}}
        result = traverser(environ)
        self.assertEqual(result['context'], model)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ('a', 'b','c'))
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], model)
        self.assertEqual(result['virtual_root'], model)
        self.assertEqual(result['virtual_root_path'], ())

    def test_withroute_and_traverse_string(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        environ = {'bfg.routes.matchdict': {'traverse':'foo/bar'}}
        result = traverser(environ)
        self.assertEqual(result['context'], model)
        self.assertEqual(result['view_name'], 'foo')
        self.assertEqual(result['subpath'], ('bar',))
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], model)
        self.assertEqual(result['virtual_root'], model)
        self.assertEqual(result['virtual_root_path'], ())

    def test_withroute_and_traverse_tuple(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        environ = {'bfg.routes.matchdict': {'traverse':('foo', 'bar')}}
        result = traverser(environ)
        self.assertEqual(result['context'], model)
        self.assertEqual(result['view_name'], 'foo')
        self.assertEqual(result['subpath'], ('bar',))
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], model)
        self.assertEqual(result['virtual_root'], model)
        self.assertEqual(result['virtual_root_path'], ())

class FindInterfaceTests(unittest.TestCase):
    def _callFUT(self, context, iface):
        from repoze.bfg.traversal import find_interface
        return find_interface(context, iface)

    def test_it_interface(self):
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
        from zope.interface import directlyProvides
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        directlyProvides(root, IFoo)
        result = self._callFUT(baz, IFoo)
        self.assertEqual(result.__name__, 'root')

    def test_it_class(self):
        class DummyRoot(object):
            def __init__(self, child):
                self.child = child
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyRoot(foo)
        root.__parent__ = None
        root.__name__ = 'root'
        foo.__parent__ = root
        foo.__name__ = 'foo'
        bar.__parent__ = foo
        bar.__name__ = 'bar'
        baz.__parent__ = bar
        baz.__name__ = 'baz'
        result = self._callFUT(baz, DummyRoot)
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

    def _registerTraverser(self, traverser):
        from repoze.bfg.threadlocal import get_current_registry
        reg = get_current_registry()
        from repoze.bfg.interfaces import ITraverser
        from zope.interface import Interface
        reg.registerAdapter(traverser, (Interface,), ITraverser)

    def test_list(self):
        model = DummyContext()
        traverser = make_traverser({'context':model, 'view_name':''})
        self._registerTraverser(traverser)
        result = self._callFUT(model, [''])
        self.assertEqual(result, model)
        self.assertEqual(model.request.environ['PATH_INFO'], '/')

    def test_generator(self):
        model = DummyContext()
        traverser = make_traverser({'context':model, 'view_name':''})
        self._registerTraverser(traverser)
        def foo():
            yield ''
        result = self._callFUT(model, foo())
        self.assertEqual(result, model)
        self.assertEqual(model.request.environ['PATH_INFO'], '/')

    def test_self_string_found(self):
        model = DummyContext()
        traverser = make_traverser({'context':model, 'view_name':''})
        self._registerTraverser(traverser)
        result = self._callFUT(model, '')
        self.assertEqual(result, model)
        self.assertEqual(model.request.environ['PATH_INFO'], '')

    def test_self_tuple_found(self):
        model = DummyContext()
        traverser = make_traverser({'context':model, 'view_name':''})
        self._registerTraverser(traverser)
        result = self._callFUT(model, ())
        self.assertEqual(result, model)
        self.assertEqual(model.request.environ['PATH_INFO'], '')

    def test_relative_string_found(self):
        model = DummyContext()
        baz = DummyContext()
        traverser = make_traverser({'context':baz, 'view_name':''})
        self._registerTraverser(traverser)
        result = self._callFUT(model, 'baz')
        self.assertEqual(result, baz)
        self.assertEqual(model.request.environ['PATH_INFO'], 'baz')

    def test_relative_tuple_found(self):
        model = DummyContext()
        baz = DummyContext()
        traverser = make_traverser({'context':baz, 'view_name':''})
        self._registerTraverser(traverser)
        result = self._callFUT(model, ('baz',))
        self.assertEqual(result, baz)
        self.assertEqual(model.request.environ['PATH_INFO'], 'baz')

    def test_relative_string_notfound(self):
        model = DummyContext()
        baz = DummyContext()
        traverser = make_traverser({'context':baz, 'view_name':'bar'})
        self._registerTraverser(traverser)
        self.assertRaises(KeyError, self._callFUT, model, 'baz')
        self.assertEqual(model.request.environ['PATH_INFO'], 'baz')

    def test_relative_tuple_notfound(self):
        model = DummyContext()
        baz = DummyContext()
        traverser = make_traverser({'context':baz, 'view_name':'bar'})
        self._registerTraverser(traverser)
        self.assertRaises(KeyError, self._callFUT, model, ('baz',))
        self.assertEqual(model.request.environ['PATH_INFO'], 'baz')

    def test_absolute_string_found(self):
        root = DummyContext()
        model = DummyContext()
        model.__parent__ = root
        model.__name__ = 'baz'
        traverser = make_traverser({'context':root, 'view_name':''})
        self._registerTraverser(traverser)
        result = self._callFUT(model, '/')
        self.assertEqual(result, root)
        self.assertEqual(root.wascontext, True)
        self.assertEqual(root.request.environ['PATH_INFO'], '/')

    def test_absolute_tuple_found(self):
        root = DummyContext()
        model = DummyContext()
        model.__parent__ = root
        model.__name__ = 'baz'
        traverser = make_traverser({'context':root, 'view_name':''})
        self._registerTraverser(traverser)
        result = self._callFUT(model, ('',))
        self.assertEqual(result, root)
        self.assertEqual(root.wascontext, True)
        self.assertEqual(root.request.environ['PATH_INFO'], '/')

    def test_absolute_string_notfound(self):
        root = DummyContext()
        model = DummyContext()
        model.__parent__ = root
        model.__name__ = 'baz'
        traverser = make_traverser({'context':root, 'view_name':'fuz'})
        self._registerTraverser(traverser)
        self.assertRaises(KeyError, self._callFUT, model, '/')
        self.assertEqual(root.wascontext, True)
        self.assertEqual(root.request.environ['PATH_INFO'], '/')

    def test_absolute_tuple_notfound(self):
        root = DummyContext()
        model = DummyContext()
        model.__parent__ = root
        model.__name__ = 'baz'
        traverser = make_traverser({'context':root, 'view_name':'fuz'})
        self._registerTraverser(traverser)
        self.assertRaises(KeyError, self._callFUT, model, ('',))
        self.assertEqual(root.wascontext, True)
        self.assertEqual(root.request.environ['PATH_INFO'], '/')


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

    def test_root_default_emptystring(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = ''
        result = self._callFUT(root)
        self.assertEqual(result, '/')

    def test_root_object_nonnull_name_direct(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = 'flubadub'
        result = self._callFUT(root)
        self.assertEqual(result, 'flubadub') # insane case

    def test_root_object_nonnull_name_indirect(self):
        root = DummyContext()
        root.__parent__ = None
        root.__name__ = 'flubadub'
        other = DummyContext()
        other.__parent__ = root
        other.__name__ = 'barker'
        result = self._callFUT(other)
        self.assertEqual(result, 'flubadub/barker') # insane case

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

    def _registerTraverser(self, traverser):
        from repoze.bfg.threadlocal import get_current_registry
        reg = get_current_registry()
        from repoze.bfg.interfaces import ITraverser
        from zope.interface import Interface
        reg.registerAdapter(traverser, (Interface,), ITraverser)

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

    def test_call_with_virtual_root_path(self):
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

    def test_virtual_root_no_virtual_root_path(self):
        root = DummyContext()
        root.__name__ = None
        root.__parent__ = None
        one = DummyContext()
        one.__name__ = 'one'
        one.__parent__ = root
        request = DummyRequest()
        context_url = self._makeOne(one, request)
        self.assertEqual(context_url.virtual_root(), root)

    def test_virtual_root_no_virtual_root_path_with_root_on_request(self):
        context = DummyContext()
        context.__parent__ = None
        request = DummyRequest()
        request.root = DummyContext()
        context_url = self._makeOne(context, request)
        self.assertEqual(context_url.virtual_root(), request.root)

    def test_virtual_root_with_virtual_root_path(self):
        from repoze.bfg.interfaces import VH_ROOT_KEY
        context = DummyContext()
        context.__parent__ = None
        traversed_to = DummyContext()
        environ = {VH_ROOT_KEY:'/one'}
        request = DummyRequest(environ)
        traverser = make_traverser({'context':traversed_to, 'view_name':''})
        self._registerTraverser(traverser)
        context_url = self._makeOne(context, request)
        self.assertEqual(context_url.virtual_root(), traversed_to)
        self.assertEqual(context.request.environ['PATH_INFO'], '/one')

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

    def test_registered(self):
        from repoze.bfg.interfaces import IContextURL
        from zope.interface import Interface
        request = _makeRequest()
        request.registry.registerAdapter(DummyContextURL, (Interface,Interface),
                                         IContextURL)
        context = DummyContext()
        result = self._callFUT(context, request)
        self.assertEqual(result, '123')

    def test_default(self):
        context = DummyContext()
        request = _makeRequest()
        request.environ['PATH_INFO'] = '/'
        result = self._callFUT(context, request)
        self.assertEqual(result, context)

    def test_default_no_registry_on_request(self):
        context = DummyContext()
        request = _makeRequest()
        del request.registry
        request.environ['PATH_INFO'] = '/'
        result = self._callFUT(context, request)
        self.assertEqual(result, context)

class TraverseTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, name):
        from repoze.bfg.traversal import traverse
        return traverse(context, name)

    def _registerTraverser(self, traverser):
        from repoze.bfg.threadlocal import get_current_registry
        reg = get_current_registry()
        from repoze.bfg.interfaces import ITraverser
        from zope.interface import Interface
        reg.registerAdapter(traverser, (Interface,), ITraverser)

    def test_request_has_registry(self):
        from repoze.bfg.threadlocal import get_current_registry
        model = DummyContext()
        traverser = make_traverser({'context':model, 'view_name':''})
        self._registerTraverser(traverser)
        self._callFUT(model, [''])
        self.assertEqual(model.request.registry, get_current_registry())

    def test_list(self):
        model = DummyContext()
        traverser = make_traverser({'context':model, 'view_name':''})
        self._registerTraverser(traverser)
        self._callFUT(model, [''])
        self.assertEqual(model.request.environ['PATH_INFO'], '/')

    def test_generator(self):
        model = DummyContext()
        traverser = make_traverser({'context':model, 'view_name':''})
        self._registerTraverser(traverser)
        def foo():
            yield ''
        self._callFUT(model, foo())
        self.assertEqual(model.request.environ['PATH_INFO'], '/')

    def test_self_string_found(self):
        model = DummyContext()
        traverser = make_traverser({'context':model, 'view_name':''})
        self._registerTraverser(traverser)
        self._callFUT(model, '')
        self.assertEqual(model.request.environ['PATH_INFO'], '')

    def test_self_tuple_found(self):
        model = DummyContext()
        traverser = make_traverser({'context':model, 'view_name':''})
        self._registerTraverser(traverser)
        self._callFUT(model, ())
        self.assertEqual(model.request.environ['PATH_INFO'], '')

    def test_relative_string_found(self):
        model = DummyContext()
        baz = DummyContext()
        traverser = make_traverser({'context':baz, 'view_name':''})
        self._registerTraverser(traverser)
        self._callFUT(model, 'baz')
        self.assertEqual(model.request.environ['PATH_INFO'], 'baz')

    def test_relative_tuple_found(self):
        model = DummyContext()
        baz = DummyContext()
        traverser = make_traverser({'context':baz, 'view_name':''})
        self._registerTraverser(traverser)
        self._callFUT(model, ('baz',))
        self.assertEqual(model.request.environ['PATH_INFO'], 'baz')

    def test_absolute_string_found(self):
        root = DummyContext()
        model = DummyContext()
        model.__parent__ = root
        model.__name__ = 'baz'
        traverser = make_traverser({'context':root, 'view_name':''})
        self._registerTraverser(traverser)
        self._callFUT(model, '/')
        self.assertEqual(root.wascontext, True)
        self.assertEqual(root.request.environ['PATH_INFO'], '/')

    def test_absolute_tuple_found(self):
        root = DummyContext()
        model = DummyContext()
        model.__parent__ = root
        model.__name__ = 'baz'
        traverser = make_traverser({'context':root, 'view_name':''})
        self._registerTraverser(traverser)
        self._callFUT(model, ('',))
        self.assertEqual(root.wascontext, True)
        self.assertEqual(root.request.environ['PATH_INFO'], '/')

    def test_empty_sequence(self):
        root = DummyContext()
        model = DummyContext()
        model.__parent__ = root
        model.__name__ = 'baz'
        traverser = make_traverser({'context':root, 'view_name':''})
        self._registerTraverser(traverser)
        self._callFUT(model, [])
        self.assertEqual(model.wascontext, True)
        self.assertEqual(model.request.environ['PATH_INFO'], '')

    def test_default_traverser(self):
        model = DummyContext()
        result = self._callFUT(model, '')
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['context'], model)

class TestDefaultRootFactory(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.traversal import DefaultRootFactory
        return DefaultRootFactory

    def _makeOne(self, environ):
        return self._getTargetClass()(environ)

    def test_no_matchdict(self):
        environ = {}
        root = self._makeOne(environ)
        self.assertEqual(root.__parent__, None)
        self.assertEqual(root.__name__, None)

    def test_matchdict(self):
        class DummyRequest:
            pass
        request = DummyRequest()
        request.matchdict = {'a':1, 'b':2}
        root = self._makeOne(request)
        self.assertEqual(root.a, 1)
        self.assertEqual(root.b, 2)


def make_traverser(result):
    class DummyTraverser(object):
        def __init__(self, context):
            self.context = context
            context.wascontext = True
        def __call__(self, request):
            self.context.request = request
            return result
    return DummyTraverser
        
class DummyContext(object):
    __parent__ = None
    def __init__(self, next=None, name=None):
        self.next = next
        self.__name__ = name
        
    def __getitem__(self, name):
        if self.next is None:
            raise KeyError, name
        return self.next

    def __repr__(self):
        return '<DummyContext with name %s at id %s>'%(self.__name__, id(self))

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

def _makeRequest(environ=None):
    from repoze.bfg.registry import Registry
    request = DummyRequest()
    request.registry = Registry()
    return request
