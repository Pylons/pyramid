from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.view import static

static_view = static('templates/static')

def my_view(context, request):
    return render_template_to_response('templates/mytemplate.pt',
                                       request = request,
                                       project = 'MyProject')
