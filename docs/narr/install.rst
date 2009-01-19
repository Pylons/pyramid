.. _installing_chapter:

Installing :mod:`repoze.bfg`
============================

How To Install
--------------

You will need `Python <http://python.org>`_ version 2.4 or better to
run :mod:`repoze.bfg`.  It has been tested under Python 2.4.5, Python
2.5.2 and Python 2.6.  Development of :mod:`repoze.bfg` is currently
done primarily under Python 2.4.  :mod:`repoze.bfg` does *not* run
under any version of Python before 2.4, and does *not* run under
Python 3.X.

.. warning:: To succesfully install :mod:`repoze.bfg`, you will need
   an environment capable of compiling C code.  See the documentation
   about installing, e.g. ``gcc`` for your system.  Additionally, the
   Python development libraries for your Python version will need to
   be installed and the ``lixbml2`` and ``libxslt`` development
   libraries will need to be installed.  These requirements are often
   satisfied by installing the ``python-devel``, ``libxml2-devel`` and
   ``libxslt-devel`` packages into your system.  You will also need
   :term:`setuptools` installed on within your Python system in order
   to run the ``easy_install`` command.

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

Creating a Virtualenv
---------------------

It is advisable to install :mod:`repoze.bfg` into a :term:`virtualenv`
in order to obtain isolation from any "system" packages you've got
installed in your Python version (and likewise, to prevent
:mod:`repoze.bfg` from globally installing versions of packages that
are not compatible with your system Python).

To set up a virtualenv to install :mod:`repoze.bfg` within, make sure
that the :term:`virtualenv` package is installed in your Python, then
invoke:

.. code-block:: bash
   :linenos:

   $ virtualenv --no-site-packages bfgenv
   New python executable in bfgenv/bin/python
   Installing setuptools.............done.

.. warning:: Using ``--no-site-packages`` when generating your
   virtualenv is important. This flag provides the necessary isolation
   for running the set of packages required by :mod:`repoze.bfg`.  If
   you do not specify ``--no-site-packages``, it's possible that
   :mod:`repoze.bfg` will not install properly into the virtualenv,
   or, even if it does, may not run properly, depending on the
   packages you've already got installed into your Python's "main"
   site-packages dir.

You should perform any following commands that mention a "bin"
directory from within the ``bfgenv`` virtualenv dir.

Installing :mod:`repoze.bfg` Into A Virtualenv
----------------------------------------------

After you've got your ``bfgenv`` virtualenv installed, you may install
:mod:`repoze.bfg` itself using the following commands from within the
virtualenv (``bfgenv``) directory:

.. code-block:: bash
   :linenos:

   $ bin/easy_install -i http://dist.repoze.org/lemonade/dev/simple repoze.bfg

What Gets Installed
-------------------

When you ``easy_install`` :mod:`repoze.bfg`, various Zope libraries,
WebOb, Paste, PasteScript, and PasteDeploy libraries are installed.

Additionally, as shown in the next section, PasteScript (aka *paster*)
templates will be registered that make it easy to start a new
:mod:`repoze.bfg` project.

If You Can't Install Via ``easy_install`` (Alternate Installation)
------------------------------------------------------------------

If you can't get :mod:`repoze.bfg` installed using ``easy_install``
because ``lxml`` fails to compile on your system, you can try the
`repoze.bfg buildout
<http://svn.repoze.org/buildouts/repoze.bfg/trunk/README.txt>`_.  This
installation mechanism builds known-compatible ``libxml2`` and
``libxslt`` from source and causes ``lxml`` to link against these
instead of your system packages, as version incompatibilities between
system packages and ``lxml`` versions are typically to blame for
compilation problems.

Alternatively, you can try installing ``lxml`` before installing
:mod:`repoze.bfg`, and instructing ``lxml`` to download its own copy
of ``libxml2``::

  $ STATIC_DEPS=true easy_install lxml

Once that completes, ``easy_install`` will know that ``lxml`` is
already installed.
