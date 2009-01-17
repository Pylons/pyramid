.. _glossary:

============================
Glossary
============================

.. glossary::

  Request
    A ``WebOb`` request object.
  Response
    An object that has three attributes: app_iter (representing an
    iterable body), headerlist (representing the http headers sent
    upstream), and status (representing the http status string).  This
    is the interface defined for ``WebOb`` response objects.
  Setuptools
    `Setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
    builds on Python's ``distutils`` to provide easier building,
    distribution, and installation of libraries and applications.
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
    setuptools configurations.
  View
    A "view" is a callable which returns a response object.  It should
    accept two values: context and request.
  View name
    The "URL name" of a view, e.g "index.html".  If a view is
    configured without a name, its name is considered to be the empty
    string (which implies the "default view").
  Virtualenv
    An isolated Python environment.  Allows you to control which
    packages are used on a particular project by cloning your main
    Python.  `virtualenv <http://pypi.python.org/pypi/virtualenv>`_
    was created by Ian Bicking.
  Model
    An object representing data in the system.  A model is part of the
    object graph traversed by the system.  Models are traversed to
    determine a context.
  Traversal
    The act of descending "down" a graph of model objects from a root
    model in order to find a :term:`context`.  The :mod:`repoze.bfg`
    :term:`router` performs traversal of model objects.  See the
    :ref:`traversal_chapter` chapter for more information.
  Router
    The :term:`WSGI` application created when you start a
    :mod:`repoze.bfg` application.  The router intercepts requests,
    invokes traversal, calls view functions, and returns responses to
    the WSGI server on behalf of your :mod:`repoze.bfg` application.
  URL dispatch
    An alternative to graph traversal as a mechanism for locating a
    :term:`context` for a :term:`view`.  When you use :term:`Routes`
    in your :mod:`repoze.bfg` application, you are using URL dispatch.
    See the :ref:`urldispatch_module` for more information.
  Context
    A object in the system that is found during :term:`traversal` or
    :term:`URL dispatch` based on URL data; if it's found via
    traversal, it's usually a :term:`model` object; if it's found via
    :term:`URL dispatch`, it's a manufactured context object that
    contains routing information.  A context becomes the subject of a
    :term:`view`, and typically has security information attached to
    it.  See the :ref:`traversal_chapter` chapter and the
    :ref:`urldispatch_chapter` chapter for more information about how
    a URL is resolved to a context.
  Application registry
    A registry which maps model types to views, as well as performing
    other application-specific component registrations.  Every
    :mod:`repoze.bfg` application has one (and only one) application
    registry, which is represented on disk by its ``configure.zcml``
    file.
  Template
    A file with replaceable parts that is capable of representing some
    text, XML, or HTML when rendered.
  Location
    The path to an object in a model graph.  See :ref:`location_aware`
    for more information about how to make a model object *location-aware*.
  Security policy
    An object that provides a mechanism to check authorization using
    authentication data and a permission associated with a model.  It
    essentially returns "true" if the combination of the authorization
    information in the model (e.g. an :term:`ACL`) and the
    authentication data in the request (e.g. the ``REMOTE_USER``
    environment variable) allow the action implied by the permission
    associated with the view (e.g. ``add`` or ``read``).
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
    one input during :term:`authorization`.
  Authorization
    The act of determining whether a user can perform a specific
    action.  In bfg terms, this means determining whether, for a given
    context, any :term:`principal` (or principals) associated with the
    request have the requisite :term:`permission` to allow the request
    to continue.
  Principal
    A *principal* is a string or unicode object representing a user or
    a user's membership in a group.  It is provided by the
    :term:`authentication` machinery "upstream", typically (such as
    :term:`repoze.who`).  For example, if a user had the user id
    "bob", and Bob was part of two groups named "group foo" and "group
    bar", the request might have information attached to it that would
    indictate that Bob was represented by three principals: "bob",
    "group foo" and "group bar".
  Security Policy
    A security policy in bfg terms is a bit of code which accepts a
    request, the :term:`ACL` associated with a context, and the
    :term:`permission` associated with a particular view, and
    subsequently determines whether or not the principals associated
    with the request can perform the action associated with the
    permission based on the ACL found on the :term:`context` (or any
    of its parents).
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
  LXML
    `lxml <http://codespeak.net/lxml/>`_ is a XML processing library
    for Python by Martijn Faassen and others.
  XSLT
    `XSL Transformations <http://www.w3.org/TR/xslt>`_.  A language
    for transforming XML documents into other XML documents.
  Chameleon
    `chameleon <http://pypi.python.org/pypi/chameleon.core>`_ is an
    attribute language template compiler which supports both the
    :term:`ZPT` and :term:`Genshi` templating specifications.  It is
    written and maintained by Malthe Borch.  It has serveral
    extensions, such as the ability to use bracketed (Genshi-style)
    ``${name}`` syntax, even within ZPT.  It is also much faster than
    the reference implementations of both ZPT and Genshi.
    :mod:`repoze.bfg` offers Chameleon templating out of the box in
    both ZPT and Genshi "flavors".
  chameleon.zpt
    ``chameleon.zpt`` is the package which provides :term:`ZPT`
    templating support under the :term:`Chameleon` templating engine.
  chameleon.genshi
    ``chameleon.genshi`` is the package which provides :term:`Genshi`
    templating support under the :term:`Chameleon` templating engine.
  z3c.pt
    This was the previous name for :term:`Chameleon`, and is now a
    Zope 3 compatibility package for Chameleon.
  ZPT
    The `Zope Page Template <http://wiki.zope.org/ZPT/FrontPage>`_
    templating language.
  Genshi
    `Genshi <http://genshi.edgewall.org/>`_ is an attribute-based XML
    templating language similar to ZPT.  Its syntax is supported
    within :mod:`repoze.bfg` via :term:`Chameleon`.
  METAL
    `Macro Expansion for TAL <http://wiki.zope.org/ZPT/METAL>`_, a
    part of :term:`ZPT` which makes it possible to share common look
    and feel between templates.  
  Routes
    A `system by Ben Bangert <http://routes.groovie.org/>`_ which
    parses URLs and compares them against a number of user defined
    mappings. In terms of :mod:`repoze.bfg`, a Route can supplant
    graph traversal when deciding which *view* should be called.  See
    :ref:`urldispatch_module` for more information about (optional)
    Routes integration in bfg.
  ZCML
    `Zope Configuration Markup Language
    <http://www.muthukadan.net/docs/zca.html#zcml>`_, the XML dialect
    used by Zope and :mod:`repoze.bfg` to describe associating a view
    with a model type.  ZCML is capable of performing many different
    registrations and declarations, but its primary purpose in
    :mod:`repoze.bfg` is to perform view mappings via the ``view``
    declaration.  The ``configure.zcml`` file in a :mod:`repoze.bfg`
    application represents the application's :term:`application
    registry`.  You can also use decorators to configure views in
    :mod:`repoze.bfg`; see
    :ref:`mapping_views_to_urls_using_a_decorator_section`.
  ReStructuredText
    A `plain text format <http://docutils.sourceforge.net/rst.html>`_
    that is the defacto standard for descriptive text shipped in
    :term:`distribution` files, and Python docstrings.
  Root
    The object at which :term:`traversal` begins when
    :mod:`repoze.bfg` searches for a context (for :term:`URL
    Dispatch`, the root is *always* the context).
  Subpath
    A list of element "left over" after the :term:`router` has
    performed a successful traversal to a view.  The subpath is a
    sequence of strings, e.g. ``['left', 'over', 'names']``.
  Interface
    A `Zope interface <http://pypi.python.org/pypi/zope.interface>`_
    object.  In bfg, an interface may be attached to an model object
    or a request object in order to identify that the object is "of a
    type".  Interfaces are used internally by :mod:`repoze.bfg` to
    perform view lookups and security policy lookups.  Interfaces are
    exposed to application programmers by the ``view`` ZCML directive
    or the corresponding ``bfg_view`` decorator in the form of both
    the ``for`` attribute and the ``request_type`` attribute.  They
    may be exposed to application developers when using the
    :term:`event` system as well. Fundamentally, :mod:`repoze.bfg`
    programmers can think of an interface as something that they can
    attach to an object that stamps it with a "type" unrelated to its
    underlying Python type.  Interfaces can also be used to describe
    the behavior of an object (its methods and attributes), but unless
    they choose to, :mod:`repoze.bfg` programmers do not need to
    understand or use this feature of interfaces.  In other words, bfg
    developers need to only understand "marker" interfaces.
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
    A callable which receives an event.  A callable becomes a
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
    ``repoze.bfg.interfaces.INewRequest`` event type.
  repoze.lemonade
    Zope2 CMF-like `data structures and helper facilities
    <http://static.repoze.org/lemonadedocs>`_ for
    CA-and-ZODB-based applications useful within bfg applications.
  repoze.catalog
    An indexing and search facility (fielded and full-text) based on
    `zope.index <http://pypi.python.org/pypi/zope.index>`_.  See
    `the documentation <http://static.repoze.org/catalogdocs>`_ for more 
    information.
  repoze.who
    `Authentication middleware <http://static.repoze.org/whodocs>`_
    for :term:`WSGI` applications.  It can be used by
    :mod:`repoze.bfg` to provide authentication information.
  repoze.workflow
    `Barebones workflow for Python apps
    <http://static.repoze.org/workflowdocs>`_ .  It can be used by
    :mod:`repoze.bfg` to form a workflow system.
  repoze.bfg.convention
    `An add-on for repoze.bfg
    <http://static.repoze.org/conventiondocs>`_ which provides
    alternative mechanisms for common :mod:`repoze.bfg` application
    configuration tasks.  The functionality of this package has been
    merged into the :mod:`repoze.bfg` core as of version 0.6.3.
