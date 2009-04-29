import unittest

from zope.testing.cleanup import cleanUp

class TestViewDirective(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import view
        return view(*arg, **kw)

    def test_no_view(self):
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, self._callFUT, context,
                          'repoze.view', None)

    def test_only_view(self):
        context = DummyContext()
        class IFoo:
            pass
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 2)

        permission = actions[0]
        permission_discriminator = ('permission', IFoo, '', IRequest,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IRequest))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IRequest, IView, True)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1], view)
        self.assertEqual(regadapt['args'][2], (IFoo, IRequest))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_request_type(self):
        context = DummyContext()
        class IFoo:
            pass
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view,
                      request_type=IDummy)
        actions = context.actions
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 2)

        permission = actions[0]
        permission_discriminator = ('permission', IFoo, '', IDummy,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IDummy))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IDummy, IView, True)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1], view)
        self.assertEqual(regadapt['args'][2], (IFoo, IDummy))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_uncacheable(self):
        context = DummyContext()
        class IFoo:
            pass
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view,
                      request_type=IDummy, cacheable=False)
        actions = context.actions
        from repoze.bfg.interfaces import IView
        from repoze.bfg.zcml import handler
        from repoze.bfg.zcml import Uncacheable

        self.assertEqual(len(actions), 2)

        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IDummy, IView, Uncacheable)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1], view)
        self.assertEqual(regadapt['args'][2], (IFoo, IDummy))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_adapted_class(self):
        from zope.interface import Interface
        import zope.component

        class IFoo(Interface):
            pass
        class IBar(Interface):
            pass

        class AView(object):
            zope.component.adapts(IFoo, IBar)

        aview = AView()

        context = DummyContext()
        self._callFUT(context, view=aview)

        actions = context.actions
        from repoze.bfg.interfaces import IView
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 1)

        regadapt = actions[0]
        regadapt_discriminator = ('view', IFoo, '', IBar, IView, True)

        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1], aview)
        self.assertEqual(regadapt['args'][2], (IFoo, IBar))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_adapted_function(self):
        from zope.interface import Interface
        import zope.component

        class IFoo(Interface):
            pass
        class IBar(Interface):
            pass

        @zope.component.adapter(IFoo, IBar)
        def aview(context, request):
            pass
        aview(None, None) # dead chicken for test coverage

        context = DummyContext()
        self._callFUT(context, view=aview)

        actions = context.actions
        from repoze.bfg.interfaces import IView
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 1)

        regadapt = actions[0]
        regadapt_discriminator = ('view', IFoo, '', IBar, IView, True)

        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1], aview)
        self.assertEqual(regadapt['args'][2], (IFoo, IBar))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_adapted_nonsense(self):
        from repoze.bfg.interfaces import IRequest
        from zope.interface import Interface
        import zope.component

        class IFoo(Interface):
            pass
        class IBar(Interface):
            pass

        @zope.component.adapter(IFoo) # too few arguments
        def aview(context, request):
            pass
        aview(None, None) # dead chicken for test coverage

        context = DummyContext()
        self._callFUT(context, view=aview)

        actions = context.actions
        from repoze.bfg.interfaces import IView
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 1)

        regadapt = actions[0]
        regadapt_discriminator = ('view', None, '', IRequest, IView, True)

        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1], aview)
        self.assertEqual(regadapt['args'][2], (None, IRequest))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

class TestRouteRequirementFunction(unittest.TestCase):
    def _callFUT(self, context, attr, expr):
        from repoze.bfg.zcml import route_requirement
        return route_requirement(context, attr, expr)

    def test_it(self):
        context = DummyContext()
        context.context = DummyContext()
        context.context.requirements = {}
        self._callFUT(context, 'a', 'b')
        self.assertEqual(context.context.requirements['a'], 'b')
        self.assertRaises(ValueError, self._callFUT, context, 'a', 'b')

class TestConnectRouteFunction(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, directive):
        from repoze.bfg.zcml import connect_route
        return connect_route(directive)

    def _registerRoutesMapper(self):
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        mapper = DummyMapper()
        from repoze.bfg.interfaces import IRoutesMapper
        gsm.registerUtility(mapper, IRoutesMapper)
        return mapper

    def test_no_mapper(self):
        directive = DummyRouteDirective()
        self._callFUT(directive) # doesn't blow up when no routes mapper reg'd

    def test_defaults(self):
        mapper = self._registerRoutesMapper()
        directive = DummyRouteDirective()
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][0], ('a/b/c',))
        self.assertEqual(mapper.connections[0][1], {'requirements': {}})

    def test_name_and_path(self):
        mapper = self._registerRoutesMapper()
        directive = DummyRouteDirective(name='abc')
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][0], ('abc', 'a/b/c',))
        self.assertEqual(mapper.connections[0][1], {'requirements': {}})

    def test_all_directives(self):
        mapper = self._registerRoutesMapper()
        def foo():
            """ """
        directive = DummyRouteDirective(
            minimize=True, explicit=True, encoding='utf-8', static=True,
            filter=foo, absolute=True, member_name='m', collection_name='c',
            parent_member_name='p', parent_collection_name='c',
            condition_method='GET', condition_subdomain=True,
            condition_function=foo, subdomains=['a'],
            factory=foo, provides=[IDummy], view_name='def')
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][0], ('a/b/c',))
        pr = {'member_name':'p', 'collection_name':'c'}
        c = {'method':'GET', 'sub_domain':['a'], 'function':foo}
        self.assertEqual(mapper.connections[0][1],
                         {'requirements': {},
                          '_minimize':True,
                          '_explicit':True,
                          '_encoding':'utf-8',
                          '_static':True,
                          '_filter':foo,
                          '_absolute':True,
                          '_member_name':'m',
                          '_collection_name':'c',
                          '_parent_resource':pr,
                          'conditions':c,
                          '_factory':foo,
                          '_provides':[IDummy],
                          'view_name':'def',
                          })

    def test_condition_subdomain_true(self):
        mapper = self._registerRoutesMapper()
        directive = DummyRouteDirective(static=True, explicit=True,
                                        condition_subdomain=True)
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][0], ('a/b/c',))
        self.assertEqual(mapper.connections[0][1],
                         {'requirements': {},
                          '_static':True,
                          '_explicit':True,
                          'conditions':{'sub_domain':True}
                          })

    def test_condition_function(self):
        mapper = self._registerRoutesMapper()
        def foo(e, r):
            """ """
        directive = DummyRouteDirective(static=True, explicit=True,
                                        condition_function=foo)
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][0], ('a/b/c',))
        self.assertEqual(mapper.connections[0][1],
                         {'requirements': {},
                          '_static':True,
                          '_explicit':True,
                          'conditions':{'function':foo}
                          })

    def test_condition_method(self):
        mapper = self._registerRoutesMapper()
        directive = DummyRouteDirective(static=True, explicit=True,
                                        condition_method='GET')
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][0], ('a/b/c',))
        self.assertEqual(mapper.connections[0][1],
                         {'requirements': {},
                          '_static':True,
                          '_explicit':True,
                          'conditions':{'method':'GET'}
                          })

    def test_subdomains(self):
        mapper = self._registerRoutesMapper()
        directive = DummyRouteDirective(static=True, explicit=True,
                                        subdomains=['a', 'b'])
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][0], ('a/b/c',))
        self.assertEqual(mapper.connections[0][1],
                         {'requirements': {},
                          '_static':True,
                          '_explicit':True,
                          'conditions':{'sub_domain':['a', 'b']}
                          })

class TestRouteGroupingContextDecorator(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.zcml import Route
        return Route

    def _makeOne(self, context, path, **kw):
        return self._getTargetClass()(context, path, **kw)

    def test_defaults(self):
        context = DummyContext()
        route = self._makeOne(context, 'abc')
        self.assertEqual(route.requirements, {})
        self.assertEqual(route.parent_member_name, None)
        self.assertEqual(route.parent_collection_name, None)

    def test_parent_collection_name_missing(self):
        context = DummyContext()
        self.assertRaises(ValueError, self._makeOne, context, 'abc',
                          parent_member_name='a')
        
    def test_parent_collection_name_present(self):
        context = DummyContext()
        route = self._makeOne(context, 'abc',
                              parent_member_name='a',
                              parent_collection_name='p')
        self.assertEqual(route.parent_member_name, 'a')
        self.assertEqual(route.parent_collection_name, 'p')

    def test_explicit_view_name(self):
        context = DummyContext()
        route = self._makeOne(context, 'abc', view_name='def')
        self.assertEqual(route.view_name, 'def')

class TestZCMLPickling(unittest.TestCase):
    i = 0
    def setUp(self):
        cleanUp()
        self.tempdir = None
        import sys
        import os
        import tempfile
        from repoze.bfg.path import package_path
        from repoze.bfg.tests import fixtureapp as package
        import shutil
        tempdir = tempfile.mkdtemp()
        modname = 'myfixture%s' % self.i
        self.i += 1
        self.packagepath = os.path.join(tempdir, modname)
        fixturedir = package_path(package)
        pckname = os.path.join(fixturedir, 'configure.zcml.cache')
        if os.path.isfile(pckname):
            os.remove(pckname)
        shutil.copytree(fixturedir, self.packagepath)
        sys.path.insert(0, tempdir)
        self.module = __import__(modname)
        self.tempdir = tempdir

    def tearDown(self):
        cleanUp()
        import sys
        import shutil
        if self.module is not None:
            del sys.modules[self.module.__name__]
        if self.tempdir is not None:
            sys.path.pop(0)
            shutil.rmtree(self.tempdir)

    def test_file_configure(self):
        import os
        import cPickle
        from repoze.bfg.zcml import file_configure
        self.assertEqual(False, file_configure('configure.zcml', self.module))
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        self.failUnless(os.path.exists(picklename))
        actions = cPickle.load(open(picklename, 'rb'))
        self.failUnless(actions)

    def test_file_configure_uncacheable_removes_cache(self):
        import os
        from repoze.bfg.zcml import file_configure
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        f = open(picklename, 'w')
        f.write('imhere')
        self.failUnless(os.path.exists(picklename))

        import repoze.bfg.zcml
        keep_view = repoze.bfg.zcml.view

        def wrap_view(*arg, **kw):
            kw['cacheable'] = False
            return keep_view(*arg, **kw)

        try:
            repoze.bfg.zcml.view = wrap_view
            file_configure('configure.zcml', self.module)
            self.failIf(os.path.exists(picklename)) # should be deleted
        finally:
            repoze.bfg.zcml.view = keep_view

    def test_file_configure_nonexistent_configure_dot_zcml(self):
        import os
        from repoze.bfg.zcml import file_configure
        os.remove(os.path.join(self.packagepath, 'configure.zcml'))
        self.assertRaises(IOError, file_configure, 'configure.zcml',
                          self.module)

    def test_file_configure_pickling_error(self):
        import os
        from repoze.bfg.zcml import file_configure
        def dumpfail(actions, f, num):
            raise IOError
        self.assertEqual(False,
                      file_configure('configure.zcml', self.module, dumpfail))
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        self.failIf(os.path.exists(picklename))

    def test_zcml_configure_writes_pickle_when_none_exists(self):
        import os
        import cPickle
        from repoze.bfg.zcml import zcml_configure
        self.assertEqual(False, zcml_configure('configure.zcml', self.module))
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        self.failUnless(os.path.exists(picklename))
        actions = cPickle.load(open(picklename, 'rb'))
        self.failUnless(actions)

    def test_zcml_configure_uses_file_configure_with_bad_pickle1(self):
        import os
        import cPickle
        from repoze.bfg.zcml import zcml_configure
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        f = open(picklename, 'wb')
        cPickle.dump((), f)
        f.close()
        self.assertEqual(False, zcml_configure('configure.zcml', self.module))

    def test_zcml_configure_uses_file_configure_with_bad_pickle2(self):
        import os
        from repoze.bfg.zcml import zcml_configure
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        f = open(picklename, 'wb')
        f.write('garbage')
        f.close()
        self.assertEqual(False, zcml_configure('configure.zcml', self.module))

    def test_zcml_configure_uses_file_configure_with_outofdate_pickle1(self):
        import os
        import cPickle
        import time
        from repoze.bfg.zcml import zcml_configure
        basename = os.path.join(self.packagepath, 'configure.zcml')
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        self.assertEqual(False, zcml_configure('configure.zcml', self.module))
        self.failUnless(os.path.exists(picklename))
        actions = cPickle.load(open(picklename, 'rb'))
        self.failUnless(actions)
        os.utime(basename, (-1, time.time() + 100))
        self.assertEqual(False, zcml_configure('configure.zcml', self.module))

    def test_zcml_configure_uses_file_configure_with_outofdate_pickle2(self):
        import os
        import cPickle
        import time
        from repoze.bfg.zcml import zcml_configure
        basename = os.path.join(self.packagepath, 'another.zcml')
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        self.assertEqual(False, zcml_configure('configure.zcml', self.module))
        self.failUnless(os.path.exists(picklename))
        actions = cPickle.load(open(picklename, 'rb'))
        self.failUnless(actions)
        os.utime(basename, (-1, time.time() + 100))
        self.assertEqual(False, zcml_configure('configure.zcml', self.module))

    def test_zcml_configure_uses_file_configure_with_missing_dependent(self):
        import os
        import cPickle
        from repoze.bfg.zcml import zcml_configure
        from zope.configuration.xmlconfig import ZopeXMLConfigurationError
        basename = os.path.join(self.packagepath, 'another.zcml')
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        self.assertEqual(False, zcml_configure('configure.zcml', self.module))
        self.failUnless(os.path.exists(picklename))
        actions = cPickle.load(open(picklename, 'rb'))
        self.failUnless(actions)
        os.remove(basename)
        self.assertRaises(ZopeXMLConfigurationError, zcml_configure,
                          'configure.zcml', self.module)

    def test_zcml_configure_uses_file_configure_with_bad_version(self):
        import os
        from repoze.bfg.zcml import zcml_configure
        from repoze.bfg.zcml import PVERSION
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        f = open(picklename, 'wb')
        import cPickle
        data = (PVERSION+1, 0, [])
        cPickle.dump(data, open(picklename, 'wb'))
        self.assertEqual(False, zcml_configure('configure.zcml', self.module))

    def test_zcml_configure_uses_file_configure_with_bad_time(self):
        import os
        from repoze.bfg.zcml import zcml_configure
        from repoze.bfg.zcml import PVERSION
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        f = open(picklename, 'wb')
        import cPickle
        data = (PVERSION, None, [])
        cPickle.dump(data, open(picklename, 'wb'))
        self.assertEqual(False, zcml_configure('configure.zcml', self.module))

    def test_zcml_configure_uses_file_configure_with_bad_actions(self):
        import os
        from repoze.bfg.zcml import zcml_configure
        from repoze.bfg.zcml import PVERSION
        import time
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        f = open(picklename, 'wb')
        import cPickle
        data = (PVERSION, time.time()+500, None)
        cPickle.dump(data, open(picklename, 'wb'))
        self.assertEqual(False, zcml_configure('configure.zcml', self.module))

    def test_zcml_configure_uses_file_configure_with_bad_actions2(self):
        import cPickle
        import os
        import time
        from repoze.bfg.zcml import zcml_configure
        from repoze.bfg.zcml import PVERSION
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        f = open(picklename, 'wb')
        actions = [(None, None, None, None, None)]
        data = (PVERSION, time.time()+500, actions)
        cPickle.dump(data, open(picklename, 'wb'))
        self.assertEqual(False, zcml_configure('configure.zcml', self.module))

    def test_zcml_configure_uses_good_pickle(self):
        import os
        import cPickle
        import time
        from repoze.bfg.zcml import zcml_configure
        from repoze.bfg.zcml import PVERSION
        basename = os.path.join(self.packagepath, 'another.zcml')
        picklename = os.path.join(self.packagepath, 'configure.zcml.cache')
        self.assertEqual(False, zcml_configure('configure.zcml', self.module))
        self.failUnless(os.path.exists(picklename))
        actions = cPickle.load(open(picklename, 'rb'))
        self.failUnless(actions)
        actions = (PVERSION, time.time()+100, actions[2])
        cPickle.dump(actions, open(picklename, 'wb'))
        self.assertEqual(True, zcml_configure('configure.zcml', self.module))

class TestRemove(unittest.TestCase):
    def _callFUT(self, name, os):
        from repoze.bfg.zcml import remove
        return remove(name, os)

    def test_fail(self):
        class FakeOS:
            def remove(self, name):
                raise IOError('foo')
        self.assertEqual(self._callFUT('name', FakeOS()), False)

    def test_succeed(self):
        class FakeOS:
            def remove(self, name):
                pass
        self.assertEqual(self._callFUT('name', FakeOS()), True)

class TestBFGViewFunctionGrokker(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.zcml import BFGViewFunctionGrokker
        return BFGViewFunctionGrokker

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_grok_is_bfg_view(self):
        from repoze.bfg.interfaces import IRequest
        from zope.interface import Interface
        grokker = self._makeOne()
        class obj:
            pass
        obj.__is_bfg_view__ = True
        obj.__permission__ = 'foo'
        obj.__for__ = Interface
        obj.__view_name__ = 'foo.html'
        obj.__request_type__ = IRequest
        context = DummyContext()
        result = grokker.grok('name', obj, context=context)
        self.assertEqual(result, True)
        actions = context.actions
        self.assertEqual(len(actions), 2)

    def test_grok_is_not_bfg_view(self):
        grokker = self._makeOne()
        class obj:
            pass
        context = DummyContext()
        result = grokker.grok('name', obj, context=context)
        self.assertEqual(result, False)
        actions = context.actions
        self.assertEqual(len(actions), 0)

class TestZCMLScanFunction(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, package, martian):
        from repoze.bfg.zcml import scan
        return scan(context, package, martian)

    def test_it(self):
        martian = DummyMartianModule()
        module_grokker = DummyModuleGrokker()
        dummy_module = DummyModule()
        from repoze.bfg.zcml import exclude
        self._callFUT(None, dummy_module, martian)
        self.assertEqual(martian.name, 'dummy')
        self.assertEqual(len(martian.module_grokker.registered), 1)
        self.assertEqual(martian.context, None)
        self.assertEqual(martian.exclude_filter, exclude)

class TestExcludeFunction(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, name):
        from repoze.bfg.zcml import exclude
        return exclude(name)

    def test_it(self):
        self.assertEqual(self._callFUT('.foo'), True)
        self.assertEqual(self._callFUT('foo'), False)
    
class DummyModule:
    __name__ = 'dummy'

class DummyModuleGrokker:
    def __init__(self):
        self.registered = []
        
    def register(self, other):
        self.registered.append(other)
        
class DummyMartianModule:
    def grok_dotted_name(self, name, grokker, context, exclude_filter=None):
        self.name = name
        self.context = context
        self.exclude_filter = exclude_filter
        return True

    def ModuleGrokker(self):
        self.module_grokker = DummyModuleGrokker()
        return self.module_grokker

class DummyContext:
    def __init__(self):
        self.actions = []
        self.info = None

    def action(self, discriminator, callable, args):
        self.actions.append(
            {'discriminator':discriminator,
             'callable':callable,
             'args':args}
            )

class Dummy:
    pass

class DummyRouteDirective:
    encoding = None
    static = False
    minimize = False
    explicit = False
    static = False
    filter = None
    absolute = False
    member_name = False
    collection_name = None
    parent_member_name = None
    parent_collection_name = None
    condition_method = None
    condition_subdomain = None
    condition_function = None
    subdomains = None
    path = 'a/b/c'
    name = None
    view_name = ''
    factory = None
    provides = ()
    def __init__(self, **kw):
        if not 'requirements' in kw:
            kw['requirements'] = {}
        self.__dict__.update(kw)

class DummyMapper:
    def __init__(self):
        self.connections = []

    def connect(self, *arg, **kw):
        self.connections.append((arg, kw))

from zope.interface import Interface
class IDummy(Interface):
    pass

    
