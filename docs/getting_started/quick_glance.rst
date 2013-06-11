============
Quick Glance
============

Pyramid lets you start small and finish big. The
:doc:`index` guide
walks you through many of the key features. Let's put the emphasis on
*start* by doing a quick tour through Pyramid.

This *Quick Glance* is shorthand, snippet-oriented. It is not intended
as full example. Instead, the other chapters will provide complete
examples.

.. note::

    Like the rest of Getting Started, we're using Python 3 in
    our samples. You can too, or you can use Python 2.7.

The Smallest
============

Microframeworks have shown that learning starts best from a very small
first step. Here's a tiny application in Pyramid:

.. literalinclude:: quick_glance/app1.py

This simple example is easy to run. Save this as ``app.py`` and run it:

.. code-block:: bash

 $ python3 ./app.py

Finally, open `http://localhost:8081/ <http://localhost:8081/>`_ in a
browser and you will see the ``Hello World!`` message.

At a high level, we wrote a Python module, which when executed,
started an HTTP server. This HTTP server ran a WSGI application with
one "view". This view handled the ``http://localhost:8081/`` URL.

More specifically:

#. We imported an HTTP server (``make_server``), a configuration system
   (``Configurator``), and a way to send HTTP responses (``Response``).

#. We made a ``hello_world`` function that returned a ``Response``.

#. Our ``main`` function started the configuration, added a "route",
   and then mapped that route to a "view".

#. To finish, we then made a WSGI app and served it.
   ``if __name__ == '__main__':`` is a standard Python technique to
   execute code when it is run from the command line instead of
   imported into another module.

.. note::

  The configuration of the route and the view are split. Other systems
  let you bundle those together. Pyramid makes you do the extra step,
  but for a reason: this lets you control the ordering. More on this
  later.

Using Decorators and Matchdicts
===============================

Let's repeat the smallest step, but make it a little more functional
and elegant by adding:

- Echo back a name sent in via the URL

- The URL is below the top of the site

- Use a decorator to register the view

Let's make update our ``app.py`` module:

.. literalinclude:: quick_glance/app2.py
    :linenos:

When you run ``python3 ./app.py`` and visit a URL such as
``http://localhost:8081/hello/amy``, the response includes ``amy`` in
the HTML.

This module, while small, starts to show how many Pyramid applications
are composed:

#. We use a decorator around the view, to put the configuration closer
   to the code.

#. We tell the ``Configurator`` to go look for decorators.

Templates
=========

You usually won't embed an HTML string directly in Python, but instead,
will use a templating language. Pyramid comes bundled with Chameleon
and Mako, but Jinja2 is popular. Let's install it:

.. code-block:: bash

    $ pip install pyramid_jinja2

With the package installed, we can include the template bindings into
our configuration:

.. code-block:: python

    config.include('pyramid_jinja2')

Our view changes. We only return Python data and let the ``renderer``
argument tell Pyramid to pass the response through Jinja2:

.. code-block:: python

    @view_config(route_name='hello', renderer="app3.jinja2")
    def hello_world(request):
        return dict(name=request.matchdict['name'])

Our template is HTML-oriented with a little logic in the ``<h1>``:

.. code-block:: html

    <html lang="en">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>Quick Glance</title>
    </head>
    <body>
    <h1>Hello {{ name }}!</h1>
    </body>
    </html>

Static Assets
=============

Of course the Web is more than just markup. You need static assets:
CSS, JS, and images. Let's point our web app at a directory where
Pyramid will serve some static assets. First, another call to the
``Configurator``:

.. code-block:: python

    config.add_static_view(name='static', path='static')

This tells our WSGI application to map requests under
``http://localhost:8081/static/`` to files and directories inside a
``static`` directory alongside our Python module.

Next, make a directory ``static`` and place ``app.css`` inside:

.. code-block:: css

    body {
        margin: 2em;
        font-family: sans-serif;
    }

All we need to do now is point to it in the ``<head>`` of our Jinja2
template:

.. code-block:: html

    <link rel="stylesheet" href="/static/app.css" />

Returning JSON
==============

Modern web apps are more than rendered HTML. Dynamic pages now use
JavaScript update the UI in the browser by requesting server data as
JSON.

Pyramid supports this with a JSON renderer:

.. code-block:: python

    @view_config(route_name='hello_json', renderer='json')
    def hello_json(request):
        return [1, 2, 3]

This wires up a view that returns some data through the JSON
"renderer", which calls Python's JSON support to serialize the data
into JSON, set the appropriate HTTP headers, and more.

The view needs a route added to the ``Configurator``:

.. code-block:: python

    config.add_route('hello_json', 'hello.json')


View Classes
============

Free-standing functions are the regular way to do views. Many times,
though, you have several views that are closely related. For example,
a document might have many different ways to look at it.

For some people, grouping these together makes logical sense. A view
class lets you group views, sharing some state assignments, and
using helper functions as class methods.

Let's re-organize our two views into methods on a view class:

.. code-block:: python

    class HelloWorldViews:
        def __init__(self, request):
            self.request = request

        @view_config(route_name='hello', renderer='app4.jinja2')
        def hello_world(self):
            return dict(name=self.request.matchdict['name'])


        @view_config(route_name='hello_json', renderer='json')
        def hello_json(self):
            return [1, 2, 3]

Everything else remains the same.

Quick Project Startup with Scaffolds
====================================

So far we have done all of our *Quick Glance* as a single Python file.
No Python packages, no structure. Most Pyramid projects, though,
aren't developed this way.

To ease the process of getting started, Pyramid provides *scaffolds*
that generate sample projects. Not just Pyramid itself: add-ons such as
``pyramid_jinja2`` (or your own projects) can register there own
scaffolds.

We use Pyramid's ``pcreate`` command to generate our starting point
from a scaffold. What does this command look like?

.. code-block:: bash

    $ pcreate --help
    Usage: pcreate [options] output_directory

    Render Pyramid scaffolding to an output directory

    Options:
      -h, --help            show this help message and exit
      -s SCAFFOLD_NAME, --scaffold=SCAFFOLD_NAME
                            Add a scaffold to the create process (multiple -s args
                            accepted)
      -t SCAFFOLD_NAME, --template=SCAFFOLD_NAME
                            A backwards compatibility alias for -s/--scaffold.
                            Add a scaffold to the create process (multiple -t args
                            accepted)
      -l, --list            List all available scaffold names
      --list-templates      A backwards compatibility alias for -l/--list.  List
                            all available scaffold names.
      --simulate            Simulate but do no work
      --overwrite           Always overwrite
      --interactive         When a file would be overwritten, interrogate

Let's see what our Pyramid install supports as starting-point scaffolds:

.. code-block:: bash

    $ pcreate --list
    Available scaffolds:
      alchemy:                 Pyramid SQLAlchemy project using url dispatch
      pyramid_jinja2_starter:  pyramid jinja2 starter project
      starter:                 Pyramid starter project
      zodb:                    Pyramid ZODB project using traversal

The ``pyramid_jinja2_starter`` looks interesting. From the parent
directory of where we want our Python package to be generated,
let's use that scaffold to make our project:

.. code-block:: bash

    $ pcreate --scaffold pyramid_jinja2_starter hello_world

After printing a bunch of lines about the files being generated,
we now have a Python package. As described in the *official
instructions*, we need to install this as a development package:

.. code-block:: bash

    $ cd hello_world
    $ python3.3 ./setup.py develop

What did we get? A top-level directory ``hello_world`` that includes
some packaging files and a subdirectory ``hello_world`` that has
sample files for our application:

.. code-block:: bash

    $ ls
    CHANGES.txt		development.ini		hello_world.egg-info
    MANIFEST.in		message-extraction.ini	setup.cfg
    README.txt		hello_world		setup.py

    $ ls hello_world
    __init__.py	locale		static		tests.py
    __pycache__	models.py	templates	views.py

We are moving in the direction of a full-featured Pyramid project,
with a proper setup for Python standards (packaging) and Pyramid
configuration. This includes a new way of running your application:

.. code-block:: bash

    $ pserve development.ini

With ``pserve``, your application isn't responsible for finding a WSGI
server and launching your WSGI app. Also, much of the wiring of your
application can be moved to a declarative ``.ini`` configuration file.

In your browser, visit
`http://localhost:6543/ <http://localhost:6543/>`_ and you'll see that
things look very different. In the next few sections we'll cover some
decisions made by this scaffold.

Let's look at ``pserve`` and configuration in more depth.

Application Running with ``pserve``
===================================

When you install Pyramid, a small command program called ``pserve`` is
written to your ``bin`` directory. This program is an executable Python
module. It's very small, getting most of its brains via import.

You can run ``pserve`` with ``--help`` to see some of its options.
Doing so reveals that you can ask ``pserve`` to watch your development
files and reload the server when they change:

.. code-block:: bash

    $ pserve development.ini --reload

By design, ``pserve`` itself isn't all that interesting. Instead,
its brains from your project's wiring, as expressed in the
configuration file you supply it.

.. seealso:: See Also: :ref:`what_is_this_pserve_thing`

Three Cool Things About ``pserve``
----------------------------------

1. *Multiple .ini files*. You might have some settings in
   development mode or some in production mode. Maybe you are writing an
   add-on that needs to be wired-up by other people.

2. *Choice of WSGI server*. ``pserve`` itself isn't a WSGI server.
   Instead, it loads the server you want from the configuration file.

3. *Friends of pserve*. With the ``pserve``/``.ini`` approach you
   also get other commands that help during development: ``pshell``,
   ``proutes``, ``pviews``, ``prequest``, etc.

Configuration with ``.ini`` Files
=================================

Earlier in *Quick Glance* we first met Pyramid's configuration system.
At that point we did all configuration in Python code,
aka *imperatively*. For example, the port number chosen for our HTTP
server was right there in Python code. Our scaffold has moved this
decision, and more, into *declarative* configuration in the
``development.ini`` file.

Let's take a quick high-level look. First, the ``.ini`` file is divided
into sections:

- ``[app:hello_world]`` configures our WSGI app

- ``[pipeline:main]`` sets up our WSGI "pipeline"

- ``[server:main]`` holds our WSGI server settings

- Various sections afterwards configure our Python logging system

Let's look at a few decisions made in this configuration:

#. *Choice of web server*. The ``use = egg:pyramid#wsgiref`` tell
   ``pserve`` to the ``wsgiref`` server that is wrapped in the Pyramid
   package.

#. *Port number*. ``port = 6543`` tells ``wsgiref`` to listen on port
   6543.

#. *WSGI app*. What package has our WSGI application in it?
   ``use = egg:hello_world`` in the app section tells the
   configuration what application to load.

#. *Easier development by automatic template reloading*. In development
   mode, you shouldn't have to restart the server when editing a Jinja2
   template. ``reload_templates = true`` sets this policy,
   which might be different in production.

Additionally, the ``development.ini`` generated by this scaffold wired
up Python's standard logging. We'll now see in the console, for example,
a log on every request that comes in, as well traceback information.

Easier Development with ``debugtoolbar``
========================================

As we introduce the basics we also want to show how to be productive in
development and debugging. For example, we just discussed template
reloading and earlier we showed ``--reload`` for application reloading.

``pyramid_debugtoolbar`` is a popular Pyramid add-on which makes
several tools available in your browser. Adding it to your project
illustrates several points about configuration.

First, change your ``setup.py`` to say:

.. code-block:: python

    requires=['pyramid>=1.0.2', 'pyramid_jinja2']

...and re-run your setup:

.. code-block:: bash

    $ python3.3 ./setup.py develop

The Python package was now installed into our environment but we
haven't told our web app to use it. We can do so imperatively in code:

.. code-block:: python

  config.include('pyramid_debugtoolbar')

Instead, let's do it in configuration by modifying our
``development.ini`` instead:

.. code-block:: ini

    [app:hello_world]
    pyramid.includes = pyramid_debugtoolbar

That is, add ``pyramid.includes = pyramid_debugtoolbar`` anywhere in the
``[app:hello_world]`` section. You'll now see an attractive (and
collapsible) menu in the right of your browser giving you introspective
access to debugging information. Even better, if your web application
generates an error, you will see a nice traceback on the screen.

Unit Tests and ``nose``
=======================

Yikes! We got this far and we haven't yet discussed tests. Particularly
egregious, as Pyramid has had a deep commitment to full test coverage
since before it was released.

Our ``pyramid_jinja2_starter`` scaffold generated a ``tests.py`` module
with one unit test in it. To run it, let's install the handy ``nose``
test runner by editing ``setup.py``. While we're at it, we'll throw in
the ``coverage`` tool which yells at us for code that isn't tested:

.. code-block:: python

    setup(name='hello_world',
          # Some lines removed...
          extras_require={
              'testing': ['nose', 'coverage'],
          }
    )

We changed ``setup.py`` which means we need to re-run
``python3.3 ./setup.py develop``. We can now run all our tests:

.. code-block:: bash

    $ nosetests
    .
    Name                  Stmts   Miss  Cover   Missing
    ---------------------------------------------------
    hello_world             12      8    33%   11-23
    hello_world.models       5      1    80%   8
    hello_world.tests       14      0   100%
    hello_world.views        4      0   100%
    ---------------------------------------------------
    TOTAL                    35      9    74%
    ----------------------------------------------------------------------
    Ran 1 test in 0.931s

    OK

Our unit test passed. What did our test look like?

.. code-block:: python

    import unittest
    from pyramid import testing


    class ViewTests(unittest.TestCase):
        def setUp(self):
            testing.setUp()

        def tearDown(self):
            testing.tearDown()

        def test_my_view(self):
            from hello_world.views import my_view

            request = testing.DummyRequest()
            response = my_view(request)
            self.assertEqual(response['project'], 'hello_world')

Pyramid supplies helpers for test writing, which we use in the
test setup and teardown. Our one test imports the view,
makes a dummy request, and sees if the view returns what we expected.



  - logging

  - resources, asset specs, tests,

sessions, logging, special views
databases, forms, security

Notes

- Change 8081 -> 6543

- See also, interlinking, teasers or "3 Extras" at the end of each
  section, links to a downloadable version of the Python module

- Read "pyramid for humans" and getting started as an attempt to kill
  those

- Do a better job at the "why"

- Explain imperative vs. declarative configuration and link to "why
  configuration"

- For see also, point also to Getting Started sections

- Debugging

- Template reloading

- Explain and link to WSGI, Python Packages