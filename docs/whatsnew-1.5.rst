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

     @implementor(IResource)
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

- The :class:`pyramid.authentication.AuthTktAuthenticationPolicy` has a new
  ``parent_domain`` option to set the authentication cookie as a wildcard
  cookie on the parent domain. This is useful if you have multiple sites
  sharing the same domain.  It also now supports IPv6 addresses when using
  the ``include_ip=True`` option. This is possibly incompatible with
  alternative ``auth_tkt`` implementations, as the specification does not
  define how to properly handle IPv6. See
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

Backwards Incompatibilities
---------------------------

- Modified the ``current_route_url`` method in pyramid.Request. The method
  previously returned the URL without the query string by default, it now does
  attach the query string unless it is overriden.


Deprecations
------------

This release has no new deprecations as compared to Pyramid 1.4.X.


Documentation Enhancements
--------------------------

Many documentation enhancements have been added, but we did not track them as
they were added.

Dependency Changes
------------------

No dependency changes from Pyramid 1.4.X were made in Pyramid 1.5.

