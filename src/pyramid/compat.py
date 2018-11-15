import platform

WIN = platform.system() == 'Windows'

try:  # pragma: no cover
    import __pypy__

    PYPY = True
except BaseException:  # pragma: no cover
    __pypy__ = None
    PYPY = False
