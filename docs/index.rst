.. _index:

===========
repoze.bfg
===========

:mod:`repoze.bfg` is a Python web application framework.  It is
inspired by Zope's publisher, though it is less ambitious in scope.
It relies heavily on :term:`Zope` libraries and :term:`WSGI`.

:mod:`repoze.bfg` is developed as part of the `Repoze
<http://repoze.org>`_ project by `Agendaless Consulting
<http://agendaless.com>`_ and other contributors.  .  It is licensed
under a `BSD-like license <http://repoze.org/license.html>`_.

Narrative documentation
=======================

Narrative documentation in chapter form explaining how to use
:mod:`repoze.bfg`.

.. toctree::
   :maxdepth: 2

   narr/introduction
   narr/install
   narr/project
   narr/traversal
   narr/views
   narr/templates
   narr/models
   narr/security
   glossary

Tutorials
=========

Step-by-step sample applications that use :mod:`repoze.bfg`.

.. toctree::
   :maxdepth: 3

   tutorials/lxmlgraph/index.rst

API documentation
=================

Per-module :mod:`repoze.bfg` API documentation.

.. toctree::
   :maxdepth: 2

   api/push
   api/router
   api/security
   api/template
   api/traversal
   api/urldispatch
   api/wsgi

Sample Applications
===================

`repoze.cluegun <http://svn.repoze.org/repoze.cluegun/trunk/>`_ is a
simple pastebin application based on Rocky Burt's `ClueBin
<http://pypi.python.org/pypi/ClueBin/0.2.3>`_.  It demonstrates form
processing, security, and the use of *ZODB* within a :mod:`repoze.bfg`
application.  Check this application out of Subversion via::

  svn co http://svn.repoze.org/repoze.cluegun/trunk repoze.cluegun

`repoze.virginia <http://svn.repoze.org/repoze.virginia/trunk/>`_ is a
very simple dynamic file rendering application.  It is willing to
render structured text documents, HTML documents, and images from a
disk directory.  This application runs the `repoze.org
<http://repoze.org>`_ website.  Check this application out of
Subversion via::

  svn co http://svn.repoze.org/repoze.virginia/trunk repoze.virginia

Support and Development
=======================

To report bugs, use the `Repoze bug tracker <http://bugs.repoze.org>`_.

If you've got questions that aren't answered by this documentation,
contact the `Repoze-dev maillist
<http://lists.repoze.org/listinfo/repoze-dev>`_ or join the `#repoze
IRC channel <irc://irc.freenode.net/#repoze>`_.

Browse and check out tagged and trunk versions of :mod:`repoze.bfg`
via the `Repoze Subversion repository
<http://http://svn.repoze.org/repoze.bfg/>`_.  To check out the trunk
via Subversion, use this command::

  svn co http://svn.repoze.org/repoze.bfg/trunk repoze.bfg

To find out how to become a contributor to :mod:`repoze.bfg`, please
see the `contributor's page <http://repoze.org/contributing.html>`_.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`glossary`

