import os

from zope.interface import implements

from repoze.bfg.interfaces import ISettings

from repoze.bfg.threadlocal import get_current_registry

class Settings(dict):
    """ Deployment settings.  Update application settings (usually
    from PasteDeploy keywords) with framework-specific key/value pairs
    (e.g. find ``BFG_DEBUG_AUTHORIZATION`` in os.environ and jam into
    keyword args)."""
    implements(ISettings)
    # _environ_ is dep inj for testing
    def __init__(self, d=None, _environ_=os.environ, **kw):
        if d is None:
            d = {}
        dict.__init__(self, d, **kw)
        eget = _environ_.get
        config_debug_all = self.get('debug_all', '')
        eff_debug_all = asbool(eget('BFG_DEBUG_ALL', config_debug_all))
        config_reload_all = self.get('reload_all', '')
        eff_reload_all = asbool(eget('BFG_RELOAD_ALL',config_reload_all))
        config_debug_auth = self.get('debug_authorization', '')
        eff_debug_auth = asbool(eget('BFG_DEBUG_AUTHORIZATION',
                                     config_debug_auth))
        config_debug_notfound = self.get('debug_notfound', '')
        eff_debug_notfound = asbool(eget('BFG_DEBUG_NOTFOUND',
                                         config_debug_notfound))
        config_reload_templates = self.get('reload_templates', '')
        eff_reload_templates = asbool(eget('BFG_RELOAD_TEMPLATES',
                                           config_reload_templates))
        config_reload_resources = self.get('reload_resources', '')
        eff_reload_resources = asbool(eget('BFG_RELOAD_RESOURCES',
                                           config_reload_resources))
        configure_zcml = self.get('configure_zcml', '')
        eff_configure_zcml = eget('BFG_CONFIGURE_ZCML', configure_zcml)
        update = {
            'debug_authorization': eff_debug_all or eff_debug_auth,
            'debug_notfound': eff_debug_all or eff_debug_notfound,
            'reload_templates': eff_reload_all or eff_reload_templates,
            'reload_resources':eff_reload_all or eff_reload_resources,
            'configure_zcml':eff_configure_zcml,
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
    Return a 'settings' object for the current application.  A
    'settings' object is a dictionary-like object that contains
    key/value pairs based on the dictionary passed as the ``settings``
    argument to the :class:`repoze.bfg.configuration.Configurator`
    constructor or the :func:`repoze.bfg.router.make_app` API.

    .. note:: For backwards compatibility, dictionary keys can also be
       looked up as attributes of the settings object.
    """
    reg = get_current_registry()
    return reg.queryUtility(ISettings)

def asbool(s):
    s = str(s).strip()
    return s.lower() in ('t', 'true', 'y', 'yes', 'on', '1')

