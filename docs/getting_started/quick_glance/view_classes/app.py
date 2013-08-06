from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.view import view_config


class HelloWorldViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='hello', renderer='app4.jinja2')
    def hello_world(self):
        return dict(name=self.request.matchdict['name'])


    @view_config(route_name='hello_json', renderer='json')
    def hello_json(self):
        return [1, 2, 3]


if __name__ == '__main__':
    config = Configurator()
    config.add_route('hello', '/howdy/{name}')
    config.add_route('hello_json', 'hello.json')
    config.add_static_view(name='static', path='static')
    config.include('pyramid_jinja2')
    config.scan()
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()