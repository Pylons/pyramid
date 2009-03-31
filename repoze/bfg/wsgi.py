from cgi import escape

try:
    from functools import wraps
except ImportError:
    # < 2.5
    from repoze.bfg.functional import wraps

def wsgiapp(wrapped):
    """ Decorator to turn a WSGI application into a repoze.bfg view callable.

    E.g.::

      @wsgiapp
      def hello_world(environ, start_response):
          body = 'Hello world'
          start_response('200 OK', [ ('Content-Type', 'text/plain'),
                                     ('Content-Length', len(body)) ] )
          return [body]

    Allows the following view declaration to be made::

       <view
          view=".views.hello_world"
          name="hello_world.txt"
          context="*"
        />

    The wsgiapp decorator will convert the result of the WSGI
    application to a Response and return it to repoze.bfg as if the
    WSGI app were a repoze.bfg view.
    """
    def decorator(context, request):
        return request.get_response(wrapped)
    return wraps(wrapped)(decorator) # pickleability

class HTTPException(object):
    def __call__(self, environ, start_response, exc_info=False):
        try:
            msg = escape(environ['message'])
        except KeyError:
            msg = ''
        html = """<body>
        <html><title>%s</title><body><h1>%s</h1>
        <code>%s</code>
        """ % (self.status, self.status, msg)
        headers = [('Content-Length', str(len(html))),
                   ('Content-Type', 'text/html')]
        start_response(self.status, headers)
        return [html]

class NotFound(HTTPException):
    """ The default NotFound WSGI application """
    status = '404 Not Found'

class Unauthorized(HTTPException):
    """ The default Unauthorized WSGI application """
    status = '401 Unauthorized'
