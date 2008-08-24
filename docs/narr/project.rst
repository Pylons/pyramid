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
project we name ``MyProject``::

  $ bin/paster create -t bfg
  Selected and implied templates:
    repoze.bfg#bfg  repoze.bfg starter project

  Enter project name: MyProject
  Variables:
    egg:      MyProject
    package:  myproject
    project:  MyProject
  Creating template bfg
  Creating directory ./MyProject
    Recursing into +package+
      Creating ./MyProject/myproject/
      Copying __init__.py to ./MyProject/myproject/__init__.py
      Copying configure.zcml to ./MyProject/myproject/configure.zcml
      Copying models.py to ./MyProject/myproject/models.py
      Copying run.py_tmpl to ./MyProject/myproject/run.py
      Recursing into templates
        Creating ./MyProject/myproject/templates/
        Copying mytemplate.pt to ./MyProject/myproject/templates/mytemplate.pt
      Copying tests.py_tmpl to ./MyProject/myproject/tests.py
      Copying views.py_tmpl to ./MyProject/myproject/views.py
    Copying +project+.ini_tmpl to ./MyProject/MyProject.ini
    Copying CHANGES.txt_tmpl to ./MyProject/CHANGES.txt
    Copying README.txt_tmpl to ./MyProject/README.txt
    Copying ez_setup.py to ./MyProject/ez_setup.py
    Copying setup.py_tmpl to ./MyProject/setup.py
  Running /Users/chrism/projects/repoze/bfg/bin/python setup.py egg_info

As a result of the above, a project is created in a directory named
``MyProject``.  That directory is a :term:`setuptools` :term:`project`
directory from which a Python setuptools :term:`distribution` can be
created.  The ``setup.py`` file in that directory can be used to
distribute your application, or install your application for
deployment or development. A sample :term:`PasteDeploy` ``.ini`` file
named ``MyProject.ini`` will also be created in the project directory.
You will use the ``paster serve`` command against this ``.ini`` file
to run your application.

The ``MyProject`` project directory contains an additional
subdirectory named ``myproject`` (note the case difference)
representing a Python :term:`package` which holds very simple
:mod:`repoze.bfg` sample code.  This is where you'll edit your
application's Python code and templates.

Installing your Newly Created Project for Development
-----------------------------------------------------

Using your favorite Python interpreter (or, better, the interpreter
from a :term:`virtualenv`), invoke the following command when inside
the project directory against the generated ``setup.py``::

  $ python setup.py develop

Elided output from a run of this command is shown below::

  $ python setup.py develop
   ...
   Finished processing dependencies for MyProject==0.1

This will install your application's :term:`package` into the
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
  writing requirements to MyProject.egg-info/requires.txt
  writing MyProject.egg-info/PKG-INFO
  writing top-level names to MyProject.egg-info/top_level.txt
  writing dependency_links to MyProject.egg-info/dependency_links.txt
  writing entry points to MyProject.egg-info/entry_points.txt
  reading manifest file 'MyProject.egg-info/SOURCES.txt'
  writing manifest file 'MyProject.egg-info/SOURCES.txt'
  running build_ext
  .
  ----------------------------------------------------------------------
  Ran 1 test in 0.647s

OK

The tests are found in the ``tests.py`` module in your ``paster
create``-generated project.  One sample test exists.

Runnning The Project Application
--------------------------------

Once the project is installed for development, you can run the
application it represents using the ``paster serve`` command against
the generated ``MyProject.ini`` configuration file::

  $ paster serve myproject/MyProject.ini

Here's sample output from a run::

  $ paster serve myproject/MyProject.ini
  Starting server in PID 16601.
  serving on 0.0.0.0:6543 view at http://127.0.0.1:6543

By default, generated :mod:`repoze.bfg` applications will listen on
port 6543.

.. note:: During development, it's often useful to run ``paster
   serve`` using its ``--reload`` option.  When any Python module your
   project uses, changes, it will restart the server, which makes
   development easier, as changes to Python code under
   :mod:`repoze.bfg` is not put into effect until the server restarts.

.. note:: When :mod:`repoze.bfg` starts, it attempts to write a
   ``.cache`` file which stores a cached version of your
   :term:`application registry`.  In a typical setup this file will be
   written as ``configure.zcml.cache`` in the same directory that your
   application's ``configure.zcml`` is stored.  This is temporary data
   that can help your :mod:`repoze.bfg` application start slightly
   faster (its existence prevents the need to parse the XML stored in
   the ``.zcml`` file if that file or any of files upon which it
   depends files have not changed).  You can delete it at will as
   necessary; it will be recreated.  If a ``.cache`` file cannot be
   written due to filesystem permissions, :mod:`repoze.bfg` will just
   reparse the ``.zcml`` file every time it starts.

Viewing the Application
-----------------------

Visit ``http://localhost:6542/`` in your browser.  You will see::

  Welcome to MyProject

That's the page shown by default when you visit an unmodified ``paster
create``-generated application.

The Project Structure
---------------------

Our generated :mod:`repoze.bfg` application is a setuptools
:term:`project` (named ``MyProject``), which contains a Python
:term:`package` (which is *also* named ``myproject``, but lowercased;
the paster template generates a project which contains a package that
shares its name except for case).

The ``MyProject`` project has the following directory structure::

  MyProject/
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
  |-- MyProject.ini
  `-- setup.py

The ``MyProject`` :term:`Project`
---------------------------------

The ``myproject`` :term:`project` is the distribution and deployment
wrapper for your application.  It contains both the ``myproject``
:term:`package` representing your application as well as files used to
describe, run, and test your application.

#. ``CHANGES.txt`` describes the changes you've made to the
   application.  It is conventionally written in
   :term:`ReStructuredText` format.

#. ``README.txt`` describes the application in general.  It is
   conventionally written in :term:`ReStructuredText` format.

#. ``ez_setup.py`` is a file that is used by ``setup.py`` to install
   :term:`Setuptools` if the executing user does not have it
   installed.

#. ``MyProject.ini`` is a :term:`PasteDeploy` configuration file that
   can be used to execute your application.

#. ``setup.py`` is the file you'll use to test and distribute your
   application.  It is a standard :term:`setuptools` ``setup.py``
   file.

We won't describe the ``CHANGES.txt`` or ``README.txt`` files.
``ez_setup.py`` is a file only used by ``setup.py`` in case a user who
wants to install your package does not have :term:`Setuptools` already
installed.  It is only imported by and used by ``setup.py``, so we
won't describe it here.

``MyProject.ini``
~~~~~~~~~~~~~~~~~

The ``MyProject.ini`` file is a :term:`PasteDeploy` configuration
file.  Its purpose is to specify an application to run when you invoke
``paster serve`` when you start an application, as well as the options
provided to that application.

The generated ``MyProject.ini`` file looks like so:

.. literalinclude:: MyProject/MyProject.ini
   :linenos:

This file contains several "sections" including ``[DEFAULT]``,
``[app:main]``, and ``[server:main]``.

The ``[DEFAULT]`` section consists of global parameters that are
shared by all the applications, servers and :term:`middleware` defined
within the configuration file.  By default it contains one key
``debug``, which is set to ``true``.  This key is used by various
components to decide whether to act in a "debugging" mode.
``repoze.bfg`` itself does not do anything with this parameter as of
this writing, and neither does the generated sample application.

The ``[app:main]`` section represents configuration for your
application.  This section name represents the ``main`` application
(and it's an ``app`` -lication, thus ``app:main``), sigifiying that
this is the default application run by ``paster serve`` when it is
invoked against this configuration file.  The name ``main`` is a
convention signifying that it the default application.

The ``use`` setting is required in the ``[app:main]`` section.  The
``use`` setting points at a :term:`setuptools` "entry point" named
``MyProject#app`` (the ``egg:`` prefix in ``egg:MyProject#app``
indicates that this is an entry point specifier).

.. note::

   This part of configuration can be confusing so let's try to clear
   things up a bit.  Take a look at the generated ``setup.py`` file
   for this project.  Note that the ``entry_point`` line in
   ``setup.py`` points at a string which looks a lot like an ``.ini``
   file.  This string representation of an ``.ini`` file has a section
   named ``[paste.app_factory]``.  Within this section, there is a key
   named ``app`` (the entry point name) which has a value
   ``myproject.run:app``.  The *key* ``app`` is what our
   ``egg:MyProject#app`` value of the ``use`` section in our config
   file is pointing at.  The value represents a Python "dotted-name"
   path, which refers to a callable in our ``myproject`` package's
   ``run.py`` module.

   In English, this entry point can thus be referred to as a "Paste
   application factory in the ``MyProject`` project which has the
   entry point named ``app`` where the entry point refers to a ``app``
   function in the ``mypackage.run`` module".  If indeed if you open
   up the ``run.py`` module generated within the ``myproject``
   package, you'll see a ``app`` function.  This is the function
   called :term:`PasteDeploy` when the ``paster serve`` command is
   invoked against our application.  It accepts a global configuration
   object and *returns* an instance of our application.

The ``use`` setting is the only setting required in the ``[app:main]``
section unless you've changed the callable referred to by the
``MyProject#app`` entry point to accept more arguments: other settings
you add to this section are passed as keywords arguments to the
callable represented by this entry point (``app`` in our ``run.py``
module).  You can provide startup-time configuration parameters to
your application by requiring more settings in this section.

The ``reload_templates`` setting in the ``[app:main]`` section is a
:mod:`repoze.bfg`-specific setting which is passed into the framework.
If it exists, and is ``true``, :term:`z3c.pt` and XSLT template
changes will not require an application restart to be detected.

.. warning:: The ``reload_templates`` option should be turned off for
   production applications, as template rendering is slowed when it is
   turned on.

The ``[server:main]`` section of the configuration file configures a
WSGI server which listens on port 6543.  It is configured to listen on
all interfaces (``0.0.0.0``), and is configured to use four threads
for our application.

.. note::

  In general, ``repoze.bfg`` applications should be threading-aware.
  It is not required that a ``repoze.bfg`` application be nonblocking
  as all application code will run in its own thread, provided by the
  server you're using.

See the :term:`PasteDeploy` documentation for more information about
other types of things you can put into this ``.ini`` file, such as
other applications, :term:`middleware` and alternate servers.

``setup.py``
~~~~~~~~~~~~

The ``setup.py`` file is a :term:`setuptools` setup file.  It is meant
to be run directly from the command line to perform a variety of
functions, such as testing your application, packaging, and
distributing your application.

.. note::

  ``setup.py`` is the defacto standard which Python developers use to
  distribute their reusable code.  You can read more about
  ``setup.py`` files and their usage in the :term:`Setuptools`
  documentation.

Our generated ``setup.py`` looks like this:

.. literalinclude:: MyProject/setup.py
   :linenos:

The top of the file imports and uses ``ez_setup``, which causes
:term:`Setuptools` to be installed on an invoking user's computer if
it isn't already.  The ``setup.py`` file calls the setuptools
``setup`` function, which does various things depending on the
arguments passed to ``setup.py`` on the command line.

Within the arguments to this function call, information about your
application is kept.  While it's beyond the scope of this
documentation to explan everything about setuptools setup files, we'll
provide a whirlwind tour of what exists in this file here.

Your application's name (this can be any string) is specified in the
``name`` field.  The version number is specified in the ``version``
value.  A short description is provided in the ``description`` field.
The ``long_description`` is conventionally the content of the README
and CHANGES file appended together.  The ``classifiers`` field is a
list of `Trove
<http://pypi.python.org/pypi?%3Aaction=list_classifiers>`_ classifiers
describing your application.  ``author`` and ``author_email`` are text
fields which probably don't need any description.  ``url`` is a field
that should point at your application project's URL (if any).
``packages=find_packages()`` causes all packages within the project to
be found when packaging the application.  ``include_package_data``
will include non-Python files when the application is packaged (if
those files are checked into version control).  ``zip_safe` indicates
that this package is not safe to ship as a zipped egg (it will unpack
as a directory, which is more convenient).  ``install_requires`` and
``tests_require`` indicate that this package depends on the
``repoze.bfg`` package.  ``test_suite`` points at the package for our
application, which means all tests found in the package will be
installed.  We examined ``entry_points`` in our discussion of the
``MyProject.ini`` file; this file defines the ``app`` entry point that
represent's our project's application.

Usually you only need to think about the contents of the ``setup.py``
file when distributing your application to other people, or when
versioning your application for your own use.  For fun, you can try
this command now::

  python setup.py sdist

This will create a tarball of your application in a ``dist``
subdirectory named ``MyProject-0.1.tar.gz``.  You can send this
tarball to other people who want to use your application.

.. note::

   By default, ``setup.py sdist`` does not place non-Python-source
   files in generated tarballs.  This means, in this case, that the
   ``mytemplate.pt`` file that's in our ``templates`` directory is not
   packaged in the tarball.  To allow this to happen, check all the
   files that you'd like to be distributed along with your
   application's Python files into a version control system such as
   Subversion.  After you do this, when you rerun ``setup.py sdist``,
   all files checked into the version control system will be included
   in the tarball.

The ``myproject`` :term:`Package`
---------------------------------

The ``myproject`` :term:`package` lives inside the ``MyProject``
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

.. literalinclude:: MyProject/myproject/configure.zcml
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
   ``myproject`` package, the shorcut ``.models.IMyModel`` could also
   be spelled ``myproject.models.IMyModel`` (forming a full Python
   dotted-path name to the ``IMyModel`` class).  Likewise the shortcut
   ``.views.my_view`` could be replaced with
   ``myproject.views.my_view``.

``views.py``
~~~~~~~~~~~~

Much of the heavy lifting in a :mod:`repoze.bfg` application comes in
the form of *views*.  A :term:`view` is the bridge between the content
in the model, and the HTML given back to the browser.

.. literalinclude:: MyProject/myproject/views.py
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
   :term:`response`.  Note that because our ``MyProject.ini`` has a
   ``reload_templates = true`` directive indicating that templates
   should be reloaded when they change, you won't need to restart the
   application server to see changes you make to templates.  During
   development, this is handy.  If this directive had been ``false``
   (or if the directive did not exist), you would need to restart the
   application server for each template change.  For production
   applications, you should set your project's ``reload_templates`` to
   ``false`` to increase the speed at which templates may be rendered.

.. note::

  This example uses ``render_template_to_response`` which is a
  shortcut function.  If you want more control over the response, use
  the ``render_template`` function, also present in
  :ref:`template_module`.  You may then create your own :term:`WebOb`
  Response object, using the result of ``render_template`` as the
  response's body.  There is also a ``get_template`` API in the same
  module, which you can use to retrieve the template object without
  rendering it at all, for additional control.

``models.py``
~~~~~~~~~~~~~

The ``models.py`` module provides the :term:`model` data for our
application.  We write a class named ``MyModel`` that provides the
behavior.  We then create an interface ``IMyModel`` that is a
:term:`interface` which serves as the "type" for our data, and we
associate it without our ``MyModel`` class by claiming that the class
``implements`` the interface.

.. literalinclude:: MyProject/myproject/models.py
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

.. literalinclude:: MyProject/myproject/run.py
   :linenos:

#. Lines 1 - 2 import functions from :mod:`repoze.bfg` that we use later.

#. Lines 4-9 define a function that returns a :mod:`repoze.bfg` Router
   application from :ref:`router_module` .  This is meant to be called
   by the :term:`PasteDeploy` framework as a result of running
   ``paster serve``.

#. Lines 11 - 13 allow this file to serve optionally as a shortcut for
   executing our program if the ``run.py`` file is executed directly.
   It starts our application under a web server on port 6543.

``templates/mytemplate.pt``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The single :term:`template` in the project looks like so:

.. literalinclude:: MyProject/myproject/templates/mytemplate.pt
   :linenos:
   :language: xml

This is a :term:`z3c.pt` template.  It displays the current project
name when it is rendered.  It is referenced by the ``my_view``
function in the ``views.py`` module.  Templates are accessed and used
by view functions.

``tests.py``
~~~~~~~~~~~~

The ``tests.py`` module includes unit tests for your application.

.. literalinclude:: MyProject/myproject/tests.py
   :linenos:

This sample ``tests.py`` file has a single unit test defined within
it.  This is the code that is executed when you run ``setup.py test
-q``.  You may add more tests here as you build your application.  You
are not required to write tests to use :mod:`repoze.bfg`, this file is
simply provided as convenience and example.

