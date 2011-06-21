import os
import sys
from code import interact

import zope.deprecation

from paste.deploy import loadapp
from paste.script.command import Command

from pyramid.scripting import get_root

from pyramid.scaffolds import PyramidTemplate # bw compat
zope.deprecation.deprecated(
    'PyramidTemplate', ('pyramid.paster.PyramidTemplate was moved to '
                        'pyramid.scaffolds.PyramidTemplate in Pyramid 1.1'),
)

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
    summary = "Open an interactive shell with a Pyramid application loaded"

    min_args = 2
    max_args = 2

    parser = Command.standard_parser(simulate=True)
    parser.add_option('-d', '--disable-ipython',
                      action='store_true',
                      dest='disable_ipython',
                      help="Don't use IPython even if it is available")

    def command(self, IPShell=_marker):
        # IPShell passed to command method is for testing purposes
        if IPShell is _marker: # pragma: no cover
            try:
                from IPython.Shell import IPShell
            except ImportError:
                IPShell = None
        cprt =('Type "help" for more information. "root" is the Pyramid app '
               'root object, "registry" is the Pyramid registry object.')
        banner = "Python %s on %s\n%s" % (sys.version, sys.platform, cprt)
        config_file, section_name = self.args
        self.logging_file_config(config_file)
        app = self.get_app(config_file, section_name, loadapp=self.loadapp[0])
        root, closer = self.get_root(app)
        shell_globals = {'root':root, 'registry':app.registry}

        if (IPShell is None) or self.options.disable_ipython:
            try:
                self.interact[0](banner, local=shell_globals)
            finally:
                closer()
        else:
            try:
                shell = IPShell(argv=[], user_ns=shell_globals)
                shell.IP.BANNER = shell.IP.BANNER + '\n\n' + banner
                shell.mainloop()
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


from pyramid.interfaces import IMultiView

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
    
    def _find_multi_routes(self, mapper, request):
        infos = []
        path = request.environ['PATH_INFO']
        # find all routes that match path, regardless of predicates
        for route in mapper.get_routes():
            match = route.match(path)
            if match is not None:
                info = {'match':match, 'route':route}
                infos.append(info)
        return infos

    def _find_view(self, url, registry):
        """
        Accept ``url`` and ``registry``; create a :term:`request` and
        find a :app:`Pyramid` view based on introspection of :term:`view
        configuration` within the application registry; return the view.
        """
        from zope.interface import providedBy
        from zope.interface import implements
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IRootFactory
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IRequestFactory
        from pyramid.interfaces import IRoutesMapper
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import ITraverser
        from pyramid.request import Request
        from pyramid.traversal import DefaultRootFactory
        from pyramid.traversal import ResourceTreeTraverser
            
        q = registry.queryUtility
        root_factory = q(IRootFactory, default=DefaultRootFactory)
        routes_mapper = q(IRoutesMapper)
        request_factory = q(IRequestFactory, default=Request)

        adapters = registry.adapters
        request = None

        class RoutesMultiView(object):
            implements(IMultiView)

            def __init__(self, infos, context_iface, root_factory, request):
                self.views = []
                for info in infos:
                    match, route = info['match'], info['route']
                    if route is not None:
                        request_iface = registry.queryUtility(
                            IRouteRequest,
                            name=route.name,
                            default=IRequest)
                        view = adapters.lookup(
                            (IViewClassifier, request_iface, context_iface),
                            IView, name='', default=None)
                        if view is None:
                            continue
                        view.__request_attrs__ = {}
                        view.__request_attrs__['matchdict'] = match
                        view.__request_attrs__['matched_route'] = route
                        root_factory = route.factory or root_factory
                        root = root_factory(request)
                        traverser = adapters.queryAdapter(root, ITraverser)
                        if traverser is None:
                            traverser = ResourceTreeTraverser(root)
                        tdict = traverser(request)
                        view.__request_attrs__.update(tdict)
                        if not hasattr(view, '__view_attr__'):
                            view.__view_attr__ = ''
                        self.views.append((None, view, None))


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
        routes_multiview = None
        attrs = request.__dict__
        attrs['registry'] = registry
        request_iface = IRequest

        # find the root object
        if routes_mapper is not None:
            infos = self._find_multi_routes(routes_mapper, request)
            if len(infos) == 1:
                info = infos[0]
                match, route = info['match'], info['route']
                if route is not None:
                    attrs['matchdict'] = match
                    attrs['matched_route'] = route
                    request.environ['bfg.routes.matchdict'] = match
                    request_iface = registry.queryUtility(
                        IRouteRequest,
                        name=route.name,
                        default=IRequest)
                    root_factory = route.factory or root_factory
            if len(infos) > 1:
                routes_multiview = infos

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
        if routes_multiview is None:
            view = adapters.lookup(
                (IViewClassifier, request_iface, context_iface),
                IView, name=view_name, default=None)
        else:
            view = RoutesMultiView(infos, context_iface, root_factory, request)

        # routes are not registered with a view name
        if view is None:
            view = adapters.lookup(
                (IViewClassifier, request_iface, context_iface),
                IView, name='', default=None)
            # we don't want a multiview here
            if IMultiView.providedBy(view):
                view = None

        if view is not None:
            view.__request_attrs__ = attrs

        return view

    def output_route_attrs(self, attrs, indent):
        route = attrs['matched_route']
        self.out("%sroute name: %s" % (indent, route.name))
        self.out("%sroute pattern: %s" % (indent, route.pattern))
        self.out("%sroute path: %s" % (indent, route.path))
        self.out("%ssubpath: %s" % (indent, '/'.join(attrs['subpath'])))
        predicates = ', '.join([p.__text__ for p in route.predicates])
        if predicates != '':
            self.out("%sroute predicates (%s)" % (indent, predicates))

    def output_view_info(self, view_wrapper, level=1):
        indent = "    " * level
        name = getattr(view_wrapper, '__name__', '')
        module = getattr(view_wrapper, '__module__', '')
        attr = getattr(view_wrapper, '__view_attr__', None)
        request_attrs = getattr(view_wrapper, '__request_attrs__', {})
        if attr is not None:
            view_callable = "%s.%s.%s" % (module, name, attr)
        else:
            attr = view_wrapper.__class__.__name__
            if attr == 'function':
                attr = name
            view_callable = "%s.%s" % (module, attr)
        self.out('')
        if 'matched_route' in request_attrs:
            self.out("%sRoute:" % indent)
            self.out("%s------" % indent)
            self.output_route_attrs(request_attrs, indent)
            permission = getattr(view_wrapper, '__permission__', None)
            if not IMultiView.providedBy(view_wrapper):
                # single view for this route, so repeat call without route data
                del request_attrs['matched_route']
                self.output_view_info(view_wrapper, level+1)
        else:
            self.out("%sView:" % indent)
            self.out("%s-----" % indent)
            self.out("%s%s" % (indent, view_callable))
            permission = getattr(view_wrapper, '__permission__', None)
            if permission is not None:
                self.out("%srequired permission = %s" % (indent, permission))
            predicates = getattr(view_wrapper, '__predicates__', None)
            if predicates is not None:
                predicate_text = ', '.join([p.__text__ for p in predicates])
                self.out("%sview predicates (%s)" % (indent, predicate_text))

    def command(self):
        config_file, section_name, url = self.args
        if not url.startswith('/'):
            url = '/%s' % url
        app = self.get_app(config_file, section_name, loadapp=self.loadapp[0])
        registry = app.registry
        view = self._find_view(url, registry)
        self.out('')
        self.out("URL = %s" % url)
        self.out('')
        if view is not None:
            self.out("    context: %s" % view.__request_attrs__['context'])
            self.out("    view name: %s" % view.__request_attrs__['view_name'])
        if IMultiView.providedBy(view):
            for dummy, view_wrapper, dummy in view.views:
                self.output_view_info(view_wrapper)
                if IMultiView.providedBy(view_wrapper):
                    for dummy, mv_view_wrapper, dummy in view_wrapper.views:
                        self.output_view_info(mv_view_wrapper, level=2)
        else:
            if view is not None:
                self.output_view_info(view)
            else:
                self.out("    Not found.")
        self.out('')

