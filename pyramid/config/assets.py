import sys

from pyramid.interfaces import IPackageOverrides

from pyramid.asset import PackageOverrides
from pyramid.exceptions import ConfigurationError

from pyramid.config.util import action_method

class AssetsConfiguratorMixin(object):
    def _override(self, package, path, override_package, override_prefix,
                  PackageOverrides=PackageOverrides):
        pkg_name = package.__name__
        override_pkg_name = override_package.__name__
        override = self.registry.queryUtility(IPackageOverrides, name=pkg_name)
        if override is None:
            override = PackageOverrides(package)
            self.registry.registerUtility(override, IPackageOverrides,
                                          name=pkg_name)
        override.insert(path, override_pkg_name, override_prefix)

    @action_method
    def override_asset(self, to_override, override_with, _override=None):
        """ Add a :app:`Pyramid` asset override to the current
        configuration state.

        ``to_override`` is a :term:`asset specification` to the
        asset being overridden.

        ``override_with`` is a :term:`asset specification` to the
        asset that is performing the override.

        See :ref:`assets_chapter` for more
        information about asset overrides."""
        if to_override == override_with:
            raise ConfigurationError('You cannot override an asset with itself')

        package = to_override
        path = ''
        if ':' in to_override:
            package, path = to_override.split(':', 1)

        override_package = override_with
        override_prefix = ''
        if ':' in override_with:
            override_package, override_prefix = override_with.split(':', 1)

        # *_isdir = override is package or directory
        overridden_isdir = path=='' or path.endswith('/') 
        override_isdir = override_prefix=='' or override_prefix.endswith('/')

        if overridden_isdir and (not override_isdir):
            raise ConfigurationError(
                'A directory cannot be overridden with a file (put a '
                'slash at the end of override_with if necessary)')

        if (not overridden_isdir) and override_isdir:
            raise ConfigurationError(
                'A file cannot be overridden with a directory (put a '
                'slash at the end of to_override if necessary)')

        override = _override or self._override # test jig

        def register():
            __import__(package)
            __import__(override_package)
            from_package = sys.modules[package]
            to_package = sys.modules[override_package]
            override(from_package, path, to_package, override_prefix)
        self.action(None, register)

    override_resource = override_asset # bw compat

