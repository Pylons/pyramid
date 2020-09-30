from pyramid.scripting import prepare
from pyramid.scripts.common import get_config_loader


def setup_logging(config_uri, global_conf=None):
    """
    Set up Python logging with the filename specified via ``config_uri``
    (a string in the form ``filename#sectionname``).

    Extra defaults can optionally be specified as a dict in ``global_conf``.
    """
    loader = get_config_loader(config_uri)
    loader.setup_logging(global_conf)


def get_app(config_uri, name=None, options=None):
    """Return the WSGI application named ``name`` in the PasteDeploy
    config file specified by ``config_uri``.

    ``options``, if passed, should be a dictionary used as variable assignments
    like ``{'http_port': 8080}``.  This is useful if e.g. ``%(http_port)s`` is
    used in the config file.

    If the ``name`` is None, this will attempt to parse the name from
    the ``config_uri`` string expecting the format ``inifile#name``.
    If no name is found, the name will default to "main".

    """
    loader = get_config_loader(config_uri)
    return loader.get_wsgi_app(name, options)


def get_appsettings(config_uri, name=None, options=None):
    """Return a dictionary representing the key/value pairs in an ``app``
    section within the file represented by ``config_uri``.

    ``options``, if passed, should be a dictionary used as variable assignments
    like ``{'http_port': 8080}``.  This is useful if e.g. ``%(http_port)s`` is
    used in the config file.

    If the ``name`` is None, this will attempt to parse the name from
    the ``config_uri`` string expecting the format ``inifile#name``.
    If no name is found, the name will default to "main".

    """
    loader = get_config_loader(config_uri)
    return loader.get_wsgi_app_settings(name, options)


def bootstrap(config_uri, request=None, options=None):
    """Load a WSGI application from the PasteDeploy config file specified
    by ``config_uri``. The environment will be configured as if it is
    currently serving ``request``, leaving a natural environment in place
    to write scripts that can generate URLs and utilize renderers.

    This function returns a dictionary with ``app``, ``root``, ``closer``,
    ``request``, and ``registry`` keys.  ``app`` is the WSGI app loaded
    (based on the ``config_uri``), ``root`` is the traversal root resource
    of the Pyramid application, and ``closer`` is a parameterless callback
    that may be called when your script is complete (it pops a threadlocal
    stack).

    .. note::

       Most operations within :app:`Pyramid` expect to be invoked within the
       context of a WSGI request, thus it's important when loading your
       application to anchor it when executing scripts and other code that is
       not normally invoked during active WSGI requests.

    .. note::

       For a complex config file containing multiple :app:`Pyramid`
       applications, this function will setup the environment under the context
       of the last-loaded :app:`Pyramid` application. You may load a specific
       application yourself by using the lower-level functions
       :meth:`pyramid.paster.get_app` and :meth:`pyramid.scripting.prepare` in
       conjunction with :attr:`pyramid.config.global_registries`.

    ``config_uri`` -- specifies the PasteDeploy config file to use for the
    interactive shell. The format is ``inifile#name``. If the name is left
    off, ``main`` will be assumed.

    ``request`` -- specified to anchor the script to a given set of WSGI
    parameters. For example, most people would want to specify the host,
    scheme and port such that their script will generate URLs in relation
    to those parameters. A request with default parameters is constructed
    for you if none is provided. You can mutate the request's ``environ``
    later to setup a specific host/port/scheme/etc.

    ``options`` Is passed to get_app for use as variable assignments like
    {'http_port': 8080} and then use %(http_port)s in the
    config file.

    This function may be used as a context manager to call the ``closer``
    automatically:

    .. code-block:: python

       with bootstrap('development.ini') as env:
           request = env['request']
           # ...

    See :ref:`writing_a_script` for more information about how to use this
    function.

    .. versionchanged:: 1.8

       Added the ability to use the return value as a context manager.

    .. versionchanged:: 2.0

       Request finished callbacks added via
       :meth:`pyramid.request.Request.add_finished_callback` will be invoked
       by the ``closer``.

    """
    app = get_app(config_uri, options=options)
    env = prepare(request)
    env['app'] = app
    return env
