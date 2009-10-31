import os
import sys
import threading

import zope.component

from zope.configuration import xmlconfig
from zope.configuration.config import ConfigurationMachine

from zope.component import getGlobalSiteManager
from zope.component import getSiteManager

from repoze.bfg.interfaces import IAuthenticationPolicy
from repoze.bfg.interfaces import IAuthorizationPolicy
from repoze.bfg.interfaces import IDefaultRootFactory
from repoze.bfg.interfaces import ILogger
from repoze.bfg.interfaces import IRootFactory
from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import ISettings

from repoze.bfg.authorization import ACLAuthorizationPolicy
from repoze.bfg.log import make_stream_logger
from repoze.bfg.registry import Registry
from repoze.bfg.settings import Settings
from repoze.bfg.settings import get_options
from repoze.bfg.threadlocal import get_current_registry
from repoze.bfg.threadlocal import manager
from repoze.bfg.urldispatch import RoutesRootFactory

def make_registry(root_factory, package=None, filename='configure.zcml',
                  authentication_policy=None, authorization_policy=None,
                  options=None, registry=None, debug_logger=None,
                  manager=manager, os=os, lock=threading.Lock()):
    # registry, debug_logger, manager, os and lock *only* for unittests
    if options is None:
        options = {}

    if not 'configure_zcml' in options:
        options['configure_zcml'] = filename

    settings = Settings(get_options(options))
    filename = settings['configure_zcml']

    # not os.path.isabs below for windows systems
    if (':' in filename) and (not os.path.isabs(filename)):
        package, filename = filename.split(':', 1)
        __import__(package)
        package = sys.modules[package]

    if registry is None:
        regname = filename
        if package:
            regname = package.__name__
        registry = Registry(regname)

    registry.registerUtility(settings, ISettings)

    if debug_logger is None:
        debug_logger = make_stream_logger('repoze.bfg.debug', sys.stderr)
    registry.registerUtility(debug_logger, ILogger, 'repoze.bfg.debug')

    if root_factory is None:
        root_factory = DefaultRootFactory

    # register the *default* root factory so apps can find it later
    registry.registerUtility(root_factory, IDefaultRootFactory)

    mapper = RoutesRootFactory(root_factory)
    registry.registerUtility(mapper, IRoutesMapper)

    if authentication_policy:
        debug_logger.warn(
            'The "authentication_policy" and "authorization_policy" '
            'arguments to repoze.bfg.router.make_app have been deprecated '
            'in repoze.bfg version 1.0.  Instead of using these arguments to '
            'configure an authorization/authentication policy pair, use '
            'a pair of ZCML directives (such as "authtktauthenticationpolicy" '
            'and "aclauthorizationpolicy" documented within the Security '
            'chapter in the BFG documentation.  If you need to use a custom '
            'authentication or authorization policy, you should make a ZCML '
            'directive for it and use that directive within your '
            'application\'s ZCML')
        registry.registerUtility(authentication_policy, IAuthenticationPolicy)
        if authorization_policy is None:
            authorization_policy = ACLAuthorizationPolicy()
        registry.registerUtility(authorization_policy, IAuthorizationPolicy)

    # We push our ZCML-defined configuration into an app-local
    # component registry in order to allow more than one bfg app to live
    # in the same process space without one unnecessarily stomping on
    # the other's component registrations (although I suspect directives
    # that have side effects are going to fail).  The only way to do
    # that currently is to override zope.component.getGlobalSiteManager
    # for the duration of the ZCML includes.  We acquire a lock in case
    # another make_app runs in a different thread simultaneously, in a
    # vain attempt to prevent mixing of registrations.  There's not much
    # we can do about non-makeRegistry code that tries to use the global
    # site manager API directly in a different thread while we hold the
    # lock.  Those registrations will end up in our application's
    # registry.

    lock.acquire()
    manager.push({'registry':registry, 'request':None})
    try:
        getSiteManager.sethook(get_current_registry)
        zope.component.getGlobalSiteManager = get_current_registry
        zcml_configure(filename, package)
    finally:
        # intentional: do not call getSiteManager.reset(); executing
        # this function means we're taking over getSiteManager for the
        # lifetime of this process
        zope.component.getGlobalSiteManager = getGlobalSiteManager
        lock.release()
        manager.pop()

    if mapper.has_routes():
        # if the user had any <route/> statements in his configuration,
        # use the RoutesRootFactory as the IRootFactory; otherwise use the
        # default root factory (optimization; we don't want to go through
        # the Routes logic if we know there are no routes to match)
        root_factory = mapper

    registry.registerUtility(root_factory, IRootFactory)

    return registry

class DefaultRootFactory:
    __parent__ = None
    __name__ = None
    def __init__(self, request):
        matchdict = getattr(request, 'matchdict', {})
        # provide backwards compatibility for applications which
        # used routes (at least apps without any custom "context
        # factory") in BFG 0.9.X and before
        self.__dict__.update(matchdict)

def zcml_configure(name, package):
    """ Given a ZCML filename as ``name`` and a Python package as
    ``package`` which the filename should be relative to, load the
    ZCML into the current ZCML registry.

    .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.
    """
    context = ConfigurationMachine()
    xmlconfig.registerCommonDirectives(context)
    context.package = package
    xmlconfig.include(context, name, package)
    context.execute_actions(clear=False)
    return context.actions

