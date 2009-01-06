import os
import sys
import threading

import zope.component

from zope.component import getGlobalSiteManager
from zope.component.interfaces import ComponentLookupError
from zope.component.interfaces import IComponentLookup
from zope.component.registry import Components
from zope.component import getSiteManager as original_getSiteManager

from zope.interface import implements

from repoze.bfg.interfaces import ISettings
from repoze.bfg.interfaces import ILogger
from repoze.bfg.zcml import zcml_configure
from repoze.bfg.log import make_stream_logger

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

def makeRegistry(filename, package, options=None, lock=threading.Lock()):
    # We push our ZCML-defined configuration into an app-local
    # component registry in order to allow more than one bfg app to
    # live in the same process space without one unnecessarily
    # stomping on the other's component registrations (although I
    # suspect directives that have side effects are going to fail).
    # The only way to do that currently is to override
    # zope.component.getGlobalSiteManager for the duration of the ZCML
    # includes.  We acquire a lock in case another make_app runs in a
    # different thread simultaneously, in a vain attempt to prevent
    # mixing of registrations.  There's not much we can do about
    # non-make_app code that tries to use the global site manager API
    # directly in a different thread while we hold the lock.  Those
    # registrations will end up in our application's registry.
    lock.acquire()
    try:
        registry = Components(package.__name__)
        registry_manager.set(registry)
        if options is None:
            options = {}
        settings = Settings(options)
        registry.registerUtility(settings, ISettings)
        debug_logger = make_stream_logger('repoze.bfg.debug', sys.stderr)
        registry.registerUtility(debug_logger, ILogger, 'repoze.bfg.debug')
        original_getSiteManager.sethook(getSiteManager)
        zope.component.getGlobalSiteManager = registry_manager.get
        zcml_configure(filename, package=package)
        return registry
    finally:
        zope.component.getGlobalSiteManager = getGlobalSiteManager
        lock.release()
        registry_manager.clear()

class Settings(object):
    implements(ISettings)
    reload_templates = False
    debug_notfound = False
    debug_authorization = False
    unicode_path_segments = True
    def __init__(self, options):
        self.__dict__.update(options)

def getSiteManager(context=None):
    if context is None:
        return registry_manager.get()
    else:
        try:
            return IComponentLookup(context)
        except TypeError, error:
            raise ComponentLookupError(*error.args)

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
    config_unicode_path_segments = kw.get('unicode_path_segments', '')
    effective_unicode_path_segments = asbool(eget('BFG_UNICODE_PATH_SEGMENTS',
                                                  config_unicode_path_segments))
    update = {
        'debug_authorization': effective_debug_all or effective_debug_auth,
        'debug_notfound': effective_debug_all or effective_debug_notfound,
        'reload_templates': effective_reload_templates,
        'unicode_path_segments': effective_unicode_path_segments,
        }

    kw.update(update)
    return kw

from zope.testing.cleanup import addCleanUp
try:
    addCleanUp(original_getSiteManager.reset)
except AttributeError:
    # zope.hookable not yet installed
    pass
addCleanUp(registry_manager.clear)
