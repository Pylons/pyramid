import os

from zope.deprecation import deprecated
from zope.interface import implements

from pyramid.interfaces import ISettings

from pyramid.threadlocal import get_current_registry
from pyramid.util import DottedNameResolver

class Settings(dict):
    """ Deployment settings.  Update application settings (usually
    from PasteDeploy keywords) with framework-specific key/value pairs
    (e.g. find ``PYRAMID_DEBUG_AUTHORIZATION`` in os.environ and jam into
    keyword args)."""
    implements(ISettings)
    # _environ_ is dep inj for testing
    def __init__(self, d=None, _environ_=os.environ, **kw):
        if d is None:
            d = {}
        dict.__init__(self, d, **kw)
        eget = _environ_.get
        config_debug_all = self.get('debug_all', '')
        config_debug_all = self.get('pyramid.debug_all', config_debug_all)
        eff_debug_all = asbool(eget('PYRAMID_DEBUG_ALL', config_debug_all))
        config_reload_all = self.get('reload_all', '')
        config_reload_all = self.get('pyramid.reload_all', config_reload_all)
        eff_reload_all = asbool(eget('PYRAMID_RELOAD_ALL', config_reload_all))
        config_debug_auth = self.get('debug_authorization', '')
        config_debug_auth = self.get('pyramid.debug_authorization',
                                     config_debug_auth)
        eff_debug_auth = asbool(eget('PYRAMID_DEBUG_AUTHORIZATION',
                                     config_debug_auth))
        config_debug_notfound = self.get('debug_notfound', '')
        config_debug_notfound = self.get('pyramid.debug_notfound',
                                         config_debug_notfound)
        eff_debug_notfound = asbool(eget('PYRAMID_DEBUG_NOTFOUND',
                                         config_debug_notfound))
        config_debug_routematch = self.get('debug_routematch', '')
        config_debug_routematch = self.get('pyramid.debug_routematch',
                                           config_debug_routematch)
        eff_debug_routematch = asbool(eget('PYRAMID_DEBUG_ROUTEMATCH',
                                         config_debug_routematch))
        config_debug_templates = self.get('debug_templates', '')
        config_debug_templates = self.get('pyramid.debug_templates',
                                          config_debug_templates)
        eff_debug_templates = asbool(eget('PYRAMID_DEBUG_TEMPLATES',
                                          config_debug_templates))
        config_reload_templates = self.get('reload_templates', '')
        config_reload_templates = self.get('pyramid.reload_templates',
                                           config_reload_templates)
        eff_reload_templates = asbool(eget('PYRAMID_RELOAD_TEMPLATES',
                                           config_reload_templates))
        config_reload_assets = self.get('reload_assets', '')
        config_reload_assets = self.get('pyramid.reload_assets',
                                        config_reload_assets)
        reload_assets = asbool(eget('PYRAMID_RELOAD_ASSETS',
                                    config_reload_assets))
        config_reload_resources = self.get('reload_resources', '')
        config_reload_resources = self.get('pyramid.reload_resources',
                                           config_reload_resources)
        reload_resources = asbool(eget('PYRAMID_RELOAD_RESOURCES',
                                    config_reload_resources))
        # reload_resources is an older alias for reload_assets
        eff_reload_assets = reload_assets or reload_resources
        locale_name = self.get('default_locale_name', 'en')
        locale_name = self.get('pyramid.default_locale_name', locale_name)
        eff_locale_name = eget('PYRAMID_DEFAULT_LOCALE_NAME', locale_name)
        config_prevent_http_cache = self.get('prevent_http_cache', '')
        config_prevent_http_cache = self.get('pyramid.prevent_http_cache',
                                             config_prevent_http_cache)
        eff_prevent_http_cache = asbool(eget('PYRAMID_PREVENT_HTTP_CACHE',
                                             config_prevent_http_cache))

        update = {
            'debug_authorization': eff_debug_all or eff_debug_auth,
            'debug_notfound': eff_debug_all or eff_debug_notfound,
            'debug_routematch': eff_debug_all or eff_debug_routematch,
            'debug_templates': eff_debug_all or eff_debug_templates,
            'reload_templates': eff_reload_all or eff_reload_templates,
            'reload_resources':eff_reload_all or eff_reload_assets,
            'reload_assets':eff_reload_all or eff_reload_assets,
            'default_locale_name':eff_locale_name,
            'prevent_http_cache':eff_prevent_http_cache,

            'pyramid.debug_authorization': eff_debug_all or eff_debug_auth,
            'pyramid.debug_notfound': eff_debug_all or eff_debug_notfound,
            'pyramid.debug_routematch': eff_debug_all or eff_debug_routematch,
            'pyramid.debug_templates': eff_debug_all or eff_debug_templates,
            'pyramid.reload_templates': eff_reload_all or eff_reload_templates,
            'pyramid.reload_resources':eff_reload_all or eff_reload_assets,
            'pyramid.reload_assets':eff_reload_all or eff_reload_assets,
            'pyramid.default_locale_name':eff_locale_name,
            'pyramid.prevent_http_cache':eff_prevent_http_cache,
            }

        self.update(update)
        
    def __getattr__(self, name):
        # backwards compatibility
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

def get_settings():
    """
    Return a :term:`deployment settings` object for the current application.
    The object is a dictionary-like object that contains key/value pairs
    based on the dictionary passed as the ``settings`` argument to the
    :class:`pyramid.config.Configurator` constructor or the
    :func:`pyramid.router.make_app` API.

    .. warning:: This method is deprecated as of Pyramid 1.0.  Use
       ``pyramid.threadlocal.get_current_registry().settings`` instead or use
       the ``settings`` attribute of the registry available from the request
       (``request.registry.settings``).
    """
    reg = get_current_registry()
    return reg.settings

deprecated(
    'get_settings',
    '(pyramid.settings.get_settings is deprecated as of Pyramid 1.0.  Use'
    '``pyramid.threadlocal.get_current_registry().settings`` instead or use '
    'the ``settings`` attribute of the registry available from the request '
    '(``request.registry.settings``)).')

def asbool(s):
    """ Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is any of ``t``, ``true``, ``y``, ``on``, or ``1``, otherwise
    return the boolean value ``False``.  If ``s`` is the value ``None``,
    return ``False``.  If ``s`` is already one of the boolean values ``True``
    or ``False``, return it."""
    if s is None:
        return False
    if s in (True, False):
        return s
    s = str(s).strip()
    return s.lower() in ('t', 'true', 'y', 'yes', 'on', '1')

def aslist_cronly(value):
    if isinstance(value, basestring):
        value = filter(None, [x.strip() for x in value.splitlines()])
    return value

def aslist(value):
    values = aslist_cronly(value)
    result = []
    for value in values:
        subvalues = value.split()
        result.extend(subvalues)
    return result
