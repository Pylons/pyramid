.. _installing_chapter:

Installing :app:`Pyramid`
=========================

.. note::

    This installation guide emphasizes the use of Python 3.4 and greater for
    simplicity.


.. index::
   single: install preparation

Before You Install Pyramid
--------------------------

Install Python version 3.4 or greater for your operating system, and satisfy
the :ref:`requirements-for-installing-packages`, as described in
the following sections.

.. sidebar:: Python Versions

    As of this writing, :app:`Pyramid` has been tested under Python 2.7,
    Python 3.3, Python 3.4, Python 3.5, PyPy, and PyPy3. :app:`Pyramid` does
    not run under any version of Python before 2.7.

:app:`Pyramid` is known to run on all popular UNIX-like systems such as Linux,
Mac OS X, and FreeBSD, as well as on Windows platforms.  It is also known to
run on :term:`PyPy` (1.9+).

:app:`Pyramid` installation does not require the compilation of any C code.
However, some :app:`Pyramid` dependencies may attempt to build binary
extensions from C code for performance speed ups. If a compiler or Python
headers are unavailable, the dependency will fall back to using pure Python
instead.

.. note::

   If you see any warnings or errors related to failing to compile the binary
   extensions, in most cases you may safely ignore those errors. If you wish to
   use the binary extensions, please verify that you have a functioning
   compiler and the Python header files installed for your operating system.


.. _for-mac-os-x-users:

For Mac OS X Users
~~~~~~~~~~~~~~~~~~

Python comes pre-installed on Mac OS X, but due to Apple's release cycle, it is
often out of date. Unless you have a need for a specific earlier version, it is
recommended to install the latest 3.x version of Python.

You can install the latest verion of Python for Mac OS X from the binaries on
`python.org <https://www.python.org/downloads/mac-osx/>`_.

Alternatively, you can use the `homebrew <http://brew.sh/>`_ package manager.

.. code-block:: text

   # for python 3.x
   $ brew install python3

If you use an installer for your Python, then you can skip to the section
:ref:`installing_unix`.


.. _if-you-don-t-yet-have-a-python-interpreter-unix:

If You Don't Yet Have a Python Interpreter (UNIX)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your system doesn't have a Python interpreter, and you're on UNIX, you can
either install Python using your operating system's package manager *or* you
can install Python from source fairly easily on any UNIX system that has
development tools.

.. seealso:: See the official Python documentation :ref:`Using Python on Unix
   platforms <python:using-on-unix>` for full details.


.. index::
   pair: install; Python (from package, Windows)

.. _if-you-don-t-yet-have-a-python-interpreter-windows:

If You Don't Yet Have a Python Interpreter (Windows)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your Windows system doesn't have a Python interpreter, you'll need to
install it by downloading a Python 3.x-series interpreter executable from
`python.org's download section <https://www.python.org/downloads/>`_ (the files
labeled "Windows Installer").  Once you've downloaded it, double click on the
executable and accept the defaults during the installation process. You may
also need to download and install the Python for Windows extensions.

.. seealso:: See the official Python documentation :ref:`Using Python on
   Windows <python:using-on-windows>` for full details.

.. seealso:: Download and install the `Python for Windows extensions
   <https://sourceforge.net/projects/pywin32/files/pywin32/>`_. Carefully read
   the README.txt file at the end of the list of builds, and follow its
   directions. Make sure you get the proper 32- or 64-bit build and Python
   version.

.. warning::

   After you install Python on Windows, you may need to add the ``C:\Python3x``
   directory to your environment's ``Path``, where ``x`` is the minor version
   of installed Python, in order to make it possible to invoke Python from a
   command prompt by typing ``python``. To do so, right click ``My Computer``,
   select ``Properties`` --> ``Advanced Tab`` --> ``Environment Variables`` and
   add that directory to the end of the ``Path`` environment variable.

   .. seealso:: See `Configuring Python (on Windows)
      <https://docs.python.org/3/using/windows.html#configuring-python>`_ for
      full details.


.. index::
   single: requirements for installing packages

.. _requirements-for-installing-packages:

Requirements for Installing Packages
------------------------------------

Use :term:`pip` for installing packages and ``python3 -m venv env`` for
creating a virtual environment. A virtual environment is a semi-isolated Python
environment that allows packages to be installed for use by a particular
application, rather than being installed system wide.

.. seealso:: See the Python Packaging Authority's (PyPA) documention
   `Requirements for Installing Packages
   <https://packaging.python.org/en/latest/installing/#requirements-for-installing-packages>`_
   for full details.


.. index::
   single: installing on UNIX
   single: installing on Mac OS X

.. _installing_unix:

Installing :app:`Pyramid` on a UNIX System
------------------------------------------

After installing Python as described previously in :ref:`for-mac-os-x-users` or
:ref:`if-you-don-t-yet-have-a-python-interpreter-unix`, and satisfying the
:ref:`requirements-for-installing-packages`, you can now install Pyramid.

#. Make a :term:`virtual environment` workspace:

   .. code-block:: bash

      $ export VENV=~/env
      $ python3 -m venv $VENV

   You can either follow the use of the environment variable ``$VENV``, or
   replace it with the root directory of the virtual environment. If you choose
   the former approach, ensure that ``$VENV`` is an absolute path. In the
   latter case, the ``export`` command can be skipped.

#. (Optional) Consider using ``$VENV/bin/activate`` to make your shell
   environment wired to use the virtual environment.

#. Use ``pip`` to get :app:`Pyramid` and its direct dependencies installed:

   .. parsed-literal::

      $ $VENV/bin/pip install "pyramid==\ |release|\ "


.. index::
   single: installing on Windows

.. _installing_windows:

Installing :app:`Pyramid` on a Windows System
---------------------------------------------

After installing Python as described previously in
:ref:`if-you-don-t-yet-have-a-python-interpreter-windows`, and satisfying the
:ref:`requirements-for-installing-packages`, you can now install Pyramid.

#. Make a :term:`virtual environment` workspace:

   .. code-block:: doscon

      c:\> set VENV=c:\env
      # replace "x" with your minor version of Python 3
      c:\> c:\Python3x\Scripts\python3 -m venv %VENV%

   You can either follow the use of the environment variable ``%VENV%``, or
   replace it with the root directory of the virtual environment. If you choose
   the former approach, ensure that ``%VENV%`` is an absolute path. In the
   latter case, the ``set`` command can be skipped.

#. (Optional) Consider using ``%VENV%\Scripts\activate.bat`` to make your shell
   environment wired to use the virtual environment.

#. Use ``pip`` to get :app:`Pyramid` and its direct dependencies installed:

   .. parsed-literal::

      c:\\env> %VENV%\\Scripts\\pip install "pyramid==\ |release|\ "


What Gets Installed
-------------------

When you install :app:`Pyramid`, various libraries such as WebOb, PasteDeploy,
and others are installed.

Additionally, as chronicled in :ref:`project_narr`, scaffolds will be
registered, which make it easy to start a new :app:`Pyramid` project.
