Starting a ``repoze.bfg`` Project
=================================

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
directory is a directory from which a Python setuptools *distribution*
can be created.  THe ``setup.py`` file in that directory can be used
to distribute your application, or install your application for
deployment or development. A sample PasteDeploy ``.ini`` file named
``myproject.ini`` will also be created in the project directory.  You
can use this to run your application.

The main ``myproject`` contains an additional subdirectory (also named
``myproject``) representing a Python pakckage which holds very simple
bfg sample code.  This is where you'll edit your application's Python
code and templates.

Installing your Newly Created Project for Development
-----------------------------------------------------

Using your favorite Python interpreter (using a virtualenv suggested
in order to get isolation), invoke the following command when inside
the project directory against the generated ``setup.py``::

  $ python setup.py develop
   ...
   Finished processing dependencies for myproject==0.1

This will install your application 's package into the interpreter so
it can be found and run under a webserver.

Runnning The Project Application
--------------------------------

Once the project is installed for development, you can run it using
the ``paster serve`` command against the generated ``myproject.ini``
configuration file::

  $ paster serve myproject/myproject.ini
  Starting server in PID 16601.
  serving on 0.0.0.0:5432 view at http://127.0.0.1:5432

It will listen on port 5432.  If you visit the unchanged sample
application using a browser (e.g. http://localhost:5432/), you will
see the following::

  Welcome to myproject

.. note:: During development, it's often useful to run ``paster serve``
   using its ``--reload`` option.  When any Python module your project
   uses, changes, it will restart the server, which makes development
   easier, as changes to Python code under ``repoze.bfg`` is not put
   into effect until the server restarts.

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

The tests are found in the ``tests.py`` module in your generated
project.  One sample test exists.
