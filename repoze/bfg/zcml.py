import cPickle
import os
from os.path import realpath
import time
import types

from zope.configuration import xmlconfig

from zope.component import getSiteManager
from zope.component import adaptedBy
import zope.configuration.config

from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject

from zope.interface import Interface

from zope.schema import TextLine

from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import IView
from repoze.bfg.path import package_path

from repoze.bfg.security import ViewPermissionFactory

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

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )

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

def adapter(_context, factory, provides=None, for_=None, name=''):

    if for_ is None:
        if len(factory) == 1:
            for_ = zope.component.adaptedBy(factory[0])

        if for_ is None:
            raise TypeError("No for attribute was provided and can't "
                            "determine what the factory adapts.")

    for_ = tuple(for_)

    if provides is None:
        if len(factory) == 1:
            p = list(zope.interface.implementedBy(factory[0]))
            if len(p) == 1:
                provides = p[0]

        if provides is None:
            raise TypeError("Missing 'provides' attribute")

    # Generate a single factory from multiple factories:
    factories = factory
    if len(factories) == 1:
        factory = factories[0]
    elif len(factories) < 1:
        raise ValueError("No factory specified")
    elif len(factories) > 1 and len(for_) != 1:
        raise ValueError("Can't use multiple factories and multiple for")
    else:
        factory = _rolledUpFactory(factories)

    _context.action(
        discriminator = ('adapter', for_, provides, name),
        callable = handler,
        args = ('registerAdapter',
                factory, for_, provides, name, _context.info),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', provides)
               )
    if for_:
        for iface in for_:
            if iface is not None:
                _context.action(
                    discriminator = None,
                    callable = provideInterface,
                    args = ('', iface)
                    )

class IAdapterDirective(zope.interface.Interface):
    """
    Register an adapter
    """

    factory = zope.configuration.fields.Tokens(
        title=u"Adapter factory/factories",
        description=(u"A list of factories (usually just one) that create"
                     " the adapter instance."),
        required=True,
        value_type=zope.configuration.fields.GlobalObject()
        )

    provides = zope.configuration.fields.GlobalInterface(
        title=u"Interface the component provides",
        description=(u"This attribute specifies the interface the adapter"
                     " instance must provide."),
        required=False,
        )

    for_ = zope.configuration.fields.Tokens(
        title=u"Specifications to be adapted",
        description=u"This should be a list of interfaces or classes",
        required=False,
        value_type=zope.configuration.fields.GlobalObject(
          missing_value=object(),
          ),
        )

    name = zope.schema.TextLine(
        title=u"Name",
        description=(u"Adapters can have names.\n\n"
                     "This attribute allows you to specify the name for"
                     " this adapter."),
        required=False,
        )

_handler = handler
def subscriber(_context, for_=None, factory=None, handler=None, provides=None):
    if factory is None:
        if handler is None:
            raise TypeError("No factory or handler provided")
        if provides is not None:
            raise TypeError("Cannot use handler with provides")
        factory = handler
    else:
        if handler is not None:
            raise TypeError("Cannot use handler with factory")
        if provides is None:
            raise TypeError(
                "You must specify a provided interface when registering "
                "a factory")

    if for_ is None:
        for_ = zope.component.adaptedBy(factory)
        if for_ is None:
            raise TypeError("No for attribute was provided and can't "
                            "determine what the factory (or handler) adapts.")

    for_ = tuple(for_)

    if handler is not None:
        _context.action(
            discriminator = None,
            callable = _handler,
            args = ('registerHandler',
                    handler, for_, u'', _context.info),
            )
    else:
        _context.action(
            discriminator = None,
            callable = _handler,
            args = ('registerSubscriptionAdapter',
                    factory, for_, provides, u'', _context.info),
            )

    if provides is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', provides)
            )

    # For each interface, state that the adapter provides that interface.
    for iface in for_:
        if iface is not None:
            _context.action(
                discriminator = None,
                callable = provideInterface,
                args = ('', iface)
                )

class ISubscriberDirective(zope.interface.Interface):
    """
    Register a subscriber
    """

    factory = zope.configuration.fields.GlobalObject(
        title=u"Subscriber factory",
        description=u"A factory used to create the subscriber instance.",
        required=False,
        )

    handler = zope.configuration.fields.GlobalObject(
        title=u"Handler",
        description=u"A callable object that handles events.",
        required=False,
        )

    provides = zope.configuration.fields.GlobalInterface(
        title=u"Interface the component provides",
        description=(u"This attribute specifies the interface the adapter"
                     " instance must provide."),
        required=False,
        )

    for_ = zope.configuration.fields.Tokens(
        title=u"Interfaces or classes that this subscriber depends on",
        description=u"This should be a list of interfaces or classes",
        required=False,
        value_type=zope.configuration.fields.GlobalObject(
          missing_value = object(),
          ),
        )

def utility(_context, provides=None, component=None, factory=None, name=''):
    if factory and component:
        raise TypeError("Can't specify factory and component.")

    if provides is None:
        if factory:
            provides = list(zope.interface.implementedBy(factory))
        else:
            provides = list(zope.interface.providedBy(component))
        if len(provides) == 1:
            provides = provides[0]
        else:
            raise TypeError("Missing 'provides' attribute")

    _context.action(
        discriminator = ('utility', provides, name),
        callable = handler,
        args = ('registerUtility', component, provides, name),
        kw = dict(factory=factory),
        )

    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (provides.__module__ + '.' + provides.getName(), provides)
        )

class IUtilityDirective(Interface):
    """Register a utility."""

    component = zope.configuration.fields.GlobalObject(
        title=u"Component to use",
        description=(u"Python name of the implementation object.  This"
                     " must identify an object in a module using the"
                     " full dotted name.  If specified, the"
                     " ``factory`` field must be left blank."),
        required=False,
        )

    factory = zope.configuration.fields.GlobalObject(
        title=u"Factory",
        description=(u"Python name of a factory which can create the"
                     " implementation object.  This must identify an"
                     " object in a module using the full dotted name."
                     " If specified, the ``component`` field must"
                     " be left blank."),
        required=False,
        )

    provides = zope.configuration.fields.GlobalInterface(
        title=u"Provided interface",
        description=u"Interface provided by the utility.",
        required=False,
        )

    name = zope.schema.TextLine(
        title=u"Name",
        description=(u"Name of the registration.  This is used by"
                     " application code when locating a utility."),
        required=False,
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
            try:
                os.remove(pckname)
            except:
                pass
            return False

    try:
        data = (PVERSION, time.time(), actions)
        dump(data, open(pckname, 'wb'), -1)
    except (OSError, IOError, TypeError, cPickle.PickleError):
        try:
            os.remove(pckname)
        except:
            pass

    return False

def _rolledUpFactory(factories):
    # This has to be named 'factory', aparently, so as not to confuse
    # apidoc :(
    def factory(ob):
        for f in factories:
            ob = f(ob)
        return ob
    # Store the original factory for documentation
    factory.factory = factories[0]
    return factory
