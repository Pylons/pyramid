import os
from pyramid.compat import configparser
from logging.config import fileConfig

def parse_vars(args):
    """
    Given variables like ``['a=b', 'c=d']`` turns it into ``{'a':
    'b', 'c': 'd'}``
    """
    result = {}
    for arg in args:
        if '=' not in arg:
            raise ValueError(
                'Variable assignment %r invalid (no "=")'
                % arg)
        name, value = arg.split('=', 1)
        result[name] = value
    return result

def setup_logging(config_uri, global_conf=None,
                  fileConfig=fileConfig,
                  configparser=configparser):
    """
    Set up logging via :func:`logging.config.fileConfig` with the filename
    specified via ``config_uri`` (a string in the form
    ``filename#sectionname``).

    ConfigParser defaults are specified for the special ``__file__``
    and ``here`` variables, similar to PasteDeploy config loading.
    Extra defaults can optionally be specified as a dict in ``global_conf``.
    """
    path = config_uri.split('#', 1)[0]
    parser = configparser.ConfigParser()
    parser.read([path])
    if parser.has_section('loggers'):
        config_file = os.path.abspath(path)
        full_global_conf = dict(
            __file__=config_file,
            here=os.path.dirname(config_file))
        if global_conf:
            full_global_conf.update(global_conf)
        return fileConfig(config_file, full_global_conf)
