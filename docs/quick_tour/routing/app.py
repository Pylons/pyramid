from wsgiref.simple_server import make_server
from pyramid.config import Configurator

if __name__ == '__main__':
    config = Configurator()
    # Start Route 1
    config.add_route('hello', '/howdy/{first}/{last}')
    # End Route 1
    config.scan('views')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()