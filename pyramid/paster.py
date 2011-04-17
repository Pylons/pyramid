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

    def post(self, *arg, **kw): # pragma: no cover
        print 'Welcome to Pyramid.  Sorry for the convenience.'
        return Template.post(self, *arg, **kw)

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

class PViewsCommand(PCommand):
    """Print, for a given URL, the views that might match. Underneath each
    potentially matching route, list the predicates required. Underneath
    each route+predicate set, print each view that might match and its
    predicates.

    This command accepts three positional arguments:

    ``config_file`` -- specifies the PasteDeploy config file to use
    for the interactive shell.  

    ``section_name`` -- specifies the section name in the PasteDeploy
    config file that represents the application.

    ``url`` -- specifies the URL that will be used to find matching views.

    Example::

        $ paster proutes myapp.ini main url

    .. note:: You should use a ``section_name`` that refers to the
              actual ``app`` section in the config file that points at
              your Pyramid app without any middleware wrapping, or this
              command will almost certainly fail.
    """
    summary = "Print all views in an application that might match a URL"
    min_args = 3
    max_args = 3
    stdout = sys.stdout

    parser = Command.standard_parser(simulate=True)

    def out(self, msg): # pragma: no cover
        print msg
    
    def _find_view(self, url, registry):
        """
        Accept ``url`` and ``registry``; create a :term:`request` and
        find a :app:`Pyramid` view based on introspection of :term:`view
        configuration` within the application registry; return the view.
        """
        from zope.interface import providedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IRootFactory
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IRequestFactory
        from pyramid.interfaces import IRoutesMapper
        from pyramid.interfaces import ITraverser
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.request import Request
        from pyramid.traversal import DefaultRootFactory
        from pyramid.traversal import ResourceTreeTraverser
            
        q = registry.queryUtility
        root_factory = q(IRootFactory, default=DefaultRootFactory)
        routes_mapper = q(IRoutesMapper)
        request_factory = q(IRequestFactory, default=Request)

        adapters = registry.adapters
        request = None

        # create the request
        environ = {
            'wsgi.url_scheme':'http',
            'SERVER_NAME':'localhost',
            'SERVER_PORT':'8080',
            'REQUEST_METHOD':'GET',
            'PATH_INFO':url,
            }
        request = request_factory(environ)
        context = None
        attrs = request.__dict__
        attrs['registry'] = registry
        request_iface = IRequest

        # find the root object
        root_factory = root_factory
        if routes_mapper is not None:
            info = routes_mapper(request)
            match, route = info['match'], info['route']
            if route is not None:
                attrs['matchdict'] = match
                attrs['matched_route'] = route

                request_iface = registry.queryUtility(
                    IRouteRequest,
                    name=route.name,
                    default=IRequest)
                root_factory = route.factory or root_factory

        root = root_factory(request)
        attrs['root'] = root

        # find a context
        traverser = adapters.queryAdapter(root, ITraverser)
        if traverser is None:
            traverser = ResourceTreeTraverser(root)
        tdict = traverser(request)
        context, view_name, subpath, traversed, vroot, vroot_path =(
            tdict['context'], tdict['view_name'], tdict['subpath'],
            tdict['traversed'], tdict['virtual_root'],
            tdict['virtual_root_path'])
        attrs.update(tdict)

        # find a view callable
        context_iface = providedBy(context)
        view_callable = adapters.lookup(
            (IViewClassifier, request_iface, context_iface),
            IView, name=view_name, default=None)

        return view_callable

    def command(self):
        from pyramid.interfaces import IMultiView

        config_file, section_name, url = self.args
        app = self.get_app(config_file, section_name, loadapp=self.loadapp[0])
        registry = app.registry
        view = self._find_view(url, registry)
        self.out('')
        self.out(url)
        if IMultiView.providedBy(view):
            for dummy, view_wrapper, dummy in view.views:
                self.out('')
                for p in view_wrapper.__predicates__:
                    text = getattr(p, '__text__', p.__name__)
                    self.out("    %s" % text)
                self.out("    %s" % str(view_wrapper.__original_view__))
        else:
            self.out('')
            self.out(view)

