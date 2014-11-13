import optparse
import sys
import textwrap

from pyramid.paster import bootstrap
from pyramid.scripts.common import parse_vars
from pyramid.config.views import MultiView


PAD = 3


def main(argv=sys.argv, quiet=False):
    command = PRoutesCommand(argv, quiet)
    return command.run()


class PRoutesCommand(object):
    description = """\
    Print all URL dispatch routes used by a Pyramid application in the
    order in which they are evaluated.  Each route includes the name of the
    route, the pattern of the route, and the view callable which will be
    invoked when the route is matched.

    This command accepts one positional argument named 'config_uri'.  It
    specifies the PasteDeploy config file to use for the interactive
    shell. The format is 'inifile#name'. If the name is left off, 'main'
    will be assumed.  Example: 'proutes myapp.ini'.

    """
    bootstrap = (bootstrap,)
    stdout = sys.stdout
    usage = '%prog config_uri'

    parser = optparse.OptionParser(
        usage,
        description=textwrap.dedent(description)
        )

    def __init__(self, argv, quiet=False):
        self.options, self.args = self.parser.parse_args(argv[1:])
        self.quiet = quiet

    def _get_mapper(self, registry):
        from pyramid.config import Configurator
        config = Configurator(registry = registry)
        return config.get_routes_mapper()

    def out(self, msg): # pragma: no cover
        if not self.quiet:
            print(msg)

    def run(self, quiet=False):
        if not self.args:
            self.out('requires a config file argument')
            return 2

        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IView
        from zope.interface import Interface
        config_uri = self.args[0]

        env = self.bootstrap[0](config_uri, options=parse_vars(self.args[1:]))
        registry = env['registry']
        mapper = self._get_mapper(registry)
        if mapper is not None:
            mapped_routes = [('Name', 'Pattern', 'View')]

            max_name = len('Name')
            max_pattern = len('Pattern')
            max_view = len('View')

            routes = mapper.get_routes()
            if not routes:
                return 0

            mapped_routes.append((
                '-' * max_name,
                '-' * max_pattern,
                '-' * max_view,
            ))

            for route in routes:
                pattern = route.pattern
                if not pattern.startswith('/'):
                    pattern = '/' + pattern
                request_iface = registry.queryUtility(IRouteRequest,
                                                      name=route.name)
                view_callable = None

                if (request_iface is None) or (route.factory is not None):
                    view_callable = '<unknown>'
                else:
                    view_callable = registry.adapters.lookup(
                        (IViewClassifier, request_iface, Interface),
                        IView, name='', default=None)

                    if view_callable is not None:
                        if isinstance(view_callable, MultiView):
                            view_callables = [
                                x[1] for x in view_callable.views
                            ]
                        else:
                            view_callables = [view_callable]

                        for view_func in view_callables:
                            view_callable = '%s.%s' % (
                                view_func.__module__,
                                view_func.__name__,
                            )
                    else:
                        view_callable = str(None)

                if len(route.name) > max_name:
                    max_name = len(route.name)

                if len(pattern) > max_pattern:
                    max_pattern = len(pattern)

                if len(view_callable) > max_view:
                    max_view = len(view_callable)

                mapped_routes.append((route.name, pattern, view_callable))

            fmt = '%-{0}s %-{1}s %-{2}s'.format(
                max_name + PAD,
                max_pattern + PAD,
                max_view + PAD,
            )

            for route_data in mapped_routes:
                self.out(fmt % route_data)

        return 0

if __name__ == '__main__': # pragma: no cover
    sys.exit(main() or 0)
