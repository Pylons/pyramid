.. _index:

=================================================
The pyramid Web Application Development Framework
=================================================

:app:`Pyramid` is a small, fast, down-to-earth Python web application
development framework.  It is developed as part of the `Pylons Project
<http://docs.pylonshq.com/>`_.  It is licensed under a `BSD-like license
<http://repoze.org/license.html>`_.

.. note::

   Pyramid is the latest iteration of the web framework previously known as
   :mod:`repoze.bfg`.

Front Matter
============

.. toctree::
   :maxdepth: 1

   copyright.rst
   conventions.rst

Narrative documentation
=======================

Narrative documentation in chapter form explaining how to use
:app:`Pyramid`.

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
   narr/handlers
   narr/static
   narr/webob
   narr/sessions
   narr/templates
   narr/models
   narr/security
   narr/i18n
   narr/vhosting
   narr/events
   narr/environment
   narr/unittesting
   narr/hooks
   narr/declarative
   narr/extending
   narr/resources
   narr/router
   narr/threadlocals
   narr/zca

Tutorials
=========

Detailed tutorials explaining how to use :app:`Pyramid` to build
various types of applications and how to deploy :app:`Pyramid`
applications to various platforms.

.. toctree::
   :maxdepth: 2

   tutorials/bfg/index.rst
   tutorials/wiki/index.rst
   tutorials/wiki2/index.rst
   tutorials/cmf/index.rst
   tutorials/gae/index.rst
   tutorials/modwsgi/index.rst
   tutorials/zeo/index.rst
   tutorials/catalog/index.rst

Reference Material
==================

Reference material includes API documentation and documentation of
every :app:`Pyramid` :term:`ZCML directive`.

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

`cluegun <https://github.com/Pylons/cluegun>`_ is a simple pastebin
application based on Rocky Burt's `ClueBin
<http://pypi.python.org/pypi/ClueBin/0.2.3>`_.  It demonstrates form
processing, security, and the use of :term:`ZODB` within a :mod:`repoze.bfg`
application.  It also has very simple :term:`repoze.who` integration. Check
this application out via::

  git clone git://github.com/Pylons/cluegun.git

`virginia <https://github.com/Pylons/virginia>`_ is a very simple dynamic
file rendering application.  It is willing to render structured text
documents, HTML documents, and images from a filesystem directory.  An
earlier version of this application runs the `repoze.org
<http://repoze.org>`_ website.  Check this application out via::

  git clone git://github.com/Pylons/virginia.git

`shootout <https://github.com/Pylons/shootout>`_ is an example "idea
competition" application by Carlos de la Guardia.  It demonstrates a hybrid
of :term:`URL dispatch` and :term:`traversal` and integration with
`SQLAlchemy <http://www.sqlalchemy.org/>`_ and :term:`repoze.who`.  Check
this application out of version control via::

  git clone git://github.com/Pylons/shootout.git

Older Sample Applications (repoze.bfg)
======================================

.. note::

   These applications are for an older version of :app:`Pyramid`, which was
   named :mod:`repoze.bfg`.  They won't work unmodified under Pyramid, but
   might provide useful clues.

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

The `Pylons Project web site <http://docs.pylonshq.com/>`_ is the main online
source of :app:`Pyramid` support and development information.

To report bugs, use the `issue tracker
<http://github.com/Pylons/pyramid/issues>`_.

If you've got questions that aren't answered by this documentation,
contact the `Pylons-devel maillist
<http://groups.google.com/group/pylons-devel>`_ or join the `#pylons
IRC channel <irc://irc.freenode.net/#pylons>`_.

Browse and check out tagged and trunk versions of :app:`Pyramid` via
the `Pyramid GitHub repository <http://github.com/Pylons/pyramid/>`_.
To check out the trunk via ``git``, use this command::

  git clone git@github.com:Pylons/pyramid.git

To find out how to become a contributor to :app:`Pyramid`, please see the
`contributor's section of the documentation
<http://docs.pylonshq.com/index.html#contributing>`_.

Index and Glossary
==================

* :ref:`glossary`
* :ref:`genindex`
* :ref:`search`
