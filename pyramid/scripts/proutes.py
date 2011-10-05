import optparse
import sys

from pyramid.compat import print_
from pyramid.paster import bootstrap

def main(argv=sys.argv):
    command = PRoutesCommand(argv)
    command.run()

class PRoutesCommand(object):
    """Print all URL dispatch routes used by a Pyramid application in the
    order in which they are evaluated.  Each route includes the name of the
    route, the pattern of the route, and the view callable which will be
    invoked when the route is matched.

    This command accepts one positional argument:

    ``config_uri`` -- specifies the PasteDeploy config file to use for the
    interactive shell. The format is ``inifile#name``. If the name is left
    off, ``main`` will be assumed.

    Example::

        $ proutes myapp.ini#main

    """
    bootstrap = (bootstrap,)
    summary = "Print all URL dispatch routes related to a Pyramid application"
    min_args = 1
    max_args = 1
    stdout = sys.stdout

    parser = optparse.OptionParser()

    def __init__(self, argv):
        self.options, self.args = self.parser.parse_args(argv[1:])

    def _get_mapper(self, registry):
        from pyramid.config import Configurator
        config = Configurator(registry = registry)
        return config.get_routes_mapper()

    def out(self, msg): # pragma: no cover
        print_(msg)
    
    def run(self):
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IView
        from zope.interface import Interface
        config_uri = self.args[0]
        env = self.bootstrap[0](config_uri)
        registry = env['registry']
        mapper = self._get_mapper(registry)
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

