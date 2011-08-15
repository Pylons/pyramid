from pyramid.settings import Settings

class SettingsConfiguratorMixin(object):
    def _set_settings(self, mapping):
        if not mapping:
            mapping = {}
        settings = Settings(mapping)
        self.registry.settings = settings
        return settings

    def add_settings(self, settings=None, **kw):
        """Augment the ``settings`` argument passed in to the Configurator
        constructor with one or more 'setting' key/value pairs.  A setting is
        a single key/value pair in the dictionary-ish object returned from
        the API :attr:`pyramid.registry.Registry.settings` and
        :meth:`pyramid.config.Configurator.get_settings`.

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
        :class:`pyramid.config.Configurator` constructor or the
        :func:`pyramid.router.make_app` API.

        .. note:: For backwards compatibility, dictionary keys can also be
           looked up as attributes of the settings object.

        .. note:: the :attr:`pyramid.registry.Registry.settings` API
           performs the same duty.
           """
        return self.registry.settings

