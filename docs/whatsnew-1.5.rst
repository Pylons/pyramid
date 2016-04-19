What's New in Pyramid 1.5
=========================

This article explains the new features in :app:`Pyramid` version 1.5 as
compared to its predecessor, :app:`Pyramid` 1.4.  It also documents backwards
incompatibilities between the two versions and deprecations added to
:app:`Pyramid` 1.5, as well as software dependency changes and notable
documentation additions.

Major Backwards Incompatibilities
---------------------------------

- Pyramid no longer depends on or configures the Mako and Chameleon templating
  system renderers by default.  Disincluding these templating systems by
  default means that the Pyramid core has fewer dependencies and can run on
  future platforms without immediate concern for the compatibility of its
  templating add-ons.  It also makes maintenance slightly more effective, as
  different people can maintain the templating system add-ons that they
  understand and care about without needing commit access to the Pyramid core,
  and it allows users who just don't want to see any packages they don't use
  come along for the ride when they install Pyramid.

  This means that upon upgrading to Pyramid 1.5a2+, projects that use either
  of these templating systems will see a traceback that ends something like
  this when their application attempts to render a Chameleon or Mako template::

     ValueError: No such renderer factory .pt

  Or::

     ValueError: No such renderer factory .mako

  Or::

     ValueError: No such renderer factory .mak

  Support for Mako templating has been moved into an add-on package named 
  ``pyramid_mako``, and support for Chameleon templating has been moved into 
  an add-on package named ``pyramid_chameleon``.  These packages are drop-in 
  replacements for the old built-in support for these templating langauges. 
  All you have to do is install them and make them active in your configuration
  to register renderer factories for ``.pt`` and/or ``.mako`` (or ``.mak``) to
  make your application work again.

  To re-add support for Chameleon and/or Mako template renderers into your
  existing projects, follow the below steps.

  If you depend on Mako templates:

  * Make sure the ``pyramid_mako`` package is installed.  One way to do this
    is by adding ``pyramid_mako`` to the ``install_requires`` section of your
    package's ``setup.py`` file and afterwards rerunning ``setup.py develop``::

        setup(
            #...
            install_requires=[
                'pyramid_mako',         # new dependency
                'pyramid',
                #...
            ],
        )

  * Within the portion of your application which instantiates a Pyramid 
    :class:`~pyramid.config.Configurator` (often the ``main()`` function in 
    your project's ``__init__.py`` file), tell Pyramid to include the 
    ``pyramid_mako`` includeme::

        config = Configurator(.....)
        config.include('pyramid_mako')

  If you depend on Chameleon templates:

  * Make sure the ``pyramid_chameleon`` package is installed.  One way to do
    this is by adding ``pyramid_chameleon`` to the ``install_requires`` section
    of your package's ``setup.py`` file and afterwards rerunning 
    ``setup.py develop``::

        setup(
            #...
            install_requires=[
                'pyramid_chameleon',         # new dependency
                'pyramid',
                #...
            ],
        )

  * Within the portion of your application which instantiates a Pyramid 
    :class:`~pyramid.config.Configurator` (often the ``main()`` function in 
    your project's ``__init__.py`` file), tell Pyramid to include the 
    ``pyramid_chameleon`` includeme::

        config = Configurator(.....)
        config.include('pyramid_chameleon')

  Note that it's also fine to install these packages into *older* Pyramids for
  forward compatibility purposes.  Even if you don't upgrade to Pyramid 1.5
  immediately, performing the above steps in a Pyramid 1.4 installation is
  perfectly fine, won't cause any difference, and will give you forward
  compatibility when you eventually do upgrade to Pyramid 1.5.

  With the removal of Mako and Chameleon support from the core, some
  unit tests that use the ``pyramid.renderers.render*`` methods may begin to 
  fail.  If any of your unit tests are invoking either 
  ``pyramid.renderers.render()``  or ``pyramid.renderers.render_to_response()``
  with either Mako or Chameleon templates then the 
  ``pyramid.config.Configurator`` instance in effect during
  the unit test should be also be updated to include the addons, as shown
  above. For example::

        class ATest(unittest.TestCase):
            def setUp(self):
                self.config = pyramid.testing.setUp()
                self.config.include('pyramid_mako')

            def test_it(self):
                result = pyramid.renderers.render('mypkg:templates/home.mako', {})

  Or::

        class ATest(unittest.TestCase):
            def setUp(self):
                self.config = pyramid.testing.setUp()
                self.config.include('pyramid_chameleon')

            def test_it(self):
                result = pyramid.renderers.render('mypkg:templates/home.pt', {})

- If you're using the Pyramid debug toolbar, when you upgrade Pyramid to
  1.5a2+, you'll also need to upgrade the ``pyramid_debugtoolbar`` package to 
  at least version 1.0.8, as older toolbar versions are not compatible with 
  Pyramid 1.5a2+ due to the removal of Mako support from the core.  It's 
  fine to use this newer version of the toolbar code with older Pyramids too.

Feature Additions
-----------------

The feature additions in Pyramid 1.5 follow.

- Python 3.4 compatibility.

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

- Users can now provide dotted Python names to as the ``factory`` argument
  the Configurator methods named 
  :meth:`~pyramid.config.Configurator.add_view_predicate`, 
  :meth:`~pyramid.config.Configurator.add_route_predicate` and 
  :meth:`~pyramid.config.Configurator.add_subscriber_predicate`.  Instead of 
  passing the predicate factory directly, you can pass a dotted name which 
  refers to the factory.

- :func:`pyramid.path.package_name` no longer thows an exception when resolving 
  the package name for namespace packages that have no ``__file__`` attribute.

- An authorization API has been added as a method of the request:
  :meth:`pyramid.request.Request.has_permission`.  It is a method-based
  alternative to the :func:`pyramid.security.has_permission` API and works
  exactly the same.  The older API is now deprecated.

- Property API attributes have been added to the request for easier access to
  authentication data: :attr:`pyramid.request.Request.authenticated_userid`,
  :attr:`pyramid.request.Request.unauthenticated_userid`, and
  :attr:`pyramid.request.Request.effective_principals`.  These are analogues,
  respectively, of :func:`pyramid.security.authenticated_userid`,
  :func:`pyramid.security.unauthenticated_userid`, and
  :func:`pyramid.security.effective_principals`.  They operate exactly the
  same, except they are attributes of the request instead of functions
  accepting a request.  They are properties, so they cannot be assigned to.
  The older function-based APIs are now deprecated.

- Pyramid's console scripts (``pserve``, ``pviews``, etc) can now be run
  directly, allowing custom arguments to be sent to the python interpreter
  at runtime. For example::

      python -3 -m pyramid.scripts.pserve development.ini

- Added a specific subclass of :class:`pyramid.httpexceptions.HTTPBadRequest`
  named :class:`pyramid.exceptions.BadCSRFToken` which will now be raised in
  response to failures in the ``check_csrf_token`` view predicate.  See
  https://github.com/Pylons/pyramid/pull/1149

- Added a new ``SignedCookieSessionFactory`` which is very similar to the
  ``UnencryptedCookieSessionFactoryConfig`` but with a clearer focus on
  signing content. The custom serializer arguments to this function should
  only focus on serializing, unlike its predecessor which required the
  serializer to also perform signing.
  See https://github.com/Pylons/pyramid/pull/1142 . Note
  that cookies generated using ``SignedCookieSessionFactory`` are not
  compatible with cookies generated using ``UnencryptedCookieSessionFactory``,
  so existing user session data will be destroyed if you switch to it.

- Added a new ``BaseCookieSessionFactory`` which acts as a generic cookie
  factory that can be used by framework implementors to create their own
  session implementations. It provides a reusable API which focuses strictly
  on providing a dictionary-like object that properly handles renewals,
  timeouts, and conformance with the ``ISession`` API.
  See https://github.com/Pylons/pyramid/pull/1142

- We no longer eagerly clear ``request.exception`` and ``request.exc_info`` in
  the exception view tween.  This makes it possible to inspect exception
  information within a finished callback.  See
  https://github.com/Pylons/pyramid/issues/1223.


Other Backwards Incompatibilities
---------------------------------

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

- If you send an ``X-Vhm-Root`` header with a value that ends with any number
  of slashes, the trailing slashes will be removed before the URL
  is generated when you use :meth:`~pyramid.request.Request.resource_url`
  or :meth:`~pyramid.request.Request.resource_path`.  Previously the virtual
  root path would not have trailing slashes stripped, which would influence URL
  generation.

- The :class:`pyramid.interfaces.IResourceURL` interface has now grown two new
  attributes: ``virtual_path_tuple`` and ``physical_path_tuple``.  These should
  be the tuple form of the resource's path (physical and virtual).

- Removed the ``request.response_*`` varying attributes (such
  as``request.response_headers``) . These attributes had been deprecated
  since Pyramid 1.1, and as per the deprecation policy, have now been removed.

- ``request.response`` will no longer be mutated when using the 
  :func:`pyramid.renderers.render` API.  Almost all renderers mutate the 
  ``request.response`` response object (for example, the JSON renderer sets
  ``request.response.content_type`` to ``application/json``), but this is
  only necessary when the renderer is generating a response; it was a bug
  when it was done as a side effect of calling 
  :func:`pyramid.renderers.render`.

- Removed the ``bfg2pyramid`` fixer script.

- The :class:`pyramid.events.NewResponse` event is now sent **after** response 
  callbacks are executed.  It previously executed before response callbacks
  were executed.  Rationale: it's more useful to be able to inspect the response
  after response callbacks have done their jobs instead of before.

- Removed the class named ``pyramid.view.static`` that had been deprecated
  since Pyramid 1.1.  Instead use :class:`pyramid.static.static_view` with the
  ``use_subpath=True`` argument.

- Removed the ``pyramid.view.is_response`` function that had been deprecated
  since Pyramid 1.1.  Use the :meth:`pyramid.request.Request.is_response`
  method instead.

- Removed the ability to pass the following arguments to
  :meth:`pyramid.config.Configurator.add_route`: ``view``, ``view_context``.
  ``view_for``, ``view_permission``, ``view_renderer``, and ``view_attr``.
  Using these arguments had been deprecated since Pyramid 1.1.  Instead of
  passing view-related arguments to ``add_route``, use a separate call to
  :meth:`pyramid.config.Configurator.add_view` to associate a view with a route
  using its ``route_name`` argument.  Note that this impacts the
  :meth:`pyramid.config.Configurator.add_static_view` function too, because
  it delegates to``add_route``.

- Removed the ability to influence and query a :class:`pyramid.request.Request`
  object as if it were a dictionary.  Previously it was possible to use methods
  like ``__getitem__``, ``get``, ``items``, and other dictlike methods to
  access values in the WSGI environment.  This behavior had been deprecated
  since Pyramid 1.1.  Use methods of ``request.environ`` (a real dictionary)
  instead.

- Removed ancient backwards compatibily hack in
  ``pyramid.traversal.DefaultRootFactory`` which populated the ``__dict__`` of
  the factory with the matchdict values for compatibility with BFG 0.9.

- The ``renderer_globals_factory`` argument to the 
  :class:`pyramid.config.Configurator` constructor and the 
  coresponding argument to :meth:`~pyramid.config.Configurator.setup_registry` 
  has been removed.  The ``set_renderer_globals_factory`` method of
  :class:`~pyramid.config.Configurator` has also been removed.  The (internal)
  ``pyramid.interfaces.IRendererGlobals`` interface was also removed.  These
  arguments, methods and interfaces had been deprecated since 1.1.  Use a
  ``BeforeRender`` event subscriber as documented in the "Hooks" chapter of the
  Pyramid narrative documentation instead of providing renderer globals values
  to the configurator.

- The key/values in the ``_query`` parameter of
  :meth:`pyramid.request.Request.route_url` and the ``query`` parameter of
  :meth:`pyramid.request.Request.resource_url` (and their variants), used to
  encode a value of ``None`` as the string ``'None'``, leaving the resulting
  query string to be ``a=b&key=None``. The value is now dropped in this
  situation, leaving a query string of ``a=b&key=``.  See
  https://github.com/Pylons/pyramid/issues/1119

Deprecations
------------

- Returning a ``("defname", dict)`` tuple from a view which has a Mako renderer
  is now deprecated.  Instead you should use the renderer spelling
  ``foo#defname.mak`` in the view configuration definition and return a dict
  only.

- The :meth:`pyramid.config.Configurator.set_request_property` method now issues
  a deprecation warning when used.  It had been docs-deprecated in 1.4
  but did not issue a deprecation warning when used.

- :func:`pyramid.security.has_permission` is now deprecated in favor of using
  :meth:`pyramid.request.Request.has_permission`.

- The :func:`pyramid.security.authenticated_userid`,
  :func:`pyramid.security.unauthenticated_userid`, and
  :func:`pyramid.security.effective_principals` functions have been
  deprecated. Use :attr:`pyramid.request.Request.authenticated_userid`,
  :attr:`pyramid.request.Request.unauthenticated_userid` and
  :attr:`pyramid.request.Request.effective_principals` instead.

- Deprecate the ``pyramid.interfaces.ITemplateRenderer`` interface. It was
  ill-defined and became unused when Mako and Chameleon template bindings were
  split into their own packages.

- The ``pyramid.session.UnencryptedCookieSessionFactoryConfig`` API has been 
  deprecated and is superseded by the 
  ``pyramid.session.SignedCookieSessionFactory``.  Note that while the cookies
  generated by the ``UnencryptedCookieSessionFactoryConfig``
  are compatible with cookies generated by old releases, cookies generated by
  the SignedCookieSessionFactory are not. See 
  https://github.com/Pylons/pyramid/pull/1142

Documentation Enhancements
--------------------------

- A new documentation chapter named :ref:`quick_tour` was added.  It describes
  starting out with Pyramid from a high level.

- Added a :ref:`quick_tutorial` to go with the Quick Tour

- Many other enhancements.

Scaffolding Enhancements
------------------------

- All scaffolds have a new HTML + CSS theme.

- Updated docs and scaffolds to keep in step with new 2.0 release of
  ``Lingua``.  This included removing all ``setup.cfg`` files from scaffolds
  and documentation environments.

Dependency Changes
------------------

- Pyramid no longer depends upon ``Mako`` or ``Chameleon``.

- Pyramid now depends on WebOb>=1.3 (it uses ``webob.cookies.CookieProfile``
  from 1.3+).
