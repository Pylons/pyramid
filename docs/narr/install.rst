.. _installing_chapter:

Installing :mod:`repoze.bfg`
============================

Before You Install
------------------

You will need `Python <http://python.org>`_ version 2.4 or better to
run :mod:`repoze.bfg`.  It has been tested under Python 2.4.5, Python
2.5.2 and Python 2.6.  Development of :mod:`repoze.bfg` is currently
done primarily under Python 2.4.  :mod:`repoze.bfg` does *not* run
under any version of Python before 2.4, and does *not* run under
Python 3.X.

.. warning:: To succesfully install :mod:`repoze.bfg`, you will need
   an environment capable of compiling C code (e.g. ``XCode Tools``
   will need to be installed if you're using MacOS X, and ``gcc`` and
   other build tools will need to be installed if you're using other
   UNIXlike systems).  See the system's documentation about installing
   this software.  Additionally, the Python development libraries for
   your Python version will need to be installed and the ``lixbml2``
   and ``libxslt`` development libraries will need to be installed.
   These requirements are often satisfied by installing the
   ``python-devel``, ``libxml2-devel`` and ``libxslt-devel`` packages
   into your system.  You will also need :term:`setuptools` installed
   on within your Python system in order to run the ``easy_install``
   command.

At the time of this writing, ``repoze.bfg`` will not install on
Windows systems unless you have development tools (e.g. *Visual C++*)
installed.

.. note:: If you'd like to help produce and maintain a version of
   :mod:`repoze.bfg` that works on Windows, we'd love to hear from
   you.  There's nothing intrinsic about :mod:`repoze.bfg` that would
   prevent it from running on Windows, but none of the current
   developers use the platform.  Please contact us via the `repoze.dev
   maillist <http://lists.repoze.org/listinfo/repoze-dev>`_ if you'd
   like to try to tackle the job of compilation and maintenance.

Installing :mod:`repoze.bfg`
----------------------------

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
even if your package manager already has a prechewed version of
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
compiles a number of dependencies.

What Gets Installed
~~~~~~~~~~~~~~~~~~~

When you ``easy_install`` :mod:`repoze.bfg`, various Zope libraries,
WebOb, Paste, PasteScript, and PasteDeploy libraries are installed.

Additionally, as shown in the next section, PasteScript (aka *paster*)
templates will be registered that make it easy to start a new
:mod:`repoze.bfg` project.

Troubleshooting
---------------

If ``lxml`` Fails to Compile During ``easy_install``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the installation of :mod:`repoze.bfg` fails due to problems
compiling ``lxml``, you should try installing ``lxml`` before
installing :mod:`repoze.bfg`.  To do so, invoke ``easy_install``,
instructing ``lxml`` to download its own copy of ``libxml2``::

  $ STATIC_DEPS=true bin/easy_install lxml

Once that completes, you can start a subsequent ``easy_install`` of
:mod:`repoze.bfg` as per the instructions above; it should then work.

If You Can't Install Via ``easy_install`` (Alternate Installation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you can't get :mod:`repoze.bfg` installed using ``easy_install``
because ``lxml`` fails to compile on your system, you can try the
`repoze.bfg buildout
<http://svn.repoze.org/buildouts/repoze.bfg/trunk/README.txt>`_.  This
installation mechanism builds known-compatible ``libxml2`` and
``libxslt`` from source and causes ``lxml`` to link against these
instead of your system packages, as version incompatibilities between
system packages and ``lxml`` versions are typically to blame for
compilation problems.



