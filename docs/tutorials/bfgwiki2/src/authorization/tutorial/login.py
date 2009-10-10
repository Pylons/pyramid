from webob.exc import HTTPFound

from repoze.bfg.security import remember
from repoze.bfg.security import forget
from repoze.bfg.url import route_url

from tutorial.security import USERS

def login(request):
    login_url = route_url('login', request)
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
    
def logout(request):
    headers = forget(request)
    return HTTPFound(location = route_url('view_wiki', request),
                     headers = headers)
    
