.. _installing_chapter:

Installing :app:`Pyramid`
============================

.. index::
   single: install preparation

Before You Install
------------------

You will need `Python <http://python.org>`_ version 2.6 or better to
run :app:`Pyramid`.  

.. sidebar:: Python Versions

    As of this writing, :app:`Pyramid` has been tested under Python 2.6.6,
    Python 2.7.2, and Python 3.2.  :app:`Pyramid` does not run under any
    version of Python before 2.6.

:app:`Pyramid` is known to run on all popular UNIX-like systems such as
Linux, MacOS X, and FreeBSD as well as on Windows platforms.  It is also
known to run on :term:`PyPy` (1.6+).

:app:`Pyramid` installation does not require the compilation of any
C code, so you need only a Python interpreter that meets the
requirements mentioned.

If You Don't Yet Have A Python Interpreter (UNIX)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your system doesn't have a Python interpreter, and you're on UNIX,
you can either install Python using your operating system's package
manager *or* you can install Python from source fairly easily on any
UNIX system that has development tools.

.. index::
   pair: install; Python (from package, UNIX)

Package Manager Method
++++++++++++++++++++++

You can use your system's "package manager" to install Python. Every
system's package manager is slightly different, but the "flavor" of
them is usually the same.

For example, on an Ubuntu Linux system, to use the system package
manager to install a Python 2.6 interpreter, use the following
command:

.. code-block:: text

   $ sudo apt-get install python2.6-dev

Once these steps are performed, the Python interpreter will usually be
invokable via ``python2.6`` from a shell prompt.

.. index::
   pair: install; Python (from source, UNIX)

Source Compile Method
+++++++++++++++++++++

It's useful to use a Python interpreter that *isn't* the "system"
Python interpreter to develop your software.  The authors of
:app:`Pyramid` tend not to use the system Python for development
purposes; always a self-compiled one.  Compiling Python is usually
easy, and often the "system" Python is compiled with options that
aren't optimal for web development.

To compile software on your UNIX system, typically you need
development tools.  Often these can be installed via the package
manager.  For example, this works to do so on an Ubuntu Linux system:

.. code-block:: text

   $ sudo apt-get install build-essential

On Mac OS X, installing `XCode
<http://developer.apple.com/tools/xcode/>`_ has much the same effect.

Once you've got development tools installed on your system, you can
install a Python 2.6 interpreter from *source*, on the same system,
using the following commands:

.. code-block:: text

   [chrism@vitaminf ~]$ cd ~
   [chrism@vitaminf ~]$ mkdir tmp
   [chrism@vitaminf ~]$ mkdir opt
   [chrism@vitaminf ~]$ cd tmp
   [chrism@vitaminf tmp]$ wget \
          http://www.python.org/ftp/python/2.6.4/Python-2.6.4.tgz
   [chrism@vitaminf tmp]$ tar xvzf Python-2.6.4.tgz
   [chrism@vitaminf tmp]$ cd Python-2.6.4
   [chrism@vitaminf Python-2.6.4]$ ./configure \
           --prefix=$HOME/opt/Python-2.6.4
   [chrism@vitaminf Python-2.6.4]$ make; make install

Once these steps are performed, the Python interpreter will be
invokable via ``$HOME/opt/Python-2.6.4/bin/python`` from a shell
prompt.

.. index::
   pair: install; Python (from package, Windows)

If You Don't Yet Have A Python Interpreter (Windows)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your Windows system doesn't have a Python interpreter, you'll need
to install it by downloading a Python 2.6-series interpreter
executable from `python.org's download section
<http://python.org/download/>`_ (the files labeled "Windows
Installer").  Once you've downloaded it, double click on the
executable and accept the defaults during the installation process.
You may also need to download and install the `Python for Windows
extensions <http://sourceforge.net/projects/pywin32/files/>`_.

.. warning::

   After you install Python on Windows, you may need to add the
   ``C:\Python26`` directory to your environment's ``Path`` in order
   to make it possible to invoke Python from a command prompt by
   typing ``python``.  To do so, right click ``My Computer``, select
   ``Properties`` --> ``Advanced Tab`` --> ``Environment Variables``
   and add that directory to the end of the ``Path`` environment
   variable.

.. index::
   single: installing on UNIX

.. _installing_unix:

Installing :app:`Pyramid` on a UNIX System
---------------------------------------------

It is best practice to install :app:`Pyramid` into a "virtual"
Python environment in order to obtain isolation from any "system"
packages you've got installed in your Python version.  This can be
done by using the :term:`virtualenv` package.  Using a virtualenv will
also prevent :app:`Pyramid` from globally installing versions of
packages that are not compatible with your system Python.

To set up a virtualenv in which to install :app:`Pyramid`, first
ensure that :term:`setuptools` is installed.  Invoke ``import
setuptools`` within the Python interpreter you'd like to run
:app:`Pyramid` under:

.. code-block:: text

   [chrism@vitaminf pyramid]$ python
   Python 2.6.5 (r265:79063, Apr 29 2010, 00:31:32) 
   [GCC 4.4.3] on linux2
   Type "help", "copyright", "credits" or "license" for more information.
   >>> import setuptools

If running ``import setuptools`` does not raise an ``ImportError``, it
means that setuptools is already installed into your Python
interpreter.  If ``import setuptools`` fails, you will need to install
setuptools manually.  Note that above we're using a Python 2.6-series
interpreter on Mac OS X; your output may differ if you're using a
later Python version or a different platform.

If you are using a "system" Python (one installed by your OS
distributor or a 3rd-party packager such as Fink or MacPorts), you can
usually install the setuptools package by using your system's package
manager.  If you cannot do this, or if you're using a self-installed
version of Python, you will need to install setuptools "by hand".
Installing setuptools "by hand" is always a reasonable thing to do,
even if your package manager already has a pre-chewed version of
setuptools for installation.

To install setuptools by hand, first download `ez_setup.py
<http://peak.telecommunity.com/dist/ez_setup.py>`_ then invoke it
using the Python interpreter into which you want to install
setuptools.

.. code-block:: text

   $ python ez_setup.py

Once this command is invoked, setuptools should be installed on your
system.  If the command fails due to permission errors, you may need
to be the administrative user on your system to successfully invoke
the script.  To remediate this, you may need to do:

.. code-block:: text

   $ sudo python ez_setup.py

.. index::
   pair: install; virtualenv

Installing the ``virtualenv`` Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've got setuptools installed, you should install the
:term:`virtualenv` package.  To install the :term:`virtualenv` package
into your setuptools-enabled Python interpreter, use the
``easy_install`` command.

.. code-block:: text

   $ easy_install virtualenv

This command should succeed, and tell you that the virtualenv package is now
installed.  If it fails due to permission errors, you may need to install it
as your system's administrative user.  For example:

.. code-block:: text

   $ sudo easy_install virtualenv

.. index::
   single: virtualenv
   pair: Python; virtual environment

Creating the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the :term:`virtualenv` package is installed in your Python, you
can then create a virtual environment.  To do so, invoke the
following:

.. code-block:: text

   $ virtualenv --no-site-packages env
   New python executable in env/bin/python
   Installing setuptools.............done.

.. warning::

   Using ``--no-site-packages`` when generating your
   virtualenv is *very important*. This flag provides the necessary
   isolation for running the set of packages required by
   :app:`Pyramid`.  If you do not specify ``--no-site-packages``,
   it's possible that :app:`Pyramid` will not install properly into
   the virtualenv, or, even if it does, may not run properly,
   depending on the packages you've already got installed into your
   Python's "main" site-packages dir.

.. warning:: *do not* use ``sudo`` to run the
   ``virtualenv`` script.  It's perfectly acceptable (and desirable)
   to create a virtualenv as a normal user.

You should perform any following commands that mention a "bin"
directory from within the ``env`` virtualenv dir.

Installing :app:`Pyramid` Into the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After you've got your ``env`` virtualenv installed, you may install
:app:`Pyramid` itself using the following commands from within the
virtualenv (``env``) directory you created in the last step.

.. code-block:: text

   $ cd env
   $ bin/easy_install pyramid

The ``easy_install`` command will take longer than the previous ones to
complete, as it downloads and installs a number of dependencies.

.. index::
   single: installing on Windows

.. _installing_windows:

Installing :app:`Pyramid` on a Windows System
-------------------------------------------------

#. Install, or find `Python 2.6
   <http://python.org/download/releases/2.6.4/>`_ for your system.

#. Install the `Python for Windows extensions
   <http://sourceforge.net/projects/pywin32/files/>`_.  Make sure to
   pick the right download for Python 2.6 and install it using the
   same Python installation from the previous step.

#. Install latest :term:`setuptools` distribution into the Python you
   obtained/installed/found in the step above: download `ez_setup.py
   <http://peak.telecommunity.com/dist/ez_setup.py>`_ and run it using
   the ``python`` interpreter of your Python 2.6 installation using a
   command prompt:

   .. code-block:: text

      c:\> c:\Python26\python ez_setup.py

#. Use that Python's `bin/easy_install` to install `virtualenv`:

   .. code-block:: text

      c:\> c:\Python26\Scripts\easy_install virtualenv

#. Use that Python's virtualenv to make a workspace:

   .. code-block:: text

      c:\> c:\Python26\Scripts\virtualenv --no-site-packages env

#. Switch to the ``env`` directory:

   .. code-block:: text

      c:\> cd env

#. (Optional) Consider using ``Scripts\activate.bat`` to make your shell
   environment wired to use the virtualenv.

#. Use ``easy_install`` pointed at the "current" index to get
   :app:`Pyramid` and its direct dependencies installed:

   .. code-block:: text

      c:\env> Scripts\easy_install pyramid

What Gets Installed
-------------------

When you ``easy_install`` :app:`Pyramid`, various other libraries such as
WebOb, PasteDeploy, and others are installed.

Additionally, as chronicled in :ref:`project_narr`, scaffolds will be
registered, which make it easy to start a new :app:`Pyramid` project.

