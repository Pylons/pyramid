.. _command_line_chapter:

Command-Line Pyramid
====================

Your :app:`Pyramid` application can be controlled and inspected using a
variety of command-line utilities.  These utilities are documented in this
chapter.

.. index::
   pair: matching views; printing
   single: pviews

.. _displaying_matching_views:

Displaying Matching Views for a Given URL
-----------------------------------------

For a big application with several views, it can be hard to keep the view
configuration details in your head, even if you defined all the views
yourself. You can use the ``pviews`` command in a terminal window to
print a summary of matching routes and views for a given URL in your
application. The ``pviews`` command accepts two arguments. The first
argument to ``pviews`` is the path to your application's ``.ini`` file and
section name inside the ``.ini`` file which points to your application.  This
should be of the format ``config_file#section_name``. The second argument is
the URL to test for matching views.  The ``section_name`` may be omitted; if
it is, it's considered to be ``main``.

Here is an example for a simple view configuration using :term:`traversal`:

.. code-block:: text
   :linenos:

   $ ../bin/pviews development.ini#tutorial /FrontPage

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

   $ ../bin/pviews development.ini#shootout /about

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

For a URL that doesn't match any views, ``pviews`` will simply print out a
*Not found* message.


.. index::
   single: interactive shell
   single: IPython
   single: pshell
   single: bpython

.. _interactive_shell:

The Interactive Shell
---------------------

Once you've installed your program for development using ``setup.py
develop``, you can use an interactive Python shell to execute expressions in
a Python environment exactly like the one that will be used when your
application runs "for real".  To do so, use the ``pshell`` command line
utility.

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

    chrism@thinko env26]$ bin/pshell starter/development.ini#MyProject
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

    chrism@thinko env26]$ bin/pshell starter/development.ini

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

    chrism@thinko env26]$ bin/pshell starter/development.ini
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

.. _ipython_or_bpython:

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
   single: proutes

.. _displaying_application_routes:

Displaying All Application Routes
---------------------------------

You can use the ``proutes`` command in a terminal window to print a summary
of routes related to your application.  Much like the ``pshell``
command (see :ref:`interactive_shell`), the ``proutes`` command
accepts one argument with the format ``config_file#section_name``.  The
``config_file`` is the path to your application's ``.ini`` file, and
``section_name`` is the ``app`` section name inside the ``.ini`` file which
points to your application.  By default, the ``section_name`` is ``main`` and
can be omitted.

For example:

.. code-block:: text
   :linenos:

   [chrism@thinko MyProject]$ ../bin/proutes development.ini
   Name            Pattern                        View
   ----            -------                        ----                     
   home            /                              <function my_view>
   home2           /                              <function my_view>
   another         /another                       None                     
   static/         static/*subpath                <static_view object>
   catchall        /*subpath                      <function static_view>

``proutes`` generates a table.  The table has three columns: a Name
column, a Pattern column, and a View column.  The items listed in the
Name column are route names, the items listed in the Pattern column are route
patterns, and the items listed in the View column are representations of the
view callable that will be invoked when a request matches the associated
route pattern.  The view column may show ``None`` if no associated view
callable could be found.  If no routes are configured within your
application, nothing will be printed to the console when ``proutes``
is executed.

.. index::
   pair: tweens; printing
   single: ptweens

.. _displaying_tweens:

Displaying "Tweens"
-------------------

A :term:`tween` is a bit of code that sits between the main Pyramid
application request handler and the WSGI application which calls it.  A user
can get a representation of both the implicit tween ordering (the ordering
specified by calls to :meth:`pyramid.config.Configurator.add_tween`) and the
explicit tween ordering (specified by the ``pyramid.tweens`` configuration
setting) orderings using the ``ptweens`` command.  Tween factories
will show up represented by their standard Python dotted name in the
``ptweens`` output.

For example, here's the ``pwteens`` command run against a system
configured without any explicit tweens:

.. code-block:: text
   :linenos:

   [chrism@thinko pyramid]$ myenv/bin/ptweens development.ini 
   "pyramid.tweens" config value NOT set (implicitly ordered tweens used)

   Implicit Tween Chain

   Position    Name                                                Alias 
   --------    ----                                                -----
   -           -                                                   INGRESS
   0           pyramid_debugtoolbar.toolbar.toolbar_tween_factory  pdbt
   1           pyramid.tweens.excview_tween_factory                excview
   -           -                                                   MAIN

Here's the ``pwteens`` command run against a system configured *with*
explicit tweens defined in its ``development.ini`` file:

.. code-block:: text
   :linenos:

   [chrism@thinko pyramid]$ ptweens development.ini  
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
by the above ``ptweens`` command which reports that the explicit tween chain
is used:

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

.. index::
   single: invoking a request
   single: prequest

.. _invoking_a_request:

Invoking a Request
------------------

You can use the ``prequest`` command-line utility to send a request to your
application and see the response body without starting a server.

There are two required arguments to ``prequest``:

- The config file/section: follows the format ``config_file#section_name``
  where ``config_file`` is the path to your application's ``.ini`` file and
  ``section_name`` is the ``app`` section name inside the ``.ini`` file.  The
  ``section_name`` is optional, it defaults to ``main``.  For example:
  ``development.ini``.

- The path: this should be the non-url-quoted path element of the URL to the
  resource you'd like to be rendered on the server.  For example, ``/``.

For example::

   $ bin/prequest development.ini /

This will print the body of the response to the console on which it was
invoked.

Several options are supported by ``prequest``.  These should precede any
config file name or URL.

``prequest`` has a ``-d`` (aka ``--display-headers``) option which prints the
status and headers returned by the server before the output::

   $ bin/prequest -d development.ini /

This will print the status, then the headers, then the body of the response
to the console.

You can add request header values by using the ``--header`` option::

   $ bin/prequest --header=Host=example.com development.ini /

Headers are added to the WSGI environment by converting them to their
CGI/WSGI equivalents (e.g. ``Host=example.com`` will insert the ``HTTP_HOST``
header variable as the value ``example.com``).  Multiple ``--header`` options
can be supplied.  The special header value ``content-type`` sets the
``CONTENT_TYPE`` in the WSGI environment.

By default, ``prequest`` sends a ``GET`` request.  You can change this by
using the ``-m`` (aka ``--method``) option.  ``GET``, ``HEAD``, ``POST`` and
``DELETE`` are currently supported.  When you use ``POST``, the standard
input of the ``prequest`` process is used as the ``POST`` body::

   $ bin/prequest -mPOST development.ini / < somefile

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
handling requests from a certain base. For example, we want to simulate
mounting our application at `https://example.com/prefix`, to ensure that
the generated URLs are correct for our deployment. This can be done by
either mutating the resulting request object, or more simply by constructing
the desired request and passing it into :func:`~pyramid.paster.bootstrap`:

.. code-block:: python

   from pyramid.paster import bootstrap
   from pyramid.request import Request

   request = Request.blank('/', base_url='https://example.com/prefix')
   env = bootstrap('/path/to/my/development.ini#another', request=request)
   print env['request'].application_url
   # will print 'https://example.com/prefix'

Now you can readily use Pyramid's APIs for generating URLs:

.. code-block:: python

   env['request'].route_url('verify', code='1337')
   # will return 'https://example.com/prefix/verify/1337'

Cleanup
~~~~~~~

When your scripting logic finishes, it's good manners to call the ``closer``
callback:

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

.. index::
   single: console script

.. _making_a_console_script:

Making Your Script into a Console Script
----------------------------------------

A "console script" is :term:`setuptools` terminology for a script that gets
installed into the ``bin`` directory of a Python :term:`virtualenv` (or
"base" Python environment) when a :term:`distribution` which houses that
script is installed.  Because it's installed into the ``bin`` directory of a
virtualenv when the distribution is installed, it's a convenient way to
package and distribute functionality that you can call from the command-line.
It's often more convenient to create a console script than it is to create a
``.py`` script and instruct people to call it with the "right" Python
interpreter.  A console script generates a file that lives in ``bin``, and when it's
invoked it will always use the "right" Python environment, which means it
will always be invoked in an environment where all the libraries it needs
(such as Pyramid) are available.

In general, you can make your script into a console script by doing the
following:

- Use an existing distribution (such as one you've already created via
  ``pcreate``) or create a new distribution that possesses at least one
  package or module.  It should, within any module within the distribution,
  house a callable (usually a function) that takes no arguments and which
  runs any of the code you wish to run.

- Add a ``[console_scripts]`` section to the ``entry_points`` argument of the
  distribution which creates a mapping between a script name and a dotted
  name representing the callable you added to your distribution.

- Run ``setup.py develop``, ``setup.py install``, or ``easy_install`` to get
  your distribution reinstalled.  When you reinstall your distribution, a
  file representing the script that you named in the last step will be in the
  ``bin`` directory of the virtualenv in which you installed the
  distribution.  It will be executable.  Invoking it from a terminal will
  execute your callable.

As an example, let's create some code that can be invoked by a console script
that prints the deployment settings of a Pyramid application.  To do so,
we'll pretend you have a distribution with a package in it named
``myproject``.  Within this package, we'll pretend you've added a
``scripts.py`` module which contains the following code:

.. code-block:: python
   :linenos:

   # myproject.scripts module

   import optparse
   import sys
   import textwrap

   from pyramid.paster import bootstrap

   def settings_show():
       description = """\
       Print the deployment settings for a Pyramid application.  Example:
       'psettings deployment.ini'
       """
       usage = "usage: %prog config_uri"
       parser = optparse.OptionParser(
           usage=usage,
           description=textwrap.dedent(description)
           )
       parser.add_option(
           '-o', '--omit',
           dest='omit',
           metavar='PREFIX',
           type='string',
           action='append',
           help=("Omit settings which start with PREFIX (you can use this "
                 "option multiple times)")
           )

       options, args = parser.parse_args(sys.argv[1:])
       if not len(args) >= 1:
           print('You must provide at least one argument')
           return 2
       config_uri = args[0]
       omit = options.omit
       if omit is None:
           omit = []
       env = bootstrap(config_uri)
       settings, closer = env['registry'].settings, env['closer']
       try:
           for k, v in settings.items():
               if any([k.startswith(x) for x in omit]):
                   continue
               print('%-40s     %-20s' % (k, v))
       finally:
           closer()

This script uses the Python ``optparse`` module to allow us to make sense out
of extra arguments passed to the script.  It uses the
:func:`pyramid.paster.bootstrap` function to get information about the the
application defined by a config file, and prints the deployment settings
defined in that config file.

After adding this script to the package, you'll need to tell your
distribution's ``setup.py`` about its existence.  Within your distribution's
top-level directory your ``setup.py`` file will look something like this:

.. code-block:: python
   :linenos:

   import os

   from setuptools import setup, find_packages

   here = os.path.abspath(os.path.dirname(__file__))
   README = open(os.path.join(here, 'README.txt')).read()
   CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

   requires = ['pyramid', 'pyramid_debugtoolbar']

   setup(name='MyProject',
         version='0.0',
         description='My project',
         long_description=README + '\n\n' +  CHANGES,
         classifiers=[
           "Programming Language :: Python",
           "Framework :: Pylons",
           "Topic :: Internet :: WWW/HTTP",
           "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
           ],
         author='',
         author_email='',
         url='',
         keywords='web pyramid pylons',
         packages=find_packages(),
         include_package_data=True,
         zip_safe=False,
         install_requires=requires,
         tests_require=requires,
         test_suite="myproject",
         entry_points = """\
         [paste.app_factory]
         main = myproject:main
         """,
         )

We're going to change the setup.py file to add an ``[console_scripts]``
section with in the ``entry_points`` string.  Within this section, you should
specify a ``scriptname = dotted.path.to:yourfunction`` line.  For example::

  [console_scripts]
  show_settings = myproject.scripts:settings_show

The ``show_settings`` name will be the name of the script that is installed
into ``bin``.  The colon (``:``) between ``myproject.scripts`` and
``settings_show`` above indicates that ``myproject.scripts`` is a Python
module, and ``settings_show`` is the function in that module which contains
the code you'd like to run as the result of someone invoking the
``show_settings`` script from their command line.

The result will be something like:

.. code-block:: python
   :linenos:

   import os

   from setuptools import setup, find_packages

   here = os.path.abspath(os.path.dirname(__file__))
   README = open(os.path.join(here, 'README.txt')).read()
   CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

   requires = ['pyramid', 'pyramid_debugtoolbar']

   setup(name='MyProject',
         version='0.0',
         description='My project',
         long_description=README + '\n\n' +  CHANGES,
         classifiers=[
           "Programming Language :: Python",
           "Framework :: Pylons",
           "Topic :: Internet :: WWW/HTTP",
           "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
           ],
         author='',
         author_email='',
         url='',
         keywords='web pyramid pylons',
         packages=find_packages(),
         include_package_data=True,
         zip_safe=False,
         install_requires=requires,
         tests_require=requires,
         test_suite="myproject",
         entry_points = """\
         [paste.app_factory]
         main = myproject:main
         [console_scripts]
         show_settings = myproject.scripts:settings_show
         """,
         )

Once you've done this, invoking ``$somevirtualenv/bin/python setup.py
develop`` will install a file named ``show_settings`` into the
``$somevirtualenv/bin`` directory with a small bit of Python code that points
to your entry point.  It will be executable.  Running it without any
arguments will print an error and exit.  Running it with a single argument
that is the path of a config file will print the settings.  Running it with
an ``--omit=foo`` argument will omit the settings that have keys that start
with ``foo``.  Running it with two "omit" options (e.g. ``--omit=foo
--omit=bar``) will omit all settings that have keys that start with either
``foo`` or ``bar``::

  [chrism@thinko somevenv]$ bin/show_settings development.ini \
                            --omit=pyramid \
                            --omit=debugtoolbar
  debug_routematch                             False               
  debug_templates                              True                
  reload_templates                             True                
  mako.directories                             []                  
  debug_notfound                               False               
  default_locale_name                          en                  
  reload_resources                             False               
  debug_authorization                          False               
  reload_assets                                False               
  prevent_http_cache                           False               

Pyramid's ``pserve``, ``pcreate``, ``pshell``, ``prequest``, ``ptweens`` and
other ``p*`` scripts are implemented as console scripts.  When you invoke one
of those, you are using a console script.
