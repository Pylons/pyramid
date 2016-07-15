# (c) 2005 Ian Bicking and contributors; written for Paste
# (http://pythonpaste.org) Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php
#
# For discussion of daemonizing:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/278731
#
# Code taken also from QP: http://www.mems-exchange.org/software/qp/ From
# lib/site.py

import atexit
import ctypes
import optparse
import os
import py_compile
import re
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import traceback
import webbrowser

from paste.deploy import loadserver
from paste.deploy import loadapp
from paste.deploy.loadwsgi import loadcontext, SERVER

from pyramid.compat import PY2
from pyramid.compat import WIN

from pyramid.paster import setup_logging

from pyramid.scripts.common import parse_vars

MAXFD = 1024

try:
    import termios
except ImportError: # pragma: no cover
    termios = None

if WIN and not hasattr(os, 'kill'): # pragma: no cover
    # py 2.6 on windows
    def kill(pid, sig=None):
        """kill function for Win32"""
        # signal is ignored, semibogus raise message
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(1, 0, pid)
        if (0 == kernel32.TerminateProcess(handle, 0)):
            raise OSError('No such process %s' % pid)
else:
    kill = os.kill

def main(argv=sys.argv, quiet=False):
    command = PServeCommand(argv, quiet=quiet)
    return command.run()

class PServeCommand(object):

    usage = '%prog config_uri [var=value]'
    description = """\
    This command serves a web application that uses a PasteDeploy
    configuration file for the server and application.

    You can also include variable assignments like 'http_port=8080'
    and then use %(http_port)s in your config files.
    """
    default_verbosity = 1

    parser = optparse.OptionParser(
        usage,
        description=textwrap.dedent(description)
        )
    parser.add_option(
        '-n', '--app-name',
        dest='app_name',
        metavar='NAME',
        help="Load the named application (default main)")
    parser.add_option(
        '-s', '--server',
        dest='server',
        metavar='SERVER_TYPE',
        help="Use the named server.")
    parser.add_option(
        '--server-name',
        dest='server_name',
        metavar='SECTION_NAME',
        help=("Use the named server as defined in the configuration file "
              "(default: main)"))
    parser.add_option(
        '--reload',
        dest='reload',
        action='store_true',
        help="Use auto-restart file monitor")
    parser.add_option(
        '--reload-interval',
        dest='reload_interval',
        default=1,
        help=("Seconds between checking files (low number can cause "
              "significant CPU usage)"))
    parser.add_option(
        '-b', '--browser',
        dest='browser',
        action='store_true',
        help="Open a web browser to server url")
    parser.add_option(
        '-v', '--verbose',
        default=default_verbosity,
        dest='verbose',
        action='count',
        help="Set verbose level (default " + str(default_verbosity) + ")")
    parser.add_option(
        '-q', '--quiet',
        action='store_const',
        const=0,
        dest='verbose',
        help="Suppress verbose output")

    _scheme_re = re.compile(r'^[a-z][a-z]+:', re.I)

    _reloader_environ_key = 'PYTHON_RELOADER_SHOULD_RUN'
    _monitor_environ_key = 'PASTE_MONITOR_SHOULD_RUN'

    def __init__(self, argv, quiet=False):
        self.options, self.args = self.parser.parse_args(argv[1:])
        if quiet:
            self.options.verbose = 0

    def out(self, msg): # pragma: no cover
        if self.options.verbose > 0:
            print(msg)

    def get_options(self):
        restvars = self.args[1:]
        return parse_vars(restvars)

    def run(self):  # pragma: no cover
        if not self.args:
            self.out('You must give a config file')
            return 2
        app_spec = self.args[0]

        if self.options.reload:
            if os.environ.get(self._reloader_environ_key):
                if self.options.verbose > 1:
                    self.out('Running reloading file monitor')
                install_reloader(int(self.options.reload_interval), [app_spec])
                # if self.requires_config_file:
                #     watch_file(self.args[0])
            else:
                return self.restart_with_reloader()

        app_name = self.options.app_name

        vars = self.get_options()

        if not self._scheme_re.search(app_spec):
            app_spec = 'config:' + app_spec
        server_name = self.options.server_name
        if self.options.server:
            server_spec = 'egg:pyramid'
            assert server_name is None
            server_name = self.options.server
        else:
            server_spec = app_spec
        base = os.getcwd()

        log_fn = app_spec
        if log_fn.startswith('config:'):
            log_fn = app_spec[len('config:'):]
        elif log_fn.startswith('egg:'):
            log_fn = None
        if log_fn:
            log_fn = os.path.join(base, log_fn)
            setup_logging(log_fn, global_conf=vars)

        server = self.loadserver(server_spec, name=server_name,
                                 relative_to=base, global_conf=vars)

        app = self.loadapp(app_spec, name=app_name, relative_to=base,
                global_conf=vars)

        if self.options.verbose > 0:
            if hasattr(os, 'getpid'):
                msg = 'Starting server in PID %i.' % os.getpid()
            else:
                msg = 'Starting server.'
            self.out(msg)

        def serve():
            try:
                server(app)
            except (SystemExit, KeyboardInterrupt) as e:
                if self.options.verbose > 1:
                    raise
                if str(e):
                    msg = ' ' + str(e)
                else:
                    msg = ''
                self.out('Exiting%s (-v to see traceback)' % msg)

        if self.options.browser:
            def open_browser():
                context = loadcontext(SERVER, app_spec, name=server_name, relative_to=base,
                        global_conf=vars)
                url = 'http://127.0.0.1:{port}/'.format(**context.config())
                time.sleep(1)
                webbrowser.open(url)
            t = threading.Thread(target=open_browser)
            t.setDaemon(True)
            t.start()

        serve()

    def loadapp(self, app_spec, name, relative_to, **kw): # pragma: no cover
        return loadapp(app_spec, name=name, relative_to=relative_to, **kw)

    def loadserver(self, server_spec, name, relative_to, **kw):# pragma:no cover
        return loadserver(
            server_spec, name=name, relative_to=relative_to, **kw)

    def quote_first_command_arg(self, arg): # pragma: no cover
        """
        There's a bug in Windows when running an executable that's
        located inside a path with a space in it.  This method handles
        that case, or on non-Windows systems or an executable with no
        spaces, it just leaves well enough alone.
        """
        if (sys.platform != 'win32' or ' ' not in arg):
            # Problem does not apply:
            return arg
        try:
            import win32api
        except ImportError:
            raise ValueError(
                "The executable %r contains a space, and in order to "
                "handle this issue you must have the win32api module "
                "installed" % arg)
        arg = win32api.GetShortPathName(arg)
        return arg

    def find_script_path(self, name): # pragma: no cover
        """
        Return the path to the script being invoked by the python interpreter.

        There's an issue on Windows when running the executable from
        a console_script causing the script name (sys.argv[0]) to
        not end with .exe or .py and thus cannot be run via popen.
        """
        if sys.platform == 'win32':
            if not name.endswith('.exe') and not name.endswith('.py'):
                name += '.exe'
        return name

    def restart_with_reloader(self): # pragma: no cover
        self.restart_with_monitor(reloader=True)

    def restart_with_monitor(self, reloader=False): # pragma: no cover
        if self.options.verbose > 0:
            if reloader:
                self.out('Starting subprocess with file monitor')
            else:
                self.out('Starting subprocess with monitor parent')
        while 1:
            args = [
                self.quote_first_command_arg(sys.executable),
                self.find_script_path(sys.argv[0]),
            ] + sys.argv[1:]
            new_environ = os.environ.copy()
            if reloader:
                new_environ[self._reloader_environ_key] = 'true'
            else:
                new_environ[self._monitor_environ_key] = 'true'
            proc = None
            try:
                try:
                    _turn_sigterm_into_systemexit()
                    proc = subprocess.Popen(args, env=new_environ)
                    exit_code = proc.wait()
                    proc = None
                except KeyboardInterrupt:
                    self.out('^C caught in monitor process')
                    if self.options.verbose > 1:
                        raise
                    return 1
            finally:
                if proc is not None:
                    import signal
                    try:
                        kill(proc.pid, signal.SIGTERM)
                    except (OSError, IOError):
                        pass

            if reloader:
                # Reloader always exits with code 3; but if we are
                # a monitor, any exit code will restart
                if exit_code != 3:
                    return exit_code
            if self.options.verbose > 0:
                self.out('%s %s %s' % ('-' * 20, 'Restarting', '-' * 20))

class LazyWriter(object):

    """
    File-like object that opens a file lazily when it is first written
    to.
    """

    def __init__(self, filename, mode='w'):
        self.filename = filename
        self.fileobj = None
        self.lock = threading.Lock()
        self.mode = mode

    def open(self):
        if self.fileobj is None:
            with self.lock:
                self.fileobj = open(self.filename, self.mode)
        return self.fileobj

    def close(self):
        fileobj = self.fileobj
        if fileobj is not None:
            fileobj.close()

    def __del__(self):
        self.close()

    def write(self, text):
        fileobj = self.open()
        fileobj.write(text)
        fileobj.flush()

    def writelines(self, text):
        fileobj = self.open()
        fileobj.writelines(text)
        fileobj.flush()

    def flush(self):
        self.open().flush()

def ensure_port_cleanup(
    bound_addresses, maxtries=30, sleeptime=2): # pragma: no cover
    """
    This makes sure any open ports are closed.

    Does this by connecting to them until they give connection
    refused.  Servers should call like::

        ensure_port_cleanup([80, 443])
    """
    atexit.register(_cleanup_ports, bound_addresses, maxtries=maxtries,
                    sleeptime=sleeptime)

def _cleanup_ports(
    bound_addresses, maxtries=30, sleeptime=2): # pragma: no cover
    # Wait for the server to bind to the port.
    import socket
    import errno
    for bound_address in bound_addresses:
        for attempt in range(maxtries):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect(bound_address)
            except socket.error as e:
                if e.args[0] != errno.ECONNREFUSED:
                    raise
                break
            else:
                time.sleep(sleeptime)
        else:
            raise SystemExit('Timeout waiting for port.')
        sock.close()

def _turn_sigterm_into_systemexit(): # pragma: no cover
    """
    Attempts to turn a SIGTERM exception into a SystemExit exception.
    """
    try:
        import signal
    except ImportError:
        return
    def handle_term(signo, frame):
        raise SystemExit
    signal.signal(signal.SIGTERM, handle_term)

def ensure_echo_on(): # pragma: no cover
    if termios:
        fd = sys.stdin
        if fd.isatty():
            attr_list = termios.tcgetattr(fd)
            if not attr_list[3] & termios.ECHO:
                attr_list[3] |= termios.ECHO
                termios.tcsetattr(fd, termios.TCSANOW, attr_list)

def install_reloader(poll_interval=1, extra_files=None): # pragma: no cover
    """
    Install the reloading monitor.

    On some platforms server threads may not terminate when the main
    thread does, causing ports to remain open/locked.
    """
    ensure_echo_on()
    mon = Monitor(poll_interval=poll_interval)
    if extra_files is None:
        extra_files = []
    mon.extra_files.extend(extra_files)
    t = threading.Thread(target=mon.periodic_reload)
    t.setDaemon(True)
    t.start()

class classinstancemethod(object):
    """
    Acts like a class method when called from a class, like an
    instance method when called by an instance.  The method should
    take two arguments, 'self' and 'cls'; one of these will be None
    depending on how the method was called.
    """

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__

    def __get__(self, obj, type=None):
        return _methodwrapper(self.func, obj=obj, type=type)

class _methodwrapper(object):

    def __init__(self, func, obj, type):
        self.func = func
        self.obj = obj
        self.type = type

    def __call__(self, *args, **kw):
        assert 'self' not in kw and 'cls' not in kw, (
            "You cannot use 'self' or 'cls' arguments to a "
            "classinstancemethod")
        return self.func(*((self.obj, self.type) + args), **kw)


class Monitor(object): # pragma: no cover
    """
    A file monitor and server restarter.

    Use this like:

    ..code-block:: Python

        install_reloader()

    Then make sure your server is installed with a shell script like::

        err=3
        while test "$err" -eq 3 ; do
            python server.py
            err="$?"
        done

    or is run from this .bat file (if you use Windows)::

        @echo off
        :repeat
            python server.py
        if %errorlevel% == 3 goto repeat

    or run a monitoring process in Python (``pserve --reload`` does
    this).

    Use the ``watch_file(filename)`` function to cause a reload/restart for
    other non-Python files (e.g., configuration files).  If you have
    a dynamic set of files that grows over time you can use something like::

        def watch_config_files():
            return CONFIG_FILE_CACHE.keys()
        add_file_callback(watch_config_files)

    Then every time the reloader polls files it will call
    ``watch_config_files`` and check all the filenames it returns.
    """
    instances = []
    global_extra_files = []
    global_file_callbacks = []

    def __init__(self, poll_interval):
        self.module_mtimes = {}
        self.keep_running = True
        self.poll_interval = poll_interval
        self.extra_files = list(self.global_extra_files)
        self.instances.append(self)
        self.syntax_error_files = set()
        self.pending_reload = False
        self.file_callbacks = list(self.global_file_callbacks)
        temp_pyc_fp = tempfile.NamedTemporaryFile(delete=False)
        self.temp_pyc = temp_pyc_fp.name
        temp_pyc_fp.close()

    def _exit(self):
        try:
            os.unlink(self.temp_pyc)
        except IOError:
            # not worried if the tempfile can't be removed
            pass
        # use os._exit() here and not sys.exit() since within a
        # thread sys.exit() just closes the given thread and
        # won't kill the process; note os._exit does not call
        # any atexit callbacks, nor does it do finally blocks,
        # flush open files, etc.  In otherwords, it is rude.
        os._exit(3)

    def periodic_reload(self):
        while True:
            if not self.check_reload():
                self._exit()
                break
            time.sleep(self.poll_interval)

    def check_reload(self):
        filenames = list(self.extra_files)
        for file_callback in self.file_callbacks:
            try:
                filenames.extend(file_callback())
            except:
                print(
                    "Error calling reloader callback %r:" % file_callback)
                traceback.print_exc()
        for module in list(sys.modules.values()):
            try:
                filename = module.__file__
            except (AttributeError, ImportError):
                continue
            if filename is not None:
                filenames.append(filename)
        new_changes = False
        for filename in filenames:
            try:
                stat = os.stat(filename)
                if stat:
                    mtime = stat.st_mtime
                else:
                    mtime = 0
            except (OSError, IOError):
                continue
            if filename.endswith('.pyc') and os.path.exists(filename[:-1]):
                mtime = max(os.stat(filename[:-1]).st_mtime, mtime)
                pyc = True
            else:
                pyc = False
            old_mtime = self.module_mtimes.get(filename)
            self.module_mtimes[filename] = mtime
            if old_mtime is not None and old_mtime < mtime:
                new_changes = True
                if pyc:
                    filename = filename[:-1]
                is_valid = True
                if filename.endswith('.py'):
                    is_valid = self.check_syntax(filename)
                if is_valid:
                    print("%s changed ..." % filename)
        if new_changes:
            self.pending_reload = True
            if self.syntax_error_files:
                for filename in sorted(self.syntax_error_files):
                    print("%s has a SyntaxError; NOT reloading." % filename)
        if self.pending_reload and not self.syntax_error_files:
            self.pending_reload = False
            return False
        return True

    def check_syntax(self, filename):
        # check if a file has syntax errors.
        # If so, track it until it's fixed.
        try:
            py_compile.compile(filename, cfile=self.temp_pyc, doraise=True)
        except py_compile.PyCompileError as ex:
            print(ex.msg)
            self.syntax_error_files.add(filename)
            return False
        else:
            if filename in self.syntax_error_files:
                self.syntax_error_files.remove(filename)
        return True

    def watch_file(self, cls, filename):
        """Watch the named file for changes"""
        filename = os.path.abspath(filename)
        if self is None:
            for instance in cls.instances:
                instance.watch_file(filename)
            cls.global_extra_files.append(filename)
        else:
            self.extra_files.append(filename)

    watch_file = classinstancemethod(watch_file)

    def add_file_callback(self, cls, callback):
        """Add a callback -- a function that takes no parameters -- that will
        return a list of filenames to watch for changes."""
        if self is None:
            for instance in cls.instances:
                instance.add_file_callback(callback)
            cls.global_file_callbacks.append(callback)
        else:
            self.file_callbacks.append(callback)

    add_file_callback = classinstancemethod(add_file_callback)

watch_file = Monitor.watch_file
add_file_callback = Monitor.add_file_callback

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
    if ssl_pem is not None:
        if PY2:
            server.ssl_certificate = server.ssl_private_key = ssl_pem
        else:
            # creates wsgiserver.ssl_builtin as side-effect
            wsgiserver.get_ssl_adapter_class()
            server.ssl_adapter = wsgiserver.ssl_builtin.BuiltinSSLAdapter(
                ssl_pem, ssl_pem)

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

if __name__ == '__main__': # pragma: no cover
    sys.exit(main() or 0)
