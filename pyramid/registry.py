from zope.component.registry import Components
from pyramid.interfaces import ISettings

class Registry(Components, dict):

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
