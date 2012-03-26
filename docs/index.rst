.. _index:

=================================================
The Pyramid Web Application Development Framework
=================================================

:app:`Pyramid` is a small, fast, down-to-earth Python web application
development framework.  It is developed as part of the `Pylons Project
<http://docs.pylonsproject.org/>`_.  It is licensed under a `BSD-like license
<http://repoze.org/license.html>`_.

Here is one of the simplest :app:`Pyramid` applications you can make:

.. literalinclude:: narr/helloworld.py

When saved to ``helloworld.py``, the above application can be run via:

.. code-block:: text

   $ easy_install pyramid
   $ python helloworld.py

When you visit ``http://localhost:8080/hello/world`` in a browser, you will
see the text ``Hello, world!``.

See :ref:`firstapp_chapter` for a full explanation of how this application
works. Read the :ref:`html_narrative_documentation` to understand how
:app:`Pyramid` is designed to scale from simple applications like this to
very large web applications.

Front Matter
============

.. toctree::
   :maxdepth: 1

   copyright.rst
   conventions.rst

What's New
==========

.. toctree::
   :maxdepth: 1

   whatsnew-1.3
   whatsnew-1.2
   whatsnew-1.1
   whatsnew-1.0

.. _html_narrative_documentation:

Narrative documentation
=======================

Narrative documentation in chapter form explaining how to use
:app:`Pyramid`.

.. toctree::
   :maxdepth: 2

   narr/introduction
   narr/install
   narr/firstapp
   narr/configuration
   narr/project
   narr/startup
   narr/router
   narr/urldispatch
   narr/views
   narr/renderers
   narr/templates
   narr/viewconfig
   narr/assets
   narr/webob
   narr/sessions
   narr/events
   narr/environment
   narr/logging
   narr/paste
   narr/commandline
   narr/i18n
   narr/vhosting
   narr/testing
   narr/resources
   narr/hellotraversal
   narr/muchadoabouttraversal
   narr/traversal
   narr/security
   narr/hybrid
   narr/hooks
   narr/introspector
   narr/extending
   narr/advconfig
   narr/extconfig
   narr/scaffolding
   narr/threadlocals
   narr/zca

Tutorials
=========

Tutorials explaining how to use :app:`Pyramid` to build various types of
applications, and how to deploy :app:`Pyramid` applications to various
platforms.

.. toctree::
   :maxdepth: 2

   tutorials/wiki2/index.rst
   tutorials/wiki/index.rst
   tutorials/bfg/index.rst
   tutorials/modwsgi/index.rst

API Documentation
==================

Documentation for every :app:`Pyramid` API.

.. toctree::
   :maxdepth: 2

   api

Quick reference
===============

.. toctree::
   :maxdepth: 1

   quickref

Change History
==============

.. toctree::
   :maxdepth: 1

   changes

Design Documents
================

.. toctree::
   :maxdepth: 1

   designdefense

Sample Applications
===================

`cluegun <https://github.com/Pylons/cluegun>`_ is a simple pastebin
application based on Rocky Burt's `ClueBin
<http://pypi.python.org/pypi/ClueBin/0.2.3>`_.  It demonstrates form
processing, security, and the use of :term:`ZODB` within a :app:`Pyramid`
application.  Check this application out via:

.. code-block:: text

  git clone git://github.com/Pylons/cluegun.git

`virginia <https://github.com/Pylons/virginia>`_ is a very simple dynamic
file rendering application.  It is willing to render structured text
documents, HTML documents, and images from a filesystem directory.
It's also a good example of :term:`traversal`. An
earlier version of this application runs the `repoze.org
<http://repoze.org>`_ website.  Check this application out via:

.. code-block:: text

  git clone git://github.com/Pylons/virginia.git

`shootout <https://github.com/Pylons/shootout>`_ is an example "idea
competition" application by Carlos de la Guardia and Lukasz Fidosz.  It
demonstrates :term:`URL dispatch`, simple authentication, integration
with `SQLAlchemy <http://www.sqlalchemy.org/>`_ and ``pyramid_simpleform``.
Check this application out of version control via:

.. code-block:: text

  git clone git://github.com/Pylons/shootout.git

`KARL <http://karlproject.org>`_ is a moderately-sized application (roughly
80K lines of Python code) built on top of :app:`Pyramid`.  It is an open
source web system for collaboration, organizational intranets, and knowledge
management. It provides facilities for wikis, calendars, manuals, searching,
tagging, commenting, and file uploads.  See the `KARL site
<http://karlproject.org>`_ for download and installation details.

Support and Development
=======================

The `Pylons Project web site <http://pylonsproject.org/>`_ is the main online
source of :app:`Pyramid` support and development information.

To report bugs, use the `issue tracker
<http://github.com/Pylons/pyramid/issues>`_.

If you've got questions that aren't answered by this documentation,
contact the `Pylons-discuss maillist
<http://groups.google.com/group/pylons-discuss>`_ or join the `#pyramid
IRC channel <irc://irc.freenode.net/#pyramid>`_.

Browse and check out tagged and trunk versions of :app:`Pyramid` via
the `Pyramid GitHub repository <http://github.com/Pylons/pyramid/>`_.
To check out the trunk via ``git``, use this command:

.. code-block:: text

  git clone git@github.com:Pylons/pyramid.git

To find out how to become a contributor to :app:`Pyramid`, please see the
`contributor's section of the documentation
<http://docs.pylonsproject.org/index.html#contributing>`_.

Index and Glossary
==================

* :ref:`glossary`
* :ref:`genindex`
* :ref:`search`


.. add glossary, foreword, and latexindex in a hidden toc to avoid warnings

.. toctree::
   :hidden:

   glossary
   foreword.rst
   latexindex.rst

