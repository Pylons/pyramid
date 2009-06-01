============
Installation
============

For the most part, the installation process for this tutorial follows
the `Installing repoze.bfg
<http://docs.repoze.org/bfg/narr/install.html>`_ and `Creating a
repoze.bfg Project <http://docs.repoze.org/bfg/narr/project.html>`_
pages.

Preparation (with CD)
=====================

Follow the instructions within the ``INSTALL.txt`` file found on the
CD.

Preparation (without CD)
========================

If you don't possess a CDROM with the tutorial files on it, take the
following steps.  The steps are slightly different depending on
whether you're using UNIX or Windows.

Preparation (without CD), UNIX
------------------------------

#. Obtain, install, or find `Python 2.5
   <http://python.org/download/releases/2.5.4/>`_ for your system.

#. Install latest `setuptools` into the Python you
   obtained/installed/found in the step above: download `ez_setup.py
   <http://peak.telecommunity.com/dist/ez_setup.py>`_ and run it using
   the ``python`` interpreter of your Python 2.5 installation:

   .. code-block:: bash

    $ /path/to/my/Python-2.5/bin/python ez_setup.py

#. Use that Python's `bin/easy_install` to install `virtualenv`:

   .. code-block:: bash

    $ /path/to/my/Python-2.5/bin/easy_install virtualenv

#. Use that Python's virtualenv to make a workspace:

   .. code-block:: bash

     $ path/to/my/Python-25/bin/virtualenv --no-site-packages bigfntut

#. Switch to the ``bigfntut`` directory:

   .. code-block:: bash

     $ cd bigfntut

#. (Optional) Consider using ``source bin/activate`` to make your
   shell environment wired to use the virtualenv.

#. Use ``easy_install`` and point to the BFG "current" index to get
   BFG and its direct dependencies installed:

   .. code-block:: bash

     $ bin/easy_install -i http://dist.repoze.org/bfg/current/simple repoze.bfg

#. Use ``easy_install`` to install ``docutils``, ``repoze.tm``,
   ``repoze.zodbconn``, ``repoze.who``, ``nose`` and ``coverage`` from
   a *different* index (the "lemonade" index).

   .. code-block:: bash

     $ bin/easy_install -i http://dist.repoze.org/lemonade/dev/simple \
        docutils repoze.tm repoze.zodbconn repoze.who nose coverage

Preparation (without CD), Windows
---------------------------------

#. Install, or find `Python 2.5
   <http://python.org/download/releases/2.5.4/>`_ for your system.

#. Install latest `setuptools` into the Python you
   obtained/installed/found in the step above: download `ez_setup.py
   <http://peak.telecommunity.com/dist/ez_setup.py>`_ and run it using
   the ``python`` interpreter of your Python 2.5 installation using a
   command prompt:

   .. code-block:: bat

    c:\> c:\Python25\python ez_setup.py

#. Use that Python's `bin/easy_install` to install `virtualenv`:

   .. code-block:: bat

    c:\> c:\Python25\Scripts\easy_install virtualenv

#. Use that Python's virtualenv to make a workspace:

   .. code-block:: bat

     c:\> c:\Python25\Scripts\virtualenv --no-site-packages bigfntut

#. Switch to the ``bigfntut`` directory:

   .. code-block:: bat

     c:\> cd bigfntut

#. (Optional) Consider using ``bin\activate.bat`` to make your shell
   environment wired to use the virtualenv.

#. Use ``easy_install`` and point to the BFG "current index to get BFG
   and its direct dependencies installed:

   .. code-block:: bat

     c:\bigfntut> Scripts/easy_install -i http://dist.repoze.org/bfg/current/simple repoze.bfg

#. Use ``easy_install`` to install ``docutils``, ``repoze.tm``,
   ``repoze.zodbconn``, ``repoze.who``, ``nose`` and ``coverage`` from
   a *different* index (the "lemonade" index).

   .. code-block:: bat

     c:\bigfntut> Scripts\easy_install -i http://dist.repoze.org/lemonade/dev/simple docutils repoze.tm repoze.zodbconn repoze.who nose coverage

.. _making_a_project:

Making a Project
================

Whether you arrived at this point by installing your own environment
using the steps above, or you used the instructions in the tutorial
disc, your next steps are to create a project.

BFG supplies a variety of templates to generate sample projects.  We
will use the :term:`ZODB` -oriented template.

The below instructions assume your current working directory is the
"virtualenv" named "bigfntut".

On UNIX:

.. code-block:: bash

  $ bin/paster create -t bfg_zodb tutorial

On Windows:

.. code-block:: bat

   c:\bigfntut> Scripts\paster create -t bfg_zodb tutorial

Installing the Project in "Development Mode"
============================================

In order to do development on the project easily, you must "register"
the project as a development egg in your workspace using the
``setup.py develop`` command.  In order to do so, cd to the "tutorial"
directory you created in :ref:`making_a_project`, and run the
"setup.py develop" command using virtualenv Python interpreter.

On UNIX:

.. code-block:: bash

  $ cd tutorial
  $ ../bin/python setup.py develop

On Windows:

.. code-block:: bat

  C:\bigfntut> cd tutorial
  C:\bigfntut\tutorial> ..\Scripts\python setup.py develop

.. _running_tests:

Running the Tests
=================

After you've installed the project in development mode, you may run
the tests for the project.

On UNIX:

.. code-block:: bash

  $ ../bin/python setup.py test -q

On Windows:

.. code-block:: bat

  c:\bigfntut\tutorial> ..\Scripts\python setup.py test -q

Starting the Application
========================

Start the application.

On UNIX:

.. code-block:: bash

  $ ../bin/paster serve tutorial.ini --reload

On Windows:

.. code-block:: bat

  c:\bifgfntut\tutorial> ..\Scripts\paster serve tutorial.ini --reload

Exposing Test Coverage Information
==================================

You can run the ``nosetests`` command to see test coverage
information.  This runs the tests in the same way that ``setup.py
test`` does but provides additional "coverage" information, exposing
which lines of your project are "covered" (or not covered) by the
tests.

On UNIX:

.. code-block:: bash

  $ ../bin/nosetests --cover-package=tutorial --cover-erase --with-coverage

On Windows:

.. code-block:: bat

  c:\bigfntut\tutorial> ..\Scripts\nosetests --cover-package=tutorial --cover-erase --with-coverage

Looks like the BFG template for ZODB projects is missing some test
coverage, particularly in the file named ``models.py``.

Visit the Application in a Browser
==================================

In a browser, visit `http://localhost:6543/ <http://localhost:6543>`_.
You will see the generated application's default page.

Decisions the ``bfg_zodb`` Template Has Made For You
=====================================================

Creating a project using the ``bfg_zodb`` template makes the
assumption that you are willing to use :term:`ZODB` as persistent
storage and :term:`traversal` to map URLs to code.  BFG supports any
persistent storage mechanism (e.g. a SQL database or filesystem files,
etc), and supports an additional mechanism to map URLs to code
(:term:`URL dispatch`).  However, for the purposes of this tutorial,
we'll be using traversal and ZODB.

