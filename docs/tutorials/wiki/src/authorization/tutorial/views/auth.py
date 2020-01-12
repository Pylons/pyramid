from pyramid.httpexceptions import HTTPSeeOther
from pyramid.security import (
    forget,
    remember,
)
from pyramid.view import (
    forbidden_view_config,
    view_config,
)

from ..security import check_password, USERS


@view_config(context='..models.Wiki', name='login',
             renderer='tutorial:templates/login.pt')
@forbidden_view_config(renderer='tutorial:templates/login.pt')
def login(request):
    login_url = request.resource_url(request.root, 'login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/'  # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if check_password(USERS.get(login), password):
            headers = remember(request, login)
            return HTTPSeeOther(location=came_from, headers=headers)
        message = 'Failed login'

    return dict(
        message=message,
        url=login_url,
        came_from=came_from,
        login=login,
        password=password,
        title='Login',
    )


@view_config(context='..models.Wiki', name='logout')
def logout(request):
    headers = forget(request)
    return HTTPSeeOther(
        location=request.resource_url(request.context),
        headers=headers,
    )
