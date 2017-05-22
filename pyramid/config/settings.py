import os

from pyramid.settings import asbool, aslist

class SettingsConfiguratorMixin(object):
    def _set_settings(self, mapping):
        if mapping is None:
            mapping = {}
        settings = Settings(mapping)
        self.registry.settings = settings
        return settings

    def add_settings(self, settings=None, **kw):
        """Augment the :term:`deployment settings` with one or more
        key/value pairs.

        You may pass a dictionary::

           config.add_settings({'external_uri':'http://example.com'})

        Or a set of key/value pairs::

           config.add_settings(external_uri='http://example.com')

        This function is useful when you need to test code that accesses the
        :attr:`pyramid.registry.Registry.settings` API (or the
        :meth:`pyramid.config.Configurator.get_settings` API) and
        which uses values from that API.
        """
        if settings is None:
            settings = {}
        utility = self.registry.settings
        if utility is None:
            utility = self._set_settings(settings)
        utility.update(settings)
        utility.update(kw)

    def get_settings(self):
        """
        Return a :term:`deployment settings` object for the current
        application.  A deployment settings object is a dictionary-like
        object that contains key/value pairs based on the dictionary passed
        as the ``settings`` argument to the
        :class:`pyramid.config.Configurator` constructor.

        .. note:: the :attr:`pyramid.registry.Registry.settings` API
           performs the same duty.
           """
        return self.registry.settings


def Settings(d=None, _environ_=os.environ, **kw):
    """ Deployment settings.  Update application settings (usually
    from PasteDeploy keywords) with framework-specific key/value pairs
    (e.g. find ``PYRAMID_DEBUG_AUTHORIZATION`` in os.environ and jam into
    keyword args)."""
    if d is None:
        d = {}
    d = dict(d)
    d.update(**kw)

    eget = _environ_.get
    def expand_key(key):
        keys = [key]
        if not key.startswith('pyramid.'):
            keys.append('pyramid.' + key)
        return keys
    def S(settings_key, env_key=None, type_=str, default=False):
        value = default
        keys = expand_key(settings_key)
        for key in keys:
            value = d.get(key, value)
        if env_key:
            value = eget(env_key, value)
        value = type_(value)
        d.update({k: value for k in keys})
    def O(settings_key, override_key):
        for key in expand_key(settings_key):
            d[key] = d[key] or d[override_key]

    S('debug_all', 'PYRAMID_DEBUG_ALL', asbool)
    S('debug_authorization', 'PYRAMID_DEBUG_AUTHORIZATION', asbool)
    O('debug_authorization', 'debug_all')
    S('debug_notfound', 'PYRAMID_DEBUG_NOTFOUND', asbool)
    O('debug_notfound', 'debug_all')
    S('debug_routematch', 'PYRAMID_DEBUG_ROUTEMATCH', asbool)
    O('debug_routematch', 'debug_all')
    S('debug_templates', 'PYRAMID_DEBUG_TEMPLATES', asbool)
    O('debug_templates', 'debug_all')

    S('reload_all', 'PYRAMID_RELOAD_ALL', asbool)
    S('reload_templates', 'PYRAMID_RELOAD_TEMPLATES', asbool)
    O('reload_templates', 'reload_all')
    S('reload_assets', 'PYRAMID_RELOAD_ASSETS', asbool)
    O('reload_assets', 'reload_all')
    S('reload_resources', 'PYRAMID_RELOAD_RESOURCES', asbool)
    O('reload_resources', 'reload_all')
    # reload_resources is an older alias for reload_assets
    for k in expand_key('reload_assets') + expand_key('reload_resources'):
        d[k] = d['reload_assets'] or d['reload_resources']

    S('default_locale_name', 'PYRAMID_DEFAULT_LOCALE_NAME', str, 'en')
    S('prevent_http_cache', 'PYRAMID_PREVENT_HTTP_CACHE', asbool)
    S('prevent_cachebust', 'PYRAMID_PREVENT_CACHEBUST', asbool)
    S('csrf_trusted_origins', 'PYRAMID_CSRF_TRUSTED_ORIGINS', aslist, [])

    return d
