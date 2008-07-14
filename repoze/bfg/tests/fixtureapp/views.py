from repoze.bfg.view import TemplateView

class FixtureView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        pass
    
class FixtureTemplateView(TemplateView):
    pass
