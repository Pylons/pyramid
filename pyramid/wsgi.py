from repoze.bfg.compat import wraps
from repoze.bfg.traversal import quote_path_segment

def wsgiapp(wrapped):
    """ Decorator to turn a WSGI application into a :mod:`repoze.bfg`
    :term:`view callable`.  This decorator differs from the
    :func:`repoze.bfg.wsgi.wsgiapp2` decorator inasmuch as fixups of
    ``PATH_INFO`` and ``SCRIPT_NAME`` within the WSGI environment *are
    not* performed before the application is invoked.

    E.g., the following in a ``views.py`` module::

      @wsgiapp
      def hello_world(environ, start_response):
          body = 'Hello world'
          start_response('200 OK', [ ('Content-Type', 'text/plain'),
                                     ('Content-Length', len(body)) ] )
          return [body]

    Allows the following ZCML view declaration to be made::

       <view
          view=".views.hello_world"
          name="hello_world.txt"
        />

    Or the following call to
    :meth:`repoze.bfg.configuration.Configurator.add_view`::

        from views import hello_world
        config.add_view(hello_world, name='hello_world.txt')

    The ``wsgiapp`` decorator will convert the result of the WSGI
    application to a :term:`Response` and return it to
    :mod:`repoze.bfg` as if the WSGI app were a :mod:`repoze.bfg`
    view.
    
    """
    def decorator(context, request):
        return request.get_response(wrapped)
    return wraps(wrapped)(decorator) # grokkability

def wsgiapp2(wrapped):
    """ Decorator to turn a WSGI application into a :mod:`repoze.bfg`
    view callable.  This decorator differs from the
    :func:`repoze.bfg.wsgi.wsgiapp` decorator inasmuch as fixups of
    ``PATH_INFO`` and ``SCRIPT_NAME`` within the WSGI environment
    *are* performed before the application is invoked.

    E.g. the following in a ``views.py`` module::

      @wsgiapp2
      def hello_world(environ, start_response):
          body = 'Hello world'
          start_response('200 OK', [ ('Content-Type', 'text/plain'),
                                     ('Content-Length', len(body)) ] )
          return [body]

    Allows the following ZCML view declaration to be made::

       <view
          view=".views.hello_world"
          name="hello_world.txt"
        />

    Or the following call to
    :meth:`repoze.bfg.configuration.Configurator.add_view`::

        from views import hello_world
        config.add_view(hello_world, name='hello_world.txt')

    The ``wsgiapp2`` decorator will convert the result of the WSGI
    application to a Response and return it to :mod:`repoze.bfg` as if
    the WSGI app were a :mod:`repoze.bfg` view.  The ``SCRIPT_NAME``
    and ``PATH_INFO`` values present in the WSGI environment are fixed
    up before the application is invoked.  """
    
    def decorator(context, request):
        traversed = request.traversed
        vroot_path = request.virtual_root_path or ()
        view_name = request.view_name
        subpath = request.subpath or ()
        script_tuple = traversed[len(vroot_path):]
        script_list = [ quote_path_segment(name) for name in script_tuple ]
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
    return wraps(wrapped)(decorator) # grokkability

