
.. _quick_tour:

=====================
Quick Tour of Pyramid
=====================

Pyramid lets you start small and finish big.  This *Quick Tour* of Pyramid is
for those who want to evaluate Pyramid, whether you are new to Python web
frameworks, or a pro in a hurry. For more detailed treatment of each topic,
give the :ref:`quick_tutorial` a try.

If you would prefer to cut and paste the example code in this tour you may browse the source code located in the `Pyramid repository in the directory "docs/quick_tour" <https://github.com/Pylons/pyramid/>`. If you have downloaded the source code, you will find the tour in the same location.

Installation
============

Once you have a standard Python environment setup, getting started with Pyramid is a breeze.
Unfortunately "standard" is not so simple in Python.
For this Quick Tour, it means `Python <https://www.python.org/downloads/>`_, :mod:`python:venv`, `pip <https://pypi.org/project/pip/>`_, and `Setuptools <https://pypi.org/project/setuptools/>`_.

To save a little bit of typing and to be certain that we use the modules,
scripts, and packages installed in our virtual environment, we'll set an
environment variable, too.

As an example, for Python 3 on Linux:

.. parsed-literal::

    # set an environment variable to where you want your virtual environment
    $ export VENV=~/env
    # create the virtual environment
    $ python3 -m venv $VENV
    # install pyramid
    $ $VENV/bin/pip install pyramid
    # or for a specific released version
    $ $VENV/bin/pip install "pyramid==\ |release|\ "

For Windows:

.. parsed-literal::

    # set an environment variable to where you want your virtual environment
    c:\\> set VENV=c:\\env
    # create the virtual environment
    c:\\> python -m venv %VENV%
    # install pyramid
    c:\\> %VENV%\\Scripts\\pip install pyramid
    # or for a specific released version
    c:\\> %VENV%\\Scripts\\pip install "pyramid==\ |release|\ "

As of version 2.0, Pyramid runs on Python 3 only.
For simplicity, the remaining examples will show only Unix commands.

.. seealso:: See also:
    :ref:`Quick Tutorial section on Requirements <qtut_requirements>`,
    :ref:`installing_unix`, :ref:`Before You Install <installing_chapter>`,
    :ref:`Why use $VENV/bin/pip instead of source bin/activate, then pip
    <venv-bin-pip-vs-source-bin-activate>`, and
    :ref:`Installing Pyramid on a Windows System <installing_windows>`.


Hello World
===========

Microframeworks have shown that learning starts best from a very small first
step. Here's a tiny application in Pyramid:

.. literalinclude:: quick_tour/hello_world/app.py
    :linenos:
    :language: python

This simple example is easy to run. Save this as ``app.py`` and run it:

.. code-block:: bash

    $ $VENV/bin/python ./app.py

Next open http://localhost:6543/ in a browser, and you will see the ``Hello
World!`` message.

New to Python web programming? If so, some lines in the module merit
explanation:

#. *Lines 6-7*. Implement the view code that generates the :term:`response`.

#. *Line 10*. ``if __name__ == '__main__':`` is Python's way of saying "Start
   here when running from the command line".

#. *Lines 11-13*. Use Pyramid's :term:`configurator` in a :term:`context manager` to connect :term:`view`
   code to a particular URL :term:`route`.

#. *Lines 14-16*. Publish a :term:`WSGI` app using an HTTP server.

As shown in this example, the :term:`configurator` plays a central role in
Pyramid development. Building an application from loosely-coupled parts via
:doc:`../narr/configuration` is a central idea in Pyramid, one that we will
revisit regularly in this *Quick Tour*.

.. seealso:: See also:
   :ref:`Quick Tutorial Hello World <qtut_hello_world>`,
   :ref:`firstapp_chapter`, and :ref:`Todo List Application in One File
   <cookbook:single-file-tutorial>`.


Handling web requests and responses
===================================

Developing for the web means processing web requests. As this is a critical
part of a web application, web developers need a robust, mature set of software
for web requests.

Pyramid has always fit nicely into the existing world of Python web development
(virtual environments, packaging, cookiecutters, one of the first to embrace
Python 3, etc.). Pyramid turned to the well-regarded :term:`WebOb` Python
library for request and response handling. In our example above, Pyramid hands
``hello_world`` a ``request`` that is :ref:`based on WebOb <webob_chapter>`.

Let's see some features of requests and responses in action:

.. literalinclude:: quick_tour/requests/app.py
    :language: python
    :pyobject: hello_world

In this Pyramid view, we get the URL being visited from ``request.url``. Also
if you visited http://localhost:6543/?name=alice in a browser, the name is
included in the body of the response:

.. code-block:: text

    URL http://localhost:6543/?name=alice with name: alice

Finally we set the response's content type, and return the Response.

.. seealso:: See also:
    :ref:`Quick Tutorial Request and Response <qtut_request_response>` and
    :ref:`webob_chapter`.


Views
=====

For the examples above, the ``hello_world`` function is a "view". In Pyramid
views are the primary way to accept web requests and return responses.

So far our examples place everything in one file:

- the view function

- its registration with the configurator

- the route to map it to an URL

- the WSGI application launcher

Let's move the views out to their own ``views.py`` module and change the
``app.py`` to scan that module, looking for decorators that set up the views.

First our revised ``app.py``:

.. literalinclude:: quick_tour/views/app.py
    :language: python
    :linenos:

We added some more routes, but we also removed the view code. Our views and
their registrations (via decorators) are now in a module ``views.py``, which is
scanned via ``config.scan('views')``.

We now have a ``views.py`` module that is focused on handling requests and
responses:

.. literalinclude:: quick_tour/views/views.py
    :language: python
    :linenos:

We have four views, each leading to the other. If you start at
http://localhost:6543/, you get a response with a link to the next view. The
``hello_view`` (available at the URL ``/howdy``) has a link to the
``redirect_view``, which issues a redirect to the final view.

Earlier we saw ``config.add_view`` as one way to configure a view. This section
introduces ``@view_config``. Pyramid's configuration supports :term:`imperative
configuration`, such as the ``config.add_view`` in the previous example. You
can also use :term:`declarative configuration` in which a Python
:term:`decorator` is placed on the line above the view. Both approaches result
in the same final configuration, thus usually it is simply a matter of taste.

.. seealso:: See also:
   :ref:`Quick Tutorial Views <qtut_views>`, :doc:`../narr/views`,
   :doc:`../narr/viewconfig`, and :ref:`debugging_view_configuration`.


Routing
=======

Writing web applications usually means sophisticated URL design. We just saw
some Pyramid machinery for requests and views. Let's look at features that help
with routing.

Above we saw the basics of routing URLs to views in Pyramid:

- Your project's "setup" code registers a route name to be used when matching
  part of the URL.

- Elsewhere a view is configured to be called for that route name.

.. note::

    Why do this twice? Other Python web frameworks let you create a route and
    associate it with a view in one step. As illustrated in
    :ref:`routes_need_ordering`, multiple routes might match the same URL
    pattern. Rather than provide ways to help guess, Pyramid lets you be
    explicit in ordering. Pyramid also gives facilities to avoid the problem.

What if we want part of the URL to be available as data in my view? We can use
this route declaration, for example:

.. literalinclude:: quick_tour/routing/app.py
    :language: python
    :linenos:
    :lines: 6
    :lineno-start: 6

With this, URLs such as ``/howdy/amy/smith`` will assign ``amy`` to ``first``
and ``smith`` to ``last``. We can then use this data in our view:

.. literalinclude:: quick_tour/routing/views.py
    :language: python
    :linenos:
    :lines: 5-8
    :lineno-start: 5
    :emphasize-lines: 3

``request.matchdict`` contains values from the URL that match the "replacement
patterns" (the curly braces) in the route declaration. This information can
then be used in your view.

.. seealso:: See also:
   :ref:`Quick Tutorial Routing <qtut_routing>`, :doc:`../narr/urldispatch`,
   :ref:`debug_routematch_section`, and :doc:`../narr/router`.


Templating
==========

Ouch. We have been making our own ``Response`` and filling the response body
with HTML. You usually won't embed an HTML string directly in Python, but
instead you will use a templating language.

Pyramid doesn't mandate a particular database system, form library, and so on.
It encourages replaceability. This applies equally to templating, which is
fortunate: developers have strong views about template languages. That said,
the Pylons Project officially supports bindings for Chameleon, Jinja2, and
Mako. In this step let's use Chameleon.

Let's add ``pyramid_chameleon``, a Pyramid :term:`add-on` which enables
Chameleon as a :term:`renderer` in our Pyramid application:

.. code-block:: bash

    $VENV/bin/pip install pyramid_chameleon

With the package installed, we can include the template bindings into our
configuration in ``app.py``:

.. literalinclude:: quick_tour/templating/app.py
    :language: python
    :linenos:
    :lines: 6-8
    :lineno-start: 6
    :emphasize-lines: 2

Now lets change our ``views.py`` file:

.. literalinclude:: quick_tour/templating/views.py
    :language: python
    :linenos:
    :emphasize-lines: 4,6

Ahh, that looks better. We have a view that is focused on Python code. Our
``@view_config`` decorator specifies a :term:`renderer` that points to our
template file. Our view then simply returns data which is then supplied to our
template ``hello_world.pt``:

.. literalinclude:: quick_tour/templating/hello_world.pt
    :language: html

Since our view returned ``dict(name=request.matchdict['name'])``, we can use
``name`` as a variable in our template via ``${name}``.

.. seealso:: See also:
    :ref:`Quick Tutorial Templating <qtut_templating>`,
    :doc:`../narr/templates`, :ref:`debugging_templates`, and
    :ref:`available_template_system_bindings`.


Templating with Jinja2
======================

We just said Pyramid doesn't prefer one templating language over another. Time
to prove it. Jinja2 is a popular templating system, modeled after Django's
templates. Let's add ``pyramid_jinja2``, a Pyramid :term:`add-on` which enables
Jinja2 as a :term:`renderer` in our Pyramid applications:

.. code-block:: bash

    $VENV/bin/pip install pyramid_jinja2

With the package installed, we can include the template bindings into our
configuration:

.. literalinclude:: quick_tour/jinja2/app.py
    :language: python
    :linenos:
    :lines: 6-8
    :lineno-start: 6
    :emphasize-lines: 2

The only change in our view is to point the renderer at the ``.jinja2`` file:

.. literalinclude:: quick_tour/jinja2/views.py
    :language: python
    :linenos:
    :lines: 4-6
    :lineno-start: 4
    :emphasize-lines: 1

Our Jinja2 template is very similar to our previous template:

.. literalinclude:: quick_tour/jinja2/hello_world.jinja2
    :language: html

Pyramid's templating add-ons register a new kind of renderer into your
application. The renderer registration maps to different kinds of filename
extensions. In this case, changing the extension from ``.pt`` to ``.jinja2``
passed the view response through the ``pyramid_jinja2`` renderer.

.. seealso:: See also:
    :ref:`Quick Tutorial Jinja2 <qtut_jinja2>`, `Jinja2 homepage
    <https://palletsprojects.com/p/jinja/>`_, and :ref:`pyramid_jinja2 Overview
    <jinja2:overview>`.


Static assets
=============

Of course the Web is more than just markup. You need static assets: CSS, JS,
and images. Let's point our web app at a directory from which Pyramid will
serve some static assets. First let's make another call to the
:term:`configurator` in ``app.py``:

.. literalinclude:: quick_tour/static_assets/app.py
    :language: python
    :linenos:
    :lines: 6-8
    :lineno-start: 6
    :emphasize-lines: 2

This tells our WSGI application to map requests under
http://localhost:6543/static/ to files and directories inside a ``static``
directory alongside our Python module.

Next make a directory named ``static``, and place ``app.css`` inside:

.. literalinclude:: quick_tour/static_assets/static/app.css
    :language: css

All we need to do now is point to it in the ``<head>`` of our Jinja2 template,
``hello_world.jinja2``:

.. literalinclude:: quick_tour/static_assets/hello_world_static.jinja2
    :language: jinja
    :linenos:
    :lines: 4-6
    :lineno-start: 4
    :emphasize-lines: 2

This link presumes that our CSS is at a URL starting with ``/static/``. What if
the site is later moved under ``/somesite/static/``? Or perhaps a web developer
changes the arrangement on disk? Pyramid provides a helper to allow flexibility
on URL generation:

.. literalinclude:: quick_tour/static_assets/hello_world.jinja2
    :language: jinja
    :linenos:
    :lines: 4-6
    :lineno-start: 4
    :emphasize-lines: 2

By using ``request.static_url`` to generate the full URL to the static assets,
you ensure that you stay in sync with the configuration and gain refactoring
flexibility later.

.. seealso:: See also:
    :ref:`Quick Tutorial Static Assets <qtut_static_assets>`,
    :doc:`../narr/assets`, :ref:`preventing_http_caching`, and
    :ref:`influencing_http_caching`.


Returning JSON
==============

Modern web apps are more than rendered HTML. Dynamic pages now use JavaScript
to update the UI in the browser by requesting server data as JSON. Pyramid
supports this with a JSON renderer:

.. literalinclude:: quick_tour/json/views.py
    :language: python
    :linenos:
    :lines: 9-
    :lineno-start: 9

This wires up a view that returns some data through the JSON :term:`renderer`,
which calls Python's JSON support to serialize the data into JSON, and sets the
appropriate HTTP headers.

We also need to add a route to ``app.py`` so that our app will know how to
respond to a request for ``hello.json``.

.. literalinclude:: quick_tour/json/app.py
    :language: python
    :linenos:
    :lines: 6-8
    :lineno-start: 6
    :emphasize-lines: 2

.. seealso:: See also:
    :ref:`Quick Tutorial JSON <qtut_json>`, :ref:`views_which_use_a_renderer`,
    :ref:`json_renderer`, and :ref:`adding_and_overriding_renderers`.


View classes
============

So far our views have been simple, free-standing functions. Many times your
views are related. They may have different ways to look at or work on the same
data, or they may be a REST API that handles multiple operations. Grouping
these together as a :ref:`view class <class_as_view>` makes sense and achieves
the following goals.

- Group views

- Centralize some repetitive defaults

- Share some state and helpers

The following shows a "Hello World" example with three operations: view a form,
save a change, or press the delete button in our ``views.py``:

.. literalinclude:: quick_tour/view_classes/views.py
    :language: python
    :linenos:
    :lines: 7-
    :lineno-start: 7

As you can see, the three views are logically grouped together. Specifically:

- The first view is returned when you go to ``/howdy/amy``. This URL is mapped
  to the ``hello`` route that we centrally set using the optional
  ``@view_defaults``.

- The second view is returned when the form data contains a field with
  ``form.edit``, such as clicking on ``<input type="submit" name="form.edit"
  value="Save">``. This rule is specified in the ``@view_config`` for that
  view.

- The third view is returned when clicking on a button such as ``<input
  type="submit" name="form.delete" value="Delete">``.

Only one route is needed, stated in one place atop the view class. Also, the
assignment of ``name`` is done in the ``__init__`` function. Our templates can
then use ``{{ view.name }}``.

Pyramid view classes, combined with built-in and custom predicates, have much
more to offer:

- All the same view configuration parameters as function views

- One route leading to multiple views, based on information in the request or
  data such as ``request_param``, ``request_method``, ``accept``, ``header``,
  ``xhr``, ``containment``, and custom predicates.

.. seealso:: See also:
    :ref:`View Classes <qtut_view_classes>` and :ref:`More View Classes <qtut_more_view_classes>`
    in the Quick Tutorial, :ref:`class_as_view`, and :ref:`view_and_route_predicates`.


Quick project startup with cookiecutters
========================================

So far we have done all of our *Quick Tour* as a single Python file. No Python
packages, no structure. Most Pyramid projects, though, aren't developed this
way.

To ease the process of getting started, the Pylons Project provides a :term:`cookiecutter` that generates a sample Pyramid project from project templates.
This cookiecutter will install Pyramid and its dependencies as well.

First you'll need to install cookiecutter.

.. code-block:: bash

    $VENV/bin/pip install cookiecutter

Let's use the cookiecutter ``pyramid-cookiecutter-starter`` to create a starter Pyramid project in the current directory, entering values at the prompts as shown below for the following command.

.. code-block:: bash

    $VENV/bin/cookiecutter gh:Pylons/pyramid-cookiecutter-starter --checkout main

If prompted for the first item, accept the default ``yes`` by hitting return.

.. code-block:: text

    You've cloned ~/.cookiecutters/pyramid-cookiecutter-starter before.
    Is it okay to delete and re-clone it? [yes]: yes
    project_name [Pyramid Scaffold]: hello_world
    repo_name [hello_world]: hello_world
    Select template_language:
    1 - jinja2
    2 - chameleon
    3 - mako
    Choose from 1, 2, 3 [1]: 1
    Select backend:
    1 - none
    2 - sqlalchemy
    3 - zodb
    Choose from 1, 2, 3 [1]: 1

We then run through the following commands.

.. code-block:: bash

    # Change directory into your newly created project.
    cd hello_world
    # Create a new virtual environment...
    python3 -m venv env
    # ...where we upgrade packaging tools...
    env/bin/pip install --upgrade pip setuptools
    # ...and into which we install our project and its testing requirements.
    env/bin/pip install -e ".[testing]"
    # Reset our environment variable for a new virtual environment.
    export VENV=~/hello_world/env

We are moving in the direction of a full-featured Pyramid project, with a
proper setup for Python standards (packaging) and Pyramid configuration. This
includes a new way of running your application:

.. code-block:: bash

    $VENV/bin/pserve development.ini

Let's look at ``pserve`` and configuration in more depth.

.. seealso:: See also:
    :ref:`Quick Tutorial Cookiecutters <qtut_cookiecutters>`,
    :ref:`project_narr`, and
    :doc:`../narr/cookiecutters`

Application running with ``pserve``
===================================

Prior to the cookiecutter, our project mixed a number of operational details into our
code. Why should my main code care which HTTP server I want and what port
number to run on?

``pserve`` is Pyramid's application runner, separating operational details from
your code. When you install Pyramid, a small command program called ``pserve``
is written to your ``bin`` directory. This program is an executable Python
module. It's very small, getting most of its brains via import.

You can run ``pserve`` with ``--help`` to see some of its options. Doing so
reveals that you can ask ``pserve`` to watch your development files and reload
the server when they change:

.. code-block:: bash

    $VENV/bin/pserve development.ini --reload

The ``pserve`` command has a number of other options and operations. Most of
the work, though, comes from your project's wiring, as expressed in the
configuration file you supply to ``pserve``. Let's take a look at this
configuration file.

.. seealso:: See also:
    :ref:`what_is_this_pserve_thing`

Configuration with ``.ini`` files
=================================

Earlier in *Quick Tour* we first met Pyramid's configuration system. At that
point we did all configuration in Python code. For example, the port number
chosen for our HTTP server was right there in Python code. Our cookiecutter has
moved this decision and more into the ``development.ini`` file:

.. literalinclude:: quick_tour/package/development.ini
    :language: ini

Let's take a quick high-level look. First the ``.ini`` file is divided into
sections:

- ``[app:main]`` configures our WSGI app

- ``[server:main]`` holds our WSGI server settings

- Various sections afterwards configure our Python logging system

We have a few decisions made for us in this configuration:

#. *WSGI app:* What package has our WSGI application in it?
   ``use = egg:hello_world`` in the app section tells the configuration what
   application to load.

#. *Easier development by automatic template reloading:* In development mode,
   you shouldn't have to restart the server when editing a Jinja2 template.
   ``pyramid.reload_templates = true`` sets this policy, which might be
   different in production.

#. *Choice of web server:* ``use = egg:waitress#main`` tells ``pserve`` to
   use the ``waitress`` server.

#. *Interfaces:* ``listen = localhost:6543`` tells ``waitress`` to listen on all interfaces on port 6543 for both IPv4 and IPv6.

Additionally the ``development.ini`` generated by this cookiecutter wired up
Python's standard logging. We'll now see in the console, for example, a log on
every request that comes in, as well as traceback information.

.. seealso:: See also:
    :ref:`Quick Tutorial Application Configuration <qtut_ini>`,
    :ref:`environment_chapter` and
    :doc:`../narr/paste`


Easier development with ``debugtoolbar``
========================================

As we introduce the basics, we also want to show how to be productive in
development and debugging. For example, we just discussed template reloading
and earlier we showed ``--reload`` for application reloading.

``pyramid_debugtoolbar`` is a popular Pyramid add-on which makes several tools
available in your browser. Adding it to your project illustrates several points
about configuration.

Our cookiecutter ``pyramid-cookiecutter-starter`` already configured our package to include the
add-on ``pyramid_debugtoolbar`` in its ``setup.py``:

.. literalinclude:: quick_tour/package/setup.py
    :language: python
    :lineno-match:
    :lines: 11-17
    :emphasize-lines: 5

It was installed when you previously ran:

.. code-block:: bash

    $VENV/bin/pip install -e ".[testing]"

The ``pyramid_debugtoolbar`` package is a Pyramid add-on, which means we need
to include its configuration into our web application. The cookiecutter already took care of this for us in its ``development.ini`` using the ``pyramid.includes`` facility:

.. literalinclude:: quick_tour/package/development.ini
    :language: ini
    :lineno-match:
    :lines: 14-15

You'll now see a Pyramid logo on the right side of your browser window, which
when clicked opens a new window that provides introspective access to debugging
information. Even better, if your web application generates an error, you will
see a nice traceback on the screen. When you want to disable this toolbar,
there's no need to change code: you can remove it from ``pyramid.includes`` in
the relevant ``.ini`` configuration file.

.. seealso:: See also:
    :ref:`Quick Tutorial pyramid_debugtoolbar <qtut_debugtoolbar>` and
    :ref:`pyramid_debugtoolbar <toolbar:overview>`

Unit and functional tests and ``pytest``
========================================

Yikes! We got this far and we haven't yet discussed tests. This is particularly
egregious, as Pyramid has had a deep commitment to full test coverage since
before its release.

Our ``pyramid-cookiecutter-starter`` cookiecutter generated ``conftest.py``, ``test_functional.py``, and ``test_views.py`` modules inside the ``tests`` package with two unit tests and two functional tests in it.
It also configured ``setup.py`` with test requirements:
``pytest`` as the test runner, ``WebTest`` for running view tests, and the
``pytest-cov`` tool which yells at us for code that isn't tested:

.. literalinclude:: quick_tour/package/setup.py
    :language: python
    :lineno-match:
    :lines: 19-23

.. literalinclude:: quick_tour/package/setup.py
    :language: python
    :lineno-match:
    :lines: 43-45

We already installed the test requirements when we ran the command ``$VENV/bin/pip install -e ".[testing]"``. We can now run all our tests:

.. code-block:: bash

    $VENV/bin/pytest --cov --cov-report=term-missing

This yields the following output.

.. code-block:: text

    =========================== test session starts ===========================
    platform darwin -- Python 3.9.0, pytest-6.2.1, py-1.10.0, pluggy-0.13.1
    rootdir: /<somepath>/hello_world, configfile: pytest.ini, testpaths: hello_world, tests
    plugins: cov-2.10.1
    collected 4 items

    tests/test_functional.py ..                                          [ 50%]
    tests/test_views.py ..                                               [100%]

    ---------- coverage: platform darwin, python 3.9.0-final-0 -----------
    Name                            Stmts   Miss  Cover   Missing
    -------------------------------------------------------------
    hello_world/__init__.py             7      0   100%
    hello_world/routes.py               3      0   100%
    hello_world/views/__init__.py       0      0   100%
    hello_world/views/default.py        4      0   100%
    hello_world/views/notfound.py       5      0   100%
    -------------------------------------------------------------
    TOTAL                              19      0   100%

    ======================== 4 passed in 0.65 seconds =========================

Our tests passed, and its coverage is complete. What did our tests look like?

.. literalinclude:: quick_tour/package/tests/test_functional.py
    :language: python
    :linenos:

.. literalinclude:: quick_tour/package/tests/test_views.py
    :language: python
    :linenos:

Pyramid supplies helpers for test writing, which we use in the test setup and teardown.
Our view tests import the view, make a dummy request, and sees if the view returns what we expected.
Our functional tests verify that the response body from a request to the web root contains what we expected and that the expected response code for making a request to ``/badurl`` results in ``404``.

.. seealso:: See also:
    :ref:`Quick Tutorial Unit Testing <qtut_unit_testing>`, :ref:`Quick
    Tutorial Functional Testing <qtut_functional_testing>`, and
    :ref:`testing_chapter`

Logging
=======

It's important to know what is going on inside our web application. In
development we might need to collect some output. In production we might need
to detect situations when other people use the site. We need *logging*.

Fortunately Pyramid uses the normal Python approach to logging. The ``development.ini`` file for your project has a number of lines that configure the
logging for you to some reasonable defaults. You then see messages sent by
Pyramid (for example, when a new request comes in).

Maybe you would like to log messages in your code? In your Python module,
import and set up the logging in your ``views/default.py``:

.. literalinclude:: quick_tour/logging/hello_world/views/default.py
    :language: python
    :lineno-match:
    :lines: 3-4

You can now, in your code, log messages:

.. literalinclude:: quick_tour/logging/hello_world/views/default.py
    :language: python
    :lineno-match:
    :lines: 7-8
    :emphasize-lines: 2

This will log ``Some Message`` at a ``DEBUG`` log level to the
application-configured logger in your ``development.ini``. What controls that?
These emphasized sections in the configuration file:

.. literalinclude:: quick_tour/logging/development.ini
    :language: ini
    :lineno-match:
    :lines: 34-50
    :emphasize-lines: 1-2,14-17

Our application, a package named ``hello_world``, is set up as a logger and
configured to log messages at a ``DEBUG`` or higher level. When you visit
http://localhost:6543, your console will now show:

.. code-block:: text

    2016-12-25 03:03:57,059 DEBUG [hello_world.views:8][waitress] Some Message

.. seealso:: See also:
    :ref:`Quick Tutorial Logging <qtut_logging>` and :ref:`logging_chapter`.

Sessions
========

When people use your web application, they frequently perform a task that
requires semi-permanent data to be saved. For example, a shopping cart. This is
called a :term:`session`.

Pyramid has basic built-in support for sessions. Third party packages such as
``pyramid_redis_sessions`` provide richer session support. Or you can create
your own custom sessioning engine. Let's take a look at the :doc:`built-in
sessioning support <../narr/sessions>`. In our ``__init__.py`` we first import
the kind of sessioning we want:

.. literalinclude:: quick_tour/sessions/hello_world/__init__.py
    :language: python
    :lineno-match:
    :lines: 1-2
    :emphasize-lines: 2

.. warning::

    As noted in the session docs, this example implementation is not intended
    for use in settings with security implications.

Now make a "factory" and pass it to the :term:`configurator`'s
``session_factory`` argument:

.. literalinclude:: quick_tour/sessions/hello_world/__init__.py
    :language: python
    :lineno-match:
    :lines: 9-12
    :emphasize-lines: 2-3

Pyramid's :term:`request` object now has a ``session`` attribute that we can
use in our view code in ``views/default.py``:

.. literalinclude:: quick_tour/sessions/hello_world/views/default.py
    :language: python
    :lineno-match:
    :lines: 7-
    :emphasize-lines: 3-7

We need to update our Jinja2 template ``templates/mytemplate.jinja2`` to show counter increment in the session:

.. literalinclude:: quick_tour/sessions/hello_world/templates/mytemplate.jinja2
    :language: jinja
    :lineno-match:
    :lines: 4-8
    :emphasize-lines: 4

.. seealso:: See also:
    :ref:`Quick Tutorial Sessions <qtut_sessions>`, :ref:`sessions_chapter`,
    :ref:`flash_messages`, :ref:`session_module`, and
    :term:`pyramid_redis_sessions`.


Databases
=========

Web applications mean data. Data means databases. Frequently SQL databases. SQL
databases frequently mean an "ORM" (object-relational mapper.) In Python, ORM
usually leads to the mega-quality *SQLAlchemy*, a Python package that greatly
eases working with databases.

Pyramid and SQLAlchemy are great friends. That friendship includes a cookiecutter!

.. code-block:: bash

    cd ~
    env/bin/cookiecutter gh:Pylons/pyramid-cookiecutter-starter --checkout main

If prompted for the first item, accept the default ``yes`` by hitting return.

.. code-block:: text

    You've cloned ~/.cookiecutters/pyramid-cookiecutter-starter before.
    Is it okay to delete and re-clone it? [yes]: yes
    project_name [Pyramid Scaffold]: sqla_demo
    repo_name [sqla_demo]: sqla_demo
    Select template_language:
    1 - jinja2
    2 - chameleon
    3 - mako
    Choose from 1, 2, 3 [1]: 1
    Select backend:
    1 - none
    2 - sqlalchemy
    3 - zodb
    Choose from 1, 2, 3 [1]: 2

We then run through the following commands as before.

.. code-block:: bash

    # Change directory into your newly created project.
    cd sqla_demo
    # Create a new virtual environment...
    python3 -m venv env
    # ...where we upgrade packaging tools...
    env/bin/pip install --upgrade pip setuptools
    # ...and into which we install our project and its testing requirements.
    env/bin/pip install -e ".[testing]"
    # Reset our environment variable for a new virtual environment.
    export VENV=~/sqla_demo/env

We now have a working sample SQLAlchemy application with all dependencies installed.
The sample project provides a method to generate a database migration from existing models and upgrade the database schema using Alembic.
Let's generate the first revision.

.. code-block:: bash

    $VENV/bin/alembic -c development.ini revision --autogenerate -m "init"

Now let's upgrade the database schema.

.. code-block:: bash

    $VENV/bin/alembic -c development.ini upgrade head

The sample project also provides a console script to load data into the SQLite database.
Let's run it, then start the application:

.. code-block:: bash

    $VENV/bin/initialize_sqla_demo_db development.ini
    $VENV/bin/pserve development.ini

The ORM eases the mapping of database structures into a programming language.
SQLAlchemy uses "models" for this mapping. The cookiecutter generated a sample
model:

.. literalinclude:: quick_tour/sqla_demo/sqla_demo/models/mymodel.py
    :language: python
    :lineno-match:
    :pyobject: MyModel

View code, which mediates the logic between web requests and the rest of the
system, can then easily get at the data thanks to SQLAlchemy:

.. literalinclude:: quick_tour/sqla_demo/sqla_demo/views/default.py
    :language: python
    :lineno-match:
    :pyobject: my_view

.. seealso:: See also:
    :ref:`Quick Tutorial Databases <qtut_databases>`, `SQLAlchemy
    <https://www.sqlalchemy.org/>`_, :ref:`making_a_console_script`,
    :ref:`bfg_sql_wiki_tutorial`, and :ref:`Application Transactions with
    pyramid_tm <tm:overview>`.


Forms
=====

Developers have lots of opinions about web forms, thus there are many form
libraries for Python. Pyramid doesn't directly bundle a form library, but
*Deform* is a popular choice for forms, along with its related *Colander*
schema system.

As an example, imagine we want a form that edits a wiki page. The form should
have two fields on it, one of them a required title and the other a rich text
editor for the body. With Deform we can express this as a Colander schema:

.. code-block:: python

    class WikiPage(colander.MappingSchema):
        title = colander.SchemaNode(colander.String())
        body = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.RichTextWidget()
        )

With this in place, we can render the HTML for a form, perhaps with form data
from an existing page:

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

Deform and Colander provide a very flexible combination for forms, widgets,
schemas, and validation. Recent versions of Deform also include a :ref:`retail
mode <deform:retail>` for gaining Deform features on custom forms.

Deform uses attractive CSS from Twitter Bootstrap and more powerful select, checkbox, and date and time widgets.

.. seealso:: See also:
    :ref:`Quick Tutorial Forms <qtut_forms>`, :ref:`Deform <deform:overview>`, and :ref:`Colander <colander:overview>`.

Conclusion
==========

This *Quick Tour* covered a little about a lot. We introduced a long list
of concepts in Pyramid, many of which are expanded on more fully in the
Pyramid developer docs.
