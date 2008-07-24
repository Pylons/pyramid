Installing :mod:`repoze.bfg`
============================

How To Install
--------------

You will need `Python <http://python.org>`_ version 2.4 or better to
run :mod:`repoze.bfg`.  Development of :mod:`repoze.bfg` is done under
Python 2.4, so is recommended.  :mod:`repoze.bfg` does *not* run under
any version of Python before 2.4, and does *not* run under Python 3.X.

You may install :mod:`repoze.bfg` into your Python environment using
the following command::

  $ easy_install -i http://dist.repoze.org/lemonade/dev/simple repoze.bfg

You will need :term:`setuptools` installed on within your Python
system in order to run the ``easy_install`` command.

It is advisable to install :mod:`repoze.bfg` into a `virtualenv
<http://pypi.python.org/pypi/virtualenv>`_ in order to obtain
isolation from any "system" packages you've got installed in your
Python version (and likewise, to prevent :mod:`repoze.bfg` from
globally installing versions of packages that are not compatible with
your system Python).

What Gets Installed
-------------------

When you ``easy_install`` repoze.bfg, various Zope libraries, WebOb,
PasteScript, PasteDeploy, PasteScript, and FormEncode libraries are
installed.

Additionally, as shown in the next section, Paster templates will ge
registered with your site packages.  These templates make starting a
new :mod:`repoze.bfg` project a breeze.
