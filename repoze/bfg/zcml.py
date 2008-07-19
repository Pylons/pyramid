import os

from zope.component.zcml import handler
from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Path

from zope.interface import Interface
from zope.interface import implements
from zope.interface import classProvides

from zope.schema import TextLine

from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import ITemplateFactory
from repoze.bfg.interfaces import ITemplate
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import IView

from repoze.bfg.template import Z3CPTTemplateFactory
from repoze.bfg.template import render_template_to_response

from repoze.bfg.security import ViewPermissionFactory

class TemplateOnlyViewFactory(object):
    """ Pickleable template-only view factory """
    classProvides(ITemplateFactory)
    implements(IView)

    def __init__(self, template):
        self.template = template

    def __call__(self, context, request):
        kw = dict(view=self, context=context, request=request)
        return render_template_to_response(self.template, **kw)
        
def view(_context,
         permission=None,
         for_=None,
         view=None,
         name="",
         template=None,
         ):

    if (template and view):
        raise ConfigurationError(
            'One of template or view must be specified, not both')

    if template:
        template_abs = os.path.abspath(str(_context.path(template)))
        if not os.path.exists(template_abs):
            raise ConfigurationError('No template file named %s' % template_abs)
        utility = Z3CPTTemplateFactory(template_abs)
        _context.action(
            discriminator = ('utility', ITemplate, template_abs),
            callable = handler,
            args = ('registerUtility', utility, ITemplate, template_abs),
            )
        view = TemplateOnlyViewFactory(template_abs)

    if not view:
        raise ConfigurationError(
            'Neither template nor factory was specified, though one must be '
            'specified.')

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )

    if permission:
        pfactory = ViewPermissionFactory(permission)
        _context.action(
            discriminator = ('permission', for_,name, IRequest,IViewPermission),
            callable = handler,
            args = ('registerAdapter',
                    pfactory, (for_, IRequest), IViewPermission, name,
                    _context.info),
            )

    _context.action(
        discriminator = ('view', for_, name, IRequest, IView),
        callable = handler,
        args = ('registerAdapter',
                view, (for_, IRequest), IView, name,
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

    template = Path(
        title=u"The name of a template that implements the view.",
        description=u"""Refers to a file containing a z3c.pt page template""",
        required=False
        )


