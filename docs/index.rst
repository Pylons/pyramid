.. _index:

===========
repoze.bfg
===========

:mod:`repoze.bfg` is a Python web application framework.  It is
inspired by :term:`Zope`, :term:`Pylons`, and :term:`Django`.  It uses
various Zope-related libraries internally to do much of its work.
:mod:`repoze.bfg` uses the WSGI protocol to handle request and
responses.

:mod:`repoze.bfg` is developed as part of the `Repoze
<http://repoze.org>`_ project by `Agendaless Consulting
<http://agendaless.com>`_ and other contributors.  It is licensed
under a `BSD-like license <http://repoze.org/license.html>`_.

"What's New" Documents
======================

.. toctree::
   :maxdepth: 2

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
   narr/scanning
   narr/project
   narr/startup
   narr/urlmapping
   narr/traversal
   narr/urldispatch
   narr/views
   narr/webob
   narr/templates
   narr/models
   narr/security
   narr/hybrid
   narr/vhosting
   narr/events
   narr/environment
   narr/unittesting
   narr/hooks
   narr/extending
   narr/resources
   narr/router
   glossary

API documentation
=================

Per-module :mod:`repoze.bfg` API documentation.

.. toctree::
   :maxdepth: 2

   api/chameleon_text
   api/chameleon_zpt
   api/configuration
   api/events
   api/exceptions
   api/location
   api/paster
   api/router
   api/scripting
   api/security
   api/settings
   api/testing
   api/threadlocal
   api/traversal
   api/url
   api/view
   api/wsgi

Tutorials
=========

ZODB + traversal Wiki tutorial, demonstrating how to build a
:term:`traversal` based application using :term:`ZODB` and
:term:`authentication`.  Good for people with prior Zope experience
(or no experience at all).

.. toctree::
   :maxdepth: 2

   tutorials/bfgwiki/index.rst

SQLAlchemy + url dispatch Wiki tutorial, demonstrating how to build a
:term:`url dispatch` based application using :term:`SQLAlchemy` and
:term:`authentication`.  Good for people with prior Pylons experience
(or no experience at all).

.. toctree::
   :maxdepth: 2

   tutorials/bfgwiki2/index.rst

:mod:`repoze.bfg` for Zope CMF Developers

.. toctree::
   :maxdepth: 2

   tutorials/cmf/index.rst

:mod:`repoze.bfg` on Google's App Engine

.. toctree::
   :maxdepth: 2

   tutorials/gae/index.rst

:mod:`repoze.bfg` under :term:`mod_wsgi`

.. toctree::
   :maxdepth: 2

   tutorials/modwsgi/index.rst

Using ZODB's :term:`ZEO` with :mod:`repoze.bfg`

.. toctree::
   :maxdepth: 2

   tutorials/zeo/index.rst

Using ZODB Sessions in :mod:`repoze.bfg`

.. toctree::
   :maxdepth: 2

   tutorials/zodbsessions/index.rst

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

