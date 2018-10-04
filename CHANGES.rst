unreleased
==========

Features
--------

Bug Fixes
---------

Deprecations
------------

Backward Incompatibilities
--------------------------

- ``pcreate`` and the builtin scaffolds have been removed in favor of
  using the ``cookiecutter`` tool and the ``pyramid-cookiecutter-starter``
  cookiecutter. The script and scaffolds were deprecated in Pyramid 1.8.
  See https://github.com/Pylons/pyramid/pull/3406

- Removed ``pyramid.interfaces.ITemplateRenderer``. This interface was
  deprecated since Pyramid 1.5 and was an interface
  used by libraries like ``pyramid_mako`` and ``pyramid_chameleon`` but
  provided no functionality within Pyramid itself.
  See https://github.com/Pylons/pyramid/pull/3409

- Removed ``pyramid.security.has_permission``,
  ``pyramid.security.authenticated_userid``,
  ``pyramid.security.unauthenticated_userid``, and
  ``pyramid.security.effective_principals``. These methods were deprecated
  in Pyramid 1.5 and all have equivalents available as properties on the
  request. For example, ``request.authenticated_userid``.
  See https://github.com/Pylons/pyramid/pull/3410

Documentation Changes
---------------------

