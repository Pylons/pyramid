from pyramid.httpexceptions import HTTPFound

from pyramid.security import remember
from pyramid.security import forget
from pyramid.view import view_config

from tutorial.security import USERS

@view_config(context='tutorial.models.Wiki', name='login',
             renderer='templates/login.pt')
@view_config(context='pyramid.httpexceptions.HTTPForbidden',
             renderer='templates/login.pt')
def login(request):
    login_url = request.resource_url(request.context, 'login')
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
    
@view_config(context='tutorial.models.Wiki', name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.resource_url(request.context),
                     headers = headers)
    
