import os
import pkg_resources
import sys

def caller_path(path, level=2):
    if not os.path.isabs(path):
        module = caller_module(level+1)
        prefix = package_path(module)
        path = os.path.join(prefix, path)
    return path

def caller_module(level=2):
    module_globals = sys._getframe(level).f_globals
    module_name = module_globals['__name__']
    module = sys.modules[module_name]
    return module

def package_name(pkg_or_module):
    """ If this function is passed a module, return the dotted Python
    package name of the package in which the module lives.  If this
    function is passed a package, return the dotted Python package
    name of the package itself."""
    if pkg_or_module is None:
        return '__main__'
    pkg_filename = pkg_or_module.__file__
    pkg_name = pkg_or_module.__name__
    splitted = os.path.split(pkg_filename)
    if splitted[-1] in ('__init__.py', '__init__.pyc', '__init__.pyo'):
        # it's a package
        return pkg_name
    return pkg_name.rsplit('.', 1)[0]

def caller_package(level=2, caller_module=caller_module):
    # caller_module in arglist for tests
    module = caller_module(level+1)
    if '__init__.py' in getattr(module, '__file__', ''): # empty at >>>
        # Module is a package
        return module
    # Go up one level to get package
    package_name = module.__name__.rsplit('.', 1)[0]
    return sys.modules[package_name]

def package_path(package):
    # computing the abspath is actually kinda expensive so we memoize
    # the result
    prefix = getattr(package, '__bfg_abspath__', None)
    if prefix is None:
        prefix = pkg_resources.resource_filename(package.__name__, '')
        # pkg_resources doesn't care whether we feed it a package
        # name or a module name within the package, the result
        # will be the same: a directory name to the package itself
        try:
            package.__bfg_abspath__ = prefix
        except:
            # this is only an optimization, ignore any error
            pass
    return prefix

