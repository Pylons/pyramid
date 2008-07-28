.. _project_narr:

Starting a :mod:`repoze.bfg` Project
====================================

You can use :mod:`repoze.bfg` 's sample application generator to get
started.  This generator uses :term:`Paste` templates to allow
creation of a new project by answering a series of questions.

Creating the Project
--------------------

To start a :mod:`repoze.bfg` :term:`project`, use the ``paster
create`` facility::

  $ paster create -t bfg

``paster create`` will ask you a single question: the *name* of the
project.  You should use a string without spaces and with only letters
in it.  Here's sample output from a run of ``paster create`` for a
project we name ``myproject``::

  $ paster create -t bfg
  Selected and implied templates:
    repoze.bfg#bfg  repoze.bfg starter project

  Enter project name: myproject
  Variables:
    egg:      myproject
    package:  myproject
    project:  myproject
  Creating template bfg
  Creating directory ./myproject
    Recursing into +package+
      Creating ./myproject/myproject/
      Copying __init__.py to ./myproject/myproject/__init__.py
      Copying configure.zcml to ./myproject/myproject/configure.zcml
      Copying models.py to ./myproject/myproject/models.py
      Copying run.py_tmpl to ./myproject/myproject/run.py
      Recursing into templates
        Creating ./myproject/myproject/templates/
        Copying mytemplate.pt to ./myproject/myproject/templates/mytemplate.pt
      Copying views.py_tmpl to ./myproject/myproject/views.py
    Copying +package+.ini_tmpl to ./myproject/myproject.ini
    Copying CHANGES.txt_tmpl to ./myproject/CHANGES.txt
    Copying README.txt_tmpl to ./myproject/README.txt
    Copying ez_setup.py to ./myproject/ez_setup.py
    Copying setup.py_tmpl to ./myproject/setup.py
  Running /Users/chrism/projects/repoze-devel/bfg/bin/python setup.py egg_info

As a result of the above, a project is created in a directory named
``myproject``.  That directory is a :term:`setuptools` :term:`project`
directory from which a Python setuptools :term:`distribution` can be
created.  The ``setup.py`` file in that directory can be used to
distribute your application, or install your application for
deployment or development. A sample :term:`PasteDeploy` ``.ini`` file
named ``myproject.ini`` will also be created in the project directory.
You will use the ``paster serve`` command against this ``ini`` file to
run your application.

The main ``myproject`` directory contains an additional subdirectory
(also named ``myproject``) representing a Python :term:`package` which
holds very simple :mod:`repoze.bfg` sample code.  This is where you'll
edit your application's Python code and templates.

Installing your Newly Created Project for Development
-----------------------------------------------------

Using your favorite Python interpreter (or, better, the interpreter
from a :term:`virtualenv`), invoke the following command when inside
the project directory against the generated ``setup.py``::

  $ python setup.py develop

Elided output from a run of this command is shown below::

  $ python setup.py develop
   ...
   Finished processing dependencies for myproject==0.1

This will install your application 's :term:`package` into the
interpreter so it can be found and run as a :term:`WSGI` application
inside a WSGI server.

Running The Tests For Your Application
--------------------------------------

To run unit tests for your application, you should invoke them like
so::

  $ python setup.py test -q

Here's sample output from a test run::

  $ python setup.py test -q
  running test
  running egg_info
  writing requirements to myproject.egg-info/requires.txt
  writing myproject.egg-info/PKG-INFO
  writing top-level names to myproject.egg-info/top_level.txt
  writing dependency_links to myproject.egg-info/dependency_links.txt
  writing entry points to myproject.egg-info/entry_points.txt
  reading manifest file 'myproject.egg-info/SOURCES.txt'
  writing manifest file 'myproject.egg-info/SOURCES.txt'
  running build_ext
  .
  ----------------------------------------------------------------------
  Ran 1 test in 0.566s

  OK

The tests are found in the ``tests.py`` module in your
paster-create-generated project.  One sample test exists.

Runnning The Project Application
--------------------------------

Once the project is installed for development, you can run the
application it represents using the ``paster serve`` command against
the generated ``myproject.ini`` configuration file::

  $ paster serve myproject/myproject.ini

Here's sample output from a run::

  $ paster serve myproject/myproject.ini
  Starting server in PID 16601.
  serving on 0.0.0.0:5432 view at http://127.0.0.1:5432

By default, generated :mod:`repoze.bfg` applications will listen on
port 5432.

.. note:: During development, it's often useful to run ``paster
   serve`` using its ``--reload`` option.  When any Python module your
   project uses, changes, it will restart the server, which makes
   development easier, as changes to Python code under
   :mod:`repoze.bfg` is not put into effect until the server restarts.

Viewing the Application
-----------------------

Visit *http://localhost:5432/* in your browser.  You will see::

  Welcome to myproject

That's the page shown by default when you visit an unmodified ``paster
create``-generated application.

The Project Structure
---------------------

Our generated :mod:`repoze.bfg` application is a setuptools
:term:`project` (named ``myproject``), which contains a Python
:term:`package` (which is *also* named ``myproject``; the paster
template generates a project which contains a package that shares its
name).

The ``myproject`` project has the following directory structure::

  myproject/
  |-- CHANGES.txt
  |-- README.txt
  |-- ez_setup.py
  |-- myproject
  |   |-- __init__.py
  |   |-- configure.zcml
  |   |-- models.py
  |   |-- run.py
  |   |-- templates
  |   |   `-- mytemplate.pt
  |   |-- tests.py
  |   `-- views.py
  |-- myproject.ini
  `-- setup.py

The ``myproject`` :term:`Project`
---------------------------------

The ``myproject`` :term:`project` is the distribution and deployment
wrapper for your application.  It contains both the ``myproject``
:term:`package` representing your application as well as files used to
describe, run, and test your application.

#. ``CHANGES.txt`` describes the changes you've made to the
   application.  It is conventionally written in
   :term:`ReStructuredText` format.

#. ``README.txt`` describes the application in general.  It is
   conventionally written in :term:`RestructuredText` format.

#. ``ez_setup.py`` is a file that is used by ``setup.py`` to install
   :term:`setuptools` if the executing user does not have it
   installed.

#. ``myproject.ini`` is a :term:`PasteDeploy` configuration file that
   can be used to execute your application.

#. ``setup.py`` is the file you'll use to test and distribute your
   application.  It is a standard :term:`setuptools` ``setup.py``
   file.

It also contains the ``myproject`` :term:`package`, described below.

The ``myproject`` :term:`Package`
---------------------------------

The ``myproject`` :term:`package` lives inside the ``myproject``
:term:`project`.  It contains:

#. An ``__init__.py`` file which signifies that this is a Python
   :term:`package`.  It is conventionally empty, save for a single
   comment at the top.

#. A ``configure.zcml`` is a :term:`ZCML` file which maps view names
   to model types.  This is also known as the :term:`application
   registry`.

#. A ``models.py`` module, which contains :term:`model` code.

#. A ``run.py`` module, which contains code that helps users run the
   application.

#. A ``templates`` directory, which is full of :term:`z3c.pt` and/or
   :term:`XSLT` templates.

#. A ``tests.py`` module, which contains unit test code for the
   application.

#. A ``views.py`` module, which contains view code for the
   application.

These are purely conventions established by the ``paster`` template:
:mod:`repoze.bfg` doesn't insist that you name things in any
particular way.

``configure.zcml``
~~~~~~~~~~~~~~~~~~

The ``configure.zcml`` represents the :term:`application
registry`. It looks like so:

.. literalinclude:: myproject/myproject/configure.zcml
   :linenos:
   :language: xml

#. Lines 1-3 provide the root node and namespaces for the
   configuration language.  ``bfg`` is the namespace for
   :mod:`repoze.bfg` -specific configuration directives.

#. Line 6 initializes :mod:`repoze.bfg`-specific configuration
   directives by including it as a package.

#. Lines 8-11 register a single view.  It is ``for`` model objects
   that support the IMyModel interface.  The ``view`` attribute points
   at a Python function that does all the work for this view.  Note
   that the values of both the ``for`` attribute and the ``view``
   attribute begin with a single period.  Names that begin with a
   period are "shortcuts" which point at files relative to the
   :term:`package` in which the ``configure.zcml`` file lives.  In
   this case, since the ``configure.zcml`` file lives within the
   ``myproject`` project, the shorcut ``.models.IMyModel`` could also
   be spelled ``myproject.models.IMyModel`` (forming a full Python
   dotted-path name to the ``IMyModel`` class).  Likewise the shortcut
   ``.views.my_view`` could be replaced with
   ``myproject.views.my_view``.

``views.py``
~~~~~~~~~~~~

Much of the heavy lifting in a :mod:`repoze.bfg` application comes in
the form of *views*.  A :term:`view` is the bridge between the content
in the model, and the HTML given back to the browser.

.. literalinclude:: myproject/myproject/views.py
   :linenos:

#. Lines 3-5 provide the ``my_view`` that was registered as the view.
   ``configure.zcml`` said that the default URL for ``IMyModel``
   content should run this ``my_view`` function.

   The function is handed two pieces of information: the
   :term:`context` and the term:`request`.  The *context* is the term
   :term:`model` found via :term:`traversal` (or via :term:`URL
   dispatch`).  The *request* is an instance of the :term:`WebOb`
   ``Request`` class representing the browser's request to our server.

#. The view renders a :term:`template` and returns the result as the
   :term:`response`.

.. note::

  This example uses ``render_template_to_response`` which is a
  shortcut function.  If you want more control over the response, use
  the ``render_template`` function, also present in
  :ref:`template_module`.  You may then create your own :term:`WebOb`
  Response object, using the result of ``render_template`` as the
  response's body.

``models.py``
~~~~~~~~~~~~~

The ``models.py`` module provides the :term:`model` data for our
application.  We write a class named ``MyModel`` that provides the
behavior.  We then create an interface ``IMyModel`` that is a
:term:`interface` which serves as the "type" for our data, and we
associate it without our ``MyModel`` class by claiming that the class
``implements`` the interface.

.. literalinclude:: myproject/myproject/models.py
   :linenos:

#. Lines 4-5 define the interface.

#. Lines 7-9 provide a class that implements this interface.

#. Line 11 defines an instance of MyModel as the root.

#. Line 13 is a function that will be called by the :mod:`repoze.bfg`
   *Router* for each request when it wants to find the root of the model
   graph.  Conventionally this is called ``get_root``.

In a "real" application, the root object would not be such a simple
object.  Instead, it would be an object that could access some
persistent data store, such as a database.  :mod:`repoze.bfg` doesn't
make any assumption about which sort of datastore you'll want to use,
so the sample application uses an instance of ``MyModel`` to represent
the root.

What will likely frighten new developers in the model file is the use
of :term:`interface` classes.  In their simplest form (which is the
only form that :mod:`repoze.bfg` requires you to understand),
interfaces are simply "marker" attributes indicating the *type* of a
model object.  These can be attached to classes (via the
``implements`` function with one or more interfaces as arguments at
class scope).  In more advanced usage, they can be attached directly
to instances.  We do not demonstrate that here.

``run.py``
~~~~~~~~~~

We need a small Python module that configures our application and
advertises itself to our :term:`PasteDeploy` ``.ini`` file.  For
convenience, we also make it possible to run this module directory
without the PasteDeploy configuration file:

.. literalinclude:: myproject/myproject/run.py
   :linenos:

#. Lines 1 - 7 define a function that returns a :mod:`repoze.bfg`
   Router application from :ref:`router_module` .  This is meant to be
   called by the :term:`PasteDeploy` framework as a result of running
   ``paster serve``.

#. Lines 9 - 12 allow this file to serve optionally as a shortcut for
   executing our program if the ``run.py`` file is executed directly.
   It starts our application under a web server on port 5432.

``templates/mytemplate.pt``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The single :term:`template` in the project looks like so:

.. literalinclude:: myproject/myproject/templates/mytemplate.pt
   :linenos:
   :language: xml

This is a :term:`z3c.pt` template.  It displays the current project
name when it is rendered.  It is referenced by the ``my_view``
function in the ``views.py`` module.  Templates are accessed and used
by view functions.

``tests.py``
~~~~~~~~~~~~

The ``tests.py`` module includes unit tests for your application.

.. literalinclude:: myproject/myproject/tests.py
   :linenos:

This sample ``tests.py`` file has a single unit test defined within
it.  This is the code that is executed when you run ``setup.py test
-q``.  You may add more tests here as you build your application.  You
are not required to write tests to use :mod:`repoze.bfg`, this file is
simply provided as convenience and example.

