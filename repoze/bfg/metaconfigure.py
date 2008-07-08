import os

from zope.schema import TextLine
from zope.configuration.fields import Path
from zope.interface import Interface
from zope.component.zcml import handler
from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject
from zope.security.zcml import Permission

from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IViewFactory

from repoze.bfg.template import ViewPageTemplateFile

class ViewBase:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *arg, **kw):
        return self.index(*arg, **kw)

def page(_context,
         permission,
         for_,
         name="",
         template=None,
         class_=None,
         ):

    # XXX we do nothing yet with permission

    if not (class_ or template):
        raise ConfigurationError("Must specify a class or a template")

    if template:
        template = os.path.abspath(str(_context.path(template)))
        if not os.path.isfile(template):
            raise ConfigurationError("No such file", template)

    def view_factory(context, request):
        if template:
            if class_ is None:
                base = ViewBase
            else:
                base = class_
            class ViewClass(base):
                __name__ = name
                index = ViewPageTemplateFile(template)
            return ViewClass(context, request)
                    
        else:
            return class_(context, request)
        
    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )

    _context.action(
        discriminator = ('view', for_, name, IRequest, IViewFactory),
        callable = handler,
        args = ('registerAdapter',
                view_factory, (for_, IRequest), IViewFactory, name,
                _context.info),
        )

class IPageDirective(Interface):
    """
    The page directive is used to create views that provide a single
    url or page.

    The page directive creates a new view class from a given template
    and/or class and registers it.
    """

    for_ = GlobalObject(
        title=u"The interface or class this view is for.",
        required=False
        )

    permission = Permission(
        title=u"Permission",
        description=u"The permission needed to use the view.",
        required=True
        )

    class_ = GlobalObject(
        title=u"Class",
        description=u"A class that provides a __call__ used by the view.",
        required=False,
        )

    name = TextLine(
        title=u"The name of the page (view)",
        description=u"""
        The name shows up in URLs/paths. For example 'foo' or
        'foo.html'.""",
        required=False,
        )

    template = Path(
        title=u"The name of a template that implements the page.",
        description=u"""
        Refers to a file containing a page template (should end in
        extension '.pt' or '.html').""",
        required=False
        )

