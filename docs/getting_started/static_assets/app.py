from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config


@view_config(route_name='hello', renderer='app4.jinja2')
def hello_world(request):
    return dict(name=request.matchdict['name'])


if __name__ == '__main__':
    config = Configurator()
    config.add_route('hello', '/hello/{name}')
    config.add_static_view(name='static', path='static')
    config.include('pyramid_jinja2')
    config.scan()
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()