import os

from zope.component import queryUtility
from zope.interface import implements

from repoze.bfg.interfaces import ISettings

class Settings(dict):
    implements(ISettings)
    def __getattr__(self, name):
        # backwards compatibility
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

def get_settings():
    """
    Return a 'settings' object for the current application.  A
    'settings' object is a dictionary-like object that contains
    key/value pairs based on the dictionary passed as the ``options``
    argument to the ``repoze.bfg.router.make_app`` API.

    For backwards compatibility, dictionary keys can also be looked up
    as attributes of the settings object.
    """
    return queryUtility(ISettings)

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
    update = {
        'debug_authorization': effective_debug_all or effective_debug_auth,
        'debug_notfound': effective_debug_all or effective_debug_notfound,
        'reload_templates': effective_reload_templates,
        }

    kw.update(update)
    return kw

