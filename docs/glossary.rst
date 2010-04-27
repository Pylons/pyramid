.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   request
     A ``WebOb`` request object.  See :ref:`webob_chapter` for
     information about request objects.

   response
     An object that has three attributes: ``app_iter`` (representing an
     iterable body), ``headerlist`` (representing the http headers sent
     to the user agent), and ``status`` (representing the http status
     string sent to the user agent).  This is the interface defined for
     ``WebOb`` response objects.  See :ref:`webob_chapter` for
     information about response objects.

   Repoze
     "Repoze" is essentially a "brand" of software developed by
     `Agendaless Consulting <http://agendaless.com>`_ and a set of
     contributors.  The term has no special intrinsic meaning.  The
     project's `website <http://repoze.org>`_ has more information.
     The software developed "under the brand" is available in a
     `Subversion repository <http://svn.repoze.org>`_.

   setuptools
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

   resource
     Any file contained within a Python :term:`package` which is *not*
     a Python source code file.

   resource specification
     A colon-delimited identifier for a :term:`resource`.  The colon
     separates a Python :term:`package` name from a package subpath.
     For example, the resource specification
     ``my.package:static/baz.css`` identifies the file named
     ``baz.css`` in the ``static`` subdirectory of the ``my.package``
     Python :term:`package`.

   package
     A directory on disk which contains an ``__init__.py`` file, making
     it recognizable to Python as a location which can be ``import`` -ed.

   project
     (Setuptools/distutils terminology). A directory on disk which
     contains a ``setup.py`` file and one or more Python packages.  The
     ``setup.py`` file contains code that allows the package(s) to be
     installed, distributed, and tested.

   distribution
     (Setuptools/distutils terminology).  A file representing an
     installable library or application.  Distributions are usually
     files that have the suffix of ``.egg``, ``.tar.gz``, or ``.zip``.
     Distributions are the target of Setuptools commands such as
     ``easy_install``.

   entry point
     A :term:`setuptools` indirection, defined within a setuptools
     :term:`distribution` setup.py.  It is usually a name which refers
     to a function somewhere in a package which is held by the
     distribution.

   dotted Python name
     A reference to a Python object by name using a string, in the form
     ``path.to.modulename:attributename``.  Often used in Paste and
     setuptools configurations.  A variant is used in dotted names
     within :term:`ZCML` attributes that name objects (such as the ZCML
     "view" directive's "view" attribute): the colon (``:``) is not
     used; in its place is a dot.

   view
     Common vernacular for a :term:`view callable`.

   view callable
     A "view callable" is a callable Python object which is associated
     with a :term:`view configuration`; it returns a :term:`response`
     object .  A view callable accepts a single argument: ``request``,
     which will be an instance of a :term:`request` object.  An
     alternate calling convention allows a view to be defined as a
     callable which accepts a pair of arguments: ``context`` and
     ``request``: this calling convention is useful for traversal-based
     applications in which a :term:`context` is always very important.  A
     view callable is the primary mechanism by which a developer writes
     user interface code within :mod:`repoze.bfg`.  See
     :ref:`views_chapter` for more information about :mod:`repoze.bfg`
     view callables.

   view configuration
     View configuration is the act of associating a :term:`view
     callable` with configuration information.  This configuration
     information helps map a given :term:`request` to a particular view
     callable and it can influence the response of a view callable.
     :mod:`repoze.bfg` views can be configured via :term:`imperative
     configuration`, :term:`ZCML` or by a special ``@bfg_view``
     decorator coupled with a :term:`scan`.  See :ref:`views_chapter`
     for more information about view configuration.

   view name
     The "URL name" of a view, e.g ``index.html``.  If a view is
     configured without a name, its name is considered to be the empty
     string (which implies the :term:`default view`).

   Default view
     The default view of a model is the view invoked when the
     :term:`view name` is the empty string (``''``).  This is the case
     when :term:`traversal` exhausts the path elements in the PATH_INFO
     of a request before it returns a :term:`context`.

   virtualenv
     An isolated Python environment.  Allows you to control which
     packages are used on a particular project by cloning your main
     Python.  `virtualenv <http://pypi.python.org/pypi/virtualenv>`_
     was created by Ian Bicking.

   model
     An object representing data in the system.  If :mod:`traversal` is
     used, a model is a node in the object graph traversed by the
     system.  When traversal is used, a model instance becomes the
     :term:`context` of a :term:`view`.  If :mod:`url dispatch` is
     used, a single :term:`context` is generated for each request and
     is used as the context of a view: this object is also technically
     a "model" in :mod:`repoze.bfg` terms, although this terminology
     can be a bit confusing: see :ref:`model_traversal_confusion`.

   traversal
     The act of descending "down" a graph of model objects from a root
     model in order to find a :term:`context`.  The :mod:`repoze.bfg`
     :term:`router` performs traversal of model objects when a
     :term:`root factory` is specified.  See the
     :ref:`traversal_chapter` chapter for more information.  Traversal
     can be performed *instead* of :term:`URL dispatch` or can be
     combined *with* URL dispatch.  See :ref:`hybrid_chapter` for more
     information about combining traversal and URL dispatch (advanced).

   router
     The :term:`WSGI` application created when you start a
     :mod:`repoze.bfg` application.  The router intercepts requests,
     invokes traversal and/or URL dispatch, calls view functions, and
     returns responses to the WSGI server on behalf of your
     :mod:`repoze.bfg` application.

   URL dispatch
     An alternative to graph traversal as a mechanism for locating a
     :term:`context` for a :term:`view`.  When you use a :term:`route`
     in your :mod:`repoze.bfg` application via a :term:`route
     configuration`, you are using URL dispatch. See the
     :ref:`urldispatch_chapter` for more information.

   context
     An object in the system that is found during :term:`traversal` or
     :term:`URL dispatch` based on URL data; if it's found via
     traversal, it's usually a :term:`model` object that is part of an
     object graph; if it's found via :term:`URL dispatch`, it's a
     object manufactured on behalf of the route's "factory".  A context
     becomes the subject of a :term:`view`, and typically has security
     information attached to it.  See the :ref:`traversal_chapter`
     chapter and the :ref:`urldispatch_chapter` chapter for more
     information about how a URL is resolved to a context.

   application registry
     A registry of configuration information consulted by
     :mod:`repoze.bfg` while servicing an application.  An application
     registry maps model types to views, as well as housing other
     application-specific component registrations.  Every
     :mod:`repoze.bfg` application has one (and only one) application
     registry.

   template
     A file with replaceable parts that is capable of representing some
     text, XML, or HTML when rendered.

   location
     The path to an object in an object graph.  See :ref:`location_aware`
     for more information about how to make a model object *location-aware*.

   permission
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

   authentication
     The act of determining that the credentials a user presents
     during a particular request are "good".  Authentication in
     :mod:`repoze.bfg` is performed via an :term:`authentication
     policy`.

   authorization
     The act of determining whether a user can perform a specific
     action.  In bfg terms, this means determining whether, for a given
     context, any :term:`principal` (or principals) associated with the
     request have the requisite :term:`permission` to allow the request
     to continue.  Authorization in :mod:`repoze.bfg` is performed via
     its :term:`authorization policy`.

   principal
     A *principal* is a string or unicode object representing a userid
     or a group id.  It is provided by an :term:`authentication
     policy`.  For example, if a user had the user id "bob", and Bob
     was part of two groups named "group foo" and "group bar", the
     request might have information attached to it that would
     indicate that Bob was represented by three principals: "bob",
     "group foo" and "group bar".

   authorization policy
     An authorization policy in :mod:`repoze.bfg` terms is a bit of
     code which has an API which determines whether or not the
     principals associated with the request can perform an action
     associated with a permission, based on the information found on the
     :term:`context`.

   authentication policy
     An authentication policy in :mod:`repoze.bfg` terms is a bit of
     code which has an API which determines the current
     :term:`principal` (or principals) associated with a request.

   WSGI
     `Web Server Gateway Interface <http://wsgi.org/>`_.  This is a
     Python standard for connecting web applications to web servers,
     similar to the concept of Java Servlets.  ``repoze.bfg`` requires
     that your application be served as a WSGI application.

   middleware
     *Middleware* is a :term:`WSGI` concept.  It is a WSGI component
     that acts both as a server and an application.  Interesting uses
     for middleware exist, such as caching, content-transport
     encoding, and other functions.  See `WSGI.org <http://wsgi.org>`_
     or `PyPI <http://python.org/pypi>`_ to find middleware for your
     application.

   pipeline
     The :term:`Paste` term for a single configuration of a WSGI
     server, a WSGI application, with a set of middleware in-between.

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
      `Zope Object Database <http://zodb.org>`_, a
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
     Chameleon templating out of the box in ZPT and text flavors.

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

   route
     A single pattern matched by the :term:`url dispatch` subsystem,
     which generally resolves to a :term:`root factory` (and then
     ultimately a :term:`view`).  See also :term:`url dispatch`.

   route configuration
     Route configuration is the act of using :term:`imperative
     configuration` or a :term:`ZCML` ``<route>`` statement to
     associate request parameters with a particular :term:`route` using
     pattern matching and :term:`route predicate` statements.  See
     :ref:`urldispatch_chapter` for more information about route
     configuration.

   ZCML
     `Zope Configuration Markup Language
     <http://www.muthukadan.net/docs/zca.html#zcml>`_, an XML dialect
     used by Zope and :mod:`repoze.bfg` for configuration tasks.  ZCML
     is capable of performing different types of :term:`configuration
     declaration`, but its primary purpose in :mod:`repoze.bfg` is to
     perform :term:`view configuration` and :term:`route configuration`
     within the ``configure.zcml`` file in a :mod:`repoze.bfg`
     application.  You can use ZCML as an alternative to
     :term:`imperative configuration`.

   ZCML directive
     A ZCML "tag" such as ``<view>`` or ``<route>``.

   ZCML declaration
     The concrete use of a :term:`ZCML directive` within a ZCML file.

   Zope Component Architecture
     The `Zope Component Architecture
     <http://www.muthukadan.net/docs/zca.html>`_ (aka ZCA) is a system
     which allows for application pluggability and complex dispatching
     based on objects which implement an :term:`interface`.
     :mod:`repoze.bfg` uses the ZCA "under the hood" to perform view
     dispatching and other application configuration tasks.

   reStructuredText
     A `plain text format <http://docutils.sourceforge.net/rst.html>`_
     that is the defacto standard for descriptive text shipped in
     :term:`distribution` files, and Python docstrings.  This
     documentation is authored in ReStructuredText format.

   root
     The object at which :term:`traversal` begins when
     :mod:`repoze.bfg` searches for a :term:`context` (for :term:`URL
     Dispatch`, the root is *always* the context).

   subpath
     A list of element "left over" after the :term:`router` has
     performed a successful traversal to a view.  The subpath is a
     sequence of strings, e.g. ``['left', 'over', 'names']``.  Within
     BFG applications that use URL dispatch rather than traversal, you
     can use ``*subpath`` in the route pattern to influence the
     subpath.  See :ref:`star_subpath` for more information.

   interface
     A `Zope interface <http://pypi.python.org/pypi/zope.interface>`_
     object.  In :mod:`repoze.bfg`, an interface may be attached to a
     :term:`model` object or a :term:`request` object in order to
     identify that the object is "of a type".  Interfaces are used
     internally by :mod:`repoze.bfg` to perform view lookups and other
     policy lookups.  The ability to make use of an interface is
     exposed to an application programmers during :term:`view
     configuration` via the ``context`` argument, the ``request_type``
     argument and the ``containment`` argument.  Interfaces are also
     exposed to application developers when they make use of the
     :term:`event` system. Fundamentally, :mod:`repoze.bfg`
     programmers can think of an interface as something that they can
     attach to an object that stamps it with a "type" unrelated to its
     underlying Python type.  Interfaces can also be used to describe
     the behavior of an object (its methods and attributes), but
     unless they choose to, :mod:`repoze.bfg` programmers do not need
     to understand or use this feature of interfaces.

   event
     An object broadcast to zero or more :term:`subscriber` callables
     during normal :mod:`repoze.bfg` system operations during the
     lifetime of an application.  Application code can subscribe to
     these events by using the subscriber functionality described in
     :ref:`events_chapter`.

   subscriber
     A callable which receives an :term:`event`.  A callable becomes a
     subscriber via :term:`imperative configuration` or the
     ``<subscriber>`` ZCML directive.  See :ref:`events_chapter` for
     more information.

   request type
     An attribute of a :term:`request` that allows for specialization
     of view invocation based on arbitrary categorization.  The every
     :term:`request` object that :mod:`repoze.bfg` generates and
     manipulates has one or more :term:`interface` objects attached to
     it.  The default interface attached to a request object is
     ``repoze.bfg.interfaces.IRequest``.

   repoze.lemonade
     Zope2 CMF-like `data structures and helper facilities
     <http://docs.repoze.org/lemonade>`_ for CA-and-ZODB-based
     applications useful within :mod:`repoze.bfg` applications.

   repoze.catalog
     An indexing and search facility (fielded and full-text) based on
     `zope.index <http://pypi.python.org/pypi/zope.index>`_.  See `the
     documentation <http://docs.repoze.org/catalog>`_ for more
     information.  A tutorial for its usage in :mod:`repoze.bfg`
     exists in :ref:`catalog_tutorial`.

   repoze.who
     `Authentication middleware <http://docs.repoze.org/who>`_ for
     :term:`WSGI` applications.  It can be used by :mod:`repoze.bfg` to
     provide authentication information.

   repoze.workflow
     `Barebones workflow for Python apps
     <http://docs.repoze.org/workflow>`_ .  It can be used by
     :mod:`repoze.bfg` to form a workflow system.

   virtual root
     A model object representing the "virtual" root of a request; this
     is typically the physical root object (the object returned by the
     application root factory) unless :ref:`vhosting_chapter` is in
     use.

   lineage
     An ordered sequence of objects based on a ":term:`location`
     -aware" context.  The lineage of any given :term:`context` is
     composed of itself, its parent, its parent's parent, and so on.
     The order of the sequence is context-first, then the parent of the
     context, then its parent's parent, and so on.  The parent of an
     object in a lineage is available as its ``__parent__`` attribute.

   root factory
     The "root factory" of an :mod:`repoze.bfg` application is called
     on every request sent to the application.  The root factory
     returns the traversal root of an application.  It is
     conventionally named ``get_root``.  An application may supply a
     root factory to :mod:`repoze.bfg` during the construction of a
     :term:`Configurator`.  If a root factory is not supplied, the
     application uses a default root object.  Use of the default root
     object is useful in application which use :term:`URL dispatch` for
     all URL-to-view code mappings.

   SQLAlchemy
     `SQLAlchemy' <http://www.sqlalchemy.org/>`_ is an object
     relational mapper used in tutorials within this documentation.

   JSON
     `JavaScript Object Notation <http://www.json.org/>`_ is a data
     serialization format.

   renderer
     A serializer that can be referred to via :term:`view
     configuration` which converts a non-:term:`Response` return
     values from a :term:`view` into a string (and ultimately a
     response).  Using a renderer can make writing views that require
     templating or other serialization less tedious.  See
     :ref:`views_which_use_a_renderer` for more information.

   renderer factory
     A factory which creates a :term:`renderer`.  See
     :ref:`adding_and_overriding_renderers` for more information.

   mod_wsgi
     `mod_wsgi <http://code.google.com/p/modwsgi/>`_ is an Apache
     module developed by Graham Dumpleton.  It allows :term:`WSGI`
     applications (such as applications developed using
     :mod:`repoze.bfg`) to be served using the Apache web server.

   view predicate
     An argument to a :term:`view configuration` which evaluates to
     ``True`` or ``False`` for a given :term:`request`.  All predicates
     attached to a view configuration must evaluate to true for the
     associated view to be considered as a possible callable for a
     given request.

   route predicate
     An argument to a :term:`route configuration` which implies a value
     that evaluates to ``True`` or ``False`` for a given
     :term:`request`.  All predicates attached to a :term:`route
     configuration` must evaluate to ``True`` for the associated route
     to "match" the current request.  If a route does not match the
     current request, the next route (in definition order) is
     attempted.

   predicate
     A test which returns ``True`` or ``False``.  Two different types
     of predicates exist in :mod:`repoze.bfg`: a :term:`view predicate`
     and a :term:`route predicate`.  View predicates are attached to
     :term:`view configuration` and route predicates are attached to
     :term:`route configuration`.

   decorator
     A wrapper around a Python function or class which accepts the
     function or class as its first argument and which returns an
     arbitrary object.  :mod:`repoze.bfg` provides several decorators,
     used for configuration and return value modification purposes.  See
     also `PEP 318 <http://www.python.org/dev/peps/pep-0318/>`_.

   configuration declaration
     An individual method call made to an instance of a
     :mod:`repoze.bfg` :term:`Configurator` object which performs an
     arbitrary action, such as registering a :term:`view configuration`
     (via the ``view`` method of the configurator) or :term:`route
     configuration` (via the ``route`` method of the configurator).  A
     set of configuration declarations is also usually implied via the
     use of a :term:`ZCML declaration` within an application, or a set
     of configuration declarations might be performed by a :term:`scan`
     of code in a package.

   configuration decoration
     Metadata implying one or more :term:`configuration declaration`
     invocations.  Often set by configuration Python :term:`decorator`
     attributes, such as ``repoze.bfg.view.bfg_view``, aka ``@bfg_view``.

   scan
     The term used by :mod:`repoze.bfg` to define the process of
     importing and examining all code in a Python package or module for
     :term:`configuration decoration`.

   configurator
     An object used to do :term:`configuration declaration` within an
     application.  The most common configurator is an instance of the
     ``repoze.bfg.configuration.Configurator`` class.

   imperative configuration
     The configuration mode in which you use Python to call methods on
     a :term:`Configurator` in order to add each :term:`configuration
     declaration` required by your application.

   declarative configuration
     The configuration mode in which you use :term:`ZCML` to make
     a set of :term:`configuration declaration` statements.

   Not Found view
      The :term:`view callable` invoked by :mod:`repoze.bfg` when the
      developer explicitly raises a
      ``repoze.bfg.exceptions.NotFound`` exception from within
      :term:`view` code or :term:`root factory` code, or when the
      current request doesn't match any :term:`view configuration`.
      :mod:`repoze.bfg` provides a default implementation of a not
      found view; it can be overridden.  See
      :ref:`changing_the_notfound_view`.

   Forbidden view
      The :term:`view callable` invoked by :mod:`repoze.bfg` when the
      developer explicitly raises a
      ``repoze.bfg.exceptions.Forbidden`` exception from within
      :term:`view` code or :term:`root factory` code, or when the
      :term:`view configuration` and :term:`authorization policy` found
      for a request disallows a particular view invocation.
      :mod:`repoze.bfg` provides a default implementation of a
      forbidden view; it can be overridden.  See
      :ref:`changing_the_forbidden_view`.

   thread local
      A thread-local variable is one which is essentially a global
      variable in terms of how it is accessed and treated, however,
      each `thread
      <http://en.wikipedia.org/wiki/Thread_(computer_science)>` used by
      the application may have a different value for this same "global"
      variable.  :mod:`repoze.bfg` uses a small number of thread local
      variables, as described in :ref:`threadlocals_chapter`. See also
      the `threading.local documentation
      <http://docs.python.org/library/threading.html#threading.local>`
      for more information.

   multidict
     An ordered dictionary that can have multiple values for each
     key. Adds the methods ``getall``, ``getone``, ``mixed``, and
     ``add`` to the normal dictionary interface.  See
     http://pythonpaste.org/webob/class-webob.multidict.MultiDict.html

   PyPI
     `The Python Package Index <http://pypi.python.org/pypi>`_, a
     collection of software available for Python.

   Agendaless Consulting
     A consulting organization formed by Paul Everitt, Tres Seaver,
     and Chris McDonough.  See also http://agendaless.com .

   Jython
     A `Python implementation <http://www.jython.org/>` written for
     the Java Virtual Machine.

   Python
     The `programming language <http://python.org>` in which
     :mod:`repoze.bfg` is written.

   CPython
     The C implementation of the Python language.  This is the
     reference implementation that most people refer to as simply
     "Python"; :term:`Jython`, Google's App Engine, and `PyPy
     <http://codespeak.net/pypy/dist/pypy/doc/>`_ are examples of
     non-C based Python implementations.

   View Lookup
     The act of finding and invoking the "best" :term:`view callable`
     given a :term:`request`, a :term:`context`, and a :term:`view
     name`.

   Context Finding
     The act of locating a :term:`context` and a :term:`view name`
     given a :term:`request`.  :term:`Traversal` and :term:`URL
     dispatch` are the context finding subsystems used by
     :mod:`repoze.bfg`.

   Triad
     The three bits of information used by :term:`view lookup` to find
     "the best" view callable for a given circumstance: a
     :term:`context` type, a :term:`view name` and a :term:`request`.

   Google App Engine
     `Google App Engine <http://code.google.com/appengine/>`_ (aka
     "GAE") is a Python application hosting service offered by Google.
     :mod:`repoze.bfg` runs on GAE.

   Venusian
     `Venusian <http://docs.repoze.org/venusian>`_ is a library which
     allows framework authors to defer decorator actions.  Instead of
     taking actions when a function (or class) decorator is executed
     at import time, the action usually taken by the decorator is
     deferred until a separate "scan" phase.  :mod:`repoze.bfg` relies
     on Venusian to provide a basis for its :term:`scan` feature.

   Translation String
     An instance of :class:`repoze.bfg.i18n.TranslationString`, which
     is a class that behaves like a Unicode string, but has several
     extra attributes such as ``domain``, ``msgid``, and ``mapping``
     for use during translation.  Translation strings are usually
     created by hand within software, but are sometimes created on the
     behalf of the system for automatic template translation.  For
     more information, see :ref:`i18n_chapter`.

   Translation Domain
     A string representing the "context" in which a translation was
     made.  For example the word "java" might be translated
     differently if the translation domain is "programming-languages"
     than would be if the translation domain was "coffee".  A
     translation domain is represnted by a collection of ``.mo`` files
     within one or more :term:`translation directory` directories.

   Translator
     A callable which receives a :term:`translation string` and
     returns a translated Unicode object for the purposes of
     internationalization.  A :term:`localizer` supplies a
     translator to a :mod:`repoze.bfg` application accessible via its
     ``translate`` method.

   Translation Directory
     A translation directory is a :term:`gettext` translation
     directory.  It contains language folders, which themselves
     contain ``LC_MESSAGES`` folders, which contain ``.mo`` files.
     Each ``.mo`` file represents a set of translations for a language
     in a :term:`translation domain`.  The name of the ``.mo`` file
     (minus the .mo extension) is the translation domain name.

   Localizer
     An instance of the class :class:`repoze.bfg.i18n.Localizer` which
     provides translation and pluralization services to an
     application.  It is retrieved via the
     :func:`repoze.bfg.i18n.get_localizer` function.

   Locale Name
     A string like ``en``, ``en_US``, ``de``, or ``de_AT`` which
     uniquely identifies a particular locale.

   Default Locale Name
     The :term:`locale name` used by an application when no explicit
     locale name is set.  See :ref:`localization_deployment_settings`.

   Locale Negotiator
     An object supplying a policy determining which :term:`locale
     name` best represents a given :term:`request`.  It is used by the
     :func:`repoze.bfg.i18n.get_locale_name`, and
     :func:`repoze.bfg.i18n.negotiate_locale_name` functions, and
     indirectly by :func:`repoze.bfg.i18n.get_localizer`.  The
     :func:`repoze.bfg.i18n.default_locale_negotiator` function
     is an example of a locale negotiator.

   Gettext
     The GNU `gettext <http://www.gnu.org/software/gettext/>`_
     library, used by the :mod:`repoze.bfg` translation machinery.

   Babel
     A `collection of tools <http://babel.edgewall.org/>`_ for
     internationalizing Python applications.  :mod:`repoze.bfg` does
     not depend on Babel to operate, but if Babel is installed,
     additional locale functionality becomes available to your
     application.

   Message Identifier
     A string used as a translation lookup key during localization.
     The ``msgid`` argument to a :term:`translation string` is a
     message identifier.  Message identifiers are also present in a
     :term:`message catalog`.

   Message Catalog
     A :term:`gettext` ``.mo`` file containing translations.

   Internationalization
     The act of creating software with a user interface that can
     potentially be displayed in more than one language or cultural
     context.  Often shortened to "i18n" (because the word
     "internationalization" is I, 18 letters, then N).  See also:
     :term:`Localization`.

   Localization
     The process of displaying the user interface of an
     internationalized application in a particular language or
     cultural context.  Often shortened to "l10" (because the word
     "localization" is L, 10 letters, then N).  See also:
     :term:`Internationalization`.
