.. _installing_chapter:

Installing :mod:`repoze.bfg`
============================

Before You Install
------------------

You will need `Python <http://python.org>`_ version 2.4 or better to
run :mod:`repoze.bfg`.  It has been tested under Python 2.4.5, Python
2.5.2 and Python 2.6.  Development of :mod:`repoze.bfg` is currently
done primarily under Python 2.4 and Python 2.5.  :mod:`repoze.bfg`
does *not* run under any version of Python before 2.4, and does *not*
run under Python 3.X.

.. note:: You will need :term:`setuptools` installed
   on within your Python system in order to run the ``easy_install``
   command.

.. note:: As of version 0.8.0, installation of :mod:`repoze.bfg` does
   not require the compilation of any C code, so you do not need to
   have development tools installed on the target machine.

BFG is known to run properly on all popular (and even some
less-popular) Unix-like systems such as Linux, MacOS X, and FreeBSD.

``repoze.bfg`` runs on Windows systems.  However, none of its main
developers use the Windows platform.  Therefor, most of the
platform-specific documentation (excepting this chapter) assumes
you're using a UNIX system. If you're using a Windows system, you'll
need to transliterate command lines in the documentation to their
Windows equivalents.  :mod:`repoze.bfg` is also known to run on
Google's App Engine.

It is not known whether :mod:`repoze.bfg` will or will not run under
Jython or IronPython.

.. note:: If you'd like to help make sure :mod:`repoze.bfg` keeps
   running on your favorite alternate platform, we'd love to hear from
   you.  Please contact us via the `repoze.dev maillist
   <http://lists.repoze.org/listinfo/repoze-dev>`_ if you'd like to
   contribute.

Installing :mod:`repoze.bfg` on a UNIX System
---------------------------------------------

It is advisable to install :mod:`repoze.bfg` into a :term:`virtualenv`
in order to obtain isolation from any "system" packages you've got
installed in your Python version (and likewise, to prevent
:mod:`repoze.bfg` from globally installing versions of packages that
are not compatible with your system Python).

To set up a virtualenv to install :mod:`repoze.bfg` within, first
ensure that setuptools is installed.  Invoke ``import setuptools``
within the Python interpreter you'd like to run :mod:`repoze.bfg`
under.

.. code-block:: bash

  [chrism@vitaminf bfg]$ python
  Python 2.4.5 (#1, Aug 29 2008, 12:27:37) 
  [GCC 4.0.1 (Apple Inc. build 5465)] on darwin
  Type "help", "copyright", "credits" or "license" for more information.
  >>> import setuptools

If ``import setuptools`` does not raise an ``ImportError``, it means
that setuptools is already installed into your Python interpreter.  If
``import setuptools`` fails, you will need to install setuptools
manually.  If you are using a "system" Python (one installed by your
OS distributor or a 3rd-party packager such as Fink or MacPorts), you
can usually install a setuptools package using your system's package
manager.  If you cannot do this, or if you're using a self-installed
version of Python, you will need to install setuptools "by hand".
Installing setuptools "by hand" is always a reasonable thing to do,
even if your package manager already has a pre-chewed version of
setuptools for installation.

To install setuptools by hand, first download `ez_setup.py
<http://peak.telecommunity.com/dist/ez_setup.py>`_ then invoke it
using the Python interpreter you want to install setuptools into.

.. code-block:: bash

  $ python ez_setup.py

Once this command is invoked, setuptools should be installed on your
system.  If the command fails due to permission errors, you may need
to be the administrative user on your system to successfully invoke
the script.

Installing the ``virtualenv`` Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've got setuptools installed, you should install the
:term:`virtualenv` package.  To install the :term:`virtualenv` package
into your setuptools-enabled Python interpreter, use the
``easy_install`` command.

.. code-block:: bash

  $ easy_install virtualenv

This command should succeed, and tell you that the virtualenv package
is now installed.  If it fails due to permission errors, you may need
to install it as your system's administrative user.

Creating the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the :term:`virtualenv` package is installed in your Python, you
can actually create a virtual environment.  To do so, invoke the
following:

.. code-block:: bash
   :linenos:

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

You should perform any following commands that mention a "bin"
directory from within the ``bfgenv`` virtualenv dir.

Installing :mod:`repoze.bfg` Into the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After you've got your ``bfgenv`` virtualenv installed, you may install
:mod:`repoze.bfg` itself using the following commands from within the
virtualenv (``bfgenv``) directory:

.. code-block:: bash
   :linenos:

   $ bin/easy_install -i http://dist.repoze.org/bfg/current/simple repoze.bfg

.. warning:: Note carefully the ``-i
   http://dist.repoze.org/bfg/current/simple`` above.  It is required.
   :mod:`repoze.bfg` software is maintained in its own index;
   :mod:`repoze.bfg` cannot be installed from PyPI.

This command will take longer than the previous ones to complete, as it
downloads and installs a number of dependencies.

Installing :mod:`repoze.bfg` on a Windows System
-------------------------------------------------

#. Install, or find `Python 2.5
   <http://python.org/download/releases/2.5.4/>`_ for your system.

#. Install the `Python for Windows extensions
   <http://www.sourceforge.net/project/showfiles.php?group_id=78018>`_.

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

     c:\> c:\Python25\Scripts\virtualenv --no-site-packages bfgenv

#. Switch to the ``bfgenv`` directory:

   .. code-block:: bat

     c:\> cd bfgenv

#. (Optional) Consider using ``bin\activate.bat`` to make your shell
   environment wired to use the virtualenv.

#. Use ``easy_install`` and point to the BFG "current index to get BFG
   and its direct dependencies installed:

   .. code-block:: bat

     c:\bfgenv> Scripts\easy_install -i http://dist.repoze.org/bfg/current/simple repoze.bfg

Installing :mod:`repoze.bfg` on Google App Engine
-------------------------------------------------

:ref:`appengine_tutorial` documents the steps required to install a
:mod:`repoze.bfg` application on Google App Engine.

What Gets Installed
~~~~~~~~~~~~~~~~~~~

When you ``easy_install`` :mod:`repoze.bfg`, various Zope libraries,
various Chameleon libraries, WebOb, Paste, PasteScript, and
PasteDeploy libraries are installed.

Additionally, as shown in the next section, PasteScript (aka *paster*)
templates will be registered that make it easy to start a new
:mod:`repoze.bfg` project.



