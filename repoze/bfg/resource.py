import os
import pkg_resources

from zope.interface import implements

from repoze.bfg.interfaces import IPackageOverrides

from repoze.bfg.path import package_path
from repoze.bfg.path import package_name
from repoze.bfg.threadlocal import get_current_registry

class OverrideProvider(pkg_resources.DefaultProvider):
    def __init__(self, module):
        pkg_resources.DefaultProvider.__init__(self, module)
        self.module_name = module.__name__

    def _get_overrides(self):
        reg = get_current_registry()
        overrides = reg.queryUtility(IPackageOverrides, self.module_name)
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

    def has_resource(self, resource_name):
        overrides = self._get_overrides()
        if overrides is not None:
            result = overrides.has_resource(resource_name)
            if result is not None:
                return result
        return pkg_resources.DefaultProvider.has_resource(
            self, resource_name)

    def resource_isdir(self, resource_name):
        overrides = self._get_overrides()
        if overrides is not None:
            result = overrides.isdir(resource_name)
            if result is not None:
                return result
        return pkg_resources.DefaultProvider.resource_isdir(
            self, resource_name)

    def resource_listdir(self, resource_name):
        overrides = self._get_overrides()
        if overrides is not None:
            result = overrides.listdir(resource_name)
            if result is not None:
                return result
        return pkg_resources.DefaultProvider.resource_listdir(
            self, resource_name)
        
class PackageOverrides:
    implements(IPackageOverrides)
    # pkg_resources arg in kw args below for testing
    def __init__(self, package, pkg_resources=pkg_resources):
        if hasattr(package, '__loader__') and not isinstance(package.__loader__,
                                                             self.__class__):
            raise TypeError('Package %s already has a non-%s __loader__ '
                            '(probably a module in a zipped egg)' %
                            (package, self.__class__))
        # We register ourselves as a __loader__ *only* to support the
        # setuptools _find_adapter adapter lookup; this class doesn't
        # actually support the PEP 302 loader "API".  This is
        # excusable due to the following statement in the spec:
        # ... Loader objects are not
        # required to offer any useful functionality (any such functionality,
        # such as the zipimport get_data() method mentioned above, is
        # optional)...
        # A __loader__ attribute is basically metadata, and setuptools
        # uses it as such.
        package.__loader__ = self 
        # we call register_loader_type for every instantiation of this
        # class; that's OK, it's idempotent to do it more than once.
        pkg_resources.register_loader_type(self.__class__, OverrideProvider)
        self.overrides = []
        self.overridden_package_name = package.__name__

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

    def has_resource(self, resource_name):
        for package, rname in self.search_path(resource_name):
            if pkg_resources.resource_exists(package, rname):
                return True

    def isdir(self, resource_name):
        for package, rname in self.search_path(resource_name):
            if pkg_resources.resource_exists(package, rname):
                return pkg_resources.resource_isdir(package, rname)

    def listdir(self, resource_name):
        for package, rname in self.search_path(resource_name):
            if pkg_resources.resource_exists(package, rname):
                return pkg_resources.resource_listdir(package, rname)
    

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

def resolve_resource_spec(spec, pname='__main__'):
    if os.path.isabs(spec):
        return None, spec
    filename = spec
    if ':' in spec:
        pname, filename = spec.split(':', 1)
    elif pname is None:
        pname, filename = None, spec
    return pname, filename

def resource_spec_from_abspath(abspath, package):
    """ Try to convert an absolute path to a resource in a package to
    a resource specification if possible; otherwise return the
    absolute path.  """
    if getattr(package, '__name__', None) == '__main__':
        return abspath
    pp = package_path(package) + os.path.sep
    if abspath.startswith(pp):
        relpath = abspath[len(pp):]
        return '%s:%s' % (package_name(package),
                          relpath.replace(os.path.sep, '/'))
    return abspath
            
    
