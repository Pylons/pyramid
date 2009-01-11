import os

from zope.interface import implements

from repoze.bfg.interfaces import ISettings

class Settings(object):
    implements(ISettings)

    # defaults
    reload_templates = False
    debug_notfound = False
    debug_authorization = False
    unicode_path_segments = True

    def __init__(self, options):
        options = get_options(options)
        self.__dict__.update(options)

def asbool(s):
    s = str(s).strip()
    return s.lower() in ('t', 'true', 'y', 'yes', 'on', '1')

def get_options(kw, environ=os.environ):
    """ Update PasteDeploy application settings keywords with
    framework-specific key/value pairs (e.g. find
    'BFG_DEBUG_AUTHORIZATION' in os.environ and jam into keyword
    args)."""
    # environ is passed in for unit tests
    eget = environ.get
    config_debug_all = kw.get('debug_all', '')
    effective_debug_all = asbool(eget('BFG_DEBUG_ALL',
                                      config_debug_all))
    config_debug_auth = kw.get('debug_authorization', '')
    effective_debug_auth = asbool(eget('BFG_DEBUG_AUTHORIZATION',
                                       config_debug_auth))
    config_debug_notfound = kw.get('debug_notfound', '')
    effective_debug_notfound = asbool(eget('BFG_DEBUG_NOTFOUND',
                                           config_debug_notfound))
    config_reload_templates = kw.get('reload_templates', '')
    effective_reload_templates = asbool(eget('BFG_RELOAD_TEMPLATES',
                                        config_reload_templates))
    config_unicode_path_segments = kw.get('unicode_path_segments', 't')
    effective_unicode_path_segments = asbool(eget('BFG_UNICODE_PATH_SEGMENTS',
                                                  config_unicode_path_segments))
    update = {
        'debug_authorization': effective_debug_all or effective_debug_auth,
        'debug_notfound': effective_debug_all or effective_debug_notfound,
        'reload_templates': effective_reload_templates,
        'unicode_path_segments': effective_unicode_path_segments,
        }

    kw.update(update)
    return kw

