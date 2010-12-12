from zope.component.registry import Components

from pyramid.interfaces import ISettings

class Registry(Components, dict):
    """ A registry object is an :term:`application registry`.  The existence
    of a registry implementation detail of :app:`pyramid`.  It is used by the
    framework itself to perform mappings of URLs to view callables, as well
    as servicing other various duties. Despite being an implementation detail
    of the framework, it has a number of attributes that may be useful within
    application code.

    For information about the purpose and usage of the application registry,
    see :ref:`zca_chapter`.

    The application registry is usually accessed as ``request.registry`` in
    application code.

    """

    # for optimization purposes, if no listeners are listening, don't try
    # to notify them
    has_listeners = False
    _settings = None

    def registerSubscriptionAdapter(self, *arg, **kw):
        result = Components.registerSubscriptionAdapter(self, *arg, **kw)
        self.has_listeners = True
        return result

    def registerHandler(self, *arg, **kw):
        result = Components.registerHandler(self, *arg, **kw)
        self.has_listeners = True
        return result

    def notify(self, *events):
        if self.has_listeners:
            # iterating over subscribers assures they get executed
            [ _ for _ in self.subscribers(events, None) ]

    # backwards compatibility for code that wants to look up a settings
    # object via ``registry.getUtility(ISettings)``
    def _get_settings(self):
        return self._settings

    def _set_settings(self, settings):
        self.registerUtility(settings, ISettings)
        self._settings = settings

    settings = property(_get_settings, _set_settings)

global_registry = Registry('global')
