import os
import sys

def caller_path(path, level=2, package_globals=None): # package_globals==testing
    if not os.path.isabs(path):

        if package_globals is None:
            package_globals = sys._getframe(level).f_globals

        if '__bfg_abspath__' in package_globals:
            return os.path.join(package_globals['__bfg_abspath__'], path)

        # computing the abspath is actually kinda expensive so we
        # memoize the result
        package_name = package_globals['__name__']
        package = sys.modules[package_name]
        prefix = package_path(package)
        try:
            package_globals['__bfg_abspath__'] = prefix
        except:
            pass
        path = os.path.join(prefix, path)
    return path

def package_path(package):
    return os.path.abspath(os.path.dirname(package.__file__))

