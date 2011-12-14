import os
import sys
from code import interact

from paste.deploy import loadapp
from paste.script.command import Command
from paste.script.templates import Template
from paste.util.template import paste_script_template_renderer

from pyramid.scripting import get_root

class PyramidTemplate(Template):
    def pre(self, command, output_dir, vars): # pragma: no cover
        vars['random_string'] = os.urandom(20).encode('hex')
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        return Template.pre(self, command, output_dir, vars)

class StarterProjectTemplate(PyramidTemplate):
    _template_dir = 'paster_templates/starter'
    summary = 'pyramid starter project'
    template_renderer = staticmethod(paste_script_template_renderer)

class ZODBProjectTemplate(PyramidTemplate):
    _template_dir = 'paster_templates/zodb'
    summary = 'pyramid ZODB starter project'
    template_renderer = staticmethod(paste_script_template_renderer)

class RoutesAlchemyProjectTemplate(PyramidTemplate):
    _template_dir = 'paster_templates/routesalchemy'
    summary = 'pyramid SQLAlchemy project using url dispatch (no traversal)'
    template_renderer = staticmethod(paste_script_template_renderer)

class AlchemyProjectTemplate(PyramidTemplate):
    _template_dir = 'paster_templates/alchemy'
    summary = 'pyramid SQLAlchemy project using traversal'
    template_renderer = staticmethod(paste_script_template_renderer)

def get_app(config_file, name, loadapp=loadapp):
    """ Return the WSGI application named ``name`` in the PasteDeploy
    config file ``config_file``"""
    config_name = 'config:%s' % config_file
    here_dir = os.getcwd()
    app = loadapp(config_name, name=name, relative_to=here_dir)
    return app

_marker = object()

class PCommand(Command):
    get_app = staticmethod(get_app) # hook point
    get_root = staticmethod(get_root) # hook point
    group_name = 'pyramid'
    interact = (interact,) # for testing
    loadapp = (loadapp,) # for testing
    verbose = 3

    def __init__(self, *arg, **kw):
        # needs to be in constructor to support Jython (used to be at class
        # scope as ``usage = '\n' + __doc__``.
        self.usage = '\n' + self.__doc__
        Command.__init__(self, *arg, **kw)

class PShellCommand(PCommand):
    """Open an interactive shell with a :app:`Pyramid` app loaded.

    This command accepts two positional arguments:

    ``config_file`` -- specifies the PasteDeploy config file to use
    for the interactive shell.  

    ``section_name`` -- specifies the section name in the PasteDeploy
    config file that represents the application.

    Example::

        $ paster pshell myapp.ini main

    .. note:: You should use a ``section_name`` that refers to the
              actual ``app`` section in the config file that points at
              your Pyramid app without any middleware wrapping, or this
              command will almost certainly fail.

    """
    summary = "Open an interactive shell with a pyramid app loaded"

    min_args = 2
    max_args = 2

    parser = Command.standard_parser(simulate=True)
    parser.add_option('-d', '--disable-ipython',
                      action='store_true',
                      dest='disable_ipython',
                      help="Don't use IPython even if it is available")

    def command(self, IPShell=_marker):
        if IPShell is _marker:
            try: #pragma no cover
                from IPython.Shell import IPShell
            except ImportError: #pragma no cover
                IPShell = None
        cprt =('Type "help" for more information. "root" is the Pyramid app '
               'root object, "registry" is the Pyramid registry object.')
        banner = "Python %s on %s\n%s" % (sys.version, sys.platform, cprt)
        config_file, section_name = self.args
        self.logging_file_config(config_file)
        app = self.get_app(config_file, section_name, loadapp=self.loadapp[0])
        root, closer = self.get_root(app)
        shell_globals = {'root':root, 'registry':app.registry}
        if IPShell is not None and not self.options.disable_ipython:
            try:
                shell = IPShell(argv=[], user_ns=shell_globals)
                shell.IP.BANNER = shell.IP.BANNER + '\n\n' + banner
                shell.mainloop()
            finally:
                closer()
        else:
            try:
                self.interact[0](banner, local=shell_globals)
            finally:
                closer()

BFGShellCommand = PShellCommand # b/w compat forever

class PRoutesCommand(PCommand):
    """Print all URL dispatch routes used by a Pyramid application in the
    order in which they are evaluated.  Each route includes the name of the
    route, the pattern of the route, and the view callable which will be
    invoked when the route is matched.

    This command accepts two positional arguments:

    ``config_file`` -- specifies the PasteDeploy config file to use
    for the interactive shell.  

    ``section_name`` -- specifies the section name in the PasteDeploy
    config file that represents the application.

    Example::

        $ paster proutes myapp.ini main

    .. note:: You should use a ``section_name`` that refers to the
              actual ``app`` section in the config file that points at
              your Pyramid app without any middleware wrapping, or this
              command will almost certainly fail.
    """
    summary = "Print all URL dispatch routes related to a Pyramid application"
    min_args = 2
    max_args = 2
    stdout = sys.stdout

    parser = Command.standard_parser(simulate=True)

    def _get_mapper(self, app):
        from pyramid.config import Configurator
        registry = app.registry
        config = Configurator(registry = registry)
        return config.get_routes_mapper()

    def out(self, msg): # pragma: no cover
        print msg
    
    def command(self):
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IView
        from zope.interface import Interface
        config_file, section_name = self.args
        app = self.get_app(config_file, section_name, loadapp=self.loadapp[0])
        registry = app.registry
        mapper = self._get_mapper(app)
        if mapper is not None:
            routes = mapper.get_routes()
            fmt = '%-15s %-30s %-25s'
            if not routes:
                return
            self.out(fmt % ('Name', 'Pattern', 'View'))
            self.out(
                fmt % ('-'*len('Name'), '-'*len('Pattern'), '-'*len('View')))
            for route in routes:
                request_iface = registry.queryUtility(IRouteRequest,
                                                      name=route.name)
                view_callable = None
                if (request_iface is None) or (route.factory is not None):
                    self.out(fmt % (route.name, route.pattern, '<unknown>'))
                else:
                    view_callable = registry.adapters.lookup(
                        (IViewClassifier, request_iface, Interface),
                        IView, name='', default=None)
                    self.out(fmt % (route.name, route.pattern, view_callable))

# For paste.deploy server instantiation (egg:pyramid#wsgiref)
def wsgiref_server_runner(wsgi_app, global_conf, **kw): # pragma: no cover
    from wsgiref.simple_server import make_server
    host = kw.get('host', '0.0.0.0')
    port = int(kw.get('port', 8080))
    server = make_server(host, port, wsgi_app)
    print('Starting HTTP server on http://%s:%s' % (host, port))
    server.serve_forever()

# For paste.deploy server instantiation (egg:pyramid#cherrypy)
def cherrypy_server_runner(
        app, global_conf=None, host='127.0.0.1', port=None,
        ssl_pem=None, protocol_version=None, numthreads=None,
        server_name=None, max=None, request_queue_size=None,
        timeout=None
        ): # pragma: no cover
    """
    Entry point for CherryPy's WSGI server

    Serves the specified WSGI app via CherryPyWSGIServer.

    ``app``

        The WSGI 'application callable'; multiple WSGI applications
        may be passed as (script_name, callable) pairs.

    ``host``

        This is the ipaddress to bind to (or a hostname if your
        nameserver is properly configured).  This defaults to
        127.0.0.1, which is not a public interface.

    ``port``

        The port to run on, defaults to 8080 for HTTP, or 4443 for
        HTTPS. This can be a string or an integer value.

    ``ssl_pem``

        This an optional SSL certificate file (via OpenSSL) You can
        generate a self-signed test PEM certificate file as follows:

            $ openssl genrsa 1024 > host.key
            $ chmod 400 host.key
            $ openssl req -new -x509 -nodes -sha1 -days 365  \\
                          -key host.key > host.cert
            $ cat host.cert host.key > host.pem
            $ chmod 400 host.pem

    ``protocol_version``

        The protocol used by the server, by default ``HTTP/1.1``.

    ``numthreads``

        The number of worker threads to create.

    ``server_name``

        The string to set for WSGI's SERVER_NAME environ entry.

    ``max``

        The maximum number of queued requests. (defaults to -1 = no
        limit).

    ``request_queue_size``

        The 'backlog' argument to socket.listen(); specifies the
        maximum number of queued connections.

    ``timeout``

        The timeout in seconds for accepted connections.
    """
    is_ssl = False
    if ssl_pem:
        port = port or 4443
        is_ssl = True

    if not port:
        if ':' in host:
            host, port = host.split(':', 1)
        else:
            port = 8080
    bind_addr = (host, int(port))

    kwargs = {}
    for var_name in ('numthreads', 'max', 'request_queue_size', 'timeout'):
        var = locals()[var_name]
        if var is not None:
            kwargs[var_name] = int(var)

    from cherrypy import wsgiserver

    server = wsgiserver.CherryPyWSGIServer(bind_addr, app,
                                           server_name=server_name, **kwargs)
    server.ssl_certificate = server.ssl_private_key = ssl_pem
    if protocol_version:
        server.protocol = protocol_version

    try:
        protocol = is_ssl and 'https' or 'http'
        if host == '0.0.0.0':
            print('serving on 0.0.0.0:%s view at %s://127.0.0.1:%s' % 
                  (port, protocol, port))
        else:
            print('serving on %s://%s:%s' % (protocol, host, port))
        server.start()
    except (KeyboardInterrupt, SystemExit):
        server.stop()

    return server
