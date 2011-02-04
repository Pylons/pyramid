.. _project_narr:

Creating a :app:`Pyramid` Project
====================================

As we saw in :ref:`firstapp_chapter`, it's possible to create a
:app:`Pyramid` application completely manually.  However, it's usually more
convenient to use a *template* to generate a basic :app:`Pyramid`
:term:`project`.

A project is a directory that contains at least one Python :term:`package`.
You'll use a template to create a project, and you'll create your application
logic within a package that lives inside the project.  Even if your
application is extremely simple, it is useful to place code that drives the
application within a package, because a package is more easily extended with
new code.  An application that lives inside a package can also be distributed
more easily than one which does not live within a package.

:app:`Pyramid` comes with a variety of templates that you can use to generate
a project.  Each template makes different configuration assumptions about
what type of application you're trying to construct.

These templates are rendered using the :term:`PasteDeploy` ``paster`` script,
and so therefore they are often referred to as "paster templates".

.. index::
   single: paster templates
   single: pyramid_starter paster template
   single: pyramid_zodb paster template
   single: pyramid_alchemy paster template
   single: pyramid_routesalchemy paster template

.. _additional_paster_templates:

Paster Templates Included with :app:`Pyramid`
------------------------------------------------

The convenience ``paster`` templates included with :app:`Pyramid` differ from
each other on a number of axes:

- the persistence mechanism they offer (no persistence mechanism,
  :term:`ZODB`, or :term:`SQLAlchemy`).

- the mechanism they use to map URLs to code (:term:`traversal` or :term:`URL
  dispatch`).

- whether or not the ``pyramid_beaker`` library is relied upon as the
  sessioning implementation (as opposed to no sessioning or default
  sessioning).

The included templates are these:

``pyramid_starter``
  URL mapping via :term:`traversal` and no persistence mechanism.

``pyramid_zodb``
  URL mapping via :term:`traversal` and persistence via :term:`ZODB`.

``pyramid_routesalchemy`` 
  URL mapping via :term:`URL dispatch` and persistence via
  :term:`SQLAlchemy`

``pyramid_alchemy``
  URL mapping via :term:`traversal` and persistence via
  :term:`SQLAlchemy`

.. note:: At this time, each of these templates uses the :term:`Chameleon`
   templating system, which is incompatible with both Jython and PyPy.  To
   use paster templates to build applications which will run on Jython and
   PyPy, you can try the ``pyramid_jinja2_starter`` template which ships as
   part of the :term:`pyramid_jinja2` package or the ``pyramid_sqla`` paster
   template which ships with the :term:`pyramid_sqla` package (it uses Mako),
   both available from :term:`PyPI`.  You can also just use the above paster
   templates to build a skeleton and replace the Chameleon template it
   includes with a :term:`Mako` analogue.

Rather than use any of the above templates, Pylons 1 users may feel more
comfortable installing the :term:`pyramid_sqla` add-on package, which
provides a paster template named ``pyramid_sqla``.  This paster template
configures a Pyramid application in a "Pylons-esque" way, including the use
of a :term:`view handler` to map URLs to code (it's much like a Pylons
"controller").

.. index::
   single: creating a project
   single: project

.. _creating_a_project:

Creating the Project
--------------------

In :ref:`installing_chapter`, you created a virtual Python environment via
the ``virtualenv`` command.  To start a :app:`Pyramid` :term:`project`, use
the ``paster`` facility installed within the virtualenv.  In
:ref:`installing_chapter` we called the virtualenv directory ``env``; the
following command assumes that our current working directory is that
directory.

We'll choose the ``pyramid_starter`` template for this purpose.

.. code-block:: text

   $ bin/paster create -t pyramid_starter

The above command uses the ``paster`` command to create a project using the
``pyramid_starter`` template.  The ``paster create`` command creates project
from a template.  To use a different template, such as
``pyramid_routesalchemy``, you'd just change the last argument.  For example:

.. code-block:: text

   $ bin/paster create -t pyramid_routesalchemy

``paster create`` will ask you a single question: the *name* of the
project.  You should use a string without spaces and with only letters
in it.  Here's sample output from a run of ``paster create`` for a
project we name ``MyProject``:

.. code-block:: text

   $ bin/paster create -t pyramid_starter
   Selected and implied templates:
     pyramid#pyramid_starter  pyramid starter project

   Enter project name: MyProject
   Variables:
     egg:      MyProject
     package:  myproject
     project:  MyProject
   Creating template pyramid
   Creating directory ./MyProject
   # ... more output ...
   Running /Users/chrism/projects/pyramid/bin/python setup.py egg_info

.. note:: You can skip the interrogative question about a project
   name during ``paster create`` by adding the project name to the
   command line, e.g. ``paster create -t pyramid_starter MyProject``.

.. note:: You may encounter an error when using ``paster create`` if a
   dependent Python package is not installed. This will result in a traceback
   ending in ``pkg_resources.DistributionNotFound: <package name>``.
   Simply run ``bin/easy_install``, with the missing package name from the
   error message to work around this issue.

As a result of invoking the ``paster create`` command, a project is created
in a directory named ``MyProject``.  That directory is a :term:`project`
directory.  The ``setup.py`` file in that directory can be used to distribute
your application, or install your application for deployment or development.

A :term:`PasteDeploy` ``.ini`` file named ``development.ini`` will be created
in the project directory.  You will use this ``.ini`` file to configure a
server, to run your application, and to and debug your application.  It
sports configuration that enables an interactive debugger and settings
optimized for development.

Another :term:`PasteDeploy` ``.ini`` file named ``production.ini`` will also
be created in the project directory.  It sports configuration that disables
any interactive debugger (to prevent inappropriate access and disclosure),
and turns off a number of debugging settings.  You can use this file to put
your application into production, and you can modify it to do things like
send email when an exception occurs.

The ``MyProject`` project directory contains an additional subdirectory named
``myproject`` (note the case difference) representing a Python
:term:`package` which holds very simple :app:`Pyramid` sample code.  This is
where you'll edit your application's Python code and templates.

.. index::
   single: setup.py develop
   single: development install

Installing your Newly Created Project for Development
-----------------------------------------------------

To install a newly created project for development, you should ``cd`` to the
newly created project directory and use the Python interpreter from the
:term:`virtualenv` you created during :ref:`installing_chapter` to invoke the
command ``python setup.py develop``

The file named ``setup.py`` will be in the root of the paster-generated
project directory.  The ``python`` you're invoking should be the one that
lives in the ``bin`` directory of your virtual Python environment.  Your
terminal's current working directory *must* the the newly created project
directory.  For example:

.. code-block:: text

   $ ../bin/python setup.py develop

Elided output from a run of this command is shown below:

.. code-block:: text

   $ ../bin/python setup.py develop
   ...
   Finished processing dependencies for MyProject==0.0

This will install a :term:`distribution` representing your project into the
interpreter's library set so it can be found by ``import`` statements and by
:term:`PasteDeploy` commands such as ``paster serve`` and ``paster pshell``.

.. index::
   single: running tests
   single: tests (running)

Running The Tests For Your Application
--------------------------------------

To run unit tests for your application, you should invoke them using the
Python interpreter from the :term:`virtualenv` you created during
:ref:`installing_chapter` (the ``python`` command that lives in the ``bin``
directory of your virtualenv):

.. code-block:: text

   $ ../bin/python setup.py test -q

Here's sample output from a test run:

.. code-block:: text

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
   ..
   ----------------------------------------------------------------------
   Ran 1 test in 0.108s

   OK

.. note::

   The ``-q`` option is passed to the ``setup.py test`` command to limit the
   output to a stream of dots.  If you don't pass ``-q``, you'll see more
   verbose test result output (which normally isn't very useful).

The tests themselves are found in the ``tests.py`` module in your ``paster
create`` -generated project.  Within a project generated by the
``pyramid_starter`` template, a single sample test exists.

.. index::
   single: interactive shell
   single: IPython
   single: paster pshell

.. _interactive_shell:

The Interactive Shell
---------------------

Once you've installed your program for development using ``setup.py
develop``, you can use an interactive Python shell to examine your
:app:`Pyramid` project's :term:`resource` and :term:`view` objects from a
Python prompt.  To do so, use your virtualenv's ``paster pshell`` command.

The first argument to ``pshell`` is the path to your application's ``.ini``
file.  The second is the ``app`` section name inside the ``.ini`` file which
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

   [chrism@vitaminf shellenv]$ ../bin/paster pshell development.ini MyProject
   Python 2.4.5 (#1, Aug 29 2008, 12:27:37) 
   [GCC 4.0.1 (Apple Inc. build 5465)] on darwin
   Type "help" for more information. "root" is the Pyramid app root object,
   "registry" is the Pyramid registry object.
   >>> root
   <myproject.resources.MyResource object at 0x445270>
   >>> registry
   <Registry myproject>
   >>> registry.settings['debug_notfound']
   False
   >>> from myproject.views import my_view
   >>> from pyramid.request import Request
   >>> r = Request.blank('/')
   >>> my_view(r)
   {'project': 'myproject'}

Two names are made available to the pshell user as globals: ``root`` and
``registry``.  ``root`` is the the object returned by the default :term:`root
factory` in your application.  ``registry`` is the :term:`application
registry` object associated with your project's application (often accessed
within view code as ``request.registry``).

If you have `IPython <http://en.wikipedia.org/wiki/IPython>`_ installed in
the interpreter you use to invoke the ``paster`` command, the ``pshell``
command will use an IPython interactive shell instead of a standard Python
interpreter shell.  If you don't want this to happen, even if you have
IPython installed, you can pass the ``--disable-ipython`` flag to the
``pshell`` command to use a standard Python interpreter shell
unconditionally.

.. code-block:: text

   [chrism@vitaminf shellenv]$ ../bin/paster pshell --disable-ipython \
                                development.ini MyProject

You should always use a section name argument that refers to the actual
``app`` section within the Paste configuration file that points at your
:app:`Pyramid` application *without any middleware wrapping*.  In particular,
a section name is inappropriate as the second argument to ``pshell`` if the
configuration section it names is a ``pipeline`` rather than an ``app``.  For
example, if you have the following ``.ini`` file content:

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
development.ini MyProject``).  If you use ``main`` instead, an error will
occur.  Use the most specific reference to your application within the
``.ini`` file possible as the section name argument.

Press ``Ctrl-D`` to exit the interactive shell (or ``Ctrl-Z`` on Windows).

.. index::
   single: running an application
   single: paster serve
   single: reload
   single: startup
   single: mod_wsgi

Running The Project Application
-------------------------------

Once a project is installed for development, you can run the application it
represents using the ``paster serve`` command against the generated
configuration file.  In our case, this file is named ``development.ini``:

.. code-block:: text

   $ ../bin/paster serve development.ini

Here's sample output from a run of ``paster serve``:

.. code-block:: text

   $ ../bin/paster serve development.ini
   Starting server in PID 16601.
   serving on 0.0.0.0:6543 view at http://127.0.0.1:6543

By default, :app:`Pyramid` applications generated from a ``paster`` template
will listen on TCP port 6543.  You can shut down a server started this way by
pressing ``Ctrl-C``.

During development, it's often useful to run ``paster serve`` using its
``--reload`` option.  When ``--reload`` is passed to ``paster serve``,
changes to any Python module your project uses will cause the server to
restart.  This typically makes development easier, as changes to Python code
made within a :app:`Pyramid` application is not put into effect until the
server restarts.

For example:

.. code-block:: text

   $ ../bin/paster serve development.ini --reload
   Starting subprocess with file monitor
   Starting server in PID 16601.
   serving on 0.0.0.0:6543 view at http://127.0.0.1:6543

For more detailed information about the startup process, see
:ref:`startup_chapter`.  For more information about environment variables and
configuration file settings that influence startup and runtime behavior, see
:ref:`environment_chapter`.

Viewing the Application
-----------------------

Once your application is running via ``paster serve``, you may visit
``http://localhost:6543/`` in your browser.  You will see something in your
browser like what is displayed in the following image:

.. image:: project.png

This is the page shown by default when you visit an unmodified ``paster
create`` -generated ``pyramid_starter`` application in a browser.

.. sidebar:: Using an Alternate WSGI Server

   The code generated by :app:`Pyramid` ``paster`` templates assumes that you
   will be using the ``paster serve`` command to start your application while
   you do development.  However, ``paster serve`` is by no means the only way
   to start up and serve a :app:`Pyramid` application.  As we saw in
   :ref:`firstapp_chapter`, ``paster serve`` needn't be invoked at all to run
   a :app:`Pyramid` application.  The use of ``paster serve`` to run a
   :app:`Pyramid` application is purely conventional based on the output of
   its ``paster`` templates.

   Any :term:`WSGI` server is capable of running a :app:`Pyramid`
   application.  Some WSGI servers don't require the :term:`PasteDeploy`
   framework's ``paster serve`` command to do server process management at
   all.  Each :term:`WSGI` server has its own documentation about how it
   creates a process to run an application, and there are many of them, so we
   cannot provide the details for each here.  But the concepts are largely
   the same, whatever server you happen to use.

   One popular production alternative to a ``paster``-invoked server is
   :term:`mod_wsgi`. You can also use :term:`mod_wsgi` to serve your
   :app:`Pyramid` application using the Apache web server rather than any
   "pure-Python" server that is started as a result of ``paster serve``.  See
   :ref:`modwsgi_tutorial` for details.  However, it is usually easier to
   *develop* an application using a ``paster serve`` -invoked webserver, as
   exception and debugging output will be sent to the console.

.. index::
   single: project structure

The Project Structure
---------------------

The ``pyramid_starter`` template generated a :term:`project` (named
``MyProject``), which contains a Python :term:`package`.  The package is
*also* named ``myproject``, but it's lowercased; the paster template
generates a project which contains a package that shares its name except for
case.

All :app:`Pyramid` ``paster`` -generated projects share a similar structure.
The ``MyProject`` project we've generated has the following directory
structure:

.. code-block:: text

  MyProject/
  |-- CHANGES.txt
  |-- development.ini
  |-- MANIFEST.in
  |-- myproject
  |   |-- __init__.py
  |   |-- resources.py
  |   |-- static
  |   |   |-- favicon.ico
  |   |   |-- logo.png
  |   |   `-- pylons.css
  |   |-- templates
  |   |   `-- mytemplate.pt
  |   |-- tests.py
  |   `-- views.py
  |-- production.ini
  |-- README.txt
  |-- setup.cfg
  `-- setup.py

The ``MyProject`` :term:`Project`
---------------------------------

The ``MyProject`` :term:`project` directory is the distribution and
deployment wrapper for your application.  It contains both the ``myproject``
:term:`package` representing your application as well as files used to
describe, run, and test your application.

#. ``CHANGES.txt`` describes the changes you've made to the application.  It
   is conventionally written in :term:`ReStructuredText` format.

#. ``README.txt`` describes the application in general.  It is conventionally
   written in :term:`ReStructuredText` format.

#. ``development.ini`` is a :term:`PasteDeploy` configuration file that can
   be used to execute your application during development.

#. ``production.ini`` is a :term:`PasteDeploy` configuration file that can
   be used to execute your application in a production configuration.

#. ``setup.cfg`` is a :term:`setuptools` configuration file used by
   ``setup.py``.

#. ``MANIFEST.in`` is a :term:`distutils` "manifest" file, naming which files
   should be included in a source distribution of the package when ``python
   setup.py sdist`` is run.

#. ``setup.py`` is the file you'll use to test and distribute your
   application.  It is a standard :term:`setuptools` ``setup.py`` file.

.. index::
   single: PasteDeploy
   single: ini file

.. _MyProject_ini:

``development.ini``
~~~~~~~~~~~~~~~~~~~

The ``development.ini`` file is a :term:`PasteDeploy` configuration file.
Its purpose is to specify an application to run when you invoke ``paster
serve``, as well as the deployment settings provided to that application.

The generated ``development.ini`` file looks like so:

.. latexbroken?

.. literalinclude:: MyProject/development.ini
   :language: ini
   :linenos:

This file contains several "sections" including ``[app:MyProject]``,
``[pipeline:main]``, and ``[server:main]``.

The ``[app:MyProject]`` section represents configuration for your
application.  This section name represents the ``MyProject`` application (and
it's an ``app`` -lication, thus ``app:MyProject``)

The ``use`` setting is required in the ``[app:MyProject]`` section.  The
``use`` setting points at a :term:`setuptools` :term:`entry point` named
``MyProject`` (the ``egg:`` prefix in ``egg:MyProject`` indicates that this
is an entry point *URI* specifier, where the "scheme" is "egg").
``egg:MyProject`` is actually shorthand for a longer spelling:
``egg:MyProject#main``.  The ``#main`` part is omitted for brevity, as it is
the default.

.. sidebar::  ``setuptools`` Entry Points and PasteDeploy ``.ini`` Files

   This part of configuration can be confusing so let's try to clear things
   up a bit.  Take a look at the generated ``setup.py`` file for this
   project.  Note that the ``entry_point`` line in ``setup.py`` points at a
   string which looks a lot like an ``.ini`` file.  This string
   representation of an ``.ini`` file has a section named
   ``[paste.app_factory]``.  Within this section, there is a key named
   ``main`` (the entry point name) which has a value ``myproject:main``.  The
   *key* ``main`` is what our ``egg:MyProject#main`` value of the ``use``
   section in our config file is pointing at (although it is actually
   shortened to ``egg:MyProject`` there).  The value represents a
   :term:`dotted Python name` path, which refers to a callable in our
   ``myproject`` package's ``__init__.py`` module.  In English, this entry
   point can thus be referred to as a "Paste application factory in the
   ``MyProject`` project which has the entry point named ``main`` where the
   entry point refers to a ``main`` function in the ``mypackage`` module".
   If indeed if you open up the ``__init__.py`` module generated within the
   ``myproject`` package, you'll see a ``main`` function.  This is the
   function called by :term:`PasteDeploy` when the ``paster serve`` command
   is invoked against our application.  It accepts a global configuration
   object and *returns* an instance of our application.

The ``use`` setting is the only setting *required* in the ``[app:MyProject]``
section unless you've changed the callable referred to by the
``egg:MyProject`` entry point to accept more arguments: other settings you
add to this section are passed as keywords arguments to the callable
represented by this entry point (``main`` in our ``__init__.py`` module).
You can provide startup-time configuration parameters to your application by
adding more settings to this section.

The ``reload_templates`` setting in the ``[app:MyProject]`` section is a
:app:`Pyramid` -specific setting which is passed into the framework.  If it
exists, and its value is ``true``, :term:`Chameleon` and :term:`Mako`
template changes will not require an application restart to be detected.  See
:ref:`reload_templates_section` for more information.

.. warning:: The ``reload_templates`` option should be turned off for
   production applications, as template rendering is slowed when it is
   turned on.

The ``debug_templates`` setting in the ``[app:MyProject]`` section is a
:app:`Pyramid` -specific setting which is passed into the framework.  If it
exists, and its value is ``true``, :term:`Chameleon` template exceptions will
contained more detailed and helpful information about the error than when
this value is ``false``.  See :ref:`debug_templates_section` for more
information.

.. warning:: The ``debug_templates`` option should be turned off for
   production applications, as template rendering is slowed when it is
   turned on.

Various other settings may exist in this section having to do with debugging
or influencing runtime behavior of a :app:`Pyramid` application.  See
:ref:`environment_chapter` for more information about these settings.

``[pipeline:main]``, has the name ``main`` signifying that this is the
default 'application' (although it's actually a pipeline of middleware and an
application) run by ``paster serve`` when it is invoked against this
configuration file.  The name ``main`` is a convention used by PasteDeploy
signifying that it is the default application.

The ``[server:main]`` section of the configuration file configures a WSGI
server which listens on TCP port 6543.  It is configured to listen on all
interfaces (``0.0.0.0``).  The ``Paste#http`` server will create a new thread
for each request.

.. note::

  In general, :app:`Pyramid` applications generated from paster templates
  should be threading-aware.  It is not required that a :app:`Pyramid`
  application be nonblocking as all application code will run in its own
  thread, provided by the server you're using.

See the :term:`PasteDeploy` documentation for more information about other
types of things you can put into this ``.ini`` file, such as other
applications, :term:`middleware` and alternate :term:`WSGI` server
implementations.

.. note::

   You can add a ``[DEFAULT]`` section to your ``development.ini`` file.
   Such a section should consists of global parameters that are shared by all
   the applications, servers and :term:`middleware` defined within the
   configuration file.  The values in a ``[DEFAULT]`` section will be passed
   to your application's ``main`` function as ``global_values``.

``production.ini``
~~~~~~~~~~~~~~~~~~~

The ``development.ini`` file is a :term:`PasteDeploy` configuration file with
a purpose much like that of ``development.ini``.  However, it disables the
WebError interactive debugger, replacing it with a logger which outputs
exception messages to ``stderr`` by default.  It also turns off template
development options such that templates are not automatically reloaded when
changed, and turns off all debugging options.  You can use this file instead
of ``development.ini`` when you put your application into production.

.. index::
   single: setup.py

``setup.py``
~~~~~~~~~~~~

The ``setup.py`` file is a :term:`setuptools` setup file.  It is meant to be
run directly from the command line to perform a variety of functions, such as
testing your application, packaging, and distributing your application.

.. note::

  ``setup.py`` is the defacto standard which Python developers use to
  distribute their reusable code.  You can read more about ``setup.py`` files
  and their usage in the `Setuptools documentation
  <http://peak.telecommunity.com/DevCenter/setuptools>`_.

Our generated ``setup.py`` looks like this:

.. literalinclude:: MyProject/setup.py
   :language: python
   :linenos:

The ``setup.py`` file calls the setuptools ``setup`` function, which does
various things depending on the arguments passed to ``setup.py`` on the
command line.

Within the arguments to this function call, information about your
application is kept.  While it's beyond the scope of this documentation to
explain everything about setuptools setup files, we'll provide a whirlwind
tour of what exists in this file in this section.

Your application's name can be any string; it is specified in the ``name``
field.  The version number is specified in the ``version`` value.  A short
description is provided in the ``description`` field.  The
``long_description`` is conventionally the content of the README and CHANGES
file appended together.  The ``classifiers`` field is a list of `Trove
<http://pypi.python.org/pypi?%3Aaction=list_classifiers>`_ classifiers
describing your application.  ``author`` and ``author_email`` are text fields
which probably don't need any description.  ``url`` is a field that should
point at your application project's URL (if any).
``packages=find_packages()`` causes all packages within the project to be
found when packaging the application.  ``include_package_data`` will include
non-Python files when the application is packaged if those files are checked
into version control.  ``zip_safe`` indicates that this package is not safe
to use as a zipped egg; instead it will always unpack as a directory, which
is more convenient.  ``install_requires`` and ``tests_require`` indicate that
this package depends on the ``pyramid`` package.  ``test_suite`` points at
the package for our application, which means all tests found in the package
will be run when ``setup.py test`` is invoked.  We examined ``entry_points``
in our discussion of the ``development.ini`` file; this file defines the
``main`` entry point that represents our project's application.

Usually you only need to think about the contents of the ``setup.py`` file
when distributing your application to other people, or when versioning your
application for your own use.  For fun, you can try this command now:

.. code-block:: text

   $ python setup.py sdist

This will create a tarball of your application in a ``dist`` subdirectory
named ``MyProject-0.1.tar.gz``.  You can send this tarball to other people
who want to use your application.

.. warning::

   Without the presence of a ``MANIFEST.in`` file or without checking your
   source code into a version control repository, ``setup.py sdist`` places
   only *Python source files* (files ending with a ``.py`` extension) into
   tarballs generated by ``python setup.py sdist``.  This means, for example,
   if your project was not checked into a setuptools-compatible source
   control system, and your project directory didn't contain a ``MANIFEST.in``
   file that told the ``sdist`` machinery to include ``*.pt`` files, the
   ``myproject/templates/mytemplate.pt`` file would not be included in the
   generated tarball.

   Projects generated by Pyramid paster templates include a default
   ``MANIFEST.in`` file.  The ``MANIFEST.in`` file contains declarations
   which tell it to include files like ``*.pt``, ``*.css`` and ``*.js`` in
   the generated tarball.  If you include files with extensions other than
   the files named in the project's ``MANIFEST.in`` and you don't make use of
   a setuptools-compatible version control system, you'll need to edit the
   ``MANIFEST.in`` file and include the statements necessary to include your
   new files.  See http://docs.python.org/distutils/sourcedist.html#principle
   for more information about how to do this.

   You can also delete ``MANIFEST.in`` from your project and rely on a
   setuptools feature which simply causes all files checked into a version
   control system to be put into the generated tarball.  To allow this to
   happen, check all the files that you'd like to be distributed along with
   your application's Python files into Subversion.  After you do this, when
   you rerun ``setup.py sdist``, all files checked into the version control
   system will be included in the tarball.  If you don't use Subversion, and
   instead use a different version control system, you may need to install a
   setuptools add-on such as ``setuptools-git`` or ``setuptools-hg`` for this
   behavior to work properly.

``setup.cfg``
~~~~~~~~~~~~~

The ``setup.cfg`` file is a :term:`setuptools` configuration file.  It
contains various settings related to testing and internationalization:

Our generated ``setup.cfg`` looks like this:

.. literalinclude:: MyProject/setup.cfg
   :language: guess
   :linenos:

The values in the default setup file allow various commonly-used
internationalization commands and testing commands to work more smoothly.

.. index::
   single: package

The ``myproject`` :term:`Package`
---------------------------------

The ``myproject`` :term:`package` lives inside the ``MyProject``
:term:`project`.  It contains:

#. An ``__init__.py`` file signifies that this is a Python :term:`package`.
   It also contains code that helps users run the application, including a
   ``main`` function which is used as a Paste entry point.

#. A ``resources.py`` module, which contains :term:`resource` code.

#. A ``templates`` directory, which contains :term:`Chameleon` (or
   other types of) templates.

#. A ``tests.py`` module, which contains unit test code for the
   application.

#. A ``views.py`` module, which contains view code for the
   application.

These are purely conventions established by the ``paster`` template:
:app:`Pyramid` doesn't insist that you name things in any particular way.
However, it's generally a good idea to follow Pyramid standards for naming,
so that other Pyramid developers can get up to speed quickly on your code
when you need help.

.. index::
   single: __init__.py

``__init__.py``
~~~~~~~~~~~~~~~

We need a small Python module that configures our application and which
advertises an entry point for use by our :term:`PasteDeploy` ``.ini`` file.
This is the file named ``__init__.py``.  The presence of an ``__init__.py``
also informs Python that the directory which contains it is a *package*.

.. literalinclude:: MyProject/myproject/__init__.py
   :language: python
   :linenos:

#. Line 1 imports the :term:`Configurator` class from :mod:`pyramid.config`
   that we use later.

#. Line 2 imports the ``Root`` class from :mod:`myproject.resources` that we
   use later.

#. Lines 4-12 define a function that returns a :app:`Pyramid` WSGI
   application.  This function is meant to be called by the
   :term:`PasteDeploy` framework as a result of running ``paster serve``.

   Within this function, application configuration is performed.

   Lines 8-10 register a "default view" (a view that has no ``name``
   attribute).  It is registered so that it will be found when the
   :term:`context` of the request is an instance of the
   :class:`myproject.resources.Root` class.  The first argument to
   ``add_view`` points at a Python function that does all the work for this
   view, also known as a :term:`view callable`, via a :term:`dotted Python
   name`.  The view declaration also names a ``renderer``, which in this case
   is a template that will be used to render the result of the view callable.
   This particular view declaration points at
   ``myproject:templates/mytemplate.pt``, which is a :term:`asset
   specification` that specifies the ``mytemplate.pt`` file within the
   ``templates`` directory of the ``myproject`` package.  The template file
   it actually points to is a :term:`Chameleon` ZPT template file.

   Line 11 registers a static view, which will serve up the files from the
   ``mypackage:static`` :term:`asset specification` (the ``static``
   directory of the ``mypackage`` package).

   Line 12 returns a :term:`WSGI` application to the caller of the function
   (Paste).

``views.py``
~~~~~~~~~~~~

Much of the heavy lifting in a :app:`Pyramid` application is done by *view
callables*.  A :term:`view callable` is the main tool of a :app:`Pyramid` web
application developer; it is a bit of code which accepts a :term:`request`
and which returns a :term:`response`.

.. literalinclude:: MyProject/myproject/views.py
   :language: python
   :linenos:

This bit of code was registered as the view callable within ``__init__.py``
(via ``add_view``).  ``add_view`` said that the default URL for instances
that are of the class :class:`myproject.resources.Root` should run this
:func:`myproject.views.my_view` function.

This view callable function is handed a single piece of information: the
:term:`request`.  The *request* is an instance of the :term:`WebOb`
``Request`` class representing the browser's request to our server.

This view returns a dictionary.  When this view is invoked, a
:term:`renderer` converts the dictionary returned by the view into HTML, and
returns the result as the :term:`response`.  This view is configured to
invoke a renderer which uses a :term:`Chameleon` ZPT template
(``mypackage:templates/my_template.pt``, as specified in the ``__init__.py``
file call to ``add_view``).

See :ref:`views_which_use_a_renderer` for more information about how views,
renderers, and templates relate and cooperate.

.. note:: Because our ``development.ini`` has a ``reload_templates =
   true`` directive indicating that templates should be reloaded when
   they change, you won't need to restart the application server to
   see changes you make to templates.  During development, this is
   handy.  If this directive had been ``false`` (or if the directive
   did not exist), you would need to restart the application server
   for each template change.  For production applications, you should
   set your project's ``reload_templates`` to ``false`` to increase
   the speed at which templates may be rendered.

.. index::
   single: resources.py

.. _resourcespy_project_section:

``resources.py``
~~~~~~~~~~~~~~~~

The ``resources.py`` module provides the :term:`resource` data and behavior
for our application.  Resources are objects which exist to provide site
structure in applications which use :term:`traversal` to map URLs to code.
We write a class named ``Root`` that provides the behavior for the root
resource.

.. literalinclude:: MyProject/myproject/resources.py
   :language: python
   :linenos:

#. Lines 1-3 define the Root class.  The Root class is a "root resource
   factory" function that will be called by the :app:`Pyramid` *Router* for
   each request when it wants to find the root of the resource tree.

In a "real" application, the Root object would likely not be such a simple
object.  Instead, it might be an object that could access some persistent
data store, such as a database.  :app:`Pyramid` doesn't make any assumption
about which sort of data storage you'll want to use, so the sample
application uses an instance of :class:`myproject.resources.Root` to
represent the root.

``static``
~~~~~~~~~~

This directory contains static assets which support the ``mytemplate.pt``
template.  It includes CSS and images.

``templates/mytemplate.pt``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The single :term:`Chameleon` template exists in the project.  Its contents
are too long to show here, but it displays a default page when rendered.  It
is referenced by the call to ``add_view`` as the ``renderer`` attribute in
the ``__init__`` file.  See :ref:`views_which_use_a_renderer` for more
information about renderers.

Templates are accessed and used by view configurations and sometimes by view
functions themselves.  See :ref:`templates_used_directly` and
:ref:`templates_used_as_renderers`.

.. index::
   single: tests.py

``tests.py``
~~~~~~~~~~~~

The ``tests.py`` module includes unit tests for your application.

.. literalinclude:: MyProject/myproject/tests.py
   :language: python
   :linenos:

This sample ``tests.py`` file has a single unit test defined within it.  This
test is executed when you run ``python setup.py test``.  You may add more
tests here as you build your application.  You are not required to write
tests to use :app:`Pyramid`, this file is simply provided as convenience and
example.

See :ref:`testing_chapter` for more information about writing :app:`Pyramid`
unit tests.

.. _modifying_package_structure:

Modifying Package Structure
----------------------------

It is best practice for your application's code layout to not stray too much
from accepted Pyramid paster template defaults.  If you refrain from changing
things very much, other Pyramid coders will be able to more quickly
understand your application.  However, the code layout choices made for you
by a paster template are in no way magical or required.  Despite the choices
made for you by any paster template, you can decide to lay your code out any
way you see fit.

For example, the configuration method named
:meth:`~pyramid.config.Configurator.add_view` requires you to pass a
:term:`dotted Python name` or a direct object reference as the class or
function to be used as a view.  By default, the ``pyramid_starter`` paster
template would have you add view functions to the ``views.py`` module in your
package.  However, you might be more comfortable creating a ``views``
*directory*, and adding a single file for each view.

If your project package name was ``myproject`` and you wanted to arrange all
your views in a Python subpackage within the ``myproject`` :term:`package`
named ``views`` instead of within a single ``views.py`` file, you might:

- Create a ``views`` directory inside your ``mypackage`` package directory
  (the same directory which holds ``views.py``).

- *Move* the existing ``views.py`` file to a file inside the new ``views``
  directory named, say, ``blog.py``.

- Create a file within the new ``views`` directory named ``__init__.py`` (it
  can be empty, this just tells Python that the ``views`` directory is a
  *package*.

Then change the __init__.py of your myproject project (*not* the
``__init__.py`` you just created in the ``views`` directory, the one in its
parent directory).  For example, from something like:

.. code-block:: python
    :linenos:

    config.add_view('myproject.views.my_view',
                    renderer='myproject:templates/mytemplate.pt')

To this:

.. code-block:: python
    :linenos:

    config.add_view('myproject.views.blog.my_view',
                    renderer='myproject:templates/mytemplate.pt')

You can then continue to add files to the ``views`` directory, and refer to
view classes or functions within those files via the dotted name passed as
the first argument to ``add_view``.  For example, if you added a file named
``anothermodule.py`` to the ``views`` subdirectory, and added a view callable
named ``my_view`` to it:

.. code-block:: python
    :linenos:

    config.add_view('myproject.views.anothermodule.my_view',
                    renderer='myproject:templates/anothertemplate.pt')

This pattern can be used to rearrage code referred to by any Pyramid API
argument which accepts a :term:`dotted Python name` or direct object
reference.


