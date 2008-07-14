import os

from zope.component.zcml import handler
from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Path

from zope.schema import TextLine
from zope.interface import Interface
from zope.interface import implements

from zope.security.zcml import Permission

from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IViewFactory
from repoze.bfg.interfaces import IView

from repoze.bfg.template import Z3CPTTemplateFactory
from repoze.bfg.view import TemplateView

class TemplateViewFactory(object):
    """ Pickleable template view factory """

    implements(IViewFactory)

    def __init__(self, template):
        self.template = template

    def __call__(self, context, request):
        factory = TemplateView(context, request)
        factory.template = self.template
        return factory
        
def view(_context,
         permission,
         for_=None,
         factory=None,
         name="",
         template=None,
         ):

    # XXX we do nothing yet with permission

    if template and factory:
        raise ConfigurationError('A template must not be specified if a '
                                 'factory is also specified')

    if not (template or factory):
        raise ConfigurationError(
            'One of template or factory must be specified')
        

    if template:
        template_abs = os.path.abspath(str(_context.path(template)))
        if not os.path.exists(template_abs):
            raise ConfigurationError('No template file named %s' % template_abs)
        utility = Z3CPTTemplateFactory(template_abs)
        _context.action(
            discriminator = ('utility', IView, template_abs),
            callable = handler,
            args = ('registerUtility', utility, IView, template_abs),
            )
        factory = TemplateViewFactory(template_abs)

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
                factory, (for_, IRequest), IViewFactory, name,
                _context.info),
        )

class IViewDirective(Interface):
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

    factory = GlobalObject(
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
        description=u"""Refers to a file containing a z3c.pt page template""",
        required=False
        )


