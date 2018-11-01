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
  cookiecutter.
  See https://github.com/Pylons/pyramid/pull/3406

- Removed ``pyramid.interfaces.ITemplateRenderer``. This interface was
  deprecated since Pyramid 1.5 and was an interface
  used by libraries like ``pyramid_mako`` and ``pyramid_chameleon`` but
  provided no functionality within Pyramid itself.
  See https://github.com/Pylons/pyramid/pull/3409

Documentation Changes
---------------------

