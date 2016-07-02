.. _wiki_installation:

============
Installation
============

Before you begin
----------------

This tutorial assumes that you have already followed the steps in
:ref:`installing_chapter`, except **do not create a virtual environment or
install Pyramid**.  Thereby you will satisfy the following requirements.

* Python interpreter is installed on your operating system
* :term:`setuptools` or :term:`distribute` is installed
* :term:`virtualenv` is installed

Create directory to contain the project
---------------------------------------

We need a workspace for our project files.

On UNIX
^^^^^^^

.. code-block:: bash

    $ mkdir ~/pyramidtut

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\> mkdir pyramidtut


Create and use a virtual Python environment
-------------------------------------------

Next let's create a virtual environment workspace for our project.  We will use
the ``VENV`` environment variable instead of the absolute path of the virtual
environment.

On UNIX
^^^^^^^

.. code-block:: bash

   $ export VENV=~/pyramidtut
   $ virtualenv $VENV
   New python executable in /home/foo/env/bin/python
   Installing setuptools.............done.

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\> set VENV=c:\pyramidtut

Each version of Python uses different paths, so you will need to adjust the
path to the command for your Python version.

Python 2.7:

.. code-block:: doscon

   c:\> c:\Python27\Scripts\virtualenv %VENV%

Python 3.2:

.. code-block:: doscon

   c:\> c:\Python32\Scripts\virtualenv %VENV%

Install Pyramid and tutorial dependencies into the virtual Python environment
-----------------------------------------------------------------------------

On UNIX
^^^^^^^

.. code-block:: bash

    $ $VENV/bin/easy_install pyramid docutils pyramid_tm pyramid_zodbconn \
            pyramid_debugtoolbar nose coverage

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\> %VENV%\Scripts\easy_install pyramid docutils pyramid_tm pyramid_zodbconn \
            pyramid_debugtoolbar nose coverage

Change Directory to Your Virtual Python Environment
---------------------------------------------------

Change directory to the ``pyramidtut`` directory.

On UNIX
^^^^^^^

.. code-block:: bash

   $ cd pyramidtut

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\> cd pyramidtut


.. _making_a_project:

Making a project
----------------

Your next step is to create a project.  For this tutorial, we will use
the :term:`scaffold` named ``zodb``, which generates an application
that uses :term:`ZODB` and :term:`traversal`.

:app:`Pyramid` supplies a variety of scaffolds to generate sample projects. We
will use ``pcreate``, a script that comes with Pyramid, to create our project
using a scaffold.

By passing ``zodb`` into the ``pcreate`` command, the script creates the files
needed to use ZODB. By passing in our application name ``tutorial``, the script
inserts that application name into all the required files.

The below instructions assume your current working directory is "pyramidtut".

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/pcreate -s zodb tutorial

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut> %VENV%\Scripts\pcreate -s zodb tutorial

.. note:: If you are using Windows, the ``zodb`` scaffold may not deal
   gracefully with installation into a location that contains spaces in the
   path. If you experience startup problems, try putting both the virtual
   environment and the project into directories that do not contain spaces in
   their paths.


.. _installing_project_in_dev_mode_zodb:

Installing the project in development mode
------------------------------------------

In order to do development on the project easily, you must "register" the
project as a development egg in your workspace using the ``setup.py develop``
command. In order to do so, change directory to the ``tutorial`` directory that
you created in :ref:`making_a_project`, and run the ``setup.py develop``
command using the virtual environment Python interpreter.

On UNIX
^^^^^^^

.. code-block:: bash

   $ cd tutorial
   $ $VENV/bin/python setup.py develop

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut> cd tutorial
   c:\pyramidtut\tutorial> %VENV%\Scripts\python setup.py develop

The console will show ``setup.py`` checking for packages and installing missing
packages. Success executing this command will show a line like the following:

.. code-block:: bash

   Finished processing dependencies for tutorial==0.0


.. _running_tests:

Run the tests
-------------

After you've installed the project in development mode as well as the testing
requirements, you may run the tests for the project.

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/python setup.py test -q

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut\tutorial> %VENV%\Scripts\python setup.py test -q

For a successful test run, you should see output that ends like this:

.. code-block:: bash

  .
  ----------------------------------------------------------------------
  Ran 1 test in 0.094s
 
  OK

Expose test coverage information
--------------------------------

You can run the ``nosetests`` command to see test coverage information. This
runs the tests in the same way that ``setup.py test`` does, but provides
additional "coverage" information, exposing which lines of your project are
"covered" (or not covered) by the tests.

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/nosetests --cover-package=tutorial --cover-erase --with-coverage

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut\tutorial> %VENV%\Scripts\nosetests --cover-package=tutorial \
       --cover-erase --with-coverage

If successful, you will see output something like this:

.. code-block:: bash

    .
    Name                 Stmts   Miss  Cover   Missing
    --------------------------------------------------
    tutorial.py             12      7    42%   7-8, 14-18
    tutorial/models.py      10      6    40%   9-14
    tutorial/views.py        4      0   100%   
    --------------------------------------------------
    TOTAL                   26     13    50%   
    ----------------------------------------------------------------------
    Ran 1 test in 0.392s

    OK

Our package doesn't quite have 100% test coverage.


.. _wiki-start-the-application:

Start the application
---------------------

Start the application.

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/pserve development.ini --reload

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut\tutorial> %VENV%\Scripts\pserve development.ini --reload

.. note::

   Your OS firewall, if any, may pop up a dialog asking for authorization
   to allow python to accept incoming network connections.

If successful, you will see something like this on your console:

.. code-block:: text

   Starting subprocess with file monitor
   Starting server in PID 95736.
   serving on http://0.0.0.0:6543

This means the server is ready to accept requests.


Visit the application in a browser
----------------------------------

In a browser, visit http://localhost:6543/. You will see the generated
application's default page.

One thing you'll notice is the "debug toolbar" icon on right hand side of the
page.  You can read more about the purpose of the icon at
:ref:`debug_toolbar`.  It allows you to get information about your
application while you develop.


Decisions the ``zodb`` scaffold has made for you
------------------------------------------------

Creating a project using the ``zodb`` scaffold makes the following
assumptions:

- You are willing to use :term:`ZODB` as persistent storage.

- You are willing to use :term:`traversal` to map URLs to code.

- You want to use pyramid_zodbconn_, pyramid_tm_, and the transaction_ packages
  to manage connections and transactions with :term:`ZODB`.

- You want to use pyramid_chameleon_ to render your templates. Different
  templating engines can be used, but we had to choose one to make this
  tutorial. See :ref:`available_template_system_bindings` for some options.

.. note::

   :app:`Pyramid` supports any persistent storage mechanism (e.g., an SQL
   database or filesystem files). It also supports an additional mechanism to
   map URLs to code (:term:`URL dispatch`). However, for the purposes of this
   tutorial, we'll only be using :term:`traversal` and :term:`ZODB`.

.. _pyramid_chameleon:
   http://docs.pylonsproject.org/projects/pyramid-chameleon/en/latest/

.. _pyramid_tm:
   http://docs.pylonsproject.org/projects/pyramid-tm/en/latest/

.. _pyramid_zodbconn:
   http://docs.pylonsproject.org/projects/pyramid-zodbconn/en/latest/

.. _transaction:
   http://zodb.readthedocs.org/en/latest/transactions.html
