.. _index:

===========
repoze.bfg
===========

:mod:`repoze.bfg` is a Python web application framework.  It is
inspired by Zope's publisher, though it is less ambitious in scope.
It relies heavily on :term:`Zope` libraries and :term:`WSGI`.

:mod:`repoze.bfg` is developed as part of the `Repoze
<http://repoze.org>`_ project by `Agendaless Consulting
<http://agendaless.com>`_ and other contributors.  It is licensed
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
   narr/startup
   narr/urlmapping
   narr/traversal
   narr/urldispatch
   narr/views
   narr/templates
   narr/models
   narr/security
   narr/events
   changes
   glossary

Tutorials
=========

Step-by-step tutorials which demonstrate how you might use
:mod:`repoze.bfg`.

``lxmlgraph`` Tutorial

.. toctree::
   :maxdepth: 3

   tutorials/lxmlgraph/index.rst

:mod:`repoze.bfg` for Zope CMF Developers

.. toctree::
   :maxdepth: 3

   tutorials/cmf/index.rst
  

API documentation
=================

Per-module :mod:`repoze.bfg` API documentation.

.. toctree::
   :maxdepth: 2

   api/events
   api/push
   api/router
   api/security
   api/template
   api/traversal
   api/location
   api/urldispatch
   api/view
   api/wsgi

Sample Applications
===================

`repoze.wiki <http://svn.repoze.org/repoze.wiki/trunk/>`_ is a port of
the `TurboGears 20-Minute Wiki
<http://turbogears.org/2.0/docs/main/Wiki20/wiki20.html>`_.  It
demonstrates integration with `SQLAlchemy
<http://www.sqlalchemy.org/>`_, customized traversal, and form
processing.  Check this application out of Subversion via::

  svn co http://svn.repoze.org/repoze.wiki/trunk repoze.wiki

`repoze.cluegun <http://svn.repoze.org/repoze.cluegun/trunk/>`_ is a
simple pastebin application based on Rocky Burt's `ClueBin
<http://pypi.python.org/pypi/ClueBin/0.2.3>`_.  It demonstrates form
processing, security, and the use of :term:`ZODB` within a
:mod:`repoze.bfg` application.  It also has very simple
:term:`repoze.who` integration. Check this application out of
Subversion via::

  svn co http://svn.repoze.org/repoze.cluegun/trunk repoze.cluegun

`repoze.virginia <http://svn.repoze.org/repoze.virginia/trunk/>`_ is a
very simple dynamic file rendering application.  It is willing to
render structured text documents, HTML documents, and images from a
filesystem directory.  This application runs the `repoze.org
<http://repoze.org>`_ website.  Check this application out of
Subversion via::

  svn co http://svn.repoze.org/repoze.virginia/trunk repoze.virginia

`repoze.shootout <http://svn.repoze.org/repoze.shootout/trunk/>`_ is
an example "idea competition" application by Carlos de la Guardia.  It
demonstrates :term:`URL dispatch` and integration with `SQLAlchemy
<http://www.sqlalchemy.org/>`_ and :term:`repoze.who`.  Check this
application out of Subversion via::

  svn co http://svn.repoze.org/repoze.shootout/trunk repoze.shootout

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

