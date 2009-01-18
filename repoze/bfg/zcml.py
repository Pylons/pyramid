import cPickle
import os
from os.path import realpath
import time
import types

from zope.configuration import xmlconfig

from zope.component import getSiteManager
from zope.component import adaptedBy
import zope.configuration.config

from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject

from zope.interface import Interface

from zope.schema import TextLine

from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import IView
from repoze.bfg.path import package_path

from repoze.bfg.security import ViewPermissionFactory

import martian

def handler(methodName, *args, **kwargs):
    method = getattr(getSiteManager(), methodName)
    method(*args, **kwargs)

class Uncacheable(object):
    """ Include in discriminators of actions which are not cacheable """
    pass

def view(_context,
         permission=None,
         for_=None,
         view=None,
         name="",
         request_type=None,
         cacheable=True,
         ):

    if not view:
        raise ConfigurationError('"view" attribute was not specified')

    # adapts() decorations may be used against either functions or
    # class instances
    if isinstance(view, types.FunctionType):
        adapted_by = adaptedBy(view)
    else:
        adapted_by = adaptedBy(type(view))

    if adapted_by is not None:
        try:
            if for_ is None:
                for_, _ = adapted_by
            if request_type is None:
                _, request_type = adapted_by
        except ValueError:
            # the component adaptation annotation does not conform to
            # the view specification; we ignore it.
            pass

    if request_type is None:
        request_type = IRequest

    if permission:
        pfactory = ViewPermissionFactory(permission)
        _context.action(
            discriminator = ('permission', for_, name, request_type,
                             IViewPermission),
            callable = handler,
            args = ('registerAdapter',
                    pfactory, (for_, request_type), IViewPermission, name,
                    _context.info),
            )

    cacheable = cacheable or Uncacheable

    _context.action(
        discriminator = ('view', for_, name, request_type, IView, cacheable),
        callable = handler,
        args = ('registerAdapter',
                view, (for_, request_type), IView, name,
                _context.info),
        )

class IViewDirective(Interface):
    for_ = GlobalObject(
        title=u"The interface or class this view is for.",
        required=False
        )

    permission = TextLine(
        title=u"Permission",
        description=u"The permission needed to use the view.",
        required=False
        )

    view = GlobalObject(
        title=u"",
        description=u"The view function",
        required=False,
        )

    name = TextLine(
        title=u"The name of the view",
        description=u"""
        The name shows up in URLs/paths. For example 'foo' or
        'foo.html'.""",
        required=False,
        )

    request_type = GlobalObject(
        title=u"""The request type interface for the view""",
        description=(u"The view will be called if the interface represented by "
                     u"'request_type' is implemented by the request.  The "
                     u"default request type is repoze.bfg.interfaces.IRequest"),
        required=False
        )

PVERSION = 1

def pickle_name(name, package):
    path = package_path(package)
    basename = os.path.join(path, name)
    return os.path.join(path, basename + '.cache')

def zcml_configure(name, package, load=cPickle.load):
    """ Execute pickled zcml actions or fall back to parsing from file
    """
    pckname = pickle_name(name, package)

    if not (os.path.isfile(pckname) or os.path.islink(pckname)):
        return file_configure(name, package)

    try:
        vers, ptime, actions = load(open(pckname, 'rb'))
    except (IOError, cPickle.UnpicklingError, EOFError, TypeError, ValueError,
            AttributeError, NameError, ImportError):
        return file_configure(name, package)

    if vers != PVERSION:
        return file_configure(name, package)

    try:
        ptime = int(ptime)
    except:
        return file_configure(name, package)

    if not hasattr(actions, '__iter__'):
        return file_configure(name, package)

    files = set()
    for action in actions:
        try:
            fileset = action[4]
            files.update(fileset)
        except (TypeError, IndexError):
            return file_configure(name, package)

    for file in files:
        if not(os.path.isfile(file) or os.path.islink(file)):
            return file_configure(name, package)

        mtime = os.stat(realpath(file)).st_mtime
        
        if  mtime >= ptime:
            return file_configure(name, package)

    context = zope.configuration.config.ConfigurationMachine()
    xmlconfig.registerCommonDirectives(context)
    context.actions = actions
    context.cached_execution = True
    context.execute_actions()
    return True

def remove(name, os=os): # os parameterized for unit tests
    try:
        os.remove(name)
        return True
    except:
        pass
    return False

def file_configure(name, package, dump=cPickle.dump):
    context = zope.configuration.config.ConfigurationMachine()
    xmlconfig.registerCommonDirectives(context)
    context.package = package

    xmlconfig.include(context, name, package)
    context.execute_actions(clear=False)

    actions = context.actions
    pckname = pickle_name(name, package)

    for action in actions:
        
        discriminator = action[0]
        if discriminator and Uncacheable in discriminator:
            remove(pckname)
            return False

    try:
        data = (PVERSION, time.time(), actions)
        dump(data, open(pckname, 'wb'), -1)
    except (OSError, IOError, TypeError, cPickle.PickleError):
        remove(pckname)

    return False

def exclude(name):
    if name.startswith('.'):
        return True
    return False

def scan(_context, package, martian=martian):
    # martian overrideable only for unit tests
    module_grokker = martian.ModuleGrokker()
    module_grokker.register(BFGViewFunctionGrokker())
    martian.grok_dotted_name(package.__name__, grokker=module_grokker,
                             context=_context, exclude_filter=exclude)

class IScanDirective(Interface):
    package = GlobalObject(
        title=u"The package we'd like to scan.",
        required=True,
        )

class BFGViewFunctionGrokker(martian.InstanceGrokker):
    martian.component(types.FunctionType)

    def grok(self, name, obj, **kw):
        if hasattr(obj, '__is_bfg_view__'):
            permission = obj.__permission__
            for_ = obj.__for__
            name = obj.__view_name__
            request_type = obj.__request_type__
            context = kw['context']
            # we dont tecnically need to pass "Uncacheable" here; any
            # view function decorated with an __is_bfg_view__ attr via
            # repoze.bfg.view.bfg_view is unpickleable; but the
            # uncacheable bit helps pickling fail more quickly
            # (pickling is never attempted)
            view(context, permission=permission, for_=for_,
                 view=obj, name=name, request_type=request_type,
                 cacheable=Uncacheable)
            return True
        return False
