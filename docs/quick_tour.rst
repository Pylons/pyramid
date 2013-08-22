.. _quick_tour:

=====================
Quick Tour of Pyramid
=====================

Pyramid lets you start small and finish big. This *Quick Tour* guide
walks you through many of Pyramid's key features. Let's put the
emphasis on *start* by doing a quick tour through Pyramid, with
snippets of code to illustrate major concepts.

.. note::

    We use Python 3 in our samples. Pyramid was one of the first
    (October 2011) web frameworks to fully support Python 3. You can
    use Python 3 as well for this guide, but you can also use Python 2.7.

Python Setup
============

First things first: we need our Python environment in ship-shape.
Pyramid encourages standard Python development practices (virtual
environments, packaging tools, logging, etc.) so let's get our working
area in place. For Python 3.3:

.. code-block:: bash

  $ pyvenv-3.3 env33
  $ source env33/bin/activate
  $ wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python

If ``wget`` complains with a certificate error, run it with:

.. code-block:: bash

  $ wget --no-check-certificate

In these steps above we first made a :term:`virtualenv` and then
"activated"  it, which adjusted our path to look first in
``env33/bin`` for commands (such as ``python``). We next downloaded
Python's packaging support and installed it, giving us the
``easy_install`` command-line script for adding new packages. Python
2.7 users will need to use ``virtualenv`` instead of ``pyvenv`` to make
their virtual environment.

.. note::

   Why ``easy_install`` and not ``pip``? Pyramid encourages use of
   namespace packages which, until recently, ``pip`` didn't permit.
   Also, Pyramid has some optional C extensions for performance. With
   ``easy_install``, Windows users can get these extensions without
   needing a C compiler.

.. seealso:: See Also: Python 3's :mod:`venv module <python3:venv>`,
   the ``setuptools`` `installation
   instructions <https://pypi.python.org/pypi/setuptools/0.9.8#installation-instructions>`_,
   `easy_install help <https://pypi.python.org/pypi/setuptools/0.9.8#using-setuptools-and-easyinstall>`_,
   and Pyramid's :ref:`Before You Install <installing_chapter>`.

Pyramid Installation
====================

We now have a standard starting point for Python. Getting Pyramid
installed is easy:

.. code-block:: bash

  $ easy_install pyramid

Our virtual environment now has the Pyramid software available to its
Python.

.. seealso:: See Also: :ref:`installing_unix`

Hello World
===========

Microframeworks have shown that learning starts best from a very small
first step. Here's a tiny application in Pyramid:

.. literalinclude:: quick_tour/hello_world/app.py
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
one that we will revisit regurlarly in this *Quick Tour*.

.. seealso:: See Also: :ref:`firstapp_chapter` and
   :ref:`Single File Tasks tutorial <tutorials:single-file-tutorial>`

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

.. literalinclude:: quick_tour/requests/app.py
    :pyobject: hello_world

In this Pyramid view, we get the URL being visited from ``request.url``.
Also, if you visited ``http://localhost:6543/?name=alice``,
the name is included in the body of the response::

  URL http://localhost:6543/?name=alice with name: alice

Finally, we set the response's content type and return the Response.

.. seealso:: See Also: :ref:`webob_chapter`

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

.. literalinclude:: quick_tour/views/app.py
    :linenos:

We added some more routes, but we also removed the view code.
Our views, and their registrations (via decorators) are now in a module
``views.py`` which is scanned via ``config.scan('views')``.

We now have a ``views.py`` module that is focused on handling requests
and responses:

.. literalinclude:: quick_tour/views/views.py
    :linenos:

We have 4 views, each leading to the other. If you start at
``http://localhost:6543/``, you get a response with a link to the next
view. The ``hello_view`` (available at the URL ``/howdy``) has a link
to the ``redirect_view``, which shows issuing a redirect to the final
view.

Earlier we saw ``config.add_view`` as one way to configure a view. This
section introduces ``@view_config``. Pyramid's configuration supports
:term:`imperative configuration`, such as the ``config.add_view`` in
the previous example. You can also use :term:`declarative
configuration`, in which a Python :term:`decorator` is placed on the
line above the view. Both approaches result in the same final
configuration, thus usually, it is simply a matter of taste.

.. seealso:: See Also: :doc:`../narr/views`,
   :doc:`../narr/viewconfig`, and
   :ref:`debugging_view_configuration`

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

    Why do this twice? Other Python web frameworks let you create a
    route and associate it with a view in one step. As
    illustrated in :ref:`routes_need_ordering`, multiple routes might
    match the same URL pattern. Rather than provide ways to help guess,
    Pyramid lets you be explicit in ordering. Pyramid also gives
    facilities to avoid the problem.

What if we want part of the URL to be available as data in my view? This
route declaration:

.. literalinclude:: quick_tour/routing/app.py
    :start-after: Start Route 1
    :end-before: End Route 1

With this, URLs such as ``/howdy/amy/smith`` will assign ``amy`` to
``first`` and ``smith`` to ``last``. We can then use this data in our
view:

.. literalinclude:: quick_tour/routing/views.py
    :start-after: Start Route 1
    :end-before: End Route 1

``request.matchdict`` contains values from the URL that match the
"replacement patterns" (the curly braces) in the route declaration.
This information can then be used in your view.

.. seealso:: See Also: :doc:`../narr/urldispatch`,
   :ref:`debug_routematch_section`, and
   :doc:`../narr/router`

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

.. literalinclude:: quick_tour/templating/views.py
    :start-after: Start View 1
    :end-before: End View 1

Ahh, that looks better. We have a view that is focused on Python code.
Our ``@view_config`` decorator specifies a :term:`renderer` that points
our template file. Our view then simply returns data which is then
supplied to our template:

.. literalinclude:: quick_tour/templating/hello_world.pt
    :language: html

Since our view returned ``dict(name=request.matchdict['name'])``,
we can use ``name`` as a variable in our template via
``${name}``.

.. seealso:: See Also: :doc:`../narr/templates`,
   :ref:`debugging_templates`, and
   :ref:`mako_templates`

Templating With ``jinja2``
==========================

We just said Pyramid doesn't prefer one templating language over
another. Time to prove it. Jinja2 is a popular templating system,
modelled after Django's templates. Let's add ``pyramid_jinja2``,
a Pyramid :term:`add-on` which enables Jinja2 as a :term:`renderer` in
our Pyramid applications:

.. code-block:: bash

    $ easy_install pyramid_jinja2

With the package installed, we can include the template bindings into
our configuration:

.. code-block:: python

    config.include('pyramid_jinja2')

The only change in our view...point the renderer at the ``.jinja2`` file:

.. literalinclude:: quick_tour/jinja2/views.py
    :start-after: Start View 1
    :end-before: End View 1

Our Jinja2 template is very similar to our previous template:

.. literalinclude:: quick_tour/jinja2/hello_world.jinja2
    :language: jinja

Pyramid's templating add-ons register a new kind of renderer into your
application. The renderer registration maps to different kinds of
filename extensions. In this case, changing the extension from ``.pt``
to ``.jinja2`` passed the view response through the ``pyramid_jinja2``
renderer.

.. seealso:: See Also: `Jinja2 homepage <http://jinja.pocoo.org/>`_,
   and
   :ref:`pyramid_jinja2 Overview <jinja2:overview>`

Static Assets
=============

Of course the Web is more than just markup. You need static assets:
CSS, JS, and images. Let's point our web app at a directory where
Pyramid will serve some static assets. First, another call to the
:term:`configurator`:

.. literalinclude:: quick_tour/static_assets/app.py
    :start-after: Start Static 1
    :end-before: End Static 1

This tells our WSGI application to map requests under
``http://localhost:6543/static/`` to files and directories inside a
``static`` directory alongside our Python module.

Next, make a directory ``static`` and place ``app.css`` inside:

.. literalinclude:: quick_tour/static_assets/static/app.css
    :language: css

All we need to do now is point to it in the ``<head>`` of our Jinja2
template:

.. literalinclude:: quick_tour/static_assets/hello_world.pt
    :language: html
    :start-after: Start Link 1
    :end-before: End Link 1

This link presumes that our CSS is at a URL starting with ``/static/``.
What if the site is later moved under ``/somesite/static/``? Or perhaps
web developer changes the arrangement on disk? Pyramid gives a helper
that provides flexibility on URL generation:

.. literalinclude:: quick_tour/static_assets/hello_world.pt
    :language: html
    :start-after: Start Link 2
    :end-before: End Link 2

By using ``request.static_url`` to generate the full URL to the static
assets, you both ensure you stay in sync with the configuration and
gain refactoring flexibility later.

.. seealso:: See Also: :doc:`../narr/assets`,
   :ref:`preventing_http_caching`, and
   :ref:`influencing_http_caching`

Returning JSON
==============

Modern web apps are more than rendered HTML. Dynamic pages now use
JavaScript to update the UI in the browser by requesting server data as
JSON. Pyramid supports this with a JSON renderer:

.. literalinclude:: quick_tour/json/views.py
    :start-after: Start View 1
    :end-before: End View 2

This wires up a view that returns some data through the JSON
:term:`renderer`, which calls Python's JSON support to serialize the data
into JSON and set the appropriate HTTP headers.

.. seealso:: See Also: :ref:`views_which_use_a_renderer`,
   :ref:`json_renderer`, and
   :ref:`adding_and_overriding_renderers`

View Classes
============

So far our views have been simple, free-standing functions. Many times
your views are related: different ways to look at or work on the same
data or a REST API that handles multiple operations. Grouping these
together as a
:ref:`view class <class_as_view>` makes sense:

- Group views

- Centralize some repetitive defaults

- Share some state and helpers

The following shows a "Hello World" example with three operations: view
a form, save a change, or press the delete button:

.. literalinclude:: quick_tour/view_classes/views.py
    :start-after: Start View 1
    :end-before: End View 1

As you can see, the three views are logically grouped together.
Specifically:

- The first view is returned when you go to ``/howdy/amy``. This URL is
  mapped to the ``hello`` route that we centrally set using the optional
  ``@view_defaults``.

- The second view is returned when the form data contains a field with
  ``form.edit``, such as clicking on
  ``<input type="submit" name="form.edit" value="Save"/>``. This rule
  is specified in the ``@view_config`` for that view.

- The third view is returned when clicking on a button such
  as ``<input type="submit" name="form.delete" value="Delete"/>``.

Only one route needed, stated in one place atop the view class. Also,
the assignment of the ``name`` is done in the ``__init__``. Our
templates can then use ``{{ view.name }}``.

.. seealso:: See Also: :ref:`class_as_view`

Quick Project Startup with Scaffolds
====================================

So far we have done all of our *Quick Glance* as a single Python file.
No Python packages, no structure. Most Pyramid projects, though,
aren't developed this way.

To ease the process of getting started, Pyramid provides *scaffolds*
that generate sample projects from templates in Pyramid and Pyramid
add-ons. Pyramid's ``pcreate`` command can list the available scaffolds:

.. code-block:: bash

    $ pcreate --list
    Available scaffolds:
      alchemy:                 Pyramid SQLAlchemy project using url dispatch
      pyramid_jinja2_starter:  pyramid jinja2 starter project
      starter:                 Pyramid starter project
      zodb:                    Pyramid ZODB project using traversal

The ``pyramid_jinja2`` add-on gave us a scaffold that we can use. From
the parent directory of where we want our Python package to be generated,
let's use that scaffold to make our project:

.. code-block:: bash

    $ pcreate --scaffold pyramid_jinja2_starter hello_world

We next use the normal Python development to setup our package for
development:

.. code-block:: bash

    $ cd hello_world
    $ python ./setup.py develop

We are moving in the direction of a full-featured Pyramid project,
with a proper setup for Python standards (packaging) and Pyramid
configuration. This includes a new way of running your application:

.. code-block:: bash

    $ pserve development.ini

Let's look at ``pserve`` and configuration in more depth.

.. seealso:: See Also: :ref:`project_narr` and
   :doc:`../narr/scaffolding`

Application Running with ``pserve``
===================================

Prior to scaffolds, our project mixed a number of operations details
into our code. Why should my main code care with HTTP server I want and
what port number to run on?

``pserve`` is Pyramid's application runner, separating operational
details from your code. When you install Pyramid, a small command
program called ``pserve`` is written to your ``bin`` directory. This
program is an executable Python module. It's very small, getting most
of its brains via import.

You can run ``pserve`` with ``--help`` to see some of its options.
Doing so reveals that you can ask ``pserve`` to watch your development
files and reload the server when they change:

.. code-block:: bash

    $ pserve development.ini --reload

The ``pserve`` command has a number of other options and operations.
Most of the work, though, comes from your project's wiring, as
expressed in the configuration file you supply to ``pserve``. Let's
take a look at this configuration file.

.. seealso:: See Also: :ref:`what_is_this_pserve_thing`

Configuration with ``.ini`` Files
=================================

Earlier in *Quick Glance* we first met Pyramid's configuration system.
At that point we did all configuration in Python code. For example,
the port number chosen for our HTTP server was right there in Python
code. Our scaffold has moved this decision, and more, into the
``development.ini`` file:

.. literalinclude:: quick_tour/package/development.ini
    :language: ini

Let's take a quick high-level look. First, the ``.ini`` file is divided
into sections:

- ``[app:hello_world]`` configures our WSGI app

- ``[pipeline:main]`` sets up our WSGI "pipeline"

- ``[server:main]`` holds our WSGI server settings

- Various sections afterwards configure our Python logging system

We have a few decisions made for us in this configuration:

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

.. seealso:: See Also: :ref:`environment_chapter` and
   :doc:`../narr/paste`


Easier Development with ``debugtoolbar``
========================================

As we introduce the basics we also want to show how to be productive in
development and debugging. For example, we just discussed template
reloading and earlier we showed ``--reload`` for application reloading.

``pyramid_debugtoolbar`` is a popular Pyramid add-on which makes
several tools available in your browser. Adding it to your project
illustrates several points about configuration.

First, change your ``setup.py`` to say:

.. literalinclude:: quick_tour/package/setup.py
    :start-after: Start Requires
    :end-before: End Requires

...and re-run your setup:

.. code-block:: bash

    $ python ./setup.py develop

The Python package was now installed into our environment. The package
is a Pyramid add-on, which means we need to include its configuration
into our web application. We could do this with imperative
configuration, as we did above for the ``pyramid_jinja2`` add-on:

.. literalinclude:: quick_tour/package/hello_world/__init__.py
    :start-after: Start Include
    :end-before: End Include

Now that we have a configuration file, we can use the
``pyramid.includes`` facility and place this in our
``development.ini`` instead:

.. literalinclude:: quick_tour/package/development.ini
    :language: ini
    :start-after: Start Includes
    :end-before: End Includes

You'll now see an attractive (and
collapsible) menu in the right of your browser, providing introspective
access to debugging information. Even better, if your web application
generates an error, you will see a nice traceback on the screen. When
you want to disable this toolbar, no need to change code: you can
remove it from ``pyramid.includes`` in the relevant ``.ini``
configuration file.

.. seealso:: See Also: :ref:`pyramid_debugtoolbar <toolbar:overview>`

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

    $ nosetests hello_world/tests.py
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

.. literalinclude:: quick_tour/package/hello_world/tests.py

Pyramid supplies helpers for test writing, which we use in the
test setup and teardown. Our one test imports the view,
makes a dummy request, and sees if the view returns what we expected.

.. seealso:: See Also: :ref:`testing_chapter`

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

.. literalinclude:: quick_tour/package/hello_world/views.py
    :start-after: Start Logging 1
    :end-before: End Logging 1

You can now, in your code, log messages:

.. literalinclude:: quick_tour/package/hello_world/views.py
    :start-after: Start Logging 2
    :end-before: End Logging 2

This will log ``Some Message`` at a ``debug`` log level,
to the application-configured logger in your ``development.ini``. What
controls that? These sections in the configuration file:

.. literalinclude:: quick_tour/package/development.ini
    :language: ini
    :start-after: Start Sphinx Include
    :end-before: End Sphinx Include

Our application, a package named ``hello_world``, is setup as a logger
and configured to log messages at a ``DEBUG`` or higher level. When you
visit ``http://localhost:6543`` your console will now show::

 2013-08-09 10:42:42,968 DEBUG [hello_world.views][MainThread] Some Message

.. seealso:: See Also: :ref:`logging_chapter`

Sessions
========

When people use your web application, they frequently perform a task
that requires semi-permanent data to be saved. For example, a shopping
cart. This is called a :term:`session`.

Pyramid has basic built-in support for sessions, with add-ons such as
*Beaker* (or your own custom sessioning engine) that provide richer
session support. Let's take a look at the
:doc:`built-in sessioning support <../narr/sessions>`. In our
``__init__.py`` we first import the kind of sessioning we want:

.. literalinclude:: quick_tour/package/hello_world/__init__.py
    :start-after: Start Sphinx Include 1
    :end-before: End Sphinx Include 1

.. warning::

    As noted in the session docs, this example implementation is
    not intended for use in settings with security implications.

Now make a "factory" and pass it to the :term:`configurator`'s
``session_factory`` argument:

.. literalinclude:: quick_tour/package/hello_world/__init__.py
    :start-after: Start Sphinx Include 2
    :end-before: End Sphinx Include 2

Pyramid's :term:`request` object now has a ``session`` attribute
that we can use in our view code:

.. literalinclude:: quick_tour/package/hello_world/views.py
    :start-after: Start Sphinx Include 1
    :end-before: End Sphinx Include 1

With this, each reload will increase the counter displayed in our
Jinja2 template:

.. literalinclude:: quick_tour/package/hello_world/templates/mytemplate.jinja2
    :language: jinja
    :start-after: Start Sphinx Include 1
    :end-before: End Sphinx Include 1

.. seealso:: See Also:
   :ref:`sessions_chapter`, :ref:`flash_messages`,
   :ref:`session_module`, and
   :ref:`Beaker sessioning middleware <beaker:overview>`

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

  $ pcreate --scaffold alchemy sqla_demo
  $ cd sqla_demo
  $ python setup.py develop

We now have a working sample SQLAlchemy application with all
dependencies installed. The sample project provides a console script to
initialize a SQLite database with tables. Let's run it and then start
the application:

.. code-block:: bash

  $ initialize_sqla_demo_db development.ini
  $ pserve development.ini

The ORM eases the mapping of database structures into a programming
language. SQLAlchemy uses "models" for this mapping. The scaffold
generated a sample model:

.. literalinclude:: quick_tour/sqla_demo/sqla_demo/models.py
    :start-after: Start Sphinx Include
    :end-before: End Sphinx Include

View code, which mediates the logic between web requests and the rest
of the system, can then easily get at the data thanks to SQLAlchemy:

.. literalinclude:: quick_tour/sqla_demo/sqla_demo/views.py
    :start-after: Start Sphinx Include
    :end-before: End Sphinx Include

.. seealso:: See Also: `SQLAlchemy <http://www.sqlalchemy.org/>`_,
   :ref:`making_a_console_script`,
   :ref:`bfg_sql_wiki_tutorial`, and
   :ref:`Application Transactions With pyramid_tm <tm:overview>`

Forms
=====

Developers have lots of opinions about web forms, and thus there are many
form libraries for Python. Pyramid doesn't directly bundle a form
library, but *Deform* is a popular choice for forms,
along with its related *Colander* schema system.

As an example, imagine we want a form that edits a wiki page. The form
should have two fields on it, one of them a required title and the
other a rich text editor for the body. With Deform we can express this
as a Colander schema:

.. code-block:: python

    class WikiPage(colander.MappingSchema):
        title = colander.SchemaNode(colander.String())
        body = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.RichTextWidget()
        )

With this in place, we can render the HTML for a form,
perhaps with form data from an existing page:

.. code-block:: python

    form = self.wiki_form.render()

We'd like to handle form submission, validation, and saving:

.. code-block:: python

    # Get the form data that was posted
    controls = self.request.POST.items()
    try:
        # Validate and either raise a validation error
        # or return deserialized data from widgets
        appstruct = wiki_form.validate(controls)
    except deform.ValidationFailure as e:
        # Bail out and render form with errors
        return dict(title=title, page=page, form=e.render())

    # Change the content and redirect to the view
    page['title'] = appstruct['title']
    page['body'] = appstruct['body']

Deform and Colander provide a very flexible combination for forms,
widgets, schemas, and validation. Recent versions of Deform also
include a :ref:`retail mode <deform:retail>` for gaining Deform
features on custom forms.

Also, the ``deform_bootstrap`` Pyramid add-on restyles the stock Deform
widgets using attractive CSS from Bootstrap and more powerful widgets
from Chosen.

.. seealso:: See Also:
   :ref:`Deform <deform:overview>`,
   :ref:`Colander <colander:overview>`, and
   `deform_bootstrap <https://pypi.python.org/pypi/deform_bootstrap>`_

Conclusion
==========

This *Quick Tour* covered a little about a lot. We introduced a long list
of concepts in Pyramid, many of which are expanded on more fully in the
Pyramid developer docs.