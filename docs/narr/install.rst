.. _installing_chapter:

Installing :app:`Pyramid`
============================

.. index::
   single: install preparation

Before You Install
------------------

You will need `Python <http://python.org>`_ version 2.6 or better to run
:app:`Pyramid`.

.. sidebar:: Python Versions

    As of this writing, :app:`Pyramid` has been tested under Python 2.6, Python
    2.7, Python 3.2, and Python 3.3.  :app:`Pyramid` does not run under any
    version of Python before 2.6.

:app:`Pyramid` is known to run on all popular UNIX-like systems such as Linux,
Mac OS X, and FreeBSD as well as on Windows platforms.  It is also known to run
on :term:`PyPy` (1.9+).

:app:`Pyramid` installation does not require the compilation of any C code, so
you need only a Python interpreter that meets the requirements mentioned.

Some :app:`Pyramid` dependencies may attempt to build C extensions for
performance speedups. If a compiler or Python headers are unavailable the
dependency will fall back to using pure Python instead.

For Mac OS X Users
~~~~~~~~~~~~~~~~~~

From `Python.org <http://python.org/download/mac/>`_:

    Python comes pre-installed on Mac OS X, but due to Apple's release cycle,
    it's often one or even two years old. The overwhelming recommendation of
    the "MacPython" community is to upgrade your Python by downloading and
    installing a newer version from `the Python standard release page
    <http://python.org/download/releases/>`_.

It is recommended to download one of the *installer* versions, unless you
prefer to install your Python through a packgage manager (e.g., macports or
homebrew) or to build your Python from source.

Unless you have a need for a specific earlier version, it is recommended to
install the latest 2.x or 3.x version of Python.

If you use an installer for your Python, then you can skip to the section
:ref:`installing_unix`.

If You Don't Yet Have A Python Interpreter (UNIX)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your system doesn't have a Python interpreter, and you're on UNIX, you can
either install Python using your operating system's package manager *or* you
can install Python from source fairly easily on any UNIX system that has
development tools.

.. index::
   pair: install; Python (from package, UNIX)

Package Manager Method
++++++++++++++++++++++

You can use your system's "package manager" to install Python. Each package
manager is slightly different, but the "flavor" of them is usually the same.

For example, on a Debian or Ubuntu system, use the following command:

.. code-block:: text

   $ sudo apt-get install python2.7-dev

This command will install both the Python interpreter and its development
header files.  Note that the headers are required by some (optional) C
extensions in software depended upon by Pyramid, not by Pyramid itself.

Once these steps are performed, the Python interpreter will usually be
invokable via ``python2.7`` from a shell prompt.

.. index::
   pair: install; Python (from source, UNIX)

Source Compile Method
+++++++++++++++++++++

It's useful to use a Python interpreter that *isn't* the "system" Python
interpreter to develop your software.  The authors of :app:`Pyramid` tend not
to use the system Python for development purposes; always a self-compiled one. 
Compiling Python is usually easy, and often the "system" Python is compiled
with options that aren't optimal for web development. For an explanation, see
https://github.com/Pylons/pyramid/issues/747.

To compile software on your UNIX system, typically you need development tools. 
Often these can be installed via the package manager.  For example, this works
to do so on an Ubuntu Linux system:

.. code-block:: text

   $ sudo apt-get install build-essential

On Mac OS X, installing `XCode <http://developer.apple.com/tools/xcode/>`_ has
much the same effect.

Once you've got development tools installed on your system, you can install a
Python 2.7 interpreter from *source*, on the same system, using the following
commands:

.. code-block:: text

   $ cd ~
   $ mkdir tmp
   $ mkdir opt
   $ cd tmp
   $ wget http://www.python.org/ftp/python/2.7.3/Python-2.7.3.tgz
   $ tar xvzf Python-2.7.3.tgz
   $ cd Python-2.7.3
   $ ./configure --prefix=$HOME/opt/Python-2.7.3
   $ make && make install

Once these steps are performed, the Python interpreter will be invokable via
``$HOME/opt/Python-2.7.3/bin/python`` from a shell prompt.

.. index::
   pair: install; Python (from package, Windows)

If You Don't Yet Have A Python Interpreter (Windows)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your Windows system doesn't have a Python interpreter, you'll need to
install it by downloading a Python 2.7-series interpreter executable from
`python.org's download section <http://python.org/download/>`_ (the files
labeled "Windows Installer").  Once you've downloaded it, double click on the
executable and accept the defaults during the installation process. You may
also need to download and install the Python for Windows extensions.

.. warning::

   After you install Python on Windows, you may need to add the ``C:\Python27``
   directory to your environment's ``Path`` in order to make it possible to
   invoke Python from a command prompt by typing ``python``.  To do so, right
   click ``My Computer``, select ``Properties`` --> ``Advanced Tab`` -->
   ``Environment Variables`` and add that directory to the end of the ``Path``
   environment variable.

.. index::
   single: installing on UNIX

.. _installing_unix:

Installing :app:`Pyramid` on a UNIX System
---------------------------------------------

It is best practice to install :app:`Pyramid` into a "virtual" Python
environment in order to obtain isolation from any "system" packages you've got
installed in your Python version.  This can be done by using the
:term:`virtualenv` package.  Using a virtualenv will also prevent
:app:`Pyramid` from globally installing versions of packages that are not
compatible with your system Python.

To set up a virtualenv in which to install :app:`Pyramid`, first ensure that
:term:`setuptools` is installed.  To do so, invoke ``import setuptools`` within
the Python interpreter you'd like to run :app:`Pyramid` under.

The following command will not display anything if setuptools is already
installed:

.. code-block:: text

   $ python2.7 -c 'import setuptools'

Running the same command will yield the following output if setuptools is not
yet installed:

.. code-block:: text

   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
   ImportError: No module named setuptools

If ``import setuptools`` raises an :exc:`ImportError` as it does above, you
will need to install setuptools manually.

If you are using a "system" Python (one installed by your OS distributor or a
third-party packager such as Fink or MacPorts), you can usually install the
setuptools package by using your system's package manager.  If you cannot do
this, or if you're using a self-installed version of Python, you will need to
install setuptools "by hand".  Installing setuptools "by hand" is always a
reasonable thing to do, even if your package manager already has a pre-chewed
version of setuptools for installation.

Installing Setuptools
~~~~~~~~~~~~~~~~~~~~~

To install setuptools by hand under Python 2, first download `ez_setup.py
<https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py>`_ then invoke
it using the Python interpreter into which you want to install setuptools.

.. code-block:: text

   $ python ez_setup.py

Once this command is invoked, setuptools should be installed on your system. 
If the command fails due to permission errors, you may need to be the
administrative user on your system to successfully invoke the script.  To
remediate this, you may need to do:

.. code-block:: text

   $ sudo python ez_setup.py

.. index::
   pair: install; virtualenv

Installing the ``virtualenv`` Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've got setuptools installed, you should install the :term:`virtualenv`
package.  To install the :term:`virtualenv` package into your
setuptools-enabled Python interpreter, use the ``easy_install`` command.

.. warning::

   Python 3.3 includes ``pyvenv`` out of the box, which provides similar
   functionality to ``virtualenv``.  We however suggest using ``virtualenv``
   instead, which works well with Python 3.3.  This isn't a recommendation made
   for technical reasons; it's made because it's not feasible for the authors
   of this guide to explain setup using multiple virtual environment systems.
   We are aiming to not need to make the installation documentation
   Turing-complete.

   If you insist on using ``pyvenv``, you'll need to understand how to install
   software such as ``setuptools`` into the virtual environment manually, which
   this guide does not cover.

.. code-block:: text

   $ easy_install virtualenv

This command should succeed, and tell you that the virtualenv package is now
installed.  If it fails due to permission errors, you may need to install it as
your system's administrative user.  For example:

.. code-block:: text

   $ sudo easy_install virtualenv

.. index::
   single: virtualenv
   pair: Python; virtual environment

Creating the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the :term:`virtualenv` package is installed in your Python environment,
you can then create a virtual environment.  To do so, invoke the following:

.. code-block:: text

   $ export VENV=~/env
   $ virtualenv $VENV
   New python executable in /home/foo/env/bin/python
   Installing setuptools.............done.

You can either follow the use of the environment variable, ``$VENV``, or
replace it with the root directory of the :term:`virtualenv`. In that case, the
`export` command can be skipped. If you choose the former approach, ensure that
it's an absolute path.

.. warning::

   Avoid using the ``--system-site-packages`` option when creating the
   virtualenv unless you know what you are doing. For versions of virtualenv
   prior to 1.7, make sure to use the ``--no-site-packages`` option, because
   this option was formerly not the default and may produce undesirable
   results.

.. warning::

    *do not* use ``sudo`` to run the ``virtualenv`` script.  It's perfectly
    acceptable (and desirable) to create a virtualenv as a normal user.


Installing :app:`Pyramid` Into the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After you've got your virtualenv installed, you may install :app:`Pyramid`
itself using the following commands:

.. parsed-literal::
      
   $ $VENV/bin/easy_install "pyramid==\ |release|\ "

The ``easy_install`` command will take longer than the previous ones to
complete, as it downloads and installs a number of dependencies.

.. note::

   If you see any warnings and/or errors related to failing to compile the C
   extensions, in most cases you may safely ignore those errors. If you wish
   to use the C extensions, please verify that you have a functioning compiler
   and the Python header files installed.

.. index::
   single: installing on Windows

.. _installing_windows:

Installing :app:`Pyramid` on a Windows System
-------------------------------------------------

You can use Pyramid on Windows under Python 2 or 3.

#. Download and install the most recent `Python 2.7.x or 3.3.x version
   <http://www.python.org/download/>`_ for your system.

#. Download and install the `Python for Windows extensions
   <http://sourceforge.net/projects/pywin32/files/pywin32/>`_. Carefully read
   the README.txt file at the end of the list of builds, and follow its
   directions. Make sure you get the proper 32- or 64-bit build and Python
   version.

#. Install latest :term:`setuptools` distribution into the Python from step 1
   above: download `ez_setup.py
   <https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py>`_ and run
   it using the ``python`` interpreter of your Python 2.7 or 3.3 installation
   using a command prompt:

   .. code-block:: text

      # modify the command according to the python version, e.g.:
      # for Python 2.7:
      c:\> c:\Python27\python ez_setup.py
      # for Python 3.3:
      c:\> c:\Python33\python ez_setup.py

#. Install `virtualenv`:

   .. code-block:: text

      # modify the command according to the python version, e.g.:
      # for Python 2.7:
      c:\> c:\Python27\Scripts\easy_install virtualenv
      # for Python 3.3:
      c:\> c:\Python33\Scripts\easy_install virtualenv

#. Make a :term:`virtualenv` workspace:

   .. code-block:: text

      c:\> set VENV=c:\env
      # modify the command according to the python version, e.g.:
      # for Python 2.7:
      c:\> c:\Python27\Scripts\virtualenv %VENV%
      # for Python 3.3:
      c:\> c:\Python33\Scripts\virtualenv %VENV%

   You can either follow the use of the environment variable, ``%VENV%``, or
   replace it with the root directory of the :term:`virtualenv`. In that case,
   the `set` command can be skipped. If you choose the former approach, ensure
   that it's an absolute path.

#. (Optional) Consider using ``%VENV%\Scripts\activate.bat`` to make your shell
   environment wired to use the virtualenv.

#. Use ``easy_install`` to get :app:`Pyramid` and its direct dependencies
   installed:

   .. parsed-literal::
      
      c:\\env> %VENV%\\Scripts\\easy_install "pyramid==\ |release|\ "

What Gets Installed
-------------------

When you ``easy_install`` :app:`Pyramid`, various other libraries such as
WebOb, PasteDeploy, and others are installed.

Additionally, as chronicled in :ref:`project_narr`, scaffolds will be
registered, which make it easy to start a new :app:`Pyramid` project.

