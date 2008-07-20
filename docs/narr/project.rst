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
(named ``myproject``), which contains a Python package (also named
``myproject``).

The ``myproject`` package has the following files and directories:

  1. A ``views.py`` module, which contains view code.

  2. A ``models.py`` module, which contains model code.

  3. A ``run.py`` module, which contains code that helps users run the
     application.

  4. A ``configure.zcml`` file which maps view names to model types.
     This is also known as the "application registry", although it
     also often contains non-view-related declarations.

  5. A ``templates`` directory, which is full of zc3.pt and/or XSL
     templates.

This is purely by convention: ``repoze.bfg`` doesn't insist that you
name things in any particular way.

We don't describe any security in our sample application.  Security is
optional in a repoze.bfg application; it needn't be used until
necessary.

``views.py``
------------

The code in the views.py project looks like this::

  from repoze.bfg.template import render_template_to_response

  def my_view(context, request):
      return render_template_to_response('templates/mytemplate.pt',
                                         project = 'myproject')

``models.py``
-------------

The code in the models.py looks like this::

  from zope.interface import Interface
  from zope.interface import implements

  class IMyModel(Interface):
      pass

  class MyModel(object):
      implements(IMyModel)
      pass

  root = MyModel()

  def get_root(environ):
      return root

In a "real" application, the root object would not be such a simple
object.  Instead, it would be an object that could access some
persistent data store, such as a database.  ``repoze.bfg`` doesn't
make any assumption about which sort of datastore you'll want to use,
so the sample application uses an instance of ``MyModel`` to represent
the root.

``configure.zcml``
------------------

The ``configure.zcml`` (representing the application registry) looks
like so::

  <configure xmlns="http://namespaces.zope.org/zope"
  	   xmlns:bfg="http://namespaces.repoze.org/bfg"
  	   i18n_domain="repoze.bfg">

    <!-- this must be included for the view declarations to work -->
    <include package="repoze.bfg" />

    <bfg:view
       for=".models.IMyModel"
       view=".views.my_view"
       />

  </configure>

``templates/my.pt``
-------------------

The single template in the project looks like so::

  <html xmlns="http://www.w3.org/1999/xhtml"
       xmlns:tal="http://xml.zope.org/namespaces/tal">
  <head></head>
  <body>
    <h1>Welcome to ${project}</h1>
  </body>
  </html>

``run.py``
----------

The run.py file looks like so::

  def make_app(global_config, **kw):
      # paster app config callback
      from repoze.bfg import make_app
      from myproject.models import get_root
      import myproject
      app = make_app(get_root, myproject)
      return app

  if __name__ == '__main__':
      from paste import httpserver
      app = make_app(None)
      httpserver.serve(app, host='0.0.0.0', port='5432')

