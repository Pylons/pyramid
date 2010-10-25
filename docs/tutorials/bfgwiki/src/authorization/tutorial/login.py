from webob.exc import HTTPFound

from pyramid.view import bfg_view
from pyramid.url import model_url

from pyramid.security import remember
from pyramid.security import forget

from tutorial.models import Wiki
from tutorial.security import USERS

@bfg_view(context=Wiki, name='login', renderer='templates/login.pt')
def login(request):
    login_url = model_url(request.context, request, 'login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
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

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        )
    
@bfg_view(context=Wiki, name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = model_url(request.context, request),
                     headers = headers)
    
