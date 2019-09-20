What's New in Pyramid 2.0
=========================

This article explains the new features in :app:`Pyramid` version 2.0 as
compared to its predecessor, :app:`Pyramid` 1.10. It also documents backwards
incompatibilities between the two versions and deprecations added to
:app:`Pyramid` 2.0, as well as software dependency changes and notable
documentation additions.

Feature Additions
-----------------

The feature additions in Pyramid 2.0 are as follows:

- Added ``allow_no_origin`` option to :meth:`pyramid.config.Configurator.set_default_csrf_options`.
  See https://github.com/Pylons/pyramid/pull/3512
