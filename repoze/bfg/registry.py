import threading
import zope.component

from zope.component import getGlobalSiteManager
from zope.component.interfaces import ComponentLookupError
from zope.component.interfaces import IComponentLookup
from zope.component.registry import Components
from zope.component import getSiteManager as original_getSiteManager

from zope.configuration import xmlconfig

class ThreadLocalRegistryManager(threading.local):
    registry = getGlobalSiteManager()
    def set(self, registry):
        self.registry = registry

    def get(self):
        return self.registry

    def clear(self):
        self.registry = getGlobalSiteManager()

registry_manager = ThreadLocalRegistryManager()

def setRegistryManager(manager): # for unit tests
    global registry_manager
    old_registry_manager = registry_manager
    registry_manager = manager
    return old_registry_manager

def makeRegistry(filename, package, lock=threading.Lock()):
    # This is absurd and probably not worth it.  We want to try to
    # push our ZCML-defined configuration into an app-local component
    # registry in order to allow more than one bfg app to live in the
    # same process space without one unnecessarily stomping on the
    # other's component registrations (although I suspect directives
    # that side effects are going to fail).  The only way to do that
    # currently is to override zope.component.getGlobalSiteManager for
    # the duration of the ZCML includes.  We acquire a lock in case
    # another make_app runs in a different thread simultaneously, in a
    # vain attempt to prevent mixing of registrations.  There's not
    # much we can do about non-make_app code that tries to use the
    # global site manager API directly in a different thread while we
    # hold the lock.  Those registrations will end up in our
    # application's registry.
    lock.acquire()
    try:
        registry = Components(package.__name__)
        registry_manager.set(registry)
        original_getSiteManager.sethook(getSiteManager)
        zope.component.getGlobalSiteManager = registry_manager.get
        xmlconfig.file(filename, package=package)
        return registry
    finally:
        zope.component.getGlobalSiteManager = getGlobalSiteManager
        lock.release()
        registry_manager.clear()

def getSiteManager(context=None):
    if context is None:
        return registry_manager.get()
    else:
        try:
            return IComponentLookup(context)
        except TypeError, error:
            raise ComponentLookupError(*error.args)

from zope.testing.cleanup import addCleanUp
addCleanUp(original_getSiteManager.reset)
