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
application. The ``paster pviews`` command accepts two arguments. The
first argument to ``pviews`` is the path to your application's ``.ini`` file
and section name inside the ``.ini`` file which points to your application.
This should be of the format ``config_file#section_name``. The second argument
is the URL to test for matching views.

Here is an example for a simple view configuration using :term:`traversal`:

.. code-block:: text
   :linenos:

   $ ../bin/paster pviews development.ini tutorial /FrontPage

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
points to *your application* as opposed to any other section within the
``.ini`` file.  For example, if your application ``.ini`` file might have a
``[app:MyProject]`` section that looks like so:

.. code-block:: ini
   :linenos:

   [app:MyProject]
   use = egg:MyProject
   reload_templates = true
   debug_authorization = false
   debug_notfound = false
   debug_templates = true
   default_locale_name = en

If so, you can use the following command to invoke a debug shell using the
name ``MyProject`` as a section name:

.. code-block:: text

   [chrism@vitaminf shellenv]$ ../bin/paster pshell development.ini#MyProject
   Python 2.4.5 (#1, Aug 29 2008, 12:27:37)
   [GCC 4.0.1 (Apple Inc. build 5465)] on darwin

   Default Variables:
     app          The WSGI Application
     root         The root of the default resource tree.
     registry     The Pyramid registry object.
     settings     The Pyramid settings object.

   >>> root
   <myproject.resources.MyResource object at 0x445270>
   >>> registry
   <Registry myproject>
   >>> settings['debug_notfound']
   False
   >>> from myproject.views import my_view
   >>> from pyramid.request import Request
   >>> r = Request.blank('/')
   >>> my_view(r)
   {'project': 'myproject'}

The WSGI application that is loaded will be available in the shell as the
``app`` global. Also, if the application that is loaded is the
:app:`Pyramid` app with no surrounding middleware, the ``root`` object
returned by the default :term:`root factory`, ``registry``, and ``settings``
will be available.

The interactive shell will not be able to load some of the globals like
``root``, ``registry`` and ``settings`` if the section name specified when
loading ``pshell`` is not referencing your :app:`Pyramid` application directly.
For example, if you have the following ``.ini`` file content:

.. code-block:: ini
   :linenos:

   [app:MyProject]
   use = egg:MyProject
   reload_templates = true
   debug_authorization = false
   debug_notfound = false
   debug_templates = true
   default_locale_name = en

   [pipeline:main]
   pipeline =
       egg:WebError#evalerror
       MyProject

Use ``MyProject`` instead of ``main`` as the section name argument to
``pshell`` against the above ``.ini`` file (e.g. ``paster pshell
development.ini#MyProject``).

Press ``Ctrl-D`` to exit the interactive shell (or ``Ctrl-Z`` on Windows).

.. _extending_pshell:

Extending the Shell
~~~~~~~~~~~~~~~~~~~

It is sometimes convenient when using the interactive shell often to have
some variables significant to your application already loaded as globals
when you start the ``pshell``. To facilitate this, ``pshell`` will look
for a special ``[pshell]`` section in your INI file and expose the subsequent
key/value pairs to the shell.

For example, you want to expose your model to the shell, along with the
database session so that you can mutate the model on an actual database.
Here, we'll assume your model is stored in the ``myapp.models`` package.

.. code-block:: ini
   :linenos:

   [pshell]
   m = myapp.models
   session = myapp.models.DBSession
   t = transaction

When this INI file is loaded, the extra variables ``m``, ``session`` and
``t`` will be available for use immediately. This happens regardless of
whether the ``registry`` and other special variables are loaded.

IPython
~~~~~~~

If you have `IPython <http://en.wikipedia.org/wiki/IPython>`_ installed in
the interpreter you use to invoke the ``paster`` command, the ``pshell``
command will use an IPython interactive shell instead of a standard Python
interpreter shell.  If you don't want this to happen, even if you have
IPython installed, you can pass the ``--disable-ipython`` flag to the
``pshell`` command to use a standard Python interpreter shell
unconditionally.

.. code-block:: text

   [chrism@vitaminf shellenv]$ ../bin/paster pshell --disable-ipython \
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
The ``config_file`` is the path to your application's ``.ini`` file,
and ``section_name`` is the ``app`` section name inside the ``.ini`` file
which points to your application.

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

.. _writing_a_script:

Writing a Script
----------------

All web applications are, at their hearts, systems which accept a request and
return a response.  When a request is accepted by a :app:`Pyramid`
application, the system receives state from the request which is later relied
on your application code.  For example, one :term:`view callable` may assume
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
   info = bootstrap('/path/to/my/development.ini')
   print info['request'].route_url('home')

:func:`pyramid.paster.bootstrap` returns a dictionary containing
framework-related information.  This dictionary will always contain a
:term:`request` object as its ``request`` key.

The following keys are available in the ``info`` dictionary returned by
:func:`~pyramid.paster.bootstrap`:

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
   pipeline = egg:WebError#evalerror
              another

   [app:another]
   use = egg:MyProject

The configuration loaded by the above bootstrap example will use the
configuration implied by the ``[pipeline:main]`` section of your
configuration file by default.  Specifying ``/path/to/my/development.ini`` is
logically equivalent to specifying ``/path/to/my/development.ini#main``.  In
this case, we'll be using a configuration that includes an ``app`` object
which is wrapped in the WebError ``evalerror`` middleware.

You can also specify a particular *section* of the PasteDeploy ``.ini`` file
to load instead of ``main``:

.. code-block:: python

   from pyramid.paster import bootstrap
   info = bootstrap('/path/to/my/development.ini#another')
   print info['request'].route_url('home')

The above example specifies the ``another`` ``app``, ``pipeline``, or
``composite`` section of your PasteDeploy configuration file.  In the case
that we're using a configuration file that looks like this:

.. code-block:: ini

   [pipeline:main]
   pipeline = egg:WebError#evalerror
              another

   [app:another]
   use = egg:MyProject

It will mean that the ``/path/to/my/development.ini#another`` argument passed
to bootstrap will imply the ``[app:another]`` section in our configuration
file.  Therefore, it will not wrap the WSGI application present in the info
dictionary as ``app`` using WebError's ``evalerror`` middleware.  The ``app``
object present in the info dictionary returned by
:func:`~pyramid.paster.bootstrap` will be a :app:`Pyramid` :term:`router`
instead.

By default, Pyramid will general a request object in the ``info`` dictionary
anchored at the root path (``/``).  You can alternately supply your own
:class:`pyramid.request.Request` instance to the
:func:`~pyramid.paster.bootstrap` function, to set up request parameters
beforehand:

.. code-block:: python

   from pyramid.request import Request
   request = Request.blank('/another/url')
   from pyramid.paster import bootstrap
   info = bootstrap('/path/to/my/development.ini#another', request=request)
   print info['request'].path_info # will print '/another/url'

When your scripting logic finishes, it's good manners (but not required) to
call the ``closer`` callback:

.. code-block:: python

   from pyramid.paster import bootstrap
   info = bootstrap('/path/to/my/development.ini')

   # .. do stuff ...

   info['closer']()



