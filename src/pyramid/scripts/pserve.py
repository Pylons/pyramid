# (c) 2005 Ian Bicking and contributors; written for Paste
# (http://pythonpaste.org) Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php
#
# For discussion of daemonizing:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/278731
#
# Code taken also from QP: http://www.mems-exchange.org/software/qp/ From
# lib/site.py

import argparse
import os
import re
import sys
import textwrap
import threading
import time
import webbrowser

import hupper

from pyramid.compat import PY2

from pyramid.scripts.common import get_config_loader
from pyramid.scripts.common import parse_vars
from pyramid.path import AssetResolver
from pyramid.settings import aslist


def main(argv=sys.argv, quiet=False, original_ignore_files=None):
    command = PServeCommand(
        argv, quiet=quiet, original_ignore_files=original_ignore_files
    )
    return command.run()


class PServeCommand(object):

    description = """\
    This command serves a web application that uses a PasteDeploy
    configuration file for the server and application.

    You can also include variable assignments like 'http_port=8080'
    and then use %(http_port)s in your config files.
    """
    default_verbosity = 1

    parser = argparse.ArgumentParser(
        description=textwrap.dedent(description),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '-n',
        '--app-name',
        dest='app_name',
        metavar='NAME',
        help="Load the named application (default main)",
    )
    parser.add_argument(
        '-s',
        '--server',
        dest='server',
        metavar='SERVER_TYPE',
        help="Use the named server.",
    )
    parser.add_argument(
        '--server-name',
        dest='server_name',
        metavar='SECTION_NAME',
        help=(
            "Use the named server as defined in the configuration file "
            "(default: main)"
        ),
    )
    parser.add_argument(
        '--reload',
        dest='reload',
        action='store_true',
        help="Use auto-restart file monitor",
    )
    parser.add_argument(
        '--reload-interval',
        dest='reload_interval',
        default=1,
        help=(
            "Seconds between checking files (low number can cause "
            "significant CPU usage)"
        ),
    )
    parser.add_argument(
        '-b',
        '--browser',
        dest='browser',
        action='store_true',
        help=(
            "Open a web browser to the server url. The server url is "
            "determined from the 'open_url' setting in the 'pserve' "
            "section of the configuration file."
        ),
    )
    parser.add_argument(
        '-v',
        '--verbose',
        default=default_verbosity,
        dest='verbose',
        action='count',
        help="Set verbose level (default " + str(default_verbosity) + ")",
    )
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_const',
        const=0,
        dest='verbose',
        help="Suppress verbose output",
    )
    parser.add_argument(
        'config_uri',
        nargs='?',
        default=None,
        help='The URI to the configuration file.',
    )
    parser.add_argument(
        'config_vars',
        nargs='*',
        default=(),
        help="Variables required by the config file. For example, "
        "`http_port=%%(http_port)s` would expect `http_port=8080` to be "
        "passed here.",
    )

    _get_config_loader = staticmethod(get_config_loader)  # for testing

    open_url = None

    _scheme_re = re.compile(r'^[a-z][a-z]+:', re.I)

    def __init__(self, argv, quiet=False, original_ignore_files=None):
        self.args = self.parser.parse_args(argv[1:])
        if quiet:
            self.args.verbose = 0
        if self.args.reload:
            self.worker_kwargs = {'argv': argv, "quiet": quiet}
        self.watch_files = set()
        self.ignore_files = set()
        self.original_ignore_files = original_ignore_files

    def out(self, msg):  # pragma: no cover
        if self.args.verbose > 0:
            print(msg)

    def get_config_path(self, loader):
        return os.path.abspath(loader.uri.path)

    def pserve_file_config(self, loader, global_conf=None):
        settings = loader.get_settings('pserve', global_conf)
        config_path = self.get_config_path(loader)
        here = os.path.dirname(config_path)
        watch_files = aslist(settings.get('watch_files', ''), flatten=False)
        self.ignore_files = set(
            aslist(settings.get('ignore_files', ''), flatten=False)
        )

        # track file paths relative to the ini file
        resolver = AssetResolver(package=None)
        for file in watch_files:
            if ':' in file:
                file = resolver.resolve(file).abspath()
            elif not os.path.isabs(file):
                file = os.path.join(here, file)
            self.watch_files.add(os.path.abspath(file))

        # attempt to determine the url of the server
        open_url = settings.get('open_url')
        if open_url:
            self.open_url = open_url

    def guess_server_url(self, loader, server_name, global_conf=None):
        server_name = server_name or 'main'
        settings = loader.get_settings('server:' + server_name, global_conf)
        if 'port' in settings:
            return 'http://127.0.0.1:{port}'.format(**settings)

    def run(self):  # pragma: no cover
        if not self.args.config_uri:
            self.out('You must give a config file')
            return 2
        config_uri = self.args.config_uri
        config_vars = parse_vars(self.args.config_vars)
        app_spec = self.args.config_uri
        app_name = self.args.app_name

        loader = self._get_config_loader(config_uri)

        # setup logging only in the worker process incase the logging config
        # opens files which should not be opened by multiple processes at once
        if not self.args.reload or hupper.is_active():
            loader.setup_logging(config_vars)

        self.pserve_file_config(loader, global_conf=config_vars)

        server_name = self.args.server_name
        if self.args.server:
            server_spec = 'egg:pyramid'
            assert server_name is None
            server_name = self.args.server
        else:
            server_spec = app_spec

        server_loader = loader
        if server_spec != app_spec:
            server_loader = self.get_config_loader(server_spec)

        # do not open the browser on each reload so check hupper first
        if self.args.browser and not hupper.is_active():
            url = self.open_url

            if not url:
                url = self.guess_server_url(
                    server_loader, server_name, config_vars
                )

            if not url:
                self.out(
                    'WARNING: could not determine the server\'s url to '
                    'open the browser. To fix this set the "open_url" '
                    'setting in the [pserve] section of the '
                    'configuration file.'
                )

            else:

                def open_browser():
                    time.sleep(1)
                    webbrowser.open(url)

                t = threading.Thread(target=open_browser)
                t.setDaemon(True)
                t.start()

        if self.args.reload and not hupper.is_active():
            if self.args.verbose > 1:
                self.out('Running reloading file monitor')
            self.worker_kwargs['original_ignore_files'] = self.ignore_files
            hupper.start_reloader(
                'pyramid.scripts.pserve.main',
                reload_interval=int(self.args.reload_interval),
                verbose=self.args.verbose,
                worker_kwargs=self.worker_kwargs,
                ignore_files=self.ignore_files,
            )
            return 0

        config_path = self.get_config_path(loader)
        self.watch_files.add(config_path)

        server_path = self.get_config_path(server_loader)
        self.watch_files.add(server_path)

        if hupper.is_active():
            reloader = hupper.get_reloader()
            reloader.watch_files(list(self.watch_files))

        if (
            self.original_ignore_files is not None
            and self.original_ignore_files != self.ignore_files
        ):
            self.out(
                'A change to "ignore_files" was detected but it will not take'
                ' effect until pserve is restarted.'
            )

        server = server_loader.get_wsgi_server(server_name, config_vars)

        app = loader.get_wsgi_app(app_name, config_vars)

        if self.args.verbose > 0:
            if hasattr(os, 'getpid'):
                msg = 'Starting server in PID %i.' % os.getpid()
            else:
                msg = 'Starting server.'
            self.out(msg)

        try:
            server(app)
        except (SystemExit, KeyboardInterrupt) as e:
            if self.args.verbose > 1:
                raise
            if str(e):
                msg = ' ' + str(e)
            else:
                msg = ''
            self.out('Exiting%s (-v to see traceback)' % msg)


# For paste.deploy server instantiation (egg:pyramid#wsgiref)
def wsgiref_server_runner(wsgi_app, global_conf, **kw):  # pragma: no cover
    from wsgiref.simple_server import make_server

    host = kw.get('host', '0.0.0.0')
    port = int(kw.get('port', 8080))
    server = make_server(host, port, wsgi_app)
    print('Starting HTTP server on http://%s:%s' % (host, port))
    server.serve_forever()


# For paste.deploy server instantiation (egg:pyramid#cherrypy)
def cherrypy_server_runner(
    app,
    global_conf=None,
    host='127.0.0.1',
    port=None,
    ssl_pem=None,
    protocol_version=None,
    numthreads=None,
    server_name=None,
    max=None,
    request_queue_size=None,
    timeout=None,
):  # pragma: no cover
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

    try:
        from cheroot.wsgi import Server as WSGIServer
    except ImportError:
        from cherrypy.wsgiserver import CherryPyWSGIServer as WSGIServer

    server = WSGIServer(bind_addr, app, server_name=server_name, **kwargs)
    if ssl_pem is not None:
        if PY2:
            server.ssl_certificate = server.ssl_private_key = ssl_pem
        else:
            # creates wsgiserver.ssl_builtin as side-effect
            try:
                from cheroot.server import get_ssl_adapter_class
                from cheroot.ssl.builtin import BuiltinSSLAdapter
            except ImportError:
                from cherrypy.wsgiserver import get_ssl_adapter_class
                from cherrypy.wsgiserver.ssl_builtin import BuiltinSSLAdapter
            get_ssl_adapter_class()
            server.ssl_adapter = BuiltinSSLAdapter(ssl_pem, ssl_pem)

    if protocol_version:
        server.protocol = protocol_version

    try:
        protocol = is_ssl and 'https' or 'http'
        if host == '0.0.0.0':
            print(
                'serving on 0.0.0.0:%s view at %s://127.0.0.1:%s'
                % (port, protocol, port)
            )
        else:
            print('serving on %s://%s:%s' % (protocol, host, port))
        server.start()
    except (KeyboardInterrupt, SystemExit):
        server.stop()

    return server


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main() or 0)
