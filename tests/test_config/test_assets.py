import os.path
import unittest

# we use this folder
here = os.path.dirname(os.path.abspath(__file__))


class TestAssetsConfiguratorMixin(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.config import Configurator

        config = Configurator(*arg, **kw)
        return config

    def test_override_asset_samename(self):
        from pyramid.exceptions import ConfigurationError

        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.override_asset, 'a', 'a')

    def test_override_asset_directory_with_file(self):
        from pyramid.exceptions import ConfigurationError

        config = self._makeOne()
        self.assertRaises(
            ConfigurationError,
            config.override_asset,
            'a:foo/',
            'tests.test_config.pkgs.asset:foo.pt',
        )

    def test_override_asset_file_with_directory(self):
        from pyramid.exceptions import ConfigurationError

        config = self._makeOne()
        self.assertRaises(
            ConfigurationError,
            config.override_asset,
            'a:foo.pt',
            'tests.test_config.pkgs.asset:templates/',
        )

    def test_override_asset_file_with_package(self):
        from pyramid.exceptions import ConfigurationError

        config = self._makeOne()
        self.assertRaises(
            ConfigurationError,
            config.override_asset,
            'a:foo.pt',
            'tests.test_config.pkgs.asset',
        )

    def test_override_asset_file_with_file(self):
        from pyramid.config.assets import PackageAssetSource

        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'tests.test_config.pkgs.asset:templates/foo.pt',
            'tests.test_config.pkgs.asset.subpackage:templates/bar.pt',
            _override=override,
        )
        from tests.test_config.pkgs import asset
        from tests.test_config.pkgs.asset import subpackage

        self.assertEqual(override.package, asset)
        self.assertEqual(override.path, 'templates/foo.pt')
        source = override.source
        self.assertTrue(isinstance(source, PackageAssetSource))
        self.assertEqual(source.package, subpackage)
        self.assertEqual(source.prefix, 'templates/bar.pt')

        resource_name = ''
        expected = os.path.join(
            here, 'pkgs', 'asset', 'subpackage', 'templates', 'bar.pt'
        )
        self.assertEqual(override.source.get_filename(resource_name), expected)

    def test_override_asset_package_with_package(self):
        from pyramid.config.assets import PackageAssetSource

        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'tests.test_config.pkgs.asset',
            'tests.test_config.pkgs.asset.subpackage',
            _override=override,
        )
        from tests.test_config.pkgs import asset
        from tests.test_config.pkgs.asset import subpackage

        self.assertEqual(override.package, asset)
        self.assertEqual(override.path, '')
        source = override.source
        self.assertTrue(isinstance(source, PackageAssetSource))
        self.assertEqual(source.package, subpackage)
        self.assertEqual(source.prefix, '')

        resource_name = 'templates/bar.pt'
        expected = os.path.join(
            here, 'pkgs', 'asset', 'subpackage', 'templates', 'bar.pt'
        )
        self.assertEqual(override.source.get_filename(resource_name), expected)

    def test_override_asset_directory_with_directory(self):
        from pyramid.config.assets import PackageAssetSource

        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'tests.test_config.pkgs.asset:templates/',
            'tests.test_config.pkgs.asset.subpackage:templates/',
            _override=override,
        )
        from tests.test_config.pkgs import asset
        from tests.test_config.pkgs.asset import subpackage

        self.assertEqual(override.package, asset)
        self.assertEqual(override.path, 'templates/')
        source = override.source
        self.assertTrue(isinstance(source, PackageAssetSource))
        self.assertEqual(source.package, subpackage)
        self.assertEqual(source.prefix, 'templates/')

        resource_name = 'bar.pt'
        expected = os.path.join(
            here, 'pkgs', 'asset', 'subpackage', 'templates', 'bar.pt'
        )
        self.assertEqual(override.source.get_filename(resource_name), expected)

    def test_override_asset_directory_with_package(self):
        from pyramid.config.assets import PackageAssetSource

        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'tests.test_config.pkgs.asset:templates/',
            'tests.test_config.pkgs.asset.subpackage',
            _override=override,
        )
        from tests.test_config.pkgs import asset
        from tests.test_config.pkgs.asset import subpackage

        self.assertEqual(override.package, asset)
        self.assertEqual(override.path, 'templates/')
        source = override.source
        self.assertTrue(isinstance(source, PackageAssetSource))
        self.assertEqual(source.package, subpackage)
        self.assertEqual(source.prefix, '')

        resource_name = 'templates/bar.pt'
        expected = os.path.join(
            here, 'pkgs', 'asset', 'subpackage', 'templates', 'bar.pt'
        )
        self.assertEqual(override.source.get_filename(resource_name), expected)

    def test_override_asset_package_with_directory(self):
        from pyramid.config.assets import PackageAssetSource

        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'tests.test_config.pkgs.asset',
            'tests.test_config.pkgs.asset.subpackage:templates/',
            _override=override,
        )
        from tests.test_config.pkgs import asset
        from tests.test_config.pkgs.asset import subpackage

        self.assertEqual(override.package, asset)
        self.assertEqual(override.path, '')
        source = override.source
        self.assertTrue(isinstance(source, PackageAssetSource))
        self.assertEqual(source.package, subpackage)
        self.assertEqual(source.prefix, 'templates/')

        resource_name = 'bar.pt'
        expected = os.path.join(
            here, 'pkgs', 'asset', 'subpackage', 'templates', 'bar.pt'
        )
        self.assertEqual(override.source.get_filename(resource_name), expected)

    def test_override_asset_directory_with_absfile(self):
        from pyramid.exceptions import ConfigurationError

        config = self._makeOne()
        self.assertRaises(
            ConfigurationError,
            config.override_asset,
            'a:foo/',
            os.path.join(here, 'pkgs', 'asset', 'foo.pt'),
        )

    def test_override_asset_file_with_absdirectory(self):
        from pyramid.exceptions import ConfigurationError

        config = self._makeOne()
        abspath = os.path.join(
            here, 'pkgs', 'asset', 'subpackage', 'templates'
        )
        self.assertRaises(
            ConfigurationError, config.override_asset, 'a:foo.pt', abspath
        )

    def test_override_asset_file_with_missing_abspath(self):
        from pyramid.exceptions import ConfigurationError

        config = self._makeOne()
        self.assertRaises(
            ConfigurationError,
            config.override_asset,
            'a:foo.pt',
            os.path.join(here, 'wont_exist'),
        )

    def test_override_asset_file_with_absfile(self):
        from pyramid.config.assets import FSAssetSource

        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        abspath = os.path.join(
            here, 'pkgs', 'asset', 'subpackage', 'templates', 'bar.pt'
        )
        config.override_asset(
            'tests.test_config.pkgs.asset:templates/foo.pt',
            abspath,
            _override=override,
        )
        from tests.test_config.pkgs import asset

        self.assertEqual(override.package, asset)
        self.assertEqual(override.path, 'templates/foo.pt')
        source = override.source
        self.assertTrue(isinstance(source, FSAssetSource))
        self.assertEqual(source.prefix, abspath)

        resource_name = ''
        expected = os.path.join(
            here, 'pkgs', 'asset', 'subpackage', 'templates', 'bar.pt'
        )
        self.assertEqual(override.source.get_filename(resource_name), expected)

    def test_override_asset_directory_with_absdirectory(self):
        from pyramid.config.assets import FSAssetSource

        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        abspath = os.path.join(
            here, 'pkgs', 'asset', 'subpackage', 'templates'
        )
        config.override_asset(
            'tests.test_config.pkgs.asset:templates/',
            abspath,
            _override=override,
        )
        from tests.test_config.pkgs import asset

        self.assertEqual(override.package, asset)
        self.assertEqual(override.path, 'templates/')
        source = override.source
        self.assertTrue(isinstance(source, FSAssetSource))
        self.assertEqual(source.prefix, abspath)

        resource_name = 'bar.pt'
        expected = os.path.join(
            here, 'pkgs', 'asset', 'subpackage', 'templates', 'bar.pt'
        )
        self.assertEqual(override.source.get_filename(resource_name), expected)

    def test_override_asset_package_with_absdirectory(self):
        from pyramid.config.assets import FSAssetSource

        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        abspath = os.path.join(
            here, 'pkgs', 'asset', 'subpackage', 'templates'
        )
        config.override_asset(
            'tests.test_config.pkgs.asset', abspath, _override=override
        )
        from tests.test_config.pkgs import asset

        self.assertEqual(override.package, asset)
        self.assertEqual(override.path, '')
        source = override.source
        self.assertTrue(isinstance(source, FSAssetSource))
        self.assertEqual(source.prefix, abspath)

        resource_name = 'bar.pt'
        expected = os.path.join(
            here, 'pkgs', 'asset', 'subpackage', 'templates', 'bar.pt'
        )
        self.assertEqual(override.source.get_filename(resource_name), expected)

    def test__override_not_yet_registered(self):
        from pyramid.interfaces import IPackageOverrides

        package = DummyPackage('package')
        source = DummyAssetSource()
        config = self._makeOne()
        config._override(
            package, 'path', source, PackageOverrides=DummyPackageOverrides
        )
        overrides = config.registry.queryUtility(
            IPackageOverrides, name='package'
        )
        self.assertEqual(overrides.inserted, [('path', source)])
        self.assertEqual(overrides.package, package)

    def test__override_already_registered(self):
        from pyramid.interfaces import IPackageOverrides

        package = DummyPackage('package')
        source = DummyAssetSource()
        overrides = DummyPackageOverrides(package)
        config = self._makeOne()
        config.registry.registerUtility(
            overrides, IPackageOverrides, name='package'
        )
        config._override(
            package, 'path', source, PackageOverrides=DummyPackageOverrides
        )
        self.assertEqual(overrides.inserted, [('path', source)])
        self.assertEqual(overrides.package, package)


class TestPackageOverrides(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.config.assets import PackageOverrides

        return PackageOverrides

    def _makeOne(self, package=None):
        if package is None:
            package = DummyPackage('package')
        klass = self._getTargetClass()
        return klass(package)

    def test_class_conforms_to_IPackageOverrides(self):
        from zope.interface.verify import verifyClass

        from pyramid.interfaces import IPackageOverrides

        verifyClass(IPackageOverrides, self._getTargetClass())

    def test_instance_conforms_to_IPackageOverrides(self):
        from zope.interface.verify import verifyObject

        from pyramid.interfaces import IPackageOverrides

        verifyObject(IPackageOverrides, self._makeOne())

    def test_ctor_sets_local_state(self):
        package = DummyPackage('package')
        po = self._makeOne(package)
        self.assertEqual(po.overrides, [])
        self.assertEqual(po.overridden_package_name, 'package')

    def test_insert_directory(self):
        from pyramid.config.assets import DirectoryOverride

        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = [None]
        po.insert('foo/', DummyAssetSource())
        self.assertEqual(len(po.overrides), 2)
        override = po.overrides[0]
        self.assertEqual(override.__class__, DirectoryOverride)

    def test_insert_file(self):
        from pyramid.config.assets import FileOverride

        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = [None]
        po.insert('foo.pt', DummyAssetSource())
        self.assertEqual(len(po.overrides), 2)
        override = po.overrides[0]
        self.assertEqual(override.__class__, FileOverride)

    def test_insert_emptystring(self):
        # XXX is this a valid case for a directory?
        from pyramid.config.assets import DirectoryOverride

        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = [None]
        source = DummyAssetSource()
        po.insert('', source)
        self.assertEqual(len(po.overrides), 2)
        override = po.overrides[0]
        self.assertEqual(override.__class__, DirectoryOverride)

    def test_filtered_sources(self):
        overrides = [DummyOverride(None), DummyOverride('foo')]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(list(po.filtered_sources('whatever')), ['foo'])

    def test_get_spec(self):
        source = DummyAssetSource(spec='test:foo.pt')
        overrides = [DummyOverride(None), DummyOverride((source, ''))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        result = po.get_spec('whatever')
        self.assertEqual(result, 'test:foo.pt')
        self.assertEqual(source.resource_name, '')

    def test_get_spec_file_doesnt_exist(self):
        source = DummyAssetSource(spec=None)
        overrides = [
            DummyOverride(None),
            DummyOverride((source, 'wont_exist')),
        ]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(po.get_spec('whatever'), None)
        self.assertEqual(source.resource_name, 'wont_exist')

    def test_get_filename(self):
        source = DummyAssetSource(filename='foo.pt')
        overrides = [DummyOverride(None), DummyOverride((source, ''))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        result = po.get_filename('whatever')
        self.assertEqual(result, 'foo.pt')
        self.assertEqual(source.resource_name, '')

    def test_get_filename_file_doesnt_exist(self):
        source = DummyAssetSource(filename=None)
        overrides = [
            DummyOverride(None),
            DummyOverride((source, 'wont_exist')),
        ]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(po.get_filename('whatever'), None)
        self.assertEqual(source.resource_name, 'wont_exist')

    def test_get_stream(self):
        source = DummyAssetSource(stream='a stream?')
        overrides = [DummyOverride(None), DummyOverride((source, 'foo.pt'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(po.get_stream('whatever'), 'a stream?')
        self.assertEqual(source.resource_name, 'foo.pt')

    def test_get_stream_file_doesnt_exist(self):
        source = DummyAssetSource(stream=None)
        overrides = [
            DummyOverride(None),
            DummyOverride((source, 'wont_exist')),
        ]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(po.get_stream('whatever'), None)
        self.assertEqual(source.resource_name, 'wont_exist')

    def test_get_string(self):
        source = DummyAssetSource(string='a string')
        overrides = [DummyOverride(None), DummyOverride((source, 'foo.pt'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(po.get_string('whatever'), 'a string')
        self.assertEqual(source.resource_name, 'foo.pt')

    def test_get_string_file_doesnt_exist(self):
        source = DummyAssetSource(string=None)
        overrides = [
            DummyOverride(None),
            DummyOverride((source, 'wont_exist')),
        ]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(po.get_string('whatever'), None)
        self.assertEqual(source.resource_name, 'wont_exist')

    def test_has_resource(self):
        source = DummyAssetSource(exists=True)
        overrides = [DummyOverride(None), DummyOverride((source, 'foo.pt'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(po.has_resource('whatever'), True)
        self.assertEqual(source.resource_name, 'foo.pt')

    def test_has_resource_file_doesnt_exist(self):
        source = DummyAssetSource(exists=None)
        overrides = [
            DummyOverride(None),
            DummyOverride((source, 'wont_exist')),
        ]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(po.has_resource('whatever'), None)
        self.assertEqual(source.resource_name, 'wont_exist')

    def test_isdir_false(self):
        source = DummyAssetSource(isdir=False)
        overrides = [DummyOverride(None), DummyOverride((source, 'foo.pt'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(po.isdir('whatever'), False)
        self.assertEqual(source.resource_name, 'foo.pt')

    def test_isdir_true(self):
        source = DummyAssetSource(isdir=True)
        overrides = [DummyOverride(None), DummyOverride((source, 'foo.pt'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(po.isdir('whatever'), True)
        self.assertEqual(source.resource_name, 'foo.pt')

    def test_isdir_doesnt_exist(self):
        source = DummyAssetSource(isdir=None)
        overrides = [
            DummyOverride(None),
            DummyOverride((source, 'wont_exist')),
        ]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(po.isdir('whatever'), None)
        self.assertEqual(source.resource_name, 'wont_exist')

    def test_listdir(self):
        source = DummyAssetSource(listdir=True)
        overrides = [DummyOverride(None), DummyOverride((source, 'foo.pt'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(po.listdir('whatever'), True)
        self.assertEqual(source.resource_name, 'foo.pt')

    def test_listdir_doesnt_exist(self):
        source = DummyAssetSource(listdir=None)
        overrides = [
            DummyOverride(None),
            DummyOverride((source, 'wont_exist')),
        ]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides = overrides
        self.assertEqual(po.listdir('whatever'), None)
        self.assertEqual(source.resource_name, 'wont_exist')


class AssetSourceIntegrationTests:
    def test_get_filename(self):
        source = self._makeOne('')
        self.assertEqual(
            source.get_filename('test_assets.py'),
            os.path.join(here, 'test_assets.py'),
        )

    def test_get_filename_with_prefix(self):
        source = self._makeOne('test_assets.py')
        self.assertEqual(
            source.get_filename(''), os.path.join(here, 'test_assets.py')
        )

    def test_get_filename_file_doesnt_exist(self):
        source = self._makeOne('')
        self.assertEqual(source.get_filename('wont_exist'), None)

    def test_get_stream(self):
        source = self._makeOne('')
        with source.get_stream('test_assets.py') as stream:
            _assertBody(stream.read(), os.path.join(here, 'test_assets.py'))

    def test_get_stream_with_prefix(self):
        source = self._makeOne('test_assets.py')
        with source.get_stream('') as stream:
            _assertBody(stream.read(), os.path.join(here, 'test_assets.py'))

    def test_get_stream_file_doesnt_exist(self):
        source = self._makeOne('')
        self.assertEqual(source.get_stream('wont_exist'), None)

    def test_get_string(self):
        source = self._makeOne('')
        _assertBody(
            source.get_string('test_assets.py'),
            os.path.join(here, 'test_assets.py'),
        )

    def test_get_string_with_prefix(self):
        source = self._makeOne('test_assets.py')
        _assertBody(
            source.get_string(''), os.path.join(here, 'test_assets.py')
        )

    def test_get_string_file_doesnt_exist(self):
        source = self._makeOne('')
        self.assertEqual(source.get_string('wont_exist'), None)

    def test_exists(self):
        source = self._makeOne('')
        self.assertEqual(source.exists('test_assets.py'), True)

    def test_exists_with_prefix(self):
        source = self._makeOne('test_assets.py')
        self.assertEqual(source.exists(''), True)

    def test_exists_file_doesnt_exist(self):
        source = self._makeOne('')
        self.assertEqual(source.exists('wont_exist'), None)

    def test_isdir_false(self):
        source = self._makeOne('')
        self.assertEqual(source.isdir('test_assets.py'), False)

    def test_isdir_true(self):
        source = self._makeOne('')
        self.assertEqual(source.isdir('files'), True)

    def test_isdir_doesnt_exist(self):
        source = self._makeOne('')
        self.assertEqual(source.isdir('wont_exist'), None)

    def test_listdir(self):
        source = self._makeOne('')
        self.assertTrue(source.listdir('files'))

    def test_listdir_doesnt_exist(self):
        source = self._makeOne('')
        self.assertEqual(source.listdir('wont_exist'), None)


class TestPackageAssetSource(AssetSourceIntegrationTests, unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.config.assets import PackageAssetSource

        return PackageAssetSource

    def _makeOne(self, prefix, package='tests.test_config'):
        klass = self._getTargetClass()
        return klass(package, prefix)

    def test_get_spec(self):
        source = self._makeOne('')
        self.assertEqual(
            source.get_spec('test_assets.py'),
            'tests.test_config:test_assets.py',
        )

    def test_get_spec_with_prefix(self):
        source = self._makeOne('test_assets.py')
        self.assertEqual(
            source.get_spec(''),
            'tests.test_config:test_assets.py',
        )

    def test_get_spec_file_doesnt_exist(self):
        source = self._makeOne('')
        self.assertIsNone(source.get_spec('wont_exist'))


class TestFSAssetSource(AssetSourceIntegrationTests, unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.config.assets import FSAssetSource

        return FSAssetSource

    def _makeOne(self, prefix, base_prefix=here):
        klass = self._getTargetClass()
        return klass(os.path.join(base_prefix, prefix))

    def test_get_spec(self):
        source = self._makeOne('')
        self.assertEqual(
            source.get_spec('test_assets.py'),
            os.path.join(here, 'test_assets.py'),
        )

    def test_get_spec_with_prefix(self):
        source = self._makeOne('test_assets.py')
        self.assertEqual(
            source.get_spec(''), os.path.join(here, 'test_assets.py')
        )

    def test_get_spec_file_doesnt_exist(self):
        source = self._makeOne('')
        self.assertEqual(source.get_spec('wont_exist'), None)


class TestDirectoryOverride(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.config.assets import DirectoryOverride

        return DirectoryOverride

    def _makeOne(self, path, source):
        klass = self._getTargetClass()
        return klass(path, source)

    def test_it_match(self):
        source = DummyAssetSource()
        o = self._makeOne('foo/', source)
        result = o('foo/something.pt')
        self.assertEqual(result, (source, 'something.pt'))

    def test_it_no_match(self):
        source = DummyAssetSource()
        o = self._makeOne('foo/', source)
        result = o('baz/notfound.pt')
        self.assertEqual(result, None)


class TestFileOverride(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.config.assets import FileOverride

        return FileOverride

    def _makeOne(self, path, source):
        klass = self._getTargetClass()
        return klass(path, source)

    def test_it_match(self):
        source = DummyAssetSource()
        o = self._makeOne('foo.pt', source)
        result = o('foo.pt')
        self.assertEqual(result, (source, ''))

    def test_it_no_match(self):
        source = DummyAssetSource()
        o = self._makeOne('foo.pt', source)
        result = o('notfound.pt')
        self.assertEqual(result, None)


class DummyOverride:
    def __init__(self, result):
        self.result = result

    def __call__(self, resource_name):
        return self.result


class DummyPackageOverrides:
    def __init__(self, package):
        self.package = package
        self.inserted = []

    def insert(self, path, source):
        self.inserted.append((path, source))


class DummyPackage:
    def __init__(self, name):
        self.__name__ = name


class DummyAssetSource:
    def __init__(self, **kw):
        self.kw = kw

    def get_spec(self, resource_name):
        self.resource_name = resource_name
        return self.kw['spec']

    def get_filename(self, resource_name):
        self.resource_name = resource_name
        return self.kw['filename']

    def get_stream(self, resource_name):
        self.resource_name = resource_name
        return self.kw['stream']

    def get_string(self, resource_name):
        self.resource_name = resource_name
        return self.kw['string']

    def exists(self, resource_name):
        self.resource_name = resource_name
        return self.kw['exists']

    def isdir(self, resource_name):
        self.resource_name = resource_name
        return self.kw['isdir']

    def listdir(self, resource_name):
        self.resource_name = resource_name
        return self.kw['listdir']


class DummyUnderOverride:
    def __call__(self, package, path, source, _info=''):
        self.package = package
        self.path = path
        self.source = source


def read_(src):
    with open(src, 'rb') as f:
        contents = f.read()
    return contents


def _assertBody(body, filename):
    # strip both \n and \r for windows
    body = body.replace(b'\r', b'')
    body = body.replace(b'\n', b'')
    data = read_(filename)
    data = data.replace(b'\r', b'')
    data = data.replace(b'\n', b'')
    assert body == data
