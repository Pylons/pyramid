from webob.exc import HTTPFound

from routes import url_for

from repoze.bfg.chameleon_zpt import render_template_to_response

from repoze.bfg.security import remember
from repoze.bfg.security import forget

from tutorial.run import USERS

def login(context, request):
    login_url = url_for('login')
    referrer = request.environ.get('HTTP_REFERER', '/')
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

    return render_template_to_response(
        'templates/login.pt',
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        request  =request,
        )
    
def logout(context, request):
    headers = forget(request)
    return HTTPFound(location = url_for('view_wiki'),
                     headers = headers)
    
