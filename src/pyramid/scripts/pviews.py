import argparse
import sys
import textwrap

from pyramid.interfaces import IMultiView
from pyramid.paster import bootstrap, setup_logging
from pyramid.request import Request
from pyramid.scripts.common import parse_vars
from pyramid.view import _find_views


def main(argv=sys.argv, quiet=False):
    command = PViewsCommand(argv, quiet)
    return command.run()


class PViewsCommand:
    description = """\
    Print, for a given URL, the views that might match. Underneath each
    potentially matching route, list the predicates required. Underneath
    each route+predicate set, print each view that might match and its
    predicates.

    This command accepts two positional arguments: 'config_uri' specifies the
    PasteDeploy config file to use for the interactive shell. The format is
    'inifile#name'. If the name is left off, 'main' will be assumed.  'url'
    specifies the path info portion of a URL that will be used to find
    matching views.  Example: 'proutes myapp.ini#main /url'
    """
    script_name = 'pviews'
    stdout = sys.stdout

    parser = argparse.ArgumentParser(
        description=textwrap.dedent(description),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        'config_uri',
        nargs='?',
        default=None,
        help='The URI to the configuration file.',
    )

    parser.add_argument(
        'url',
        nargs='?',
        default=None,
        help='The path info portion of the URL.',
    )
    parser.add_argument(
        'config_vars',
        nargs='*',
        default=(),
        help="Variables required by the config file. For example, "
        "`http_port=%%(http_port)s` would expect `http_port=8080` to be "
        "passed here.",
    )

    bootstrap = staticmethod(bootstrap)  # testing
    setup_logging = staticmethod(setup_logging)  # testing

    def __init__(self, argv, quiet=False):
        self.quiet = quiet
        self.args = self.parser.parse_args(argv[1:])

    def out(self, msg):  # pragma: no cover
        if not self.quiet:
            print(msg)

    def _find_multi_routes(self, mapper, request):
        infos = []
        path = request.path_info
        # find all routes that match path, regardless of predicates
        for route in mapper.get_routes():
            match = route.match(path)
            if match is not None:
                info = {'match': match, 'route': route}
                infos.append(info)
        return infos

    def _find_view(self, request):
        """
        Accept ``url`` and ``registry``; create a :term:`request` and
        find a :app:`Pyramid` view based on introspection of :term:`view
        configuration` within the application registry; return the view.
        """
        from zope.interface import implementer, providedBy

        from pyramid.interfaces import (
            IRequest,
            IRootFactory,
            IRouteRequest,
            IRoutesMapper,
            ITraverser,
        )
        from pyramid.traversal import DefaultRootFactory, ResourceTreeTraverser

        registry = request.registry
        q = registry.queryUtility
        root_factory = q(IRootFactory, default=DefaultRootFactory)
        routes_mapper = q(IRoutesMapper)

        adapters = registry.adapters

        @implementer(IMultiView)
        class RoutesMultiView:
            def __init__(self, infos, context_iface, root_factory, request):
                self.views = []
                for info in infos:
                    match, route = info['match'], info['route']
                    if route is not None:
                        request_iface = registry.queryUtility(
                            IRouteRequest, name=route.name, default=IRequest
                        )
                        views = _find_views(
                            request.registry, request_iface, context_iface, ''
                        )
                        if not views:
                            continue
                        view = views[0]
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

        context = None
        routes_multiview = None
        attrs = request.__dict__
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
                        IRouteRequest, name=route.name, default=IRequest
                    )
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
        context, view_name = (tdict['context'], tdict['view_name'])

        attrs.update(tdict)

        # find a view callable
        context_iface = providedBy(context)
        if routes_multiview is None:
            views = _find_views(
                request.registry, request_iface, context_iface, view_name
            )
            if views:
                view = views[0]
            else:
                view = None
        else:
            view = RoutesMultiView(infos, context_iface, root_factory, request)

        # routes are not registered with a view name
        if view is None:
            views = _find_views(
                request.registry, request_iface, context_iface, ''
            )
            if views:
                view = views[0]
            else:
                view = None
            # we don't want a multiview here
            if IMultiView.providedBy(view):
                view = None

        if view is not None:
            view.__request_attrs__ = attrs

        return view

    def output_route_attrs(self, attrs, indent):
        route = attrs['matched_route']
        self.out(f"{indent}route name: {route.name}")
        self.out(f"{indent}route pattern: {route.pattern}")
        self.out(f"{indent}route path: {route.path}")
        self.out("{}subpath: {}".format(indent, '/'.join(attrs['subpath'])))
        predicates = ', '.join([p.text() for p in route.predicates])
        if predicates != '':
            self.out(f"{indent}route predicates ({predicates})")

    def output_view_info(self, view_wrapper, level=1):
        indent = "    " * level
        name = getattr(view_wrapper, '__name__', '')
        module = getattr(view_wrapper, '__module__', '')
        attr = getattr(view_wrapper, '__view_attr__', None)
        request_attrs = getattr(view_wrapper, '__request_attrs__', {})
        if attr is not None:
            view_callable = f"{module}.{name}.{attr}"
        else:
            attr = view_wrapper.__class__.__name__
            if attr == 'function':
                attr = name
            view_callable = f"{module}.{attr}"
        self.out('')
        if 'matched_route' in request_attrs:
            self.out("%sRoute:" % indent)
            self.out("%s------" % indent)
            self.output_route_attrs(request_attrs, indent)
            permission = getattr(view_wrapper, '__permission__', None)
            if not IMultiView.providedBy(view_wrapper):
                # single view for this route, so repeat call without route data
                del request_attrs['matched_route']
                self.output_view_info(view_wrapper, level + 1)
        else:
            self.out("%sView:" % indent)
            self.out("%s-----" % indent)
            self.out(f"{indent}{view_callable}")
            permission = getattr(view_wrapper, '__permission__', None)
            if permission is not None:
                self.out(f"{indent}required permission = {permission}")
            predicates = getattr(view_wrapper, '__predicates__', None)
            if predicates is not None:
                predicate_text = ', '.join([p.text() for p in predicates])
                self.out(f"{indent}view predicates ({predicate_text})")

    def run(self):
        if not self.args.config_uri or not self.args.url:
            self.out('Command requires a config file arg and a url arg')
            return 2
        config_uri = self.args.config_uri
        config_vars = parse_vars(self.args.config_vars)
        config_vars.setdefault('__script__', self.script_name)
        url = self.args.url

        self.setup_logging(config_uri, global_conf=config_vars)

        if not url.startswith('/'):
            url = '/%s' % url
        request = Request.blank(url)
        env = self.bootstrap(config_uri, options=config_vars, request=request)
        view = self._find_view(request)
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
        env['closer']()
        return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main() or 0)
