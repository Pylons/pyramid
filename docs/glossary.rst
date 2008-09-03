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
    *router* performs traversal of model objects.  See the
    :ref:`traversal_chapter` chapter for more information.
  Router
    The :term:`WSGI` application created when you start a
    :mod:`repoze.bfg` application.  The router intercepts requests,
    invokes traversal, calls view functions, and returns responses to
    the WSGI server.
  URL dispatch
    An alternative to graph traversal as a mechanism for locating a
    :term:`context` for a :term:`view`.  When you use :term:`Routes`
    in your :mod:`repoze.bfg` application, you are using URL dispatch.
    See the :ref:`urldispatch_module` for more information.
  Context
    A :term:`model` in the system that is "found" during
    :term:`traversal` or :term:`URL dispatch`; it becomes the subject
    of a :term:`view`.  See the :ref:`traversal_chapter` chapter for
    more information.
  Application registry
    A registry which maps model types to views, as well as performing
    other application-specific component registrations.  Every
    :mod:`repoze.bfg` application has one (and only one) application
    registry, which is represented on disk by its ``configure.zcml``
    file.
  Template
    A file with replaceable parts that is capable of representing some
    text, XML, or HTML when rendered.
  Interface
    An attribute of an object that determines its type.
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
    `The Z Object Publishing Framework <http://zope.org>`_.  The granddaddy 
    of Python web frameworks.
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
  z3c.pt
    `z3c.pt <http://pypi.python.org/pypi/z3c.pt>`_ is an
    implementation of :term:`ZPT` by Malthe Borch.  It has serveral
    extensions, such as the ability to use bracketed- ``${name}``
    syntax.  It is also much faster than the reference implementation
    of ZPT.  :mod:`repoze.bfg` offers z3c.pt templating out of the
    box.
  ZPT
    The `Zope Page Template <http://wiki.zope.org/ZPT/FrontPage>`_
    templating language.
  METAL
    `Macro Expansion for TAL <http://wiki.zope.org/ZPT/METAL>`_, a
    part of :term:`ZPT` which makes it possible to share common look
    and feel between templates.  :term:`z3c.pt`, the implementation of
    ZPT that :mod:`repoze.bfg` ships with does not implement the METAL
    specification.
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
    :mod:`repoze.bfg` is to perform view mappings via the ``bfg:view``
    declaration.  The ``configure.zcml`` file in a :mod:`repoze.bfg`
    application represents the application's :term:`application
    registry`.
  repoze.who
    `Authentication middleware <http://static.repoze.org/whodocs>`_
    for :term:`WSGI` applications.  It can be used by
    :mod:`repoze.bfg` to provide authentication information.
  ReStructuredText
    A `plain text format <http://docutils.sourceforge.net/rst.html>`_
    that is the defacto standard for descriptive text shipped in
    :term:`distribution` files, and Python docstrings.
  Subpath
    A list of element "left over" after the :term:`router` has
    performed a successful traversal to a view.  The subpath is a
    sequence of strings, e.g. ``['left', 'over', 'names']``.

