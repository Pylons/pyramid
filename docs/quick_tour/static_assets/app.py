from wsgiref.simple_server import make_server
from pyramid.config import Configurator

if __name__ == '__main__':
    config = Configurator()
    config.add_route('hello', '/howdy/{name}')
    config.add_static_view(name='static', path='static')
    config.include('pyramid_jinja2')
    config.scan('views')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()
