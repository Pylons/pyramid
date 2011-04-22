from pyramid.compat import wraps
from pyramid.request import call_app_subpath_as_path_info

def wsgiapp(wrapped):
    """ Decorator to turn a WSGI application into a :app:`Pyramid`
    :term:`view callable`.  This decorator differs from the
    :func:`pyramid.wsgi.wsgiapp2` decorator inasmuch as fixups of
    ``PATH_INFO`` and ``SCRIPT_NAME`` within the WSGI environment *are
    not* performed before the application is invoked.

    E.g., the following in a ``views.py`` module::

      @wsgiapp
      def hello_world(environ, start_response):
          body = 'Hello world'
          start_response('200 OK', [ ('Content-Type', 'text/plain'),
                                     ('Content-Length', len(body)) ] )
          return [body]

    Allows the following call to
    :meth:`pyramid.config.Configurator.add_view`::

        from views import hello_world
        config.add_view(hello_world, name='hello_world.txt')

    The ``wsgiapp`` decorator will convert the result of the WSGI
    application to a :term:`Response` and return it to
    :app:`Pyramid` as if the WSGI app were a :mod:`pyramid`
    view.

    """
    def decorator(context, request):
        return request.get_response(wrapped)
    return wraps(wrapped)(decorator) # grokkability

def wsgiapp2(wrapped):
    """ Decorator to turn a WSGI application into a :app:`Pyramid`
    view callable.  This decorator differs from the
    :func:`pyramid.wsgi.wsgiapp` decorator inasmuch as fixups of
    ``PATH_INFO`` and ``SCRIPT_NAME`` within the WSGI environment
    *are* performed before the application is invoked.

    E.g. the following in a ``views.py`` module::

      @wsgiapp2
      def hello_world(environ, start_response):
          body = 'Hello world'
          start_response('200 OK', [ ('Content-Type', 'text/plain'),
                                     ('Content-Length', len(body)) ] )
          return [body]

    Allows the following call to
    :meth:`pyramid.config.Configurator.add_view`::

        from views import hello_world
        config.add_view(hello_world, name='hello_world.txt')

    The ``wsgiapp2`` decorator will convert the result of the WSGI
    application to a Response and return it to :app:`Pyramid` as if
    the WSGI app were a :app:`Pyramid` view.  The ``SCRIPT_NAME``
    and ``PATH_INFO`` values present in the WSGI environment are fixed
    up before the application is invoked.  """

    def decorator(context, request):
        return call_app_subpath_as_path_info(request, wrapped)
    return wraps(wrapped)(decorator)

