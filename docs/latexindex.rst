.. _index:

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
The :mod:`repoze.bfg` Web Framework
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

:mod:`repoze.bfg` is a Python web application framework.  It is
inspired by :term:`Zope`, :term:`Pylons`, and :term:`Django`.  It uses
various Zope-related libraries internally to do much of its work.
:mod:`repoze.bfg` uses the WSGI protocol to handle request and
responses.

:mod:`repoze.bfg` is developed as part of the `Repoze
<http://repoze.org>`_ project by `Agendaless Consulting
<http://agendaless.com>`_ and other contributors.  It is licensed
under a `BSD-like license <http://repoze.org/license.html>`_.

Narrative Documentation
@@@@@@@@@@@@@@@@@@@@@@@

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
   narr/threadlocals

Tutorials
@@@@@@@@@

ZODB + traversal Wiki Tutorial
==============================

Demonstrates how to build a :term:`traversal` based application using
:term:`ZODB` and :term:`authentication`.  Good for people with prior
Zope experience (or no experience at all).

.. toctree::
   :maxdepth: 2

   tutorials/bfgwiki/index.rst

SQLAlchemy + Url Dispatch Wiki Tutorial
=======================================

Demonstrates how to build a :term:`url dispatch` based application
using :term:`SQLAlchemy` and :term:`authentication`.  Good for people
with prior Pylons experience (or no experience at all).

.. toctree::
   :maxdepth: 2

   tutorials/bfgwiki2/index.rst

:mod:`repoze.bfg` for Zope CMF Developers
=========================================

.. toctree::
   :maxdepth: 2

   tutorials/cmf/index.rst

:mod:`repoze.bfg` on Google's App Engine
========================================

.. toctree::
   :maxdepth: 2

   tutorials/gae/index.rst

:mod:`repoze.bfg` under :term:`mod_wsgi`
========================================

.. toctree::
   :maxdepth: 2

   tutorials/modwsgi/index.rst

Using ZODB's :term:`ZEO` with :mod:`repoze.bfg`
===============================================

.. toctree::
   :maxdepth: 2

   tutorials/zeo/index.rst

Using ZODB Sessions in :mod:`repoze.bfg`
========================================

.. toctree::
   :maxdepth: 2

   tutorials/zodbsessions/index.rst

API documentation
@@@@@@@@@@@@@@@@@

.. toctree::
   :maxdepth: 2

   api/authorization
   api/authentication
   api/chameleon_text
   api/chameleon_zpt
   api/configuration
   api/events
   api/exceptions
   api/interfaces
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

ZCML Directives
@@@@@@@@@@@@@@@

.. toctree::
   :maxdepth: 2

   zcml

Glossary
@@@@@@@@

.. toctree::
  :maxdepth: 1

  glossary

Index
@@@@@

* :ref:`genindex`

