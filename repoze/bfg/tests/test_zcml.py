import unittest

from zope.component.testing import PlacelessSetup

class TestViewDirective(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

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
        def view(context, request):
            pass
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler
        from zope.component.interface import provideInterface

        self.assertEqual(len(actions), 3)

        provide = actions[0]
        self.assertEqual(provide['discriminator'], None)
        self.assertEqual(provide['callable'], provideInterface)
        self.assertEqual(provide['args'][0], '')
        self.assertEqual(provide['args'][1], IFoo)

        permission = actions[1]
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
        
        regadapt = actions[2]
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
        def view(context, request):
            pass
        self._callFUT(context, 'repoze.view', IFoo, view=view,
                      request_type=IDummy)
        actions = context.actions
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler
        from zope.component.interface import provideInterface

        self.assertEqual(len(actions), 3)

        provide = actions[0]
        self.assertEqual(provide['discriminator'], None)
        self.assertEqual(provide['callable'], provideInterface)
        self.assertEqual(provide['args'][0], '')
        self.assertEqual(provide['args'][1], IFoo)

        permission = actions[1]
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
        
        regadapt = actions[2]
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
        def view(context, request):
            pass
        self._callFUT(context, 'repoze.view', IFoo, view=view,
                      request_type=IDummy, cacheable=False)
        actions = context.actions
        from repoze.bfg.interfaces import IView
        from repoze.bfg.zcml import handler
        from repoze.bfg.zcml import Uncacheable

        self.assertEqual(len(actions), 3)

        regadapt = actions[2]
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
            
            def __call__(self, context, request):
                pass

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
        def aview(self, context, request):
            pass

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
        def aview(self, context, request):
            pass

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
        

class TestFixtureApp(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def test_registry_actions_can_be_pickled_and_unpickled(self):
        import repoze.bfg.tests.fixtureapp as package
        from zope.configuration import config
        from zope.configuration import xmlconfig
        context = config.ConfigurationMachine()
        xmlconfig.registerCommonDirectives(context)
        context.package = package
        xmlconfig.include(context, 'configure.zcml', package)
        context.execute_actions(clear=False)
        actions = context.actions
        import cPickle
        dumped = cPickle.dumps(actions, -1)
        new = cPickle.loads(dumped)
        self.assertEqual(len(actions), len(new))

class TestZCMLPickling(unittest.TestCase, PlacelessSetup):
    i = 0
    def setUp(self):
        self.tempdir = None
        PlacelessSetup.setUp(self)
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
        PlacelessSetup.tearDown(self)
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
        def dumpfail(actions, f):
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

class Dummy:
    pass

class DummyContext:
    def __init__(self):
        self.actions = []
        self.info = None

    def path(self, name):
        import os
        here = os.path.dirname(__file__)
        fixtures = os.path.join(here, 'fixtures')
        return os.path.join(fixtures, name)

    def action(self, discriminator, callable, args):
        self.actions.append(
            {'discriminator':discriminator,
             'callable':callable,
             'args':args}
            )

from zope.interface import Interface
class IDummy(Interface):
    pass

    
