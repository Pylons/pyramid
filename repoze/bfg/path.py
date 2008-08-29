import os
import sys

def caller_path(path, level=2):
    if not os.path.isabs(path):
        package_globals = sys._getframe(level).f_globals
        package_name = package_globals['__name__']
        package = sys.modules[package_name]
        prefix = package_path(package)
        path = os.path.join(prefix, path)
    return path
    return os.path.normpath(path)

def package_path(package):
    return os.path.abspath(os.path.dirname(package.__file__))

