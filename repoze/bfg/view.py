from repoze.bfg.template import render_template

class View(object):
    """ Convenience base class for user-defined views """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, **kw):
        raise NotImplementedError

class TemplateView(View):
    template = None
    def __call__(self, **kw):
        if self.template is None:
            raise ValueError('a "template" attribute must be attached to '
                             'a TemplateView')
        return render_template(self, self.template, **kw)

    def __repr__(self):
        klass = self.__class__
        return '<%s.%s object at %s for %s>' % (klass.__module__,
                                                klass.__mame__,
                                                id(self),
                                                self.template)

    
