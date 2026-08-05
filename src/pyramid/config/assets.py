import importlib.resources
import os
import sys
from zope.interface import implementer

from pyramid.config.actions import action_method
from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import PHASE1_CONFIG, IPackageOverrides
from pyramid.path import ref_filename


@implementer(IPackageOverrides)
class PackageOverrides:
    def __init__(self, package):
        self.overrides = []
        self.overridden_package_name = package.__name__

    def insert(self, path, source):
        if not path or path.endswith('/'):
            override = DirectoryOverride(path, source)
        else:
            override = FileOverride(path, source)
        self.overrides.insert(0, override)
        return override

    def filtered_sources(self, resource_name):
        for override in self.overrides:
            o = override(resource_name)
            if o is not None:
                yield o

    def get_spec(self, resource_name):
        for source, path in self.filtered_sources(resource_name):
            result = source.get_spec(path)
            if result is not None:
                return result

    def get_filename(self, resource_name):
        for source, path in self.filtered_sources(resource_name):
            result = source.get_filename(path)
            if result is not None:
                return result

    def get_stream(self, resource_name):
        for source, path in self.filtered_sources(resource_name):
            result = source.get_stream(path)
            if result is not None:
                return result

    def get_string(self, resource_name):
        for source, path in self.filtered_sources(resource_name):
            result = source.get_string(path)
            if result is not None:
                return result

    def has_resource(self, resource_name):
        for source, path in self.filtered_sources(resource_name):
            if source.exists(path):
                return True

    def isdir(self, resource_name):
        for source, path in self.filtered_sources(resource_name):
            result = source.isdir(path)
            if result is not None:
                return result

    def listdir(self, resource_name):
        for source, path in self.filtered_sources(resource_name):
            result = source.listdir(path)
            if result is not None:
                return result


class DirectoryOverride:
    def __init__(self, path, source):
        self.path = path
        self.pathlen = len(self.path)
        self.source = source

    def __call__(self, resource_name):
        if resource_name.startswith(self.path):
            new_path = resource_name[self.pathlen :]
            return self.source, new_path


class FileOverride:
    def __init__(self, path, source):
        self.path = path
        self.source = source

    def __call__(self, resource_name):
        if resource_name == self.path:
            return self.source, ''


class PackageAssetSource:
    """
    An asset source relative to a package.

    If this asset source is a file, then we expect the ``prefix`` to point
    to the new name of the file, and the incoming ``resource_name`` will be
    the empty string, as returned by the ``FileOverride``.

    """

    def __init__(self, package, prefix):
        self.package = package
        if hasattr(package, '__name__'):
            self.pkg_name = package.__name__
        else:
            self.pkg_name = package
        self.prefix = prefix

    def get_path(self, resource_name):
        return f'{self.prefix}{resource_name}'

    def _ref(self, resource_name):
        path = self.get_path(resource_name)
        return importlib.resources.files(self.pkg_name) / path

    def get_spec(self, resource_name):
        ref = self._ref(resource_name)
        if ref.is_file() or ref.is_dir():
            return f'{self.pkg_name}:{self.get_path(resource_name)}'

    def get_filename(self, resource_name):
        ref = self._ref(resource_name)
        if ref.is_file() or ref.is_dir():
            return ref_filename(ref)

    def get_stream(self, resource_name):
        ref = self._ref(resource_name)
        if ref.is_file() or ref.is_dir():
            return ref.open('rb')

    def get_string(self, resource_name):
        ref = self._ref(resource_name)
        if ref.is_file() or ref.is_dir():
            with ref.open('rb') as fh:
                return fh.read()

    def exists(self, resource_name):
        ref = self._ref(resource_name)
        if ref.is_file() or ref.is_dir():
            return True

    def isdir(self, resource_name):
        ref = self._ref(resource_name)
        if ref.is_file() or ref.is_dir():
            return ref.is_dir()

    def listdir(self, resource_name):
        ref = self._ref(resource_name)
        if ref.is_file() or ref.is_dir():
            return [x.name for x in ref.iterdir()]


class FSAssetSource:
    """
    An asset source relative to a path in the filesystem.

    """

    def __init__(self, prefix):
        self.prefix = prefix

    def get_path(self, resource_name):
        if resource_name:
            path = os.path.join(self.prefix, resource_name)
        else:
            path = self.prefix
        return path

    def get_spec(self, resource_name):
        return self.get_filename(resource_name)

    def get_filename(self, resource_name):
        path = self.get_path(resource_name)
        if os.path.exists(path):
            return path

    def get_stream(self, resource_name):
        path = self.get_filename(resource_name)
        if path is not None:
            return open(path, 'rb')

    def get_string(self, resource_name):
        stream = self.get_stream(resource_name)
        if stream is not None:
            with stream:
                return stream.read()

    def exists(self, resource_name):
        path = self.get_filename(resource_name)
        if path is not None:
            return True

    def isdir(self, resource_name):
        path = self.get_filename(resource_name)
        if path is not None:
            return os.path.isdir(path)

    def listdir(self, resource_name):
        path = self.get_filename(resource_name)
        if path is not None:
            return os.listdir(path)


class AssetsConfiguratorMixin:
    def _override(
        self, package, path, override_source, PackageOverrides=PackageOverrides
    ):
        pkg_name = package.__name__
        override = self.registry.queryUtility(IPackageOverrides, name=pkg_name)
        if override is None:
            override = PackageOverrides(package)
            self.registry.registerUtility(
                override, IPackageOverrides, name=pkg_name
            )
        override.insert(path, override_source)

    @action_method
    def override_asset(self, to_override, override_with, _override=None):
        """Add a :app:`Pyramid` asset override to the current
        configuration state.

        ``to_override`` is an :term:`asset specification` to the
        asset being overridden.

        ``override_with`` is an :term:`asset specification` to the
        asset that is performing the override. This may also be an absolute
        path.

        See :ref:`assets_chapter` for more
        information about asset overrides."""
        if to_override == override_with:
            raise ConfigurationError(
                'You cannot override an asset with itself'
            )

        package = to_override
        path = ''
        if ':' in to_override:
            package, path = to_override.split(':', 1)

        # *_isdir = override is package or directory
        overridden_isdir = path == '' or path.endswith('/')

        if os.path.isabs(override_with):
            override_source = FSAssetSource(override_with)
            if not os.path.exists(override_with):
                raise ConfigurationError(
                    'Cannot override asset with an absolute path that does '
                    'not exist'
                )
            override_isdir = os.path.isdir(override_with)
            override_package = None
            override_prefix = override_with
        else:
            override_package = override_with
            override_prefix = ''
            if ':' in override_with:
                override_package, override_prefix = override_with.split(':', 1)

            __import__(override_package)
            to_package = sys.modules[override_package]
            override_source = PackageAssetSource(to_package, override_prefix)

            override_isdir = override_prefix == '' or override_with.endswith(
                '/'
            )

        if overridden_isdir and (not override_isdir):
            raise ConfigurationError(
                'A directory cannot be overridden with a file (put a '
                'slash at the end of override_with if necessary)'
            )

        if (not overridden_isdir) and override_isdir:
            raise ConfigurationError(
                'A file cannot be overridden with a directory (put a '
                'slash at the end of to_override if necessary)'
            )

        override = _override or self._override  # test jig

        def register():
            __import__(package)
            from_package = sys.modules[package]
            override(from_package, path, override_source)

        intr = self.introspectable(
            'asset overrides',
            (package, override_package, path, override_prefix),
            f'{to_override} -> {override_with}',
            'asset override',
        )
        intr['to_override'] = to_override
        intr['override_with'] = override_with
        self.action(
            None, register, introspectables=(intr,), order=PHASE1_CONFIG
        )

    override_resource = override_asset  # bw compat
