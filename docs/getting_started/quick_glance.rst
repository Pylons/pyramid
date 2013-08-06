============
Quick Glance
============

Pyramid lets you start small and finish big. This :doc:`index` guide
walks you through many of Pyramid's key features. Let's put the
emphasis on *start* by doing a quick tour through Pyramid, with
snippets of code to illustrate major concepts.

.. note::

    Like the rest of Getting Started, we're using Python 3 in
    our samples. Pyramid was one of the first (October 2011) web
    frameworks to fully support Python 3. You can use Python 3
    as well for this guide, but you can also use Python 2.7.

Python Setup
============

First things first: we need our Python environment in ship-shape.
Pyramid encourages standard Python development practices (virtual
environments, packaging tools, etc.) so let's get our working area in
place. For Python 3.3:

.. code-block:: bash

  $ pyvenv-3.3 env33
  $ source env33/bin/activate
  $ wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python
  $ easy_install-3.3 pip

We make a :term:`virtualenv` then activate it. We then get Python
packaging tools installed so we can use the popular ``pip`` tool for
installing packages. Normal first steps for any Python project.

Pyramid Installation
====================

We now have a standard starting point for Python. Getting Pyramid
installed is easy:

.. code-block:: bash

  $ pip install pyramid

Our virtual environment now has the Pyramid software available to its
Python.

Hello World
===========

Microframeworks have shown that learning starts best from a very small
first step. Here's a tiny application in Pyramid:

.. literalinclude:: quick_glance/hello_world/app.py
    :linenos:

This simple example is easy to run. Save this as ``app.py`` and run it:

.. code-block:: bash

    $ python ./app.py

Next, open `http://localhost:6543/ <http://localhost:6543/>`_ in a
browser and you will see the ``Hello World!`` message.

New to Python web programming? If so, some lines in module merit
explanation:

#. *Line 10*. The ``if __name__ == '__main__':`` is Python's way of
   saying "Start here when running from the command line".

#. *Lines 11-13*. Use Pyramid's :term:`configurator` to connect
   :term:`view` code to particular URL :term:`route`.

#. *Lines 6-7*. Implement the view code that generates the
   :term:`response`.

#. *Lines 14-16*. Publish a :term:`WSGI` app using an HTTP server.

As shown in this example, the :term:`configurator` plays a central role
in Pyramid development. Building an application from loosely-coupled
parts via :doc:`../narr/configuration` is a central idea in Pyramid,
one that we will revisit regurlarly in this *Getting Started* document.

Handling Web Requests and Responses
===================================

Developing for the web means processing web requests. As this is a
critical part of a web application, web developers need a robust,
mature set of software for web requests.

Pyramid has always fit nicely into the existing world of Python web
development (virtual environments, packaging, scaffolding,
first to embrace Python 3, etc.) For request handling, Pyramid turned
to the well-regarded :term:`WebOb` Python library for request and
response handling. In our example
above, Pyramid hands ``hello_world`` a ``request`` that is
:ref:`based on WebOb <webob_chapter>`.

Let's see some features of requests and responses in action:

.. literalinclude:: quick_glance/requests/app.py
    :pyobject: hello_world

In this Pyramid view, we get the URL being visited from ``request.url``.
Also, if you visited ``http://localhost:6543/?name=alice``,
the name is included in the body of the response::

  URL http://localhost:6543/?name=alice with name: alice

Finally, we set the response's content type and return the Response.

Views
=====

For the examples above, the ``hello_world`` function is a "view". In
Pyramid, views are the primary way to accept web requests and return
responses.

So far our examples place everything in one file:

- the view function

- its registration with the configurator

- the route to map it to a URL

- the WSGI application launcher

Let's move the views out to their own ``views.py`` module and change
the ``app.py`` to scan that module, looking for decorators that setup
the views. First, our revised ``app.py``:

.. literalinclude:: quick_glance/views/app.py
    :linenos:

We added some more routes, but we also removed the view code.
Our views, and their registrations (via decorators) are now in a module
``views.py`` which is scanned via ``config.scan('views')``.

We now have a ``views.py`` module that is focused on handling requests
and responses:

.. literalinclude:: quick_glance/views/views.py
    :linenos:

We have 4 views, each leading to the other. If you start at
``http://localhost:6543/``, you get a response with a link to the next
view. The ``hello_view`` (available at the URL ``/howdy``) has a link
to the ``redirect_view``, which shows issuing a redirect to the final
view.

.. note::

    We're focusing on one topic at a time, thus we are leaving out
    handling errors, logging, restarting, etc. These will be covered in
    sections of the *Getting Started* guide.


Routing
=======

Writing web applications usually means sophisticated URL design. We
just saw some Pyramid machinery for requests and views. Let's look at
features that help in routing.

Above we saw the basics of routing URLs to views in Pyramid:

- Your project's "setup" code registers a route name to be used when
  matching part of the URL

- Elsewhere, a view is configured to be called for that route name

.. note::

    Why do this twice? Other systems don't make us repeat this! As
    illustrated in :ref:`routes_need_ordering`, multiple routes might
    match the same URL pattern. Rather than provide ways to help guess,
    Pyramid lets you be explicit in ordering. Pyramid also gives
    facilities to avoid the problem.

What if we want part of the URL to be available as data in my view? This
route declaration:

.. literalinclude:: quick_glance/routing/app.py
    :start-after: Start Route 1
    :end-before: End Route 1

With this, URLs such as ``/howdy/amy/smith`` will assign ``amy`` to
``first`` and ``smith`` to ``last``. We can then use this data in our
view:

.. literalinclude:: quick_glance/routing/views.py
    :start-after: Start Route 1
    :end-before: End Route 1

``request.matchdict`` contains values from the URL that match the
"replacement patterns" (the curly braces) in the route declaration.
This information can then be used in your view.

As you might imagine, Pyramid provides
:doc:`many more features in routing <../narr/urldispatch>`
(route factories, custom predicates, security statements,
etc.) We will see more features later in *Geting Started*.

Templating
==========

Ouch. We have been making our own ``Response`` and filling the response
body with HTML. You usually won't embed an HTML string directly in
Python, but instead, will use a templating language.

Pyramid doesn't mandate a particular database system, form library,
etc. It encourages replaceability. This applies equally to templating,
which is fortunate: developers have strong views about template
languages. That said, Pyramid bundles Chameleon and Mako,
so in this step, let's use Chameleon as an example:

.. literalinclude:: quick_glance/templating/views.py
    :start-after: Start View 1
    :end-before: End View 1

Ahh, that looks better. We have a view that is focused on Python code.
Our ``@view_config`` decorator specifies a :term:`renderer` that points
our template file. Our view then simply returns data which is then
supplied to our template:

.. literalinclude:: quick_glance/templating/hello_world.pt
    :language: html

Since our view returned ``dict(name=request.matchdict['name'])``,
we can use ``name`` as a variable in our template via
``${name}``.

Templating With ``jinja2``
==========================

We just said Pyramid doesn't prefer one templating language over
another. Time to prove it. Jinja2 is a popular templating system,
modelled after Django's templates. Let's add ``pyramid_jinja2``,
a Pyramid :term:`add-on` which enables Jinja2 as a :term:`renderer` in
our Pyramid applications:

.. code-block:: bash

    $ pip install pyramid_jinja2

With the package installed, we can include the template bindings into
our configuration:

.. code-block:: python

    config.include('pyramid_jinja2')

The only change in our view...point the renderer at the ``.jinja2`` file:

.. literalinclude:: quick_glance/jinja2/views.py
    :start-after: Start View 1
    :end-before: End View 1

Our Jinja2 template is very similar to our previous template:

.. literalinclude:: quick_glance/jinja2/hello_world.jinja2
    :language: html

Pyramid's templating add-ons register a new kind of renderer into your
application. The renderer registration maps to different kinds of
filename extensions. In this case, changing the extension from ``.pt``
to ``.jinja2`` passed the view response through the ``pyramid_jinja2``
renderer.

.. note::

    At the time of this writing, Jinja2 had not released a version
    compatible with Python 3.3.


Static Assets
=============

Of course the Web is more than just markup. You need static assets:
CSS, JS, and images. Let's point our web app at a directory where
Pyramid will serve some static assets. First, another call to the
:term:`configurator`:

.. literalinclude:: quick_glance/static_assets/app.py
    :start-after: Start Static 1
    :end-before: End Static 1

This tells our WSGI application to map requests under
``http://localhost:6543/static/`` to files and directories inside a
``static`` directory alongside our Python module.

Next, make a directory ``static`` and place ``app.css`` inside:

.. literalinclude:: quick_glance/static_assets/static/app.css
    :language: css

All we need to do now is point to it in the ``<head>`` of our Jinja2
template:

.. literalinclude:: quick_glance/static_assets/hello_world.pt
    :language: html
    :start-after: Start Link 1
    :end-before: End Link 1

This link presumes that our CSS is at a URL starting with ``/static/``.
What if the site is later moved under ``/somesite/static/``? Or perhaps
web developer changes the arrangement on disk? Pyramid gives a helper
that provides flexibility on URL generation:

.. literalinclude:: quick_glance/static_assets/hello_world.pt
    :language: html
    :start-after: Start Link 2
    :end-before: End Link 2

By using ``request.static_url`` to generate the full URL to the static
assets, you both ensure you stay in sync with the configuration and
gain refactoring flexibility later.

Returning JSON
==============

Modern web apps are more than rendered HTML. Dynamic pages now use
JavaScript to update the UI in the browser by requesting server data as
JSON. Pyramid supports this with a JSON renderer:

.. literalinclude:: quick_glance/json/views.py
    :start-after: Start View 1
    :end-before: End View 2

This wires up a view that returns some data through the JSON
:term:`renderer`, which calls Python's JSON support to serialize the data
into JSON and set the appropriate HTTP headers.

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


Configuration
=============


#. *Line 7*. Pyramid's configuration supports
   :term:`imperative configuration`, such as the ``config.add_view`` in
   the previous example. You can also use
   :term:`declarative configuration`, in which a Python
   :term:`decorator` is placed on the line above the view.

#. *Line 15*. Tell the configurator to go look for decorators.

- Move route declarations into views, with prefix thingy

Packages
========

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
    $ python ./setup.py develop

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

    $ python ./setup.py develop

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
``python ./setup.py develop``. We can now run all our tests:

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

Logging
=======

It's important to know what is going on inside our web application.
In development we might need to collect some output. In production,
we might need to detect situations when other people use the site. We
need *logging*.

Fortunately Pyramid uses the normal Python approach to logging. The
scaffold generated, in your ``development.ini``, a number of lines that
configure the logging for you to some reasonable defaults. You then see
messages sent by Pyramid (for example, when a new request comes in.)

Maybe you would like to log messages in your code? In your Python
module, import and setup the logging:

.. code-block:: python

  import logging
  log = logging.getLogger(__name__)

You can now, in your code, log messages:

.. code-block:: python

    log.debug('Some Message')

This will log ``Some Message`` at a ``debug`` log level,
to the application-configured logger in your ``development.ini``. What
controls that? These sections in the configuration file:

.. code-block:: ini

  [loggers]
  keys = root, hello_world

  [logger_hello_world]
  level = DEBUG
  handlers =
  qualname = hello_world

Our application, a package named ``hello_world``, is setup as a logger
and configured to log messages at a ``DEBUG`` or higher level.

Sessions
========

When people use your web application, they frequently perform a task
that requires semi-permanent data to be saved. For example,a shopping
cart. These are frequently called *sessions*.

Pyramid has basic built-in support for sessions, with add-ons such as
*Beaker* (or your own custom sessioning engine) that provide richer
session support. For the built-in session support, you first import
the "factory" which provides the sessioning:

.. code-block:: python

    from pyramid.session import UnencryptedCookieSessionFactoryConfig
    my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')

We tell the configuration system that this is the source of our
sessioning support when setting up the ``Configurator``:

.. code-block:: python

  config = Configurator(session_factory = my_session_factory)

This now lets us use the session in our application code:

.. code-block:: python

    session = request.session
    if 'abc' in session:
        session['fred'] = 'yes'

Databases
=========

Web applications mean data. Data means databases. Frequently SQL
databases. SQL Databases frequently mean an "ORM"
(object-relational mapper.) In Python, ORM usually leads to the
mega-quality *SQLAlchemy*, a Python package that greatly eases working
with databases.

Pyramid and SQLAlchemy are great friends. That friendship includes a
scaffold!

.. code-block:: bash

  $ pcreate --scaffold alchemy hello_sqlalchemy
  $ cd hello_sqlalchemy
  $ python setup.py develop

We now have a working sample SQLAlchemy application with all
dependencies installed. The sample project provides a console script to
initialize a SQLite database with tables. Let's run it and then start
the application:

.. code-block:: bash

  $ initialize_hello_sqlalchemy_db development.ini
  $ pserve development.ini

We can now visit our sample at
`http://localhost:6543/ <http://localhost:6543/>`_. Some choices that
the scaffold helped us with:

- A ``setup.py`` with appropriate dependencies

- Connection strings and integration in our ``development.ini`` file

- A console script which we ran above to initialize the database

- The SQLAlchemy engine integrated into the ``Configurator`` on
  application startup

- Python modules for the SQLAlchemy models and the Pyramid views that
  go with them

- Some unit tests...yummy!

As mentioned above, an ORM is software that eases the mapping of
database structures into a programming language. SQLAlchemy uses models
for this, and its scaffold generated a sample model:

.. code-block:: python

    class MyModel(Base):
        __tablename__ = 'models'
        id = Column(Integer, primary_key=True)
        name = Column(Text, unique=True)
        value = Column(Integer)

        def __init__(self, name, value):
            self.name = name
            self.value = value

The Python module also includes this:

.. code-block:: python

  from zope.sqlalchemy import ZopeTransactionExtension

The generated application includes the optional support for
``pyramid_tm``, a unique transaction monitor that integrates your
database transactions with your code for transparent rollback and commit.

View code, which mediates the logic between web requests and the rest
of the system, can then easily get at the data:

.. code-block:: python

  one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()


Forms
=====

Developers have lots of opinions about forms, and thus there are many
form libraries for Python. Pyramid doesn't directly bundle a form
library, but *Deform* is a popular choice. Let's see it in action.
First we install it:

.. code-block:: bash

  $ pip-3.3 install deform



Authentication
==============


Authorization
=============


