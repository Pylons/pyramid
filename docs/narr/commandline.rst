.. _command_line_chapter:

Command-Line Pyramid
====================

Your :app:`Pyramid` application can be controlled and inspected using a
variety of command-line utilities.  These utilities are documented in this
chapter.

.. index::
   pair: matching views; printing
   single: paster pviews

.. _displaying_matching_views:

Displaying Matching Views for a Given URL
-----------------------------------------

For a big application with several views, it can be hard to keep the view
configuration details in your head, even if you defined all the views
yourself. You can use the ``paster pviews`` command in a terminal window to
print a summary of matching routes and views for a given URL in your
application. The ``paster pviews`` command accepts two arguments. The first
argument to ``pviews`` is the path to your application's ``.ini`` file and
section name inside the ``.ini`` file which points to your application.  This
should be of the format ``config_file#section_name``. The second argument is
the URL to test for matching views.  The ``section_name`` may be omitted; if
it is, it's considered to be ``main``.

Here is an example for a simple view configuration using :term:`traversal`:

.. code-block:: text
   :linenos:

   $ ../bin/paster pviews development.ini#tutorial /FrontPage

   URL = /FrontPage

       context: <tutorial.models.Page object at 0xa12536c>
       view name:

       View:
       -----
       tutorial.views.view_page
       required permission = view

The output always has the requested URL at the top and below that all the
views that matched with their view configuration details. In this example
only one view matches, so there is just a single *View* section. For each
matching view, the full code path to the associated view callable is shown,
along with any permissions and predicates that are part of that view
configuration.

A more complex configuration might generate something like this:

.. code-block:: text
   :linenos:

   $ ../bin/paster pviews development.ini#shootout /about

   URL = /about

       context: <shootout.models.RootFactory object at 0xa56668c>
       view name: about

       Route:
       ------
       route name: about
       route pattern: /about
       route path: /about
       subpath:
       route predicates (request method = GET)

           View:
           -----
           shootout.views.about_view
           required permission = view
           view predicates (request_param testing, header X/header)

       Route:
       ------
       route name: about_post
       route pattern: /about
       route path: /about
       subpath:
       route predicates (request method = POST)

           View:
           -----
           shootout.views.about_view_post
           required permission = view
           view predicates (request_param test)

           View:
           -----
           shootout.views.about_view_post2
           required permission = view
           view predicates (request_param test2)

In this case, we are dealing with a :term:`URL dispatch` application. This
specific URL has two matching routes. The matching route information is
displayed first, followed by any views that are associated with that route.
As you can see from the second matching route output, a route can be
associated with more than one view.

For a URL that doesn't match any views, ``paster pviews`` will simply print
out a *Not found* message.


.. index::
   single: interactive shell
   single: IPython
   single: bpython
   single: paster pshell
   single: pshell

.. _interactive_shell:

The Interactive Shell
---------------------

Once you've installed your program for development using ``setup.py
develop``, you can use an interactive Python shell to execute expressions in
a Python environment exactly like the one that will be used when your
application runs "for real".  To do so, use the ``paster pshell`` command.

The argument to ``pshell`` follows the format ``config_file#section_name``
where ``config_file`` is the path to your application's ``.ini`` file and
``section_name`` is the ``app`` section name inside the ``.ini`` file which
points to your application.  For example, if your application ``.ini`` file
might have a ``[app:main]`` section that looks like so:

.. code-block:: ini
   :linenos:

   [app:main]
   use = egg:MyProject
   pyramid.reload_templates = true
   pyramid.debug_authorization = false
   pyramid.debug_notfound = false
   pyramid.debug_templates = true
   pyramid.default_locale_name = en

If so, you can use the following command to invoke a debug shell using the
name ``MyProject`` as a section name:

.. code-block:: text

    chrism@thinko env26]$ bin/paster pshell starter/development.ini#MyProject
    Python 2.6.5 (r265:79063, Apr 29 2010, 00:31:32) 
    [GCC 4.4.3] on linux2
    Type "help" for more information.

    Environment:
      app          The WSGI application.
      registry     Active Pyramid registry.
      request      Active request object.
      root         Root of the default resource tree.
      root_factory Default root factory used to create `root`.

    >>> root
    <myproject.resources.MyResource object at 0x445270>
    >>> registry
    <Registry myproject>
    >>> registry.settings['pyramid.debug_notfound']
    False
    >>> from myproject.views import my_view
    >>> from pyramid.request import Request
    >>> r = Request.blank('/')
    >>> my_view(r)
    {'project': 'myproject'}

The WSGI application that is loaded will be available in the shell as the
``app`` global. Also, if the application that is loaded is the :app:`Pyramid`
app with no surrounding middleware, the ``root`` object returned by the
default :term:`root factory`, ``registry``, and ``request`` will be
available.

You can also simply rely on the ``main`` default section name by omitting any
hash after the filename:

.. code-block:: text

    chrism@thinko env26]$ bin/paster pshell starter/development.ini

Press ``Ctrl-D`` to exit the interactive shell (or ``Ctrl-Z`` on Windows).

.. index::
   pair: pshell; extending

.. _extending_pshell:

Extending the Shell
~~~~~~~~~~~~~~~~~~~

It is convenient when using the interactive shell often to have some
variables significant to your application already loaded as globals when
you start the ``pshell``. To facilitate this, ``pshell`` will look for a
special ``[pshell]`` section in your INI file and expose the subsequent
key/value pairs to the shell.  Each key is a variable name that will be
global within the pshell session; each value is a :term:`dotted Python name`.
If specified, the special key ``setup`` should be a :term:`dotted Python name`
pointing to a callable that accepts the dictionary of globals that will
be loaded into the shell. This allows for some custom initializing code
to be executed each time the ``pshell`` is run. The ``setup`` callable
can also be specified from the commandline using the ``--setup`` option
which will override the key in the INI file.

For example, you want to expose your model to the shell, along with the
database session so that you can mutate the model on an actual database.
Here, we'll assume your model is stored in the ``myapp.models`` package.

.. code-block:: ini
   :linenos:

   [pshell]
   setup = myapp.lib.pshell.setup
   m = myapp.models
   session = myapp.models.DBSession
   t = transaction

By defining the ``setup`` callable, we will create the module
``myapp.lib.pshell`` containing a callable named ``setup`` that will receive
the global environment before it is exposed to the shell. Here we mutate the
environment's request as well as add a new value containing a WebTest version
of the application to which we can easily submit requests.

.. code-block:: python
    :linenos:

    # myapp/lib/pshell.py
    from webtest import TestApp

    def setup(env):
        env['request'].host = 'www.example.com'
        env['request'].scheme = 'https'
        env['testapp'] = TestApp(env['app'])

When this INI file is loaded, the extra variables ``m``, ``session`` and
``t`` will be available for use immediately. Since a ``setup`` callable
was also specified, it is executed and a new variable ``testapp`` is
exposed, and the request is configured to generate urls from the host
``http://www.example.com``. For example:

.. code-block:: text

    chrism@thinko env26]$ bin/paster pshell starter/development.ini
    Python 2.6.5 (r265:79063, Apr 29 2010, 00:31:32) 
    [GCC 4.4.3] on linux2
    Type "help" for more information.

    Environment:
      app          The WSGI application.
      registry     Active Pyramid registry.
      request      Active request object.
      root         Root of the default resource tree.
      root_factory Default root factory used to create `root`.
      testapp      <webtest.TestApp object at ...>

    Custom Variables:
      m            myapp.models
      session      myapp.models.DBSession
      t            transaction

    >>> testapp.get('/')
    <200 OK text/html body='<!DOCTYPE...l>\n'/3337>
    >>> request.route_url('home')
    'https://www.example.com/'

.. index::
   single: IPython
   single: bpython

IPython or bpython
~~~~~~~~~~~~~~~~~~

If you have `IPython <http://en.wikipedia.org/wiki/IPython>`_ or  
`bpython <http://bpython-interpreter.org/>`_ or both installed in
the interpreter you use to invoke the ``pshell`` command, ``pshell`` will 
autodiscover them and use the first respectively found in this order :
IPython, bpython, standard Python interpreter. However you could 
specifically invoke one of your choice with the ``-p choice`` or  
``--python-shell choice`` option.

.. code-block:: text

   [chrism@vitaminf shellenv]$ ../bin/pshell -p ipython | bpython | python \
                                development.ini#MyProject


.. index::
   pair: routes; printing
   single: paster proutes
   single: proutes

.. _displaying_application_routes:

Displaying All Application Routes
---------------------------------

You can use the ``paster proutes`` command in a terminal window to print a
summary of routes related to your application.  Much like the ``paster
pshell`` command (see :ref:`interactive_shell`), the ``paster proutes``
command accepts one argument with the format ``config_file#section_name``.
The ``config_file`` is the path to your application's ``.ini`` file, and
``section_name`` is the ``app`` section name inside the ``.ini`` file which
points to your application.  By default, the ``section_name`` is ``main`` and
can be omitted.

For example:

.. code-block:: text
   :linenos:

   [chrism@thinko MyProject]$ ../bin/paster proutes development.ini#MyProject
   Name            Pattern                        View
   ----            -------                        ----                     
   home            /                              <function my_view>
   home2           /                              <function my_view>
   another         /another                       None                     
   static/         static/*subpath                <static_view object>
   catchall        /*subpath                      <function static_view>

``paster proutes`` generates a table.  The table has three columns: a Name
column, a Pattern column, and a View column.  The items listed in the
Name column are route names, the items listed in the Pattern column are route
patterns, and the items listed in the View column are representations of the
view callable that will be invoked when a request matches the associated
route pattern.  The view column may show ``None`` if no associated view
callable could be found.  If no routes are configured within your
application, nothing will be printed to the console when ``paster proutes``
is executed.

.. index::
   pair: tweens; printing
   single: paster ptweens
   single: ptweens

.. _displaying_tweens:

Displaying "Tweens"
-------------------

A :term:`tween` is a bit of code that sits between the main Pyramid
application request handler and the WSGI application which calls it.  A user
can get a representation of both the implicit tween ordering (the ordering
specified by calls to :meth:`pyramid.config.Configurator.add_tween`) and the
explicit tween ordering (specified by the ``pyramid.tweens`` configuration
setting) orderings using the ``paster ptweens`` command.  Tween factories
will show up represented by their standard Python dotted name in the
``paster ptweens`` output.

For example, here's the ``paster pwteens`` command run against a system
configured without any explicit tweens:

.. code-block:: text
   :linenos:

   [chrism@thinko pyramid]$ paster ptweens development.ini 
   "pyramid.tweens" config value NOT set (implicitly ordered tweens used)

   Implicit Tween Chain

   Position    Name                                                Alias 
   --------    ----                                                -----
   -           -                                                   INGRESS
   0           pyramid_debugtoolbar.toolbar.toolbar_tween_factory  pdbt
   1           pyramid.tweens.excview_tween_factory                excview
   -           -                                                   MAIN

Here's the ``paster pwteens`` command run against a system configured *with*
explicit tweens defined in its ``development.ini`` file:

.. code-block:: text
   :linenos:

   [chrism@thinko pyramid]$ paster ptweens development.ini  
   "pyramid.tweens" config value set (explicitly ordered tweens used)

   Explicit Tween Chain (used)

   Position    Name                                                             
   --------    ----                                                             
   -           INGRESS                                                          
   0           starter.tween_factory2                                           
   1           starter.tween_factory1                                           
   2           pyramid.tweens.excview_tween_factory                             
   -           MAIN                                                             

   Implicit Tween Chain (not used)

   Position    Name                                                Alias
   --------    ----                                                -----
   -           -                                                   INGRESS
   0           pyramid_debugtoolbar.toolbar.toolbar_tween_factory  pdbt
   1           pyramid.tweens.excview_tween_factory                excview
   -           -                                                   MAIN

Here's the application configuration section of the ``development.ini`` used
by the above ``paster ptweens`` command which reprorts that the explicit
tween chain is used:

.. code-block:: text
   :linenos:

   [app:main]
   use = egg:starter
   reload_templates = true
   debug_authorization = false
   debug_notfound = false
   debug_routematch = false
   debug_templates = true
   default_locale_name = en
   pyramid.include = pyramid_debugtoolbar
   pyramid.tweens = starter.tween_factory2
                    starter.tween_factory1
                    pyramid.tweens.excview_tween_factory

See :ref:`registering_tweens` for more information about tweens.

.. _writing_a_script:

Writing a Script
----------------

All web applications are, at their hearts, systems which accept a request and
return a response.  When a request is accepted by a :app:`Pyramid`
application, the system receives state from the request which is later relied
on by your application code.  For example, one :term:`view callable` may assume
it's working against a request that has a ``request.matchdict`` of a
particular composition, while another assumes a different composition of the
matchdict.

In the meantime, it's convenient to be able to write a Python script that can
work "in a Pyramid environment", for instance to update database tables used
by your :app:`Pyramid` application.  But a "real" Pyramid environment doesn't
have a completely static state independent of a request; your application
(and Pyramid itself) is almost always reliant on being able to obtain
information from a request.  When you run a Python script that simply imports
code from your application and tries to run it, there just is no request
data, because there isn't any real web request.  Therefore some parts of your
application and some Pyramid APIs will not work.

For this reason, :app:`Pyramid` makes it possible to run a script in an
environment much like the environment produced when a particular
:term:`request` reaches your :app:`Pyramid` application.  This is achieved by
using the :func:`pyramid.paster.bootstrap` command in the body of your
script.

.. note:: This feature is new as of :app:`Pyramid` 1.1.

In the simplest case, :func:`pyramid.paster.bootstrap` can be used with a
single argument, which accepts the :term:`PasteDeploy` ``.ini`` file
representing Pyramid your application configuration as a single argument:

.. code-block:: python

   from pyramid.paster import bootstrap
   env = bootstrap('/path/to/my/development.ini')
   print env['request'].route_url('home')

:func:`pyramid.paster.bootstrap` returns a dictionary containing
framework-related information.  This dictionary will always contain a
:term:`request` object as its ``request`` key.

The following keys are available in the ``env`` dictionary returned by
:func:`pyramid.paster.bootstrap`:

request

    A :class:`pyramid.request.Request` object implying the current request
    state for your script.

app

    The :term:`WSGI` application object generated by bootstrapping.

root

    The :term:`resource` root of your :app:`Pyramid` application.  This is an
    object generated by the :term:`root factory` configured in your
    application.

registry

    The :term:`application registry` of your :app:`Pyramid` application.

closer

    A parameterless callable that can be used to pop an internal
    :app:`Pyramid` threadlocal stack (used by
    :func:`pyramid.threadlocal.get_current_registry` and
    :func:`pyramid.threadlocal.get_current_request`) when your scripting job
    is finished.

Let's assume that the ``/path/to/my/development.ini`` file used in the
example above looks like so:

.. code-block:: ini

   [pipeline:main]
   pipeline = translogger
              another

   [filter:translogger]
   filter_app_factory = egg:Paste#translogger
   setup_console_handler = False
   logger_name = wsgi

   [app:another]
   use = egg:MyProject

The configuration loaded by the above bootstrap example will use the
configuration implied by the ``[pipeline:main]`` section of your
configuration file by default.  Specifying ``/path/to/my/development.ini`` is
logically equivalent to specifying ``/path/to/my/development.ini#main``.  In
this case, we'll be using a configuration that includes an ``app`` object
which is wrapped in the Paste "translogger" middleware (which logs requests
to the console).

You can also specify a particular *section* of the PasteDeploy ``.ini`` file
to load instead of ``main``:

.. code-block:: python

   from pyramid.paster import bootstrap
   env = bootstrap('/path/to/my/development.ini#another')
   print env['request'].route_url('home')

The above example specifies the ``another`` ``app``, ``pipeline``, or
``composite`` section of your PasteDeploy configuration file. The ``app``
object present in the ``env`` dictionary returned by
:func:`pyramid.paster.bootstrap` will be a :app:`Pyramid` :term:`router`.

Changing the Request
~~~~~~~~~~~~~~~~~~~~

By default, Pyramid will generate a request object in the ``env`` dictionary
for the URL ``http://localhost:80/``. This means that any URLs generated
by Pyramid during the execution of your script will be anchored here. This
is generally not what you want.

So how do we make Pyramid generate the correct URLs?

Assuming that you have a route configured in your application like so:

.. code-block:: python

   config.add_route('verify', '/verify/{code}')

You need to inform the Pyramid environment that the WSGI application is
handling requests from a certain base. For example, we want to mount our
application at `example.com/prefix` and the generated URLs should use HTTPS.
This can be done by mutating the request object:

.. code-block:: python

   from pyramid.paster import bootstrap
   env = bootstrap('/path/to/my/development.ini#another')
   env['request'].host = 'example.com'
   env['request'].scheme = 'https'
   env['request'].script_name = '/prefix'
   print env['request'].application_url
   # will print 'https://example.com/prefix/another/url'

Now you can readily use Pyramid's APIs for generating URLs:

.. code-block:: python

   env['request'].route_url('verify', code='1337')
   # will return 'https://example.com/prefix/verify/1337'

Cleanup
~~~~~~~

When your scripting logic finishes, it's good manners (but not required) to
call the ``closer`` callback:

.. code-block:: python

   from pyramid.paster import bootstrap
   env = bootstrap('/path/to/my/development.ini')

   # .. do stuff ...

   env['closer']()

Setting Up Logging
~~~~~~~~~~~~~~~~~~

By default, :func:`pyramid.paster.bootstrap` does not configure logging
parameters present in the configuration file.  If you'd like to configure
logging based on ``[logger]`` and related sections in the configuration file,
use the following command:

.. code-block:: python

   import logging.config
   logging.config.fileConfig('/path/to/my/development.ini')
