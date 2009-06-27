import os
import sys
import pkg_resources

def caller_path(path, level=2):
    """ Return an absolute path """
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
