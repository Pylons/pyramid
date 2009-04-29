from cgi import escape

try:
    from functools import wraps
except ImportError:                         #pragma NO COVERAGE
    # < 2.5
    from repoze.bfg.functional import wraps #pragma NO COVERAGE

from repoze.bfg.traversal import quote_path_segment

def wsgiapp(wrapped):
    """ Decorator to turn a WSGI application into a repoze.bfg view
    callable.  This decorator differs from the `wsgiapp2`` decorator
    inasmuch as fixups of ``PATH_INFO`` and ``SCRIPT_NAME`` within the
    WSGI environment *are not* performed before the application is
    invoked.

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

def wsgiapp2(wrapped):
    """ Decorator to turn a WSGI application into a repoze.bfg view
    callable.  This decorator differs from the `wsgiapp`` decorator
    inasmuch as fixups of ``PATH_INFO`` and ``SCRIPT_NAME`` within the
    WSGI environment *are* performed before the application is
    invoked.

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
    WSGI app were a repoze.bfg view.  The ``SCRIPT_NAME`` and
    ``PATH_INFO`` values present in the WSGI environment are fixed up
    before the application is invoked.
    """
    def decorator(context, request):
        traversed = request.traversed
        if traversed is not None:
            # We need to fix up PATH_INFO and SCRIPT_NAME to give the
            # subapplication the right information, sans the info it
            # took to traverse here.  If ``traversed`` is None here,
            # it means that no traversal was done.  For example, it
            # will be None in the case that the context is one
            # obtained via a Routes match (Routes 'traversal' doesn't
            # actually traverse).  If this view is invoked on a Routes
            # context, this fixup is not invoked.  Instead, the route
            # used to reach it should use *path_info in the actual
            # route pattern to get a similar fix-up done.
            vroot_path = request.virtual_root_path or []
            view_name = request.view_name
            subpath = request.subpath or []
            script_list = traversed[len(vroot_path):]
            script_list = [ quote_path_segment(name) for name in script_list ]
            if view_name:
                script_list.append(quote_path_segment(view_name))
            script_name =  '/' + '/'.join(script_list)
            path_list = [ quote_path_segment(name) for name in subpath ]
            path_info = '/' + '/'.join(path_list)
            request.environ['PATH_INFO'] = path_info
            script_name = request.environ['SCRIPT_NAME'] + script_name
            if script_name.endswith('/'):
                script_name = script_name[:-1]
            request.environ['SCRIPT_NAME'] = script_name
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
