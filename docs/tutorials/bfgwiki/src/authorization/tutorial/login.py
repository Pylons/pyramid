from webob.exc import HTTPFound

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.view import bfg_view
from repoze.bfg.url import model_url

from repoze.bfg.security import remember
from repoze.bfg.security import forget

from tutorial.models import Wiki
from tutorial.run import USERS

@bfg_view(for_=Wiki, name='login')
def login(context, request):
    referrer = request.environ.get('HTTP_REFERER', '/')
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if USERS.get(login) == password:
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return render_template_to_response(
        'templates/login.pt',
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        request  =request,
        )
    
@bfg_view(for_=Wiki, name='logout')
def logout(context, request):
    headers = forget(request)
    return HTTPFound(location = model_url(context, request),
                     headers = headers)
    
