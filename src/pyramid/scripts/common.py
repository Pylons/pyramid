import os
import plaster
import sys


def parse_vars(args):
    """
    Given variables like ``['a=b', 'c=d']`` turns it into ``{'a':
    'b', 'c': 'd'}``
    """
    result = {}
    for arg in args:
        if '=' not in arg:
            raise ValueError('Variable assignment %r invalid (no "=")' % arg)
        name, value = arg.split('=', 1)
        result[name] = value
    return result


def get_config_loader(config_uri, *, exit_on_error=False):
    """
    Find a ``plaster.ILoader`` object supporting the "wsgi" protocol.

    By default, any :class:`plaster.exceptions.PlasterError` raised while
    finding the loader propagates to the caller.

    If ``exit_on_error`` is ``True``, then instead of raising, an error
    message is printed to ``stderr`` and the process exits with status ``1``.
    This also happens when ``config_uri`` refers to a file which does not
    exist.  It is intended for use by command-line scripts.

    """
    try:
        loader = plaster.get_loader(config_uri, protocols=['wsgi'])
    except plaster.PlasterError as ex:
        if not exit_on_error:
            raise
        _exit_with_error(f'Unable to load config "{config_uri}": {ex}')
    if exit_on_error:
        uri = loader.uri
        # plaster parses a bare filesystem path into a "file+<ext>" scheme
        if uri.scheme.startswith('file+') and not os.path.isfile(uri.path):
            _exit_with_error(f'Config file "{uri.path}" does not exist.')
    return loader


def _exit_with_error(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)
