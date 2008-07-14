import os
import sys

from zope.component import queryUtility
from zope.component.interfaces import ComponentLookupError
from zope.component import getSiteManager

from zope.interface import classProvides
from zope.interface import implements

from webob import Response

from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import ITemplateFactory

class Z3CPTTemplateFactory(object):
    classProvides(ITemplateFactory)
    implements(IView)

    def __init__(self, path):
        from z3c.pt import PageTemplateFile
        self.template = PageTemplateFile(path)

    def __call__(self, *arg, **kw):
        result = self.template.render(**kw)
        response = Response(result)
        return response

def package_path(package):
    return os.path.abspath(os.path.dirname(package.__file__))

def render_template(view, template_path, **kw):
    # XXX use pkg_resources

    if not os.path.isabs(template_path):
        package_globals = sys._getframe(1).f_globals
        package_name = package_globals['__name__']
        package = sys.modules[package_name]
        prefix = package_path(package)
        template_path = os.path.join(prefix, template_path)

    template = queryUtility(IView, template_path)

    if template is None:
        if not os.path.exists(template_path):
            raise ValueError('Missing template file: %s' % template_path)
        template = Z3CPTTemplateFactory(template_path)
        try:
            sm = getSiteManager()
        except ComponentLookupError:
            pass
        else:
            sm.registerUtility(template, IView, name=template_path)

    return template(view=view, context=view.context, request=view.request,
                    options=kw)
