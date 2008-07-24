.. _project_narr:

Starting a ``repoze.bfg`` Project
=================================

You can use ``repoze.bfg`` 's sample application generator to get
started.

Creating the Project
--------------------

To start a ``repoze.bfg`` project, use the ``paster create``
facility::

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

The project will be created in a directory named ``myproject``.  That
directory is a setuptools *project* directory from which a Python
setuptools *distribution* can be created.  The ``setup.py`` file in
that directory can be used to distribute your application, or install
your application for deployment or development. A sample PasteDeploy
``.ini`` file named ``myproject.ini`` will also be created in the
project directory.  You can use this to run your application.

The main ``myproject`` contains an additional subdirectory (also named
``myproject``) representing a Python pakckage which holds very simple
bfg sample code.  This is where you'll edit your application's Python
code and templates.

Installing your Newly Created Project for Development
-----------------------------------------------------

Using your favorite Python interpreter (using a `virtualenv
<http://pypi.python.org/pypi/virtualenv>`_ is suggested in order to
isolate your application from your system Python's packages), invoke
the following command when inside the project directory against the
generated ``setup.py``::

  $ python setup.py develop
   ...
   Finished processing dependencies for myproject==0.1

This will install your application 's package into the interpreter so
it can be found and run under a webserver.

Running The Tests For Your Application
--------------------------------------

To run unit tests for your application, you should invoke them like so::

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
  Starting server in PID 16601.
  serving on 0.0.0.0:5432 view at http://127.0.0.1:5432

It will listen on port 5432.  

.. note:: During development, it's often useful to run ``paster serve``
   using its ``--reload`` option.  When any Python module your project
   uses, changes, it will restart the server, which makes development
   easier, as changes to Python code under ``repoze.bfg`` is not put
   into effect until the server restarts.

Viewing the Application
-----------------------

Visit http://localhost:5432/ in your browser.  You will see::

  Welcome to myproject

The Project Structure
---------------------

Our generated ``repoze.bfg`` application is a setuptools *project*
(named ``myproject``), which contains a Python package (which is
*also* named ``myproject``; the paster template generates a project
which contains a package that shares its name).

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

The ``myproject`` *Project*
---------------------------

The ``myproject`` project is the distribution and deployment wrapper
for your application.  It contains both the ``myproject`` *package*
representing your application as well as files used to describe, run,
and test your application.

#. ``CHANGES.txt`` describes the changes you've made to the application.

#. ``README.txt`` describes the application in general.

#. ``ez_setup.py`` is a file that is used by ``setup.py`` to install
   setuptools if the executing user does not have it installed.

#. ``myproject.ini`` is a PasteDeploy configuration file that can be
   used to execute your application.

#. ``setup.py`` is the file you'll use to test and distribute your
   application.  It is a standard distutils/setuptools ``setup.py`` file.

It also contains the ``myproject`` *package*, described below.

The ``myproject`` *Package*
---------------------------

The ``myproject`` package lives inside the ``myproject`` project.  It
contains:

#. An ``__init__.py`` file which signifies that this is a Python
   package.  It is conventionally empty, save for a single comment at
   the top.

#. A ``configure.zcml`` file which maps view names to model types.
   This is also known as the "application registry", although it
   also often contains non-view-related declarations.

#. A ``models.py`` module, which contains model code.

#. A ``run.py`` module, which contains code that helps users run the
   application.

#. A ``templates`` directory, which is full of zc3.pt and/or XSL
   templates.

#. A ``tests.py`` module, which contains test code.

#. A ``views.py`` module, which contains view code.

These are purely conventions established by the Paster template:
``repoze.bfg`` doesn't insist that you name things in any particular
way.

``configure.zcml``
~~~~~~~~~~~~~~~~~~

The ``configure.zcml`` (representing the application registry) looks
like so:

.. literalinclude:: myproject/myproject/configure.zcml
   :linenos:
   :language: xml

#. Lines 1-3 provide the root node and namespaces for the
   configuration language.  ``bfg`` is the namespace for
   ``repoze.bfg``-specific configuration directives.

#. Line 6 initializes ``repoze.bfg``-specific configuration
   directives by including it as a package.

#. Lines 8-11 register a single view.  It is ``for`` model objects
   that support the IMyModel interface.  The ``view`` attribute points
   at a Python function that does all the work for this view.

``views.py``
~~~~~~~~~~~~

Much of the heavy lifting in a ``repoze.bfg`` application comes in the
views.  Views are the bridge between the content in the model, and the
HTML given back to the browser.

.. literalinclude:: myproject/myproject/views.py
   :linenos:

#. Lines 3-5 provide the ``my_view`` that was registered as the view.
   ``configure.zcml`` said that the default URL for IMyModel content
   should run this ``my_view`` function.

   The function is handed two pieces of information: the ``context``
   and the ``request``.  The ``context`` is the data at the current
   hop in the URL.  (That data comes from the model.)  The request is
   an instance of a WebOb request.

#. The model renders a remplate and returns the result as the
   response.

``models.py``
~~~~~~~~~~~~~

In our sample app, the ``models.py`` module provides the model data.
We create an interface ``IMyModel`` that gives us the "type" for our
data.  We then write a class ``MyModel`` that provides the behavior
for instances of the ``IMyModel`` type.

.. literalinclude:: myproject/myproject/models.py
   :linenos:

#. Lines 4-5 define the interface.

#. Lines 7-9 provide a class that implements this interface.

#. Line 11 defines an instance of MyModel as the root.

#. Line 13 is a function that will be called by the ``repoze.bfg``
   *Router* for each request when it wants to find the root of the model
   graph.  Conventionally this is called ``get_root``.

In a "real" application, the root object would not be such a simple
object.  Instead, it would be an object that could access some
persistent data store, such as a database.  ``repoze.bfg`` doesn't
make any assumption about which sort of datastore you'll want to use,
so the sample application uses an instance of ``MyModel`` to represent
the root.

``run.py``
~~~~~~~~~~

We need a small Python module that sets everything, fires up a web
server, and handles incoming requests.  Later we'll see how to use a
Paste configuration file to do this work for us.

.. literalinclude:: myproject/myproject/run.py
   :linenos:

#. Lines 1 - 7 define a function that returns a ``repoze.bfg`` Router
   application.  This is meant to be called by the PasteDeploy framework
   as a result of running ``paster serve``.

#. Lines 9 - 12 allow this file to serve as a shortcut for executing
   our program if the ``run.py`` file is executed directly.  It starts
   our application under a web server on port 5432.

``templates/mytemplate.pt``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The single template in the project looks like so:

.. literalinclude:: myproject/myproject/templates/mytemplate.pt
   :linenos:
   :language: xml

``tests.py``
~~~~~~~~~~~~

The ``tests.py`` module includes unit tests for your application.

.. literalinclude:: myproject/myproject/tests.py
   :linenos:


