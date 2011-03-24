import os

from zope.deprecation import deprecated
from zope.interface import implements

from pyramid.interfaces import ISettings

from pyramid.threadlocal import get_current_registry

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
        eff_debug_all = asbool(eget('PYRAMID_DEBUG_ALL', config_debug_all))
        config_reload_all = self.get('reload_all', '')
        eff_reload_all = asbool(eget('PYRAMID_RELOAD_ALL',config_reload_all))
        config_debug_auth = self.get('debug_authorization', '')
        eff_debug_auth = asbool(eget('PYRAMID_DEBUG_AUTHORIZATION',
                                     config_debug_auth))
        config_debug_notfound = self.get('debug_notfound', '')
        eff_debug_notfound = asbool(eget('PYRAMID_DEBUG_NOTFOUND',
                                         config_debug_notfound))
        config_debug_routematch = self.get('debug_routematch', '')
        eff_debug_routematch = asbool(eget('PYRAMID_DEBUG_ROUTEMATCH',
                                         config_debug_routematch))
        config_debug_templates = self.get('debug_templates', '')
        eff_debug_templates = asbool(eget('PYRAMID_DEBUG_TEMPLATES',
                                          config_debug_templates))
        config_reload_templates = self.get('reload_templates', '')
        eff_reload_templates = asbool(eget('PYRAMID_RELOAD_TEMPLATES',
                                           config_reload_templates))
        config_reload_assets = self.get('reload_assets', '')
        config_reload_resources = self.get('reload_resources', '')
        reload_assets = asbool(eget('PYRAMID_RELOAD_ASSETS',
                                    config_reload_assets))
        reload_resources = asbool(eget('PYRAMID_RELOAD_RESOURCES',
                                    config_reload_resources))
        # reload_resources is an older alias for reload_assets
        eff_reload_assets = reload_assets or reload_resources
        locale_name = self.get('default_locale_name', 'en')
        eff_locale_name = eget('PYRAMID_DEFAULT_LOCALE_NAME', locale_name)
        
        update = {
            'debug_authorization': eff_debug_all or eff_debug_auth,
            'debug_notfound': eff_debug_all or eff_debug_notfound,
            'debug_routematch': eff_debug_all or eff_debug_routematch,
            'debug_templates': eff_debug_all or eff_debug_templates,
            'reload_templates': eff_reload_all or eff_reload_templates,
            'reload_resources':eff_reload_all or eff_reload_assets,
            'reload_assets':eff_reload_all or eff_reload_assets,
            'default_locale_name':eff_locale_name,
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
       ``pyramid.threadlocals.get_current_registry().settings`` instead or use
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

