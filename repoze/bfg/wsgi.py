from webob import Response
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
        caught = []
        def catch_start_response(status, headers, exc_info=None):
            caught[:] = (status, headers, exc_info)
        environ = request.environ
        body = wrapped(environ, catch_start_response)
        if caught: 
            status, headers, exc_info = caught
            response = Response()
            response.app_iter = body
            response.status = status
            response.headerlist = headers
            return response
        else:
            raise RuntimeError('WSGI start_response not called')
    return wraps(wrapped)(decorator) # for pickleability
    
