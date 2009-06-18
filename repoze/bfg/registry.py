import threading

import zope.component

from zope.component import getGlobalSiteManager
from zope.component import getSiteManager as original_getSiteManager
from zope.component.registry import Components

from zope.deprecation import deprecated

from repoze.bfg.threadlocal import manager
from repoze.bfg.threadlocal import get_current_registry

from repoze.bfg.zcml import zcml_configure

class Registry(Components):

    # for optimization purposes, if no listeners are listening, don't try
    # to notify them
    has_listeners = False

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
            for ignored in self.subscribers(events, None):
                """ """

def populateRegistry(registry, filename, package, lock=threading.Lock(),
                     manager=manager): # lock and manager for testing

    """ We push our ZCML-defined configuration into an app-local
    component registry in order to allow more than one bfg app to live
    in the same process space without one unnecessarily stomping on
    the other's component registrations (although I suspect directives
    that have side effects are going to fail).  The only way to do
    that currently is to override zope.component.getGlobalSiteManager
    for the duration of the ZCML includes.  We acquire a lock in case
    another make_app runs in a different thread simultaneously, in a
    vain attempt to prevent mixing of registrations.  There's not much
    we can do about non-makeRegistry code that tries to use the global
    site manager API directly in a different thread while we hold the
    lock.  Those registrations will end up in our application's
    registry."""
    
    lock.acquire()
    manager.push({'registry':registry, 'request':None})
    try:
        original_getSiteManager.sethook(get_current_registry)
        zope.component.getGlobalSiteManager = get_current_registry
        zcml_configure(filename, package)
    finally:
        zope.component.getGlobalSiteManager = getGlobalSiteManager
        lock.release()
        manager.pop()

class FakeRegistryManager(object):
    manager = manager # for unit tests
    def push(self, registry):
        return self.manager.push({'registry':registry, 'request':None})

    set = push # b/c

    def pop(self):
        result = self.manager.pop()
        if result:
            return result['registry']

    def get(self):
        return self.manager.get()['registry']

    def clear(self):
        self.manager.clear()

# for use in scripts for backwards compatibility *only*!
registry_manager = FakeRegistryManager() 
    
deprecated('registry_manager',
           'As of repoze.bfg 0.9, any import of registry_manager from'
           '``repoze.bfg.registry`` is '
           'deprecated.  If you are trying to use the registry manager '
           'within a "debug" script of your own making, use the ``bfgshell`` '
           'paster command instead. ``registry_manager`` will disappear in '
           'a later release of repoze.bfg')

getSiteManager = get_current_registry # b/c

deprecated('getSiteManager',
           'As of repoze.bfg 1.0, any import of getSiteManager from'
           '``repoze.bfg.registry`` is '
           'deprecated.  Use ``from zope.compponent import getSiteManager '
           'instead.')

get_registry = get_current_registry # b/c

deprecated('get_registry',
           'As of repoze.bfg 1.0, any import of get_registry from'
           '``repoze.bfg.registry`` is '
           'deprecated.  Use ``from repoze.bfg.threadlocal import '
           'get_current_registry instead.')
