.. _index:

========================================
The repoze.bfg Web Application Framework
========================================

:mod:`repoze.bfg` is a small, fast, down-to-earth Python web
application framework.  It is developed as part of the `Repoze
<http://repoze.org>`_ project by `Agendaless Consulting
<http://agendaless.com>`_ and other contributors.  It is licensed
under a `BSD-like license <http://repoze.org/license.html>`_.

Front Matter
============

.. toctree::
   :maxdepth: 1

   copyright.rst
   conventions.rst

"What's New" Documents
======================

.. toctree::
   :maxdepth: 2

   whatsnew-1.3
   whatsnew-1.2
   whatsnew-1.1

Narrative documentation
=======================

Narrative documentation in chapter form explaining how to use
:mod:`repoze.bfg`.

.. toctree::
   :maxdepth: 2

   narr/introduction
   narr/install
   narr/configuration
   narr/firstapp
   narr/project
   narr/startup
   narr/contextfinding
   narr/traversal
   narr/urldispatch
   narr/hybrid
   narr/views
   narr/static
   narr/webob
   narr/templates
   narr/models
   narr/security
   narr/i18n
   narr/vhosting
   narr/events
   narr/environment
   narr/unittesting
   narr/hooks
   narr/extending
   narr/resources
   narr/router
   narr/threadlocals
   narr/zca

Tutorials
=========

Detailed tutorials explaining how to use :mod:`repoze.bfg` to build
and various types of applications and how to deploy :mod:`repoze.bfg`
applications to various platforms.

.. toctree::
   :maxdepth: 2

   tutorials/bfgwiki/index.rst
   tutorials/bfgwiki2/index.rst
   tutorials/cmf/index.rst
   tutorials/gae/index.rst
   tutorials/modwsgi/index.rst
   tutorials/zeo/index.rst
   tutorials/zodbsessions/index.rst
   tutorials/catalog/index.rst

Reference Material
==================

Reference material includes API documentation and documentation of
every :mod:`repoze.bfg` :term:`ZCML directive`.

.. toctree::
   :maxdepth: 2

   api
   zcml

Detailed Change History
=======================

.. toctree::
   :maxdepth: 1

   changes

Design Documentation
====================

.. toctree::
   :maxdepth: 1

   designdefense

Sample Applications
===================

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
demonstrates a hybrid of :term:`URL dispatch` and :term:`traversal`
and integration with `SQLAlchemy <http://www.sqlalchemy.org/>`_ and
:term:`repoze.who`.  Check this application out of Subversion via::

  svn co http://svn.repoze.org/repoze.shootout/trunk repoze.shootout

`bfgsite <http://svn.repoze.org/bfgsite/trunk>`_ is the software which
runs the `bfg.repoze.org <http://bfg.repoze.org>`_ website.  It
demonstrates integration with Trac, and includes several
mini-applications such as a pastebin and tutorial engine.  Check a
buildout for this application out of Subversion via::

  svn co http://svn.repoze.org/buildouts/bfgsite/ bfgsite_buildout

`KARL <http://karlproject.org>`_ is a moderately-sized application
(roughly 70K lines of Python code) built on top of :mod:`repoze.bfg`
and other Repoze software.  It is an open source web system for
collaboration, organizational intranets, and knowledge management, It
provides facilities for wikis, calendars, manuals, searching, tagging,
commenting, and file uploads.  See the `KARL site
<http://karlproject.org>`_ for download and installation details.

Support and Development
=======================

The `BFG web site <http://bfg.repoze.org>`_ is the main online source
of :mod:`repoze.bfg` support and development information.

To report bugs, use the `bug tracker <http://bfg.repoze.org/trac>`_.

If you've got questions that aren't answered by this documentation,
contact the `Repoze-dev maillist
<http://lists.repoze.org/listinfo/repoze-dev>`_ or join the `#repoze
IRC channel <irc://irc.freenode.net/#repoze>`_.

Browse and check out tagged and trunk versions of :mod:`repoze.bfg`
via the `Repoze Subversion repository
<http://svn.repoze.org/repoze.bfg/>`_.  To check out the trunk
via Subversion, use this command::

  svn co http://svn.repoze.org/repoze.bfg/trunk repoze.bfg

To find out how to become a contributor to :mod:`repoze.bfg`, please
see the `contributor's page <http://repoze.org/contributing.html>`_.

Index and Glossary
==================

* :ref:`glossary`
* :ref:`genindex`
* :ref:`search`
