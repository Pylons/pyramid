.. _logging_chapter:

Logging
=======

:app:`Pyramid` allows you to make use of the Python standard library
:mod:`logging` module.  This chapter describes how to configure logging and
how to send log messages to loggers that you've configured.

.. warning::

   This chapter assumes you've used a :term:`scaffold` to create a
   project which contains ``development.ini`` and ``production.ini`` files
   which help configure logging.  All of the scaffolds which ship along with
   :app:`Pyramid` do this.  If you're not using a scaffold, or if you've used
   a third-party scaffold which does not create these files, the
   configuration information in this chapter will not be applicable.

.. _logging_config:

Logging Configuration
---------------------

A :app:`Pyramid` project created from a :term:`scaffold` is configured to
allow you to send messages to `Python standard library logging package
<http://docs.python.org/library/logging.html>`_ loggers from within your
application.  In particular, the :term:`PasteDeploy` ``development.ini`` and
``production.ini`` files created when you use a scaffold include a basic
configuration for the Python :mod:`logging` package.

PasteDeploy ``.ini`` files use the Python standard library `ConfigParser
format <http://docs.python.org/lib/module-ConfigParser.html>`_; this the same
format used as the Python `logging module's Configuration file format
<http://docs.python.org/lib/logging-config-fileformat.html>`_.  The
application-related and logging-related sections in the configuration file
can coexist peacefully, and the logging-related sections in the file are used
from when you run ``pserve``.

The ``pserve`` command calls the `logging.fileConfig function
<http://docs.python.org/lib/logging-config-api.html>`_ using the specified
ini file if it contains a ``[loggers]`` section (all of the
scaffold-generated ``.ini`` files do). ``logging.fileConfig`` reads the
logging configuration from the ini file upon which ``pserve`` was
invoked.

Default logging configuration is provided in both the default
``development.ini`` and the ``production.ini`` file.  The logging
configuration in the ``development.ini`` file is as follows:

.. code-block:: ini
   :linenos:

   # Begin logging configuration

   [loggers]
   keys = root, {{package_logger}}

   [handlers]
   keys = console

   [formatters]
   keys = generic

   [logger_root]
   level = INFO
   handlers = console

   [logger_{{package_logger}}]
   level = DEBUG
   handlers =
   qualname = {{package}}

   [handler_console]
   class = StreamHandler
   args = (sys.stderr,)
   level = NOTSET
   formatter = generic

   [formatter_generic]
   format = %(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s

   # End logging configuration

The ``production.ini`` file uses the ``WARN`` level in its logger
configuration, but it is otherwise identical.

The name ``{{package_logger}}`` above will be replaced with the name of your
project's :term:`package`, which is derived from the name you provide to your
project.  For instance, if you do:

.. code-block:: text
   :linenos:

   pcreate -s starter MyApp

The logging configuration will literally be:

.. code-block:: ini
   :linenos:

   # Begin logging configuration

   [loggers]
   keys = root, myapp

   [handlers]
   keys = console

   [formatters]
   keys = generic

   [logger_root]
   level = INFO
   handlers = console

   [logger_myapp]
   level = DEBUG
   handlers =
   qualname = myapp

   [handler_console]
   class = StreamHandler
   args = (sys.stderr,)
   level = NOTSET
   formatter = generic

   [formatter_generic]
   format = %(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s

   # End logging configuration

In this logging configuration:

- a logger named ``root`` is created that logs messages at a level above
  or equal to the ``INFO`` level to stderr, with the following format:

  .. code-block:: text 

     2007-08-17 15:04:08,704 INFO [packagename] 
                                  Loading resource, id: 86 

- a logger named ``myapp`` is configured that logs messages sent at a level
  above or equal to ``DEBUG`` to stderr in the same format as the root
  logger.

The ``root`` logger will be used by all applications in the Pyramid process
that ask for a logger (via ``logging.getLogger``) that has a name which
begins with anything except your project's package name (e.g. ``myapp``).
The logger with the same name as your package name is reserved for your own
usage in your Pyramid application.  Its existence means that you can log to a
known logging location from any Pyramid application generated via a scaffold.

Pyramid and many other libraries (such as Beaker, SQLAlchemy, Paste) log a
number of messages to the root logger for debugging purposes. Switching the
root logger level to ``DEBUG`` reveals them:

.. code-block:: ini 

    [logger_root] 
    #level = INFO 
    level = DEBUG 
    handlers = console 

Some scaffolds configure additional loggers for additional subsystems they
use (such as SQLALchemy).  Take a look at the ``production.ini`` and
``development.ini`` files rendered when you create a project from a scaffold.

Sending Logging Messages
------------------------

Python's special ``__name__`` variable refers to the current module's fully
qualified name.  From any module in a package named ``myapp``, the
``__name__`` builtin variable will always be something like ``myapp``, or
``myapp.subpackage`` or ``myapp.package.subpackage`` if your project is named
``myapp``.  Sending a message to this logger will send it to the ``myapp``
logger.

To log messages to the package-specific logger configured in your ``.ini``
file, simply create a logger object using the ``__name__`` builtin and call
methods on it.

.. code-block:: python 
   :linenos:

    import logging 
    log = logging.getLogger(__name__) 

    def myview(request):
        content_type = 'text/plain' 
        content = 'Hello World!' 
        log.debug('Returning: %s (content-type: %s)', content, content_type) 
        request.response.content_type = content_type 
        return request.response

This will result in the following printed to the console, on ``stderr``: 

.. code-block:: text 

    16:20:20,440 DEBUG [myapp.views] Returning: Hello World!
                       (content-type: text/plain) 

Filtering log messages
----------------------

Often there's too much log output to sift through, such as when switching 
the root logger's level to ``DEBUG``. 

An example: you're diagnosing database connection issues in your application
and only want to see SQLAlchemy's ``DEBUG`` messages in relation to database
connection pooling. You can leave the root logger's level at the less verbose
``INFO`` level and set that particular SQLAlchemy logger to ``DEBUG`` on its
own, apart from the root logger:

.. code-block:: ini 

    [logger_sqlalchemy.pool] 
    level = DEBUG 
    handlers = 
    qualname = sqlalchemy.pool 

then add it to the list of loggers: 

.. code-block:: ini 

    [loggers] 
    keys = root, myapp, sqlalchemy.pool 

No handlers need to be configured for this logger as by default non root
loggers will propagate their log records up to their parent logger's
handlers. The root logger is the top level parent of all loggers.

This technique is used in the default ``development.ini``. The root logger's
level is set to ``INFO``, whereas the application's log level is set to
``DEBUG``:

.. code-block:: ini 

    # Begin logging configuration 

    [loggers] 
    keys = root, myapp

    [logger_myapp] 
    level = DEBUG 
    handlers = 
    qualname = helloworld 

All of the child loggers of the ``myapp`` logger will inherit the ``DEBUG``
level unless they're explicitly set differently. Meaning the ``myapp.views``,
``myapp.models`` (and all your app's modules') loggers by default have an
effective level of ``DEBUG`` too.

For more advanced filtering, the logging module provides a `Filter
<http://docs.python.org/lib/node423.html>`_ object; however it cannot be used
directly from the configuration file.

Advanced Configuration 
----------------------

To capture log output to a separate file, use a `FileHandler
<http://docs.python.org/lib/node412.html>`_ (or a `RotatingFileHandler
<http://docs.python.org/lib/node413.html>`_):

.. code-block:: ini 

    [handler_filelog] 
    class = FileHandler 
    args = ('%(here)s/myapp.log','a') 
    level = INFO 
    formatter = generic 

Before it's recognized, it needs to be added to the list of handlers: 

.. code-block:: ini 

    [handlers] 
    keys = console, myapp, filelog

and finally utilized by a logger. 

.. code-block:: ini 

    [logger_root] 
    level = INFO 
    handlers = console, filelog

These final 3 lines of configuration directs all of the root logger's output
to the ``myapp.log`` as well as the console.

Logging Exceptions
------------------

To log (or email) exceptions generated by your :app:`Pyramid` application,
use the :term:`pyramid_exclog` package.  Details about its configuration are
in its `documentation
<http://docs.pylonsproject.org/projects/pyramid_exclog/dev/>`_.

Request Logging with Paste's TransLogger 
----------------------------------------

Paste provides the `TransLogger 
<http://pythonpaste.org/modules/translogger.html>`_ middleware for logging 
requests using the `Apache Combined Log Format 
<http://httpd.apache.org/docs/2.2/logs.html#combined>`_. TransLogger combined 
with a FileHandler can be used to create an ``access.log`` file similar to 
Apache's. 

Like any standard middleware with a Paste entry point, TransLogger can be
configured to wrap your application using ``.ini`` file syntax.  First,
rename your Pyramid ``.ini`` file's ``[app:main]`` section to
``[app:mypyramidapp]``, then add a ``[filter:translogger]`` section, then use
a ``[pipeline:main]`` section file to form a WSGI pipeline with both the
translogger and your application in it.  For instance, change from this:

.. code-block:: ini 

    [app:main]
    use = egg:MyProject

To this:

.. code-block:: ini 

    [app:mypyramidapp]
    use = egg:MyProject

    [filter:translogger] 
    use = egg:Paste#translogger 
    setup_console_handler = False

    [pipeline:main]
    pipeline = translogger
               mypyramidapp

Using PasteDeploy this way to form and serve a pipeline is equivalent to
wrapping your app in a TransLogger instance via the bottom the ``main``
function of your project's ``__init__`` file:

.. code-block:: python 

    ...
    app = config.make_wsgi_app()
    from paste.translogger import TransLogger 
    app = TransLogger(app, setup_console_handler=False) 
    return app 

TransLogger will automatically setup a logging handler to the console when
called with no arguments, so it 'just works' in environments that don't
configure logging. Since we've configured our own logging handlers, we need
to disable that option via ``setup_console_handler = False``.

With the filter in place, TransLogger's logger (named the 'wsgi' logger) will
propagate its log messages to the parent logger (the root logger), sending
its output to the console when we request a page:

.. code-block:: text 

    00:50:53,694 INFO [myapp.views] Returning: Hello World!
                      (content-type: text/plain) 
    00:50:53,695 INFO [wsgi] 192.168.1.111 - - [11/Aug/2011:20:09:33 -0700] "GET /hello
    HTTP/1.1" 404 - "-" 
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en-US; rv:1.8.1.6) Gecko/20070725
    Firefox/2.0.0.6" 

To direct TransLogger to an ``access.log`` FileHandler, we need to add that
FileHandler to the wsgi logger's list of handlers:

.. code-block:: ini 

    # Begin logging configuration 

    [loggers] 
    keys = root, myapp, wsgi 

    [logger_wsgi] 
    level = INFO 
    handlers = handler_accesslog
    qualname = wsgi 
    propagate = 0 

    [handler_accesslog] 
    class = FileHandler 
    args = ('%(here)s/access.log','a') 
    level = INFO 
    formatter = generic 

As mentioned above, non-root loggers by default propagate their log records
to the root logger's handlers (currently the console handler). Setting
``propagate`` to 0 (false) here disables this; so the ``wsgi`` logger directs
its records only to the ``accesslog`` handler.

Finally, there's no need to use the ``generic`` formatter with TransLogger as
TransLogger itself provides all the information we need. We'll use a
formatter that passes-through the log messages as is:

.. code-block:: ini 

    [formatters] 
    keys = generic, accesslog 

.. code-block:: ini 

    [formatter_accesslog] 
    format = %(message)s 

Then wire this new ``accesslog`` formatter into the FileHandler: 

.. code-block:: ini 

    [handler_accesslog] 
    class = FileHandler 
    args = ('%(here)s/access.log','a') 
    level = INFO 
    formatter = accesslog 
