import pkg_resources
from zope.component import queryUtility
from zope.interface import implements

from repoze.bfg.interfaces import IPackageOverrides

class OverrideProvider(pkg_resources.DefaultProvider):
    def __init__(self, module):
        pkg_resources.DefaultProvider.__init__(self, module)
        self.module_name = module.__name__

    def _get_overrides(self):
        overrides = queryUtility(IPackageOverrides, self.module_name)
        return overrides
    
    def get_resource_filename(self, manager, resource_name):
        """ Return a true filesystem path for resource_name,
        co-ordinating the extraction with manager, if the resource
        must be unpacked to the filesystem.
        """
        overrides = self._get_overrides()
        if overrides is not None:
            filename = overrides.get_filename(resource_name)
            if filename is not None:
                return filename
        return pkg_resources.DefaultProvider.get_resource_filename(
            self, manager, resource_name)
    
    def get_resource_stream(self, manager, resource_name):
        """ Return a readable file-like object for resource_name."""
        overrides = self._get_overrides()
        if overrides is not None:
            stream =  overrides.get_stream(resource_name)
            if stream is not None:
                return stream
        return pkg_resources.DefaultProvider.get_resource_stream(
            self, manager, resource_name)

    def get_resource_string(self, manager, resource_name):
        """ Return a string containing the contents of resource_name."""
        overrides = self._get_overrides()
        if overrides is not None:
            string = overrides.get_string(resource_name)
            if string is not None:
                return string
        return pkg_resources.DefaultProvider.get_resource_string(
            self, manager, resource_name)

class PackageOverrides:
    implements(IPackageOverrides)
    def __init__(self, overridden_package):
        self.overrides = []
        self.overridden_package = overridden_package

    def insert(self, path, package, prefix):
        if not path or path.endswith('/'):
            override = DirectoryOverride(path, package, prefix)
        else:
            override = FileOverride(path, package, prefix)
        self.overrides.insert(0, override)
        return override

    def search_path(self, resource_name):
        for override in self.overrides:
            o = override(resource_name)
            if o is not None:
                package, name = o
                yield package, name

    def get_filename(self, resource_name):
        for package, rname in self.search_path(resource_name):
            if pkg_resources.resource_exists(package, rname):
                return pkg_resources.resource_filename(package, rname)

    def get_stream(self, resource_name):
        for package, rname in self.search_path(resource_name):
            if pkg_resources.resource_exists(package, rname):
                return pkg_resources.resource_stream(package, rname)

    def get_string(self, resource_name):
        for package, rname in self.search_path(resource_name):
            if pkg_resources.resource_exists(package, rname):
                return pkg_resources.resource_string(package, rname)

class DirectoryOverride:
    def __init__(self, path, package, prefix):
        self.path = path
        self.package = package
        self.prefix = prefix
        self.pathlen = len(self.path)

    def __call__(self, resource_name):
        if resource_name.startswith(self.path):
            name = '%s%s' % (self.prefix, resource_name[self.pathlen:])
            return self.package, name

class FileOverride:
    def __init__(self, path, package, prefix):
        self.path = path
        self.package = package
        self.prefix = prefix

    def __call__(self, resource_name):
        if resource_name == self.path:
            return self.package, self.prefix

