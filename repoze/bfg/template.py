from zope.interface import classProvides
from zope.interface import implements

from z3c.pt import PageTemplateFile as PageTemplateFileBase
from webob import Response

from repoze.bfg.interfaces import IViewFactory
from repoze.bfg.interfaces import IView


class PageTemplateFile(PageTemplateFileBase):
    def render(self, *arg, **kw):
        result = PageTemplateFileBase.render(self, *arg, **kw)
        return Response(result)

class ViewPageTemplateFile(property):
    def __init__(self, filename, **kwargs):
        self.template = PageTemplateFile(filename, **kwargs)
        property.__init__(self, self.render)

    def render(self, view):
        def template(**kwargs):
            return self.template.render(view=view,
                                        context=view.context,
                                        request=view.request,
                                        options=kwargs)
        return template        
    
class TemplateView(object):
    classProvides(IViewFactory)
    implements(IView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *arg, **kw):
        """ See metaconfigure.py to see where 'index' comes from """
        return self.index(*arg, **kw)

