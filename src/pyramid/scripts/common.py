import plaster


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


def get_config_loader(config_uri):
    """
    Find a ``plaster.ILoader`` object supporting the "wsgi" protocol.

    """
    return plaster.get_loader(config_uri, protocols=['wsgi'])
