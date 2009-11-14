.. _glossary:

============================
Glossary
============================

.. glossary::

  Request
    A ``WebOb`` request object.  See :ref:`webob_chapter` for
    information about request objects.
  Response
    An object that has three attributes: app_iter (representing an
    iterable body), headerlist (representing the http headers sent
    upstream), and status (representing the http status string).  This
    is the interface defined for ``WebOb`` response objects.  See
    :ref:`webob_chapter` for information about response objects.
  Setuptools
    `Setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
    builds on Python's ``distutils`` to provide easier building,
    distribution, and installation of libraries and applications.
  pkg_resources
    A module which ships with :term:`setuptools` that provides an API
    for addressing "resource files" within Python packages.  Resource
    files are static files, template files, etc; basically anything
    non-Python-source that lives in a Python package can be considered
    a resource file.  See also `PkgResources
    <http://peak.telecommunity.com/DevCenter/PkgResources>`_
  Resource
    Any file contained within a Python :term:`package` which is *not*
    a Python source code file.
  Resource Specification
    A colon-delimited identifier for a resource.  The colon separates
    a Python :term:`package` name from a package subpath.  For
    example, the resource specification ``my.package:static/baz.css``
    identifies the file named ``baz.css`` in the ``static``
    subdirectory of the ``my.package`` Python package.
  Package
    A directory on disk which contains an ``__init__.py`` file, making
    it recognizable to Python as a location which can be ``import`` -ed.
  Project
    (Setuptools/distutils terminology). A directory on disk which
    contains a ``setup.py`` file and one or more Python packages.  The
    ``setup.py`` file contains code that allows the package(s) to be
    installed, distributed, and tested.
  Distribution
    (Setuptools/distutils terminology).  A file representing an
    installable library or application.  Distributions are usually
    files that have the suffix of ``.egg``, ``.tar.gz``, or ``.zip``.
    Distributions are the target of Setuptools commands such as
    ``easy_install``.
  Entry Point
    A :term:`setuptools` indirection, defined within a setuptools
    :term:`distribution` setup.py.  It is usually a name which refers
    to a function somewhere in a package which is held by the
    distribution.
  Dotted Python name
    A reference to a Python object by name using a string, in the form
    ``path.to.modulename:attributename``.  Often used in Paste and
    setuptools configurations.  A variant is used in dotted names
    within :term:`ZCML` attributes that name objects (such as the ZCML
    "view" directive's "view" attribute): the colon (``:``) is not
    used; in its place is a dot.
  View
    Common vernacular for a :term:`view callable`.
  View Callable
    A "view callable" is a callable Python object which returns a
    response object which is associated with a :term:`view
    configuration`.  It should accept two values: :term:`context` and
    :term:`request`.  An alternate calling convention allows a view to
    be defined as a a callable which only accepts a single ``request``
    argument.  A view callable is the primary mechanism by which a
    developer writes user interface code within :mod:`repoze.bfg`.
    See :ref:`views_chapter` for more information about
    :mod:`repoze.bfg` view callables.
  View Configuration
    View configuration is the act of associating a view callable with
    configuration information.  This configuration information helps
    map the view callable to URLs and can influence the response of a
    view callable.  :mod:`repoze.bfg` views can be configured via
    :term:`ZCML` or by a special ``@bfg_view`` decorator (see
    :ref:`mapping_views_to_urls_using_a_decorator_section`.).  See
    :ref:`views_chapter` for more information about view
    configuration. 
  View name
    The "URL name" of a view, e.g ``index.html``.  If a view is
    configured without a name, its name is considered to be the empty
    string (which implies the "default view").
  Virtualenv
    An isolated Python environment.  Allows you to control which
    packages are used on a particular project by cloning your main
    Python.  `virtualenv <http://pypi.python.org/pypi/virtualenv>`_
    was created by Ian Bicking.
  Model
    An object representing data in the system.  If :mod:`traversal` is
    used, a model is a node in the object graph traversed by the
    system.  When traversal is used, a model instance becomes the
    :term:`context` of a :term:`view`.  If :mod:`url dispatch` is
    used, a single :term:`context` (which isn't really a model,
    because it contains no data except security elements) is generated
    for each request and is used as the context of a view.
  Traversal
    The act of descending "down" a graph of model objects from a root
    model in order to find a :term:`context`.  The :mod:`repoze.bfg`
    :term:`router` performs traversal of model objects when a
    :term:`root factory` is specified.  See the
    :ref:`traversal_chapter` chapter for more information.  Traversal
    can be performed *instead* of :term:`URL dispatch` or can be
    combined *with* URL dispatch.  See :ref:`hybrid_chapter` for more
    information about combining traversal and URL dispatch (advanced).
  Router
    The :term:`WSGI` application created when you start a
    :mod:`repoze.bfg` application.  The router intercepts requests,
    invokes traversal and/or URL dispatch, calls view functions, and
    returns responses to the WSGI server on behalf of your
    :mod:`repoze.bfg` application.
  URL dispatch
    An alternative to graph traversal as a mechanism for locating a
    :term:`context` for a :term:`view`.  When you use a :term:`route`
    in your :mod:`repoze.bfg` application via a ``<route>``
    declaration in ZCML, you are using URL dispatch. See the
    :ref:`urldispatch_chapter` for more information.
  Context
    An object in the system that is found during :term:`traversal` or
    :term:`URL dispatch` based on URL data; if it's found via
    traversal, it's usually a :term:`model` object that is part of an
    object graph; if it's found via :term:`URL dispatch`, it's a
    manufactured context object that contains security information.  A
    context becomes the subject of a :term:`view`, and typically has
    security information attached to it.  See the
    :ref:`traversal_chapter` chapter and the
    :ref:`urldispatch_chapter` chapter for more information about how
    a URL is resolved to a context.
  Application registry
    A registry which maps model types to views, as well as performing
    other application-specific component registrations.  Every
    :mod:`repoze.bfg` application has one (and only one) application
    registry, which is represented on disk by its ``configure.zcml``
    file (and any other included .zcml files)
  Template
    A file with replaceable parts that is capable of representing some
    text, XML, or HTML when rendered.
  Location
    The path to an object in a model graph.  See :ref:`location_aware`
    for more information about how to make a model object *location-aware*.
  Principal
    A user id or group id.
  Permission
    A string or unicode object that represents an action being taken
    against a context.  A permission is associated with a view name
    and a model type by the developer.  Models are decorated with
    security declarations (e.g. an :term:`ACL`), which reference these
    tokens also.  Permissions are used by the active to security
    policy to match the view permission against the model's statements
    about which permissions are granted to which principal in a
    context in order to to answer the question "is this user allowed
    to do this".  Examples of permissions: ``read``, or
    ``view_blog_entries``.
  ACE
    An *access control entry*.  An access control entry is one element
    in an :term:`ACL`.  An access control entry is a three-tuple that
    describes three things: an *action* (one of either ``Allow`` or
    ``Deny``), a :term:`principal` (a string describing a user or
    group), and a :term:`permission`.  For example the ACE, ``(Allow,
    'bob', 'read')`` is a member of an ACL that indicates that the
    principal ``bob`` is allowed the permission ``read`` against the
    context the ACL is attached to.
  ACL
    An *access control list*.  An ACL is a sequence of :term:`ACE`
    tuples.  An ACL is attached to a model instance.  An example of an
    ACL is ``[ (Allow, 'bob', 'read'), (Deny, 'fred', 'write')]``.  If
    an ACL is attached to a model instance, and that model instance is
    findable via the context, it will be consulted any active security
    policy to determine wither a particular request can be fulfilled
    given the :term:`authentication` information in the request.
  Authentication
    The act of determining that the credentials a user presents during
    a particular request are "good".  :mod:`repoze.bfg` does not
    perfom authentication: it leaves it up to an upstream component
    such as :term:`repoze.who`.  :mod:`repoze.bfg` uses the
    :term:`authentication` data supplied by the upstream component as
    one input during :term:`authorization`.  Authentication in
    :mod:`repoze.bfg` is performed via an :term:`authentication
    policy`.
  Authorization
    The act of determining whether a user can perform a specific
    action.  In bfg terms, this means determining whether, for a given
    context, any :term:`principal` (or principals) associated with the
    request have the requisite :term:`permission` to allow the request
    to continue.  Authorization in :mod:`repoze.bfg` is performed via
    its :term:`authorization policy`.
  Principal
    A *principal* is a string or unicode object representing a user or
    a user's membership in a group.  It is provided by the
    :term:`authentication` machinery "upstream", typically (such as
    :term:`repoze.who`).  For example, if a user had the user id
    "bob", and Bob was part of two groups named "group foo" and "group
    bar", the request might have information attached to it that would
    indictate that Bob was represented by three principals: "bob",
    "group foo" and "group bar".
  Authorization Policy
    An authorization policy in :mod:`repoze.bfg` terms is a bit of
    code which has an API which determines whether or not the
    principals associated with the request can perform an action
    associated with a permission, based on the information found on the
    :term:`context`.
  Authentication Policy
    An authentication policy in :mod:`repoze.bfg` terms is a bit of
    code which has an API which determines the current
    :term:`principal` (or principals) associated with a request.
  WSGI
    `Web Server Gateway Interface <http://wsgi.org/>`_.  This is a
    Python standard for connecting web applications to web servers,
    similar to the concept of Java Servlets.  ``repoze.bfg`` requires
    that your application be served as a WSGI application.
  Middleware
    *Middleware* is a :term:`WSGI` concept.  It is a WSGI component
    that acts both as a server and an application.  Interesting uses
    for middleware exist, such as caching, content-transport
    encoding, and other functions.  See `WSGI.org <http://wsgi.org>`_
    or `PyPI <http://python.org/pypi>`_ to find middleware for your
    application.
  Pipeline
    The :term:`Paste` term for a single configuration of a WSGI
    server, a WSGI application, with a set of middleware in-between.
  mod_wsgi
    An `Apache module <http://code.google.com/p/modwsgi/>`_ for hosting
    Python WSGI applications.
  Zope
    `The Z Object Publishing Framework <http://zope.org>`_, a
    full-featured Python web framework.
  Grok
    `A web framework based on Zope 3 <http://grok.zope.org>`_.
  Django
    `A full-featured Python web framework <http://djangoproject.com>`_.
  Pylons
    `A lightweight Python web framework <http://pylonshq.com>`_.
  ZODB
     `Zope Object Database <http://wiki.zope.org/ZODB/FrontPage>`_, a
     persistent Python object store.
  ZEO
     `Zope Enterprise Objects
     <http://www.zope.org/Documentation/Books/ZopeBook/2_6Edition/ZEO.stx>`_
     allows multiple simultaneous processes to access a single
     :term:`ZODB` database.
  WebOb
    `WebOb <http://pythonpaste.org/webob/>`_ is a WSGI request/response
    library created by Ian Bicking.
  Paste
    `Paste <http://pythonpaste.org>`_ is a WSGI development and
    deployment system developed by Ian Bicking.
  PasteDeploy
    `PasteDeploy <http://pythonpaste.org>`_ is a library used by
    :mod:`repoze.bfg` which makes it possible to configure
    :term:`WSGI` components together declaratively within an ``.ini``
    file.  It was developed by Ian Bicking as part of :term:`Paste`.
  Chameleon
    `chameleon <http://chameleon.repoze.org>`_ is an attribute
    language template compiler which supports both the :term:`ZPT` and
    :term:`Genshi` templating specifications.  It is written and
    maintained by Malthe Borch.  It has several extensions, such as
    the ability to use bracketed (Genshi-style) ``${name}`` syntax,
    even within ZPT.  It is also much faster than the reference
    implementations of both ZPT and Genshi.  :mod:`repoze.bfg` offers
    Chameleon templating out of the box in ZPT flavor and offers the
    Genshi flavor as an add on within the
    :mod:`repoze.bfg.chameleon_genshi` package.
  chameleon.zpt
    ``chameleon.zpt`` is the package which provides :term:`ZPT`
    templating support under the :term:`Chameleon` templating engine.
  z3c.pt
    This was the previous name for :term:`Chameleon`, and is now a
    Zope 3 compatibility package for Chameleon.
  ZPT
    The `Zope Page Template <http://wiki.zope.org/ZPT/FrontPage>`_
    templating language.
  METAL
    `Macro Expansion for TAL <http://wiki.zope.org/ZPT/METAL>`_, a
    part of :term:`ZPT` which makes it possible to share common look
    and feel between templates.  
  Genshi
    An `XML templating language <http://pypi.python.org/pypi/Genshi/>`_
    by Christopher Lenz.
  Jinja2
    A `text templating language <http://jinja.pocoo.org/2/>`_ by Armin 
    Ronacher.
  Routes
    A `system by Ben Bangert <http://routes.groovie.org/>`_ which
    parses URLs and compares them against a number of user defined
    mappings. The URL pattern matching syntax in :mod:`repoze.bfg` is
    inspired by the Routes syntax (which was inspired by Ruby On
    Rails pattern syntax).
  Route
    A single pattern matched by the :term:`url dispatch` subsystem,
    which generally resolves to a :term:`root factory` (and then
    ultimately a :term:`view`).  See also :term:`url dispatch`.
  Route Configuration
    Route configuration is the act of using a :term:`ZCML` ``<route>``
    statement to associate request parameters with a particular
    :term:`route` using pattern matching and :term:`route predicate`
    statements.  See :ref:`urldispatch_chapter` for more information
    about route configuration.
  ZCML
    `Zope Configuration Markup Language
    <http://www.muthukadan.net/docs/zca.html#zcml>`_, an XML dialect
    used by Zope and :mod:`repoze.bfg` for configuration tasks.  ZCML
    is capable of performing many different registrations and
    declarations, but its primary purpose in :mod:`repoze.bfg` is to
    perform :term:`view configuration` and :term:`route configuration`
    within the ``configure.zcml`` file in a :mod:`repoze.bfg`
    application.  ZCML in a :mod:`repoze.bfg` application represents
    the application's :term:`application registry`.
  Zope Component Architecture
    The `Zope Component Architecture
    <http://www.muthukadan.net/docs/zca.html>`_ (aka ZCA) is a system
    which allows for application pluggability and complex dispatching
    based on objects which implement an :term:`interface`.
    :mod:`repoze.bfg` uses the ZCA "under the hood" to perform view
    dispatching and other application configuration tasks.
  ReStructuredText
    A `plain text format <http://docutils.sourceforge.net/rst.html>`_
    that is the defacto standard for descriptive text shipped in
    :term:`distribution` files, and Python docstrings.  This
    documentation is authored in ReStructuredText format.
  Root
    The object at which :term:`traversal` begins when
    :mod:`repoze.bfg` searches for a :term:`context` (for :term:`URL
    Dispatch`, the root is *always* the context).
  Subpath
    A list of element "left over" after the :term:`router` has
    performed a successful traversal to a view.  The subpath is a
    sequence of strings, e.g. ``['left', 'over', 'names']``.  Within
    BFG applications that use URL dispatch rather than traversal, you
    can use ``*subpath`` in the route pattern to influence the
    subpath.  See :ref:`star_subpath` for more information.
  Interface
    A `Zope interface <http://pypi.python.org/pypi/zope.interface>`_
    object.  In :mod:`repoze.bfg`, an interface may be attached to an
    model object or a request object in order to identify that the
    object is "of a type".  Interfaces are used internally by
    :mod:`repoze.bfg` to perform view lookups and other policy
    lookups.  Interfaces are exposed to application programmers by the
    ``view`` ZCML directive or the corresponding ``bfg_view``
    decorator in the form of both the ``for`` attribute and the
    ``request_type`` attribute.  They may be exposed to application
    developers when using the :term:`event` system as
    well. Fundamentally, :mod:`repoze.bfg` programmers can think of an
    interface as something that they can attach to an object that
    stamps it with a "type" unrelated to its underlying Python type.
    Interfaces can also be used to describe the behavior of an object
    (its methods and attributes), but unless they choose to,
    :mod:`repoze.bfg` programmers do not need to understand or use
    this feature of interfaces.  In other words, bfg developers need
    to only understand "marker" interfaces.
  Event
    An object broadcast to zero or more :term:`subscriber` callables
    during normal system operations.  :mod:`repoze.bfg` emits events
    during its lifetime routine.  Application code can subscribe to
    these events by using the subscriber functionality described in
    :ref:`events_chapter`.  Application code can also generate its own
    events using the ``zope.component.event.dispatch`` function.
    Application-code generated events may be subscribed to in the same
    way as system-generated events.
  Subscriber
    A callable which receives an :term:`event`.  A callable becomes a
    subscriber through an application registry registration.  See
    :ref:`events_chapter` for more information.
  Request type
    An attribute of a :term:`request` that allows for specialization
    of view code based on arbitrary categorization.  The every
    :term:`request` object that bfg generates and manipulates has one
    or more :term:`interface` objects attached to it.  The default
    interface attached to a request object is
    ``repoze.bfg.interfaces.IRequest``.  When a user writes view code,
    and registers a view without specifying a particular request type,
    the view is assumed to be registered for requests that have
    ``repoze.bfg.interfaces.IRequest`` attached to them.  However if
    the view is registered with a different interface as its request
    type, the view will be invoked only when the request possesses
    that particular interface.  Application code can cause requests to
    possess a different interface by adding the interface to the
    request object within a :term:`subscriber` to the
    ``repoze.bfg.interfaces.INewRequest`` event type.  String aliases
    such as ``GET``, ``POST``, etc. representing HTTP method names may
    be used in place of an interface specification in the
    ``request_type`` argument passed to view declarations.  ``GET`` is
    aliased to ``repoze.bfg.interfaces.IGETRequest``, ``POST`` is
    aliased to ``repoze.bfg.interfaces.IPOSTRequest``, and so on.
  repoze.lemonade
    Zope2 CMF-like `data structures and helper facilities
    <http://docs.repoze.org/lemonade>`_ for CA-and-ZODB-based
    applications useful within bfg applications.
  repoze.catalog
    An indexing and search facility (fielded and full-text) based on
    `zope.index <http://pypi.python.org/pypi/zope.index>`_.  See `the
    documentation <http://docs.repoze.org/catalog>`_ for more
    information.
  repoze.who
    `Authentication middleware <http://docs.repoze.org/who>`_ for
    :term:`WSGI` applications.  It can be used by :mod:`repoze.bfg` to
    provide authentication information.
  repoze.workflow
    `Barebones workflow for Python apps
    <http://docs.repoze.org/workflow>`_ .  It can be used by
    :mod:`repoze.bfg` to form a workflow system.
  Virtual root
    A model object representing the "virtual" root of a request; this
    is typically the physical root object (the object returned by the
    application root factory) unless :ref:`vhosting_chapter` is in
    use.
  Lineage
    An ordered sequence of objects based on a ":term:`location` -aware"
    context.  The lineage of any given :term:`context` is composed of
    itself, its parent, its parent's parent, and so on.  The order of
    the sequence is context-first, then the parent of the context,
    then its parent's parent, and so on.
  Root Factory
    The "root factory" of an :mod:`repoze.bfg` application is called
    on every request sent to the application.  The root factory
    returns the traversal root of an application.  It is
    conventionally named ``get_root``.  An application must supply a
    root factory to :mod:`repoze.bfg` within a call to
    ``repoze.bfg.router.make_app``; however, an application's root
    factory may be passed to ``make_app`` as ``None``, in which case
    the application uses a default root object (this pattern is often
    used in application which use :term:`URL dispatch` for all
    URL-to-view code mappings).
  SQLAlchemy
    `SQLAlchemy' <http://www.sqlalchemy.org/>`_ is an object
    relational mapper used in tutorials within this documentation.
  JSON
    `JavaScript Object Notation <http://www.json.org/>`_ is a data
    serialization format.
  Renderer
    A registered serializer that can be configured via :term:`view
    configuration` which converts a non-:term:`Response` return values
    from a :term:`view` into a string (and ultimately a response).
    Using a renderer can make writing views that require templating or
    other serialization less tedious.  See
    :ref:`views_which_use_a_renderer` for more information.
  mod_wsgi
    `mod_wsgi <http://code.google.com/p/modwsgi/>`_ is an Apache
    module developed by Graham Dumpleton.  It allows :term:`WSGI`
    applications (such as applications developed using
    :mod:`repoze.bfg`) to be served using the Apache web server.
  View Predicate
    An attribute of a ZCML ``view`` directive or an argument to a
    ``bfg_view`` decorator which implies a value which evaluates to
    true or false for a given :term:`request`.  All predicates
    attached to a view configuration must evaluate to true for the
    associated view to be considered as a possible callable for a
    given request.
  Route Predicate
    An attribute of a ZCML ``route`` directive which implies a value
    that evaluates to true or false for a given :term:`request`.  All
    predicates attached to a route configuration must evaluate to true
    for the associated route to "match" the current request.  If a
    route does not match the current request, the next route (in
    definition order) is attempted.
  Predicate
    A test which returns true or false.  Two different types of
    predicates exist in :mod:`repoze.bfg`: a :term:`view predicate`
    and a :term:`route predicate`.  View predicates are attached to
    :term:`view configuration` and route predicates are attached to
    :term:`route configuration`.

