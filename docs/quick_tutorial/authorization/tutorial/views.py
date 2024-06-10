from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
)

from pyramid.view import (
    view_config,
    view_defaults,
    forbidden_view_config
)

from .security import (
    USERS,
    check_password
)


@view_defaults(renderer='home.pt')
class TutorialViews:
    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid

    @view_config(route_name='home')
    def home(self):
        return {'name': 'Home View'}

    @view_config(route_name='hello', permission='edit')
    def hello(self):
        return {'name': 'Hello View'}

    @forbidden_view_config()
    def forbidden(self):
        request = self.request
        session = request.session
        if request.matched_route is not None:
            session['came_from'] = {
                'route_name': request.matched_route.name,
                'route_kwargs': request.matchdict,
            }
            if request.authenticated_userid is not None:
                session['message'] = (
                    f'User {request.authenticated_userid} is not allowed '
                    f'to see this resource.  Please log in as another user.'
                )
        else:
            if 'came_from' in session:
                del session['came_from']

        return HTTPFound(request.route_url('login'))

    @view_config(route_name='login', renderer='login.pt')
    def login(self):
        request = self.request
        session = request.session
        login_url = request.route_url('login')
        came_from = session.get('came_from')
        message = session.get('message', '')
        login = ''
        password = ''

        if 'form.submitted' in request.params:
            login = request.params['login']
            password = request.params['password']
            hashed_pw = USERS.get(login)
            if hashed_pw and check_password(password, hashed_pw):
                headers = remember(request, login)

                if came_from is not None:
                    return_to = request.route_url(
                        came_from['route_name'], **came_from['route_kwargs'],
                    )
                else:
                    return_to = request.route_url('home')

                return HTTPFound(location=return_to, headers=headers)

            message = 'Failed login'

        return dict(
            name='Login',
            message=message,
            url=request.application_url + '/login',
            login=login,
            password=password,
        )

    @view_config(route_name='logout')
    def logout(self):
        request = self.request
        headers = forget(request)
        url = request.route_url('home')
        return HTTPFound(location=url,
                         headers=headers)
