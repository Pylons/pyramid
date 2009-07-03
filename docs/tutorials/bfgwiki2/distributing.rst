=============================
Distributing Your Application
=============================

Once your application works properly, you can create a "tarball" from
it by using the ``setup.py sdist`` command.  The following commands
assume your current working directory is the ``tutorial`` package
we've created and that the parent directory of the ``tutorial``
package is a virtualenv representing a :mod:`repoze.bfg` environment.

On UNIX:

.. code-block:: bash

  $ ../bin/python setup.py sdist

On Windows:

.. code-block:: bat

   c:\bigfntut> ..\Scripts\python setup.py sdist

.. warning:: If your project files are not checked in to a version
   control repository (such as Subversion), the dist tarball will
   *not* contain all the files it needs to.  In particular, it will
   not contain non-Python-source files (such as templates and static
   files).  To ensure that these are included, check your files into a
   version control repository before running ``setup.py sdist``.

The output of such a command will be something like:

.. code-block:: bash

  running sdist
  running egg_info
  writing requirements to tutorial.egg-info/requires.txt
  writing tutorial.egg-info/PKG-INFO
  writing top-level names to tutorial.egg-info/top_level.txt
  writing dependency_links to tutorial.egg-info/dependency_links.txt
  writing entry points to tutorial.egg-info/entry_points.txt
  writing manifest file 'tutorial.egg-info/SOURCES.txt'
  warning: sdist: missing required meta-data: url
  warning: sdist: missing meta-data: either (author and author_email) or (maintainer and maintainer_email) must be supplied
  creating tutorial-0.1
  creating tutorial-0.1/tutorial
  creating tutorial-0.1/tutorial.egg-info
  creating tutorial-0.1/tutorial/templates
  creating tutorial-0.1/tutorial/templates/static
  creating tutorial-0.1/tutorial/templates/static/images
  making hard links in tutorial-0.1...
  hard linking CHANGES.txt -> tutorial-0.1
  hard linking README.txt -> tutorial-0.1
  hard linking ez_setup.py -> tutorial-0.1
  hard linking setup.cfg -> tutorial-0.1
  hard linking setup.py -> tutorial-0.1
  hard linking tutorial.ini -> tutorial-0.1
  hard linking tutorial/__init__.py -> tutorial-0.1/tutorial
  hard linking tutorial/configure.zcml -> tutorial-0.1/tutorial
  hard linking tutorial/models.py -> tutorial-0.1/tutorial
  hard linking tutorial/run.py -> tutorial-0.1/tutorial
  hard linking tutorial/tests.py -> tutorial-0.1/tutorial
  hard linking tutorial/views.py -> tutorial-0.1/tutorial
  hard linking tutorial.egg-info/PKG-INFO -> tutorial-0.1/tutorial.egg-info
  hard linking tutorial.egg-info/SOURCES.txt -> tutorial-0.1/tutorial.egg-info
  hard linking tutorial.egg-info/dependency_links.txt -> tutorial-0.1/tutorial.egg-info
  hard linking tutorial.egg-info/entry_points.txt -> tutorial-0.1/tutorial.egg-info
  hard linking tutorial.egg-info/not-zip-safe -> tutorial-0.1/tutorial.egg-info
  hard linking tutorial.egg-info/requires.txt -> tutorial-0.1/tutorial.egg-info
  hard linking tutorial.egg-info/top_level.txt -> tutorial-0.1/tutorial.egg-info
  hard linking tutorial/templates/edit.pt -> tutorial-0.1/tutorial/templates
  hard linking tutorial/templates/mytemplate.pt -> tutorial-0.1/tutorial/templates
  hard linking tutorial/templates/view.pt -> tutorial-0.1/tutorial/templates
  hard linking tutorial/templates/static/default.css -> tutorial-0.1/tutorial/templates/static
  hard linking tutorial/templates/static/style.css -> tutorial-0.1/tutorial/templates/static
  hard linking tutorial/templates/static/templatelicense.txt -> tutorial-0.1/tutorial/templates/static
  hard linking tutorial/templates/static/images/img01.gif -> tutorial-0.1/tutorial/templates/static/images
  hard linking tutorial/templates/static/images/img02.gif -> tutorial-0.1/tutorial/templates/static/images
  hard linking tutorial/templates/static/images/img03.gif -> tutorial-0.1/tutorial/templates/static/images
  hard linking tutorial/templates/static/images/img04.gif -> tutorial-0.1/tutorial/templates/static/images
  hard linking tutorial/templates/static/images/spacer.gif -> tutorial-0.1/tutorial/templates/static/images
  copying setup.cfg -> tutorial-0.1
  Writing tutorial-0.1/setup.cfg
  creating dist
  tar -cf dist/tutorial-0.1.tar tutorial-0.1
  gzip -f9 dist/tutorial-0.1.tar
  removing 'tutorial-0.1' (and everything under it)

Note that this command creates a tarball in the "dist" subdirectory
named ``tutorial-0.1.tar.gz``.  You can send this file to your friends
to show them your cool new application.  They should be able to
install it by pointing the ``easy_install`` command directly at it.
Or you can upload it to `PyPI <http://pypi.python.org>`_ and share it
with the rest of the world, where it can be downloaded via
``easy_install`` remotely like any other package people download from
PyPI.

