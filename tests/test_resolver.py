import os
import unittest

here = os.path.abspath(os.path.dirname(__file__))


class TestResolver(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.resolver import Resolver

        return Resolver

    def _makeOne(self, package):
        return self._getTargetClass()(package)

    def test_get_package_caller_package(self):
        from pyramid.path import CALLER_PACKAGE
        import tests

        self.assertEqual(self._makeOne(CALLER_PACKAGE).get_package(), tests)

    def test_get_package_name_caller_package(self):
        from pyramid.path import CALLER_PACKAGE

        self.assertEqual(
            self._makeOne(CALLER_PACKAGE).get_package_name(), 'tests'
        )

    def test_get_package_string(self):
        import tests

        self.assertEqual(self._makeOne('tests').get_package(), tests)

    def test_get_package_name_string(self):
        self.assertEqual(self._makeOne('tests').get_package_name(), 'tests')


class TestAssetResolver(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.resolver import AssetResolver

        return AssetResolver

    def _makeOne(self, package='tests'):
        return self._getTargetClass()(package)

    def test_ctor_as_package(self):
        import sys

        tests = sys.modules['tests']
        inst = self._makeOne(tests)
        self.assertEqual(inst.package, tests)

    def test_ctor_as_str(self):
        import sys

        tests = sys.modules['tests']
        inst = self._makeOne('tests')
        self.assertEqual(inst.package, tests)

    def test_resolve_abspath(self):
        from pyramid.path import FSAssetDescriptor

        inst = self._makeOne(None)
        r = inst.resolve(os.path.join(here, 'test_asset.py'))
        self.assertEqual(r.__class__, FSAssetDescriptor)
        self.assertTrue(r.exists())

    def test_resolve_absspec(self):
        from pyramid.path import PkgResourcesAssetDescriptor

        inst = self._makeOne(None)
        r = inst.resolve('tests:test_asset.py')
        self.assertEqual(r.__class__, PkgResourcesAssetDescriptor)
        self.assertTrue(r.exists())

    def test_resolve_relspec_with_pkg(self):
        from pyramid.path import PkgResourcesAssetDescriptor

        inst = self._makeOne('tests')
        r = inst.resolve('test_asset.py')
        self.assertEqual(r.__class__, PkgResourcesAssetDescriptor)
        self.assertTrue(r.exists())

    def test_resolve_relspec_no_package(self):
        inst = self._makeOne(None)
        self.assertRaises(ValueError, inst.resolve, 'test_asset.py')

    def test_resolve_relspec_caller_package(self):
        from pyramid.path import CALLER_PACKAGE, PkgResourcesAssetDescriptor

        inst = self._makeOne(CALLER_PACKAGE)
        r = inst.resolve('test_asset.py')
        self.assertEqual(r.__class__, PkgResourcesAssetDescriptor)
        self.assertTrue(r.exists())


class TestDottedNameResolver(unittest.TestCase):
    def _makeOne(self, package=None):
        from pyramid.resolver import DottedNameResolver

        return DottedNameResolver(package)

    def config_exc(self, func, *arg, **kw):
        try:
            func(*arg, **kw)
        except ValueError as e:
            return e
        else:
            raise AssertionError('Invalid not raised')  # pragma: no cover

    def test_zope_dottedname_style_resolve_builtin(self):
        typ = self._makeOne()
        result = typ._zope_dottedname_style('builtins.str', None)
        self.assertEqual(result, str)

    def test_zope_dottedname_style_resolve_absolute(self):
        typ = self._makeOne()
        result = typ._zope_dottedname_style(
            'tests.test_resolver.TestDottedNameResolver', None
        )
        self.assertEqual(result, self.__class__)

    def test_zope_dottedname_style_irrresolveable_absolute(self):
        typ = self._makeOne()
        self.assertRaises(
            ImportError,
            typ._zope_dottedname_style,
            'pyramid.test_resolver.nonexisting_name',
            None,
        )

    def test__zope_dottedname_style_resolve_relative(self):
        import tests

        typ = self._makeOne()
        result = typ._zope_dottedname_style(
            '.test_resolver.TestDottedNameResolver', tests
        )
        self.assertEqual(result, self.__class__)

    def test__zope_dottedname_style_resolve_relative_leading_dots(self):
        import tests.test_resolver

        typ = self._makeOne()
        result = typ._zope_dottedname_style(
            '..tests.test_resolver.TestDottedNameResolver', tests
        )
        self.assertEqual(result, self.__class__)

    def test__zope_dottedname_style_resolve_relative_is_dot(self):
        import tests

        typ = self._makeOne()
        result = typ._zope_dottedname_style('.', tests)
        self.assertEqual(result, tests)

    def test__zope_dottedname_style_irresolveable_relative_is_dot(self):
        typ = self._makeOne()
        e = self.config_exc(typ._zope_dottedname_style, '.', None)
        self.assertEqual(
            e.args[0], "relative name '.' irresolveable without package"
        )

    def test_zope_dottedname_style_resolve_relative_nocurrentpackage(self):
        typ = self._makeOne()
        e = self.config_exc(typ._zope_dottedname_style, '.whatever', None)
        self.assertEqual(
            e.args[0],
            "relative name '.whatever' irresolveable without package",
        )

    def test_zope_dottedname_style_irrresolveable_relative(self):
        import tests

        typ = self._makeOne()
        self.assertRaises(
            ImportError, typ._zope_dottedname_style, '.notexisting', tests
        )

    def test__zope_dottedname_style_resolveable_relative(self):
        import tests

        typ = self._makeOne()
        result = typ._zope_dottedname_style('.', tests)
        self.assertEqual(result, tests)

    def test__zope_dottedname_style_irresolveable_absolute(self):
        typ = self._makeOne()
        self.assertRaises(
            ImportError, typ._zope_dottedname_style, 'pyramid.fudge.bar', None
        )

    def test__zope_dottedname_style_resolveable_absolute(self):
        typ = self._makeOne()
        result = typ._zope_dottedname_style(
            'tests.test_resolver.TestDottedNameResolver', None
        )
        self.assertEqual(result, self.__class__)

    def test__pkg_resources_style_resolve_absolute(self):
        typ = self._makeOne()
        result = typ._pkg_resources_style(
            'tests.test_resolver:TestDottedNameResolver', None
        )
        self.assertEqual(result, self.__class__)

    def test__pkg_resources_style_irrresolveable_absolute(self):
        typ = self._makeOne()
        self.assertRaises(
            ImportError, typ._pkg_resources_style, 'tests:nonexisting', None
        )

    def test__pkg_resources_style_resolve_relative(self):
        import tests

        typ = self._makeOne()
        result = typ._pkg_resources_style(
            '.test_resolver:TestDottedNameResolver', tests
        )
        self.assertEqual(result, self.__class__)

    def test__pkg_resources_style_resolve_relative_is_dot(self):
        import tests

        typ = self._makeOne()
        result = typ._pkg_resources_style('.', tests)
        self.assertEqual(result, tests)

    def test__pkg_resources_style_resolve_relative_nocurrentpackage(self):
        typ = self._makeOne()
        self.assertRaises(
            ValueError, typ._pkg_resources_style, '.whatever', None
        )

    def test__pkg_resources_style_irrresolveable_relative(self):
        import pyramid

        typ = self._makeOne()
        self.assertRaises(
            ImportError, typ._pkg_resources_style, ':notexisting', pyramid
        )

    def test_resolve_not_a_string(self):
        typ = self._makeOne()
        e = self.config_exc(typ.resolve, None)
        self.assertEqual(e.args[0], 'None is not a string')

    def test_resolve_using_pkgresources_style(self):
        typ = self._makeOne()
        result = typ.resolve('tests.test_resolver:TestDottedNameResolver')
        self.assertEqual(result, self.__class__)

    def test_resolve_using_zope_dottedname_style(self):
        typ = self._makeOne()
        result = typ.resolve('tests.test_resolver:TestDottedNameResolver')
        self.assertEqual(result, self.__class__)

    def test_resolve_missing_raises(self):
        typ = self._makeOne()
        self.assertRaises(ImportError, typ.resolve, 'cant.be.found')

    def test_resolve_caller_package(self):
        from pyramid.path import CALLER_PACKAGE

        typ = self._makeOne(CALLER_PACKAGE)
        self.assertEqual(
            typ.resolve('.test_resolver.TestDottedNameResolver'),
            self.__class__,
        )

    def test_maybe_resolve_caller_package(self):
        from pyramid.path import CALLER_PACKAGE

        typ = self._makeOne(CALLER_PACKAGE)
        self.assertEqual(
            typ.maybe_resolve('.test_resolver.TestDottedNameResolver'),
            self.__class__,
        )

    def test_ctor_string_module_resolveable(self):
        import tests

        typ = self._makeOne('tests.test_resolver')
        self.assertEqual(typ.package, tests)

    def test_ctor_string_package_resolveable(self):
        import tests

        typ = self._makeOne('tests')
        self.assertEqual(typ.package, tests)

    def test_ctor_string_irresolveable(self):
        self.assertRaises(ValueError, self._makeOne, 'cant.be.found')

    def test_ctor_module(self):
        import tests

        from . import test_resolver

        typ = self._makeOne(test_resolver)
        self.assertEqual(typ.package, tests)

    def test_ctor_package(self):
        import tests

        typ = self._makeOne(tests)
        self.assertEqual(typ.package, tests)

    def test_ctor_None(self):
        typ = self._makeOne(None)
        self.assertEqual(typ.package, None)
