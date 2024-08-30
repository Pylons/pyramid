import plaster
import plaster.exceptions
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


def get_config_loader(config_uri, out=None):
    """
    Find a ``plaster.ILoader`` object supporting the "wsgi" protocol.

    ``out``, if passed, must be a function of one argument, a string.
    The function is called with an error message when the ``config_uri``
    cannot be used to obtain settings.  After ``out`` is called the
    program exits with a ``1`` (failure) status code.

    When ``out`` is not passed, or is None, the caller is expected
    to handle PlasterError exceptions raised by :term:`plaster`.
    """
    try:
        return plaster.get_loader(config_uri, protocols=['wsgi'])
    except plaster.exceptions.PlasterError as e:
        if not out:
            raise e
        out(f'The settings given are not available: {e}')
        sys.exit(1)
