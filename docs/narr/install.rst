.. _installing_chapter:

Installing :mod:`repoze.bfg`
============================

.. index::
   pair: install; preparation

Before You Install
------------------

You will need `Python <http://python.org>`_ version 2.4 or better to
run :mod:`repoze.bfg`.  It has been tested under Python 2.4.6, Python
2.5.4 and Python 2.6.2, and Python 2.7a1.  Development of
:mod:`repoze.bfg` is currently done primarily under Python 2.4 and
Python 2.5.  :mod:`repoze.bfg` does *not* run under any version of
Python before 2.4, and does *not* run under Python 3.X.

.. sidebar:: You Don't Need A Compiler

   Installation of :mod:`repoze.bfg` does not require the compilation
   of any C code, so as long as you have a Python interpreter that
   meets the requirements mentioned, you do not need to have
   development tools installed on the target machine to install
   :mod:`repoze.bfg`.

:mod:`repoze.bfg` is known to run properly on all popular Unix-like
systems such as Linux, MacOS X, and FreeBSD.  :mod:`repoze.bfg` is
also known to run on Windows systems.  However, none of its developers
use Windows as a primary development platform.  It is also known to
run on Google's App Engine.

.. note:: If you'd like to help us make sure :mod:`repoze.bfg` runs on
   your favorite alternate platform, we'd love to hear from you.
   Please contact us via the `repoze.dev maillist
   <http://lists.repoze.org/listinfo/repoze-dev>`_ if you'd like to
   contribute.

If You Don't Yet Have A Python Interpreter (UNIX)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your system doesn't have a Python interpreter, and you're on UNIX,
you can either install Python using your operating system's package
manager *or* you can install Python from source fairly easily on any
UNIX system that has development tools.

Package Manager Method
++++++++++++++++++++++

You can use your system's "package manager" to install Python. Every
system's package manager is slightly different, but the "flavor" of
them is usually the same.

For example, on an Ubuntu Linux system, to use the system package
manager to install a Python 2.5 interpreter, use the following
command:

.. code-block:: text

   $ sudo apt-get install python2.5-dev

Once these steps are performed, the Python interpreter will usually be
invokable via ``python2.5`` from a shell prompt.

Source Compile Method
+++++++++++++++++++++

It's useful to use a Python interpreter that *isn't* the "system"
Python interpreter to develop your software.  The authors of
:mod:`repoze.bfg` never use the system Python for development
purposes; always a self-compiled one.  Compiling Python is easy, and
often the "system" Python is compiled with options that aren't optimal
for web development.

To compile software on your UNIX system, typically you need
development tools.  Often these can be installed via the package
manager.  For example, this works to do so on an Ubuntu Linux system:

.. code-block:: text

   $ sudo apt-get install build-essential

On Mac OS X, installing XCode has much the same effect.

Once you've got development tools installed on your system, On the
same system, to install a Python 2.5 interpreter from *source*, use
the following commands:

.. code-block:: text

   [chrism@vitaminf ~]$ cd ~
   [chrism@vitaminf ~]$ mkdir tmp
   [chrism@vitaminf ~]$ mkdir opt
   [chrism@vitaminf ~]$ cd tmp
   [chrism@vitaminf tmp]$ cd tmp
   [chrism@vitaminf tmp]$ wget \
          http://python.org/ftp/python/2.5.4/Python-2.5.4.tgz
   [chrism@vitaminf tmp]$ tar xvzf Python-2.5.4.tgz
   [chrism@vitaminf tmp]$ cd Python-2.5.4
   [chrism@vitaminf Python-2.5.4]$ ./configure --prefix=$HOME/opt/Python-2.5.4
   [chrism@vitaminf Python-2.5.4]$ make; make install

Once these steps are performed, the Python interpreter will be
invokable via ``$HOME/opt/Python-2.5.4/bin/python`` from a shell
prompt.

If You Don't Yet Have A Python Interpreter (Windows)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your Windows system doesn't have a Python interpreter, you'll need
to install it by downloading a Python 2.4, 2.5 or 2.6-series
interpreter executable from `python.org's download section
<http://python.org/download/>`_ (the files labeled "Windows
Installer").  Once you've downloaded it, double click on the
executable and accept the defaults during the installation process.
You may also need to download and install the `Python for Windows
extensions <http://sourceforge.net/projects/pywin32/files/>`_.

.. index::
   pair: installing; UNIX

Installing :mod:`repoze.bfg` on a UNIX System
---------------------------------------------

It is advisable to install :mod:`repoze.bfg` into a :term:`virtualenv`
in order to obtain isolation from any "system" packages you've got
installed in your Python version (and likewise, to prevent
:mod:`repoze.bfg` from globally installing versions of packages that
are not compatible with your system Python).

To set up a virtualenv to install :mod:`repoze.bfg` within, first
ensure that :term:`setuptools` is installed.  Invoke ``import
setuptools`` within the Python interpreter you'd like to run
:mod:`repoze.bfg` under:

.. code-block:: text

   [chrism@vitaminf bfg]$ python
   Python 2.4.5 (#1, Aug 29 2008, 12:27:37) 
   [GCC 4.0.1 (Apple Inc. build 5465)] on darwin
   Type "help", "copyright", "credits" or "license" for more information.
   >>> import setuptools

If ``import setuptools`` does not raise an ``ImportError``, it means
that setuptools is already installed into your Python interpreter.  If
``import setuptools`` fails, you will need to install setuptools
manually.

If you are using a "system" Python (one installed by your OS
distributor or a 3rd-party packager such as Fink or MacPorts), you can
usually install a setuptools package using your system's package
manager.  If you cannot do this, or if you're using a self-installed
version of Python, you will need to install setuptools "by hand".
Installing setuptools "by hand" is always a reasonable thing to do,
even if your package manager already has a pre-chewed version of
setuptools for installation.

To install setuptools by hand, first download `ez_setup.py
<http://peak.telecommunity.com/dist/ez_setup.py>`_ then invoke it
using the Python interpreter you want to install setuptools into.

.. code-block:: text

   $ sudo python ez_setup.py

Once this command is invoked, setuptools should be installed on your
system.  If the command fails due to permission errors, you may need
to be the administrative user on your system to successfully invoke
the script.  To remediate this, you may need to do:

.. code-block:: text

   $ sudo python ez_setup.py

.. index::
   pair: installing; virtualenv

Installing the ``virtualenv`` Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've got setuptools installed, you should install the
:term:`virtualenv` package.  To install the :term:`virtualenv` package
into your setuptools-enabled Python interpreter, use the
``easy_install`` command.

.. code-block:: text

   $ easy_install virtualenv

This command should succeed, and tell you that the virtualenv package
is now installed.  If it fails due to permission errors, you may need
to install it as your system's administrative user.  For example:

.. code-block:: text

   $ sudo easy_install virtualenv

.. index::
   pair: creating; virtualenv

Creating the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the :term:`virtualenv` package is installed in your Python, you
can actually create a virtual environment.  To do so, invoke the
following:

.. code-block:: text

   $ virtualenv --no-site-packages bfgenv
   New python executable in bfgenv/bin/python
   Installing setuptools.............done.

.. warning:: Using ``--no-site-packages`` when generating your
   virtualenv is *very important*. This flag provides the necessary
   isolation for running the set of packages required by
   :mod:`repoze.bfg`.  If you do not specify ``--no-site-packages``,
   it's possible that :mod:`repoze.bfg` will not install properly into
   the virtualenv, or, even if it does, may not run properly,
   depending on the packages you've already got installed into your
   Python's "main" site-packages dir.

.. warning:: If you're on UNIX, *do not* use ``sudo`` to run the
   ``virtualenv`` script.  It's perfectly acceptable (and desirable)
   to create a virtualenv as a normal user.

You should perform any following commands that mention a "bin"
directory from within the ``bfgenv`` virtualenv dir.

Installing :mod:`repoze.bfg` Into the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After you've got your ``bfgenv`` virtualenv installed, you may install
:mod:`repoze.bfg` itself using the following commands from within the
virtualenv (``bfgenv``) directory:

.. code-block:: text

   $ bin/easy_install -i http://dist.repoze.org/bfg/current/simple \
         repoze.bfg

This command will take longer than the previous ones to complete, as it
downloads and installs a number of dependencies.

.. index::
   pair: installing; Windows

Installing :mod:`repoze.bfg` on a Windows System
-------------------------------------------------

#. Install, or find `Python 2.5
   <http://python.org/download/releases/2.5.4/>`_ for your system.

#. Install the `Python for Windows extensions
   <http://sourceforge.net/projects/pywin32/files/>`_.  Make sure to
   pick the right download for Python 2.5 and install it using the
   same Python installation from the previous step.

#. Install latest :term:`setuptools` distribution into the Python you
   obtained/installed/found in the step above: download `ez_setup.py
   <http://peak.telecommunity.com/dist/ez_setup.py>`_ and run it using
   the ``python`` interpreter of your Python 2.5 installation using a
   command prompt:

   .. code-block:: text

      c:\> c:\Python25\python ez_setup.py

#. Use that Python's `bin/easy_install` to install `virtualenv`:

   .. code-block:: text

      c:\> c:\Python25\Scripts\easy_install virtualenv

#. Use that Python's virtualenv to make a workspace:

   .. code-block:: text

      c:\> c:\Python25\Scripts\virtualenv --no-site-packages bfgenv

#. Switch to the ``bfgenv`` directory:

   .. code-block:: text

      c:\> cd bfgenv

#. (Optional) Consider using ``bin\activate.bat`` to make your shell
   environment wired to use the virtualenv.

#. Use ``easy_install`` and point to the :mod:`repoze.bfg` "current"
   index to get BFG and its direct dependencies installed:

   .. code-block:: text

      c:\bfgenv> Scripts\easy_install -i \
           http://dist.repoze.org/bfg/current/simple repoze.bfg

.. index::
   pair: installing; Google App Engine

Installing :mod:`repoze.bfg` on Google App Engine
-------------------------------------------------

:ref:`appengine_tutorial` documents the steps required to install a
:mod:`repoze.bfg` application on Google App Engine.

What Gets Installed
~~~~~~~~~~~~~~~~~~~

When you ``easy_install`` :mod:`repoze.bfg`, various Zope libraries,
various Chameleon libraries, WebOb, Paste, PasteScript, and
PasteDeploy libraries are installed.

Additionally, as shown in a following chapter, PasteScript (aka
*paster*) templates will be registered that make it easy to start a
new :mod:`repoze.bfg` project.
