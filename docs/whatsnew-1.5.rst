What's New In Pyramid 1.5
=========================

This article explains the new features in :app:`Pyramid` version 1.5 as
compared to its predecessor, :app:`Pyramid` 1.4.  It also documents backwards
incompatibilities between the two versions and deprecations added to
:app:`Pyramid` 1.5, as well as software dependency changes and notable
documentation additions.

Feature Additions
-----------------

The feature additions in Pyramid 1.5 follow.

- Add ``pdistreport`` script, which prints the Python version in use, the
  Pyramid version in use, and the version number and location of all Python
  distributions currently installed.

- Add the ability to invert the result of any view, route, or subscriber
  predicate value using the ``not_`` class.  For example:

  .. code-block:: python

     from pyramid.config import not_

     @view_config(route_name='myroute', request_method=not_('POST'))
     def myview(request): ...

  The above example will ensure that the view is called if the request method
  is not POST, at least if no other view is more specific.

  The :class:`pyramid.config.not_` class can be used against any value that is
  a predicate value passed in any of these contexts:

  - :meth:`pyramid.config.Configurator.add_view`

  - :meth:`pyramid.config.Configurator.add_route`

  - :meth:`pyramid.config.Configurator.add_subscriber`

  - :meth:`pyramid.view.view_config`

  - :meth:`pyramid.events.subscriber`

- View lookup will now search for valid views based on the inheritance
  hierarchy of the context. It tries to find views based on the most specific
  context first, and upon predicate failure, will move up the inheritance chain
  to test views found by the super-type of the context.  In the past, only the
  most specific type containing views would be checked and if no matching view
  could be found then a PredicateMismatch would be raised. Now predicate
  mismatches don't hide valid views registered on super-types. Here's an
  example that now works:

  .. code-block:: python

     class IResource(Interface):

         ...

     @view_config(context=IResource)
     def get(context, request):

         ...

     @view_config(context=IResource, request_method='POST')
     def post(context, request):

         ...

     @view_config(context=IResource, request_method='DELETE')
     def delete(context, request):

         ...

     @implementer(IResource)
     class MyResource:

         ...

     @view_config(context=MyResource, request_method='POST')
     def override_post(context, request):

         ...

  Previously the override_post view registration would hide the get
  and delete views in the context of MyResource -- leading to a
  predicate mismatch error when trying to use GET or DELETE
  methods. Now the views are found and no predicate mismatch is
  raised.
  See https://github.com/Pylons/pyramid/pull/786 and
  https://github.com/Pylons/pyramid/pull/1004 and
  https://github.com/Pylons/pyramid/pull/1046

- ``scripts/prequest.py`` (aka the ``prequest`` console script): added support
  for submitting ``PUT`` and ``PATCH`` requests.  See
  https://github.com/Pylons/pyramid/pull/1033.  add support for submitting
  ``OPTIONS`` and ``PROPFIND`` requests, and allow users to specify basic
  authentication credentials in the request via a ``--login`` argument to the
  script.  See https://github.com/Pylons/pyramid/pull/1039.

- The :meth:`pyramid.config.Configurator.add_route` method now supports being
  called with an external URL as pattern. See
  https://github.com/Pylons/pyramid/issues/611 and the documentation section
  :ref:`external_route_narr`.

- :class:`pyramid.authorization.ACLAuthorizationPolicy` supports ``__acl__`` as
  a callable. This removes the ambiguity between the potential
  ``AttributeError`` that would be raised on the ``context`` when the property
  was not defined and the ``AttributeError`` that could be raised from any
  user-defined code within a dynamic property. It is recommended to define a
  dynamic ACL as a callable to avoid this ambiguity. See
  https://github.com/Pylons/pyramid/issues/735.

- Allow a protocol-relative URL (e.g. ``//example.com/images``) to be passed to
  :meth:`pyramid.config.Configurator.add_static_view`. This allows
  externally-hosted static URLs to be generated based on the current protocol.

- The :class:`pyramid.authentication.AuthTktAuthenticationPolicy` class has two
  new options to configure its domain usage:

  * ``parent_domain``: if set the authentication cookie is set on
    the parent domain. This is useful if you have multiple sites sharing the
    same domain.

  * ``domain``: if provided the cookie is always set for this domain, bypassing
    all usual logic.

  See https://github.com/Pylons/pyramid/pull/1028,
  https://github.com/Pylons/pyramid/pull/1072 and
  https://github.com/Pylons/pyramid/pull/1078.

- The :class:`pyramid.authentication.AuthTktPolicy` now supports IPv6
  addresses when using the ``include_ip=True`` option. This is possibly
  incompatible with alternative ``auth_tkt`` implementations, as the
  specification does not define how to properly handle IPv6. See
  https://github.com/Pylons/pyramid/issues/831.

- Make it possible to use variable arguments via
  :func:`pyramid.paster.get_appsettings`. This also allowed the generated
  ``initialize_db`` script from the ``alchemy`` scaffold to grow support for
  options in the form ``a=1 b=2`` so you can fill in values in a parameterized
  ``.ini`` file, e.g.  ``initialize_myapp_db etc/development.ini a=1 b=2``.
  See https://github.com/Pylons/pyramid/pull/911

- The ``request.session.check_csrf_token()`` method and the ``check_csrf`` view
  predicate now take into account the value of the HTTP header named
  ``X-CSRF-Token`` (as well as the ``csrf_token`` form parameter, which they
  always did).  The header is tried when the form parameter does not exist.

- You can now generate "hybrid" urldispatch/traversal URLs more easily by using
  the new ``route_name``, ``route_kw`` and ``route_remainder_name`` arguments
  to :meth:`~pyramid.request.Request.resource_url` and
  :meth:`~pyuramid.request.Request.resource_path`.  See
  :ref:`generating_hybrid_urls`.

- A new http exception superclass named
  :class:`~pyramid.httpexceptions.HTTPSuccessful` was added.  You can use this
  class as the ``context`` of an exception view to catch all 200-series
  "exceptions" (e.g. "raise HTTPOk").  This also allows you to catch *only* the
  :class:`~pyramid.httpexceptions.HTTPOk` exception itself; previously this was
  impossible because a number of other exceptions (such as ``HTTPNoContent``)
  inherited from ``HTTPOk``, but now they do not.

- It is now possible to escape double braces in Pyramid scaffolds (unescaped, 
  these represent replacement values).  You can use ``\{\{a\}\}`` to
  represent a "bare" ``{{a}}``.  See 
  https://github.com/Pylons/pyramid/pull/862

- Add ``localizer`` and ``locale_name`` properties (reified) to
  :class:`pyramid.request.Request`.  See
  https://github.com/Pylons/pyramid/issues/508.  Note that the
  :func:`pyramid.i18n.get_localizer` and :func:`pyramid.i18n.get_locale_name`
  functions now simply look up these properties on the request.

- The ``pserve`` command now takes a ``-v`` (or ``--verbose``) flag and a
  ``-q`` (or ``--quiet``) flag.  Output from running ``pserve`` can be
  controlled using these flags.  ``-v`` can be specified multiple times to
  increase verbosity.  ``-q`` sets verbosity to ``0`` unconditionally.  The
  default verbosity level is ``1``.

- The ``alchemy`` scaffold tests now provide better coverage.  See
  https://github.com/Pylons/pyramid/pull/1029

Backwards Incompatibilities
---------------------------

- Modified the :meth:`~pyramid.request.Reuqest.current_route_url` method. The
  method previously returned the URL without the query string by default, it
  now does attach the query string unless it is overriden.

- The :meth:`~pyramid.request.Request.route_url` and
  :meth:`~pyramid.request.Request.route_path` APIs no longer quote ``/`` to
  ``%2F`` when a replacement value contains a ``/``.  This was pointless, as
  WSGI servers always unquote the slash anyway, and Pyramid never sees the
  quoted value.

- It is no longer possible to set a ``locale_name`` attribute of the request, 
  nor is it possible to set a ``localizer`` attribute of the request.  These
  are now "reified" properties that look up a locale name and localizer
  respectively using the machinery described in :ref:`i18n_chapter`.

- If you send an ``X-Vhm-Root`` header with a value that ends with a slash (or
  any number of slashes), the trailing slash(es) will be removed before a URL
  is generated when you use use :meth:`~pyramid.request.Request.resource_url`
  or :meth:`~pyramid.request.Request.resource_path`.  Previously the virtual
  root path would not have trailing slashes stripped, which would influence URL
  generation.

- The :class:`pyramid.interfaces.IResourceURL` interface has now grown two new
  attributes: ``virtual_path_tuple`` and ``physical_path_tuple``.  These should
  be the tuple form of the resource's path (physical and virtual).


Deprecations
------------

- Returning a ``("defname", dict)`` tuple from a view which has a Mako renderer
  is now deprecated.  Instead you should use the renderer spelling
  ``foo#defname.mak`` in the view configuration definition and return a dict
  only.

Documentation Enhancements
--------------------------

- A new documentation chapter named :ref:`quick_tour` was added.  It describes
  starting out with Pyramid from a high level.

- Many other enhancements.


Dependency Changes
------------------

No dependency changes from Pyramid 1.4.X were made in Pyramid 1.5.

