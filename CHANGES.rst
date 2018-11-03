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

- Removed support for supplying a media range to the ``accept`` predicate of
  both ``pyramid.config.Configurator.add_view`` and
  ``pyramid.config.Configurator.add_route``. These options were deprecated
  in Pyramid 1.10 and WebOb 1.8 because they resulted in uncontrollable
  matching that was not compliant with the RFC.
  See https://github.com/Pylons/pyramid/pull/3411

- Removed ``pyramid.session.UnencryptedCookieSessionFactoryConfig``. This
  session factory was replaced with
  ``pyramid.session.SignedCookieSessionFactory`` in Pyramid 1.5 and has been
  deprecated since then.
  See https://github.com/Pylons/pyramid/pull/3412

- Removed ``pyramid.session.signed_serialize``, and
  ``pyramid.session.signed_deserialize``. These methods were only used by
  the now-removed ``pyramid.session.UnencryptedCookieSessionFactoryConfig``
  and were coupled to the vulnerable pickle serialization format which could
  lead to remove code execution if the secret key is compromised.
  See https://github.com/Pylons/pyramid/pull/3412

Documentation Changes
---------------------

