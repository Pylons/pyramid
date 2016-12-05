.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   request
     An object that represents an HTTP request, usually an instance of the
     :class:`pyramid.request.Request` class.  See :ref:`webob_chapter`
     (narrative) and :ref:`request_module` (API documentation) for
     information about request objects.

   request factory
     An object which, provided a :term:`WSGI` environment as a single
     positional argument, returns a Pyramid-compatible request.

   response factory
     An object which, provided a :term:`request` as a single positional
     argument, returns a Pyramid-compatible response. See
     :class:`pyramid.interfaces.IResponseFactory`.

   response
     An object returned by a :term:`view callable` that represents response
     data returned to the requesting user agent.  It must implement the
     :class:`pyramid.interfaces.IResponse` interface.  A response object is
     typically an instance of the :class:`pyramid.response.Response` class or
     a subclass such as :class:`pyramid.httpexceptions.HTTPFound`.  See
     :ref:`webob_chapter` for information about response objects.

   response adapter
     A callable which accepts an arbitrary object and "converts" it to a
     :class:`pyramid.response.Response` object.  See :ref:`using_iresponse`
     for more information.

   Repoze
     "Repoze" is essentially a "brand" of software developed by `Agendaless
     Consulting <https://agendaless.com>`_ and a set of contributors.  The
     term has no special intrinsic meaning.  The project's `website
     <http://repoze.org>`_ has more information.  The software developed
     "under the brand" is available in a `Subversion repository
     <http://svn.repoze.org>`_.  Pyramid was originally known as
     :mod:`repoze.bfg`.

   setuptools
     `Setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
     builds on Python's ``distutils`` to provide easier building,
     distribution, and installation of libraries and applications.  As of
     this writing, setuptools runs under Python 2, but not under Python 3.
     You can use :term:`distribute` under Python 3 instead.

   distribute
     `Distribute <https://pythonhosted.org/distribute/>`_ is a fork of
     :term:`setuptools` which runs on both Python 2 and Python 3.

   pkg_resources
     A module which ships with :term:`setuptools` and :term:`distribute` that
     provides an API for addressing "asset files" within a Python
     :term:`package`.  Asset files are static files, template files, etc;
     basically anything non-Python-source that lives in a Python package can
     be considered a asset file.
     
     .. seealso::
         
         See also `PkgResources
         <http://peak.telecommunity.com/DevCenter/PkgResources>`_.

   asset
     Any file contained within a Python :term:`package` which is *not*
     a Python source code file.

   asset specification
     A colon-delimited identifier for an :term:`asset`.  The colon
     separates a Python :term:`package` name from a package subpath.
     For example, the asset specification
     ``my.package:static/baz.css`` identifies the file named
     ``baz.css`` in the ``static`` subdirectory of the ``my.package``
     Python :term:`package`.  See :ref:`asset_specifications` for more
     info.

   package
     A directory on disk which contains an ``__init__.py`` file, making
     it recognizable to Python as a location which can be ``import`` -ed.
     A package exists to contain :term:`module` files.

   module
     A Python source file; a file on the filesystem that typically ends with
     the extension ``.py`` or ``.pyc``.  Modules often live in a
     :term:`package`.

   project
     (Setuptools/distutils terminology). A directory on disk which
     contains a ``setup.py`` file and one or more Python packages.  The
     ``setup.py`` file contains code that allows the package(s) to be
     installed, distributed, and tested.

   distribution
     (Setuptools/distutils terminology).  A file representing an
     installable library or application.  Distributions are usually
     files that have the suffix of ``.egg``, ``.tar.gz``, or ``.zip``.
     Distributions are the target of Setuptools-related commands such as
     ``easy_install``.

   entry point
     A :term:`setuptools` indirection, defined within a setuptools
     :term:`distribution` setup.py.  It is usually a name which refers
     to a function somewhere in a package which is held by the
     distribution.

   dotted Python name
     A reference to a Python object by name using a string, in the form
     ``path.to.modulename:attributename``.  Often used in Pyramid and
     setuptools configurations.  A variant is used in dotted names within
     configurator method arguments that name objects (such as the "add_view"
     method's "view" and "context" attributes): the colon (``:``) is not
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
     ``request``: this calling convention is useful for
     traversal-based applications in which a :term:`context` is always
     very important.  A view callable is the primary mechanism by
     which a developer writes user interface code within
     :app:`Pyramid`.  See :ref:`views_chapter` for more information
     about :app:`Pyramid` view callables.

   view configuration
     View configuration is the act of associating a :term:`view callable`
     with configuration information.  This configuration information helps
     map a given :term:`request` to a particular view callable and it can
     influence the response of a view callable.  :app:`Pyramid` views can be
     configured via :term:`imperative configuration`, or by a special
     ``@view_config`` decorator coupled with a :term:`scan`.  See
     :ref:`view_config_chapter` for more information about view
     configuration.

   view name
     The "URL name" of a view, e.g ``index.html``.  If a view is
     configured without a name, its name is considered to be the empty
     string (which implies the :term:`default view`).

   Default view
     The default view of a :term:`resource` is the view invoked when the
     :term:`view name` is the empty string (``''``).  This is the case when
     :term:`traversal` exhausts the path elements in the PATH_INFO of a
     request before it returns a :term:`context` resource.

   virtualenv
     The `virtualenv tool <https://virtualenv.pypa.io/en/latest/>`_ that allows
     one to create virtual environments. In Python 3.3 and greater,
     :term:`venv` is the preferred tool.

     Note: whenever you encounter commands prefixed with ``$VENV`` (Unix)
     or ``%VENV`` (Windows), know that that is the environment variable whose
     value is the root of the virtual environment in question.

   resource
     An object representing a node in the :term:`resource tree` of an
     application.  If :term:`traversal` is used, a resource is an element in
     the resource tree traversed by the system.  When traversal is used, a
     resource becomes the :term:`context` of a :term:`view`.  If :term:`url
     dispatch` is used, a single resource is generated for each request and
     is used as the context resource of a view.

   resource tree
     A nested set of dictionary-like objects, each of which is a
     :term:`resource`.  The act of :term:`traversal` uses the resource tree
     to find a :term:`context` resource.

   domain model
     Persistent data related to your application.  For example, data stored
     in a relational database.  In some applications, the :term:`resource
     tree` acts as the domain model.

   traversal
     The act of descending "up" a tree of resource objects from a root
     resource in order to find a :term:`context` resource.  The
     :app:`Pyramid` :term:`router` performs traversal of resource objects
     when a :term:`root factory` is specified.  See the
     :ref:`traversal_chapter` chapter for more information.  Traversal can be
     performed *instead* of :term:`URL dispatch` or can be combined *with*
     URL dispatch.  See :ref:`hybrid_chapter` for more information about
     combining traversal and URL dispatch (advanced).

   router
     The :term:`WSGI` application created when you start a
     :app:`Pyramid` application.  The router intercepts requests,
     invokes traversal and/or URL dispatch, calls view functions, and
     returns responses to the WSGI server on behalf of your
     :app:`Pyramid` application.

   URL dispatch
     An alternative to :term:`traversal` as a mechanism for locating a
     :term:`context` resource for a :term:`view`.  When you use a
     :term:`route` in your :app:`Pyramid` application via a :term:`route
     configuration`, you are using URL dispatch. See the
     :ref:`urldispatch_chapter` for more information.

   context
     A resource in the resource tree that is found during :term:`traversal`
     or :term:`URL dispatch` based on URL data; if it's found via traversal,
     it's usually a :term:`resource` object that is part of a resource tree;
     if it's found via :term:`URL dispatch`, it's an object manufactured on
     behalf of the route's "factory".  A context resource becomes the subject
     of a :term:`view`, and often has security information attached to
     it.  See the :ref:`traversal_chapter` chapter and the
     :ref:`urldispatch_chapter` chapter for more information about how a URL
     is resolved to a context resource.

   application registry
     A registry of configuration information consulted by
     :app:`Pyramid` while servicing an application.  An application
     registry maps resource types to views, as well as housing other
     application-specific component registrations.  Every
     :app:`Pyramid` application has one (and only one) application
     registry.

   template
     A file with replaceable parts that is capable of representing some
     text, XML, or HTML when rendered.

   location
     The path to an object in a :term:`resource tree`.  See
     :ref:`location_aware` for more information about how to make a resource
     object *location-aware*.

   permission
     A string or Unicode object that represents an action being taken against
     a :term:`context` resource.  A permission is associated with a view name
     and a resource type by the developer.  Resources are decorated with
     security declarations (e.g. an :term:`ACL`), which reference these
     tokens also.  Permissions are used by the active security policy to
     match the view permission against the resources's statements about which
     permissions are granted to which principal in a context in order to
     answer the question "is this user allowed to do this".  Examples of
     permissions: ``read``, or ``view_blog_entries``.

   default permission
     A :term:`permission` which is registered as the default for an
     entire application.  When a default permission is in effect,
     every :term:`view configuration` registered with the system will
     be effectively amended with a ``permission`` argument that will
     require that the executing user possess the default permission in
     order to successfully execute the associated :term:`view
     callable`.

     .. seealso::
        
        See also :ref:`setting_a_default_permission`.

   ACE
     An *access control entry*.  An access control entry is one element
     in an :term:`ACL`.  An access control entry is a three-tuple that
     describes three things: an *action* (one of either ``Allow`` or
     ``Deny``), a :term:`principal` (a string describing a user or
     group), and a :term:`permission`.  For example the ACE, ``(Allow,
     'bob', 'read')`` is a member of an ACL that indicates that the
     principal ``bob`` is allowed the permission ``read`` against the
     resource the ACL is attached to.

   ACL
     An *access control list*.  An ACL is a sequence of :term:`ACE` tuples.
     An ACL is attached to a resource instance.  An example of an ACL is ``[
     (Allow, 'bob', 'read'), (Deny, 'fred', 'write')]``.  If an ACL is
     attached to a resource instance, and that resource is findable via the
     context resource, it will be consulted any active security policy to
     determine whether a particular request can be fulfilled given the
     :term:`authentication` information in the request.

   authentication
     The act of determining that the credentials a user presents
     during a particular request are "good".  Authentication in
     :app:`Pyramid` is performed via an :term:`authentication
     policy`.

   authorization
     The act of determining whether a user can perform a specific action.  In
     pyramid terms, this means determining whether, for a given resource, any
     :term:`principal` (or principals) associated with the request have the
     requisite :term:`permission` to allow the request to continue.
     Authorization in :app:`Pyramid` is performed via its
     :term:`authorization policy`.

   principal
     A *principal* is a string or Unicode object representing an entity,
     typically a user or group. Principals are provided by an
     :term:`authentication policy`. For example, if a user has the
     :term:`userid` `bob`, and is a member of two groups named `group foo` and
     `group bar`, then the request might have information attached to it
     indicating that Bob was represented by three principals: `bob`, `group
     foo` and `group bar`.

   userid
     A *userid* is a string or Unicode object used to identify and authenticate
     a real-world user or client. A userid is supplied to an
     :term:`authentication policy` in order to discover the user's
     :term:`principals <principal>`. In the authentication policies which
     :app:`Pyramid` provides, the default behavior returns the user's userid as
     a principal, but this is not strictly necessary in custom policies that
     define their principals differently.

   authorization policy
     An authorization policy in :app:`Pyramid` terms is a bit of
     code which has an API which determines whether or not the
     principals associated with the request can perform an action
     associated with a permission, based on the information found on the
     :term:`context` resource.

   authentication policy
     An authentication policy in :app:`Pyramid` terms is a bit of
     code which has an API which determines the current
     :term:`principal` (or principals) associated with a request.

   WSGI
     `Web Server Gateway Interface <http://wsgi.readthedocs.org/en/latest/>`_.
     This is a Python standard for connecting web applications to web servers,
     similar to the concept of Java Servlets.  :app:`Pyramid` requires that
     your application be served as a WSGI application.

   middleware
     *Middleware* is a :term:`WSGI` concept.  It is a WSGI component
     that acts both as a server and an application.  Interesting uses
     for middleware exist, such as caching, content-transport
     encoding, and other functions.  See `WSGI.org
     <http://wsgi.readthedocs.org/en/latest/>`_ or `PyPI
     <https://pypi.python.org/pypi>`_ to find middleware for your application.

   pipeline
     The :term:`PasteDeploy` term for a single configuration of a WSGI
     server, a WSGI application, with a set of :term:`middleware` in-between.

   Zope
     `The Z Object Publishing Framework <http://zope.org>`_, a
     full-featured Python web framework.

   Grok
     `A web framework based on Zope 3 <http://grok.zope.org>`_.

   Django
     `A full-featured Python web framework <https://www.djangoproject.com/>`_.

   Pylons
     `A lightweight Python web framework <http://docs.pylonsproject.org/projects/pylons-webframework/en/latest/>`_
     and a predecessor of Pyramid.

   ZODB
      `Zope Object Database <http://www.zodb.org/en/latest/>`_, a persistent
      Python object store.

   WebOb
     `WebOb <http://webob.org>`_ is a WSGI request/response
     library created by Ian Bicking.

   PasteDeploy
     `PasteDeploy <http://pythonpaste.org/deploy/>`_ is a library used by
     :app:`Pyramid` which makes it possible to configure
     :term:`WSGI` components together declaratively within an ``.ini``
     file.  It was developed by Ian Bicking.

   Chameleon
     `chameleon <https://chameleon.readthedocs.org/en/latest/>`_ is an
     attribute language template compiler which supports the :term:`ZPT`
     templating specification. It is written and maintained by Malthe Borch. It
     has several extensions, such as the ability to use bracketed (Mako-style)
     ``${name}`` syntax. It is also much faster than the reference
     implementation of ZPT. :app:`Pyramid` offers Chameleon templating out of
     the box in ZPT and text flavors.

   ZPT
     The `Zope Page Template <http://docs.zope.org/zope2/zope2book/ZPT.html>`_
     templating language.

   METAL
     `Macro Expansion for TAL
     <http://docs.zope.org/zope2/zope2book/AppendixC.html#metal-overview>`_, a
     part of :term:`ZPT` which makes it possible to share common look and feel
     between templates.

   Genshi
     An `XML templating language <https://pypi.python.org/pypi/Genshi/>`_
     by Christopher Lenz.

   Jinja2
     A `text templating language <http://jinja.pocoo.org/>`_ by Armin Ronacher.

   Routes
     A `system by Ben Bangert <http://routes.readthedocs.org/en/latest/>`_
     which parses URLs and compares them against a number of user defined
     mappings. The URL pattern matching syntax in :app:`Pyramid` is inspired by
     the Routes syntax (which was inspired by Ruby On Rails pattern syntax).

   route
     A single pattern matched by the :term:`url dispatch` subsystem,
     which generally resolves to a :term:`root factory` (and then
     ultimately a :term:`view`).

     .. seealso::

        See also :term:`url dispatch`.

   route configuration
     Route configuration is the act of associating request parameters with a
     particular :term:`route` using pattern matching and :term:`route
     predicate` statements.  See :ref:`urldispatch_chapter` for more
     information about route configuration.

   Zope Component Architecture
     The `Zope Component Architecture
     <http://muthukadan.net/docs/zca.html>`_ (aka ZCA) is a system
     which allows for application pluggability and complex dispatching
     based on objects which implement an :term:`interface`.
     :app:`Pyramid` uses the ZCA "under the hood" to perform view
     dispatching and other application configuration tasks.

   reStructuredText
     A `plain text markup format <http://docutils.sourceforge.net/rst.html>`_
     that is the defacto standard for documenting Python projects.
     The Pyramid documentation is written in reStructuredText.

   root
     The object at which :term:`traversal` begins when :app:`Pyramid`
     searches for a :term:`context` resource (for :term:`URL Dispatch`, the
     root is *always* the context resource unless the ``traverse=`` argument
     is used in route configuration).

   subpath
     A list of element "left over" after the :term:`router` has
     performed a successful traversal to a view.  The subpath is a
     sequence of strings, e.g. ``['left', 'over', 'names']``.  Within
     Pyramid applications that use URL dispatch rather than traversal, you
     can use ``*subpath`` in the route pattern to influence the
     subpath.  See :ref:`star_subpath` for more information.

   interface
     A `Zope interface <https://pypi.python.org/pypi/zope.interface>`_
     object.  In :app:`Pyramid`, an interface may be attached to a
     :term:`resource` object or a :term:`request` object in order to
     identify that the object is "of a type".  Interfaces are used
     internally by :app:`Pyramid` to perform view lookups and other
     policy lookups.  The ability to make use of an interface is
     exposed to an application programmers during :term:`view
     configuration` via the ``context`` argument, the ``request_type``
     argument and the ``containment`` argument.  Interfaces are also
     exposed to application developers when they make use of the
     :term:`event` system. Fundamentally, :app:`Pyramid`
     programmers can think of an interface as something that they can
     attach to an object that stamps it with a "type" unrelated to its
     underlying Python type.  Interfaces can also be used to describe
     the behavior of an object (its methods and attributes), but
     unless they choose to, :app:`Pyramid` programmers do not need
     to understand or use this feature of interfaces.

   event
     An object broadcast to zero or more :term:`subscriber` callables
     during normal :app:`Pyramid` system operations during the
     lifetime of an application.  Application code can subscribe to
     these events by using the subscriber functionality described in
     :ref:`events_chapter`.

   subscriber
     A callable which receives an :term:`event`.  A callable becomes a
     subscriber via :term:`imperative configuration` or via
     :term:`configuration decoration`.  See :ref:`events_chapter` for more
     information.

   request type
     An attribute of a :term:`request` that allows for specialization
     of view invocation based on arbitrary categorization.  The every
     :term:`request` object that :app:`Pyramid` generates and
     manipulates has one or more :term:`interface` objects attached to
     it.  The default interface attached to a request object is
     :class:`pyramid.interfaces.IRequest`.

   repoze.lemonade
     Zope2 CMF-like `data structures and helper facilities
     <http://docs.repoze.org/lemonade>`_ for CA-and-ZODB-based
     applications useful within :app:`Pyramid` applications.

   repoze.catalog
     An indexing and search facility (fielded and full-text) based on
     `zope.index <https://pypi.python.org/pypi/zope.index>`_.  See `the
     documentation <http://docs.repoze.org/catalog>`_ for more
     information.

   repoze.who
     `Authentication middleware <http://repozewho.readthedocs.org/en/latest/>`_
     for :term:`WSGI` applications.  It can be used by :app:`Pyramid` to
     provide authentication information.

   repoze.workflow
     `Barebones workflow for Python apps
     <http://docs.repoze.org/workflow>`_ .  It can be used by
     :app:`Pyramid` to form a workflow system.

   virtual root
     A resource object representing the "virtual" root of a request; this is
     typically the :term:`physical root` object unless :ref:`vhosting_chapter`
     is in use.

   physical root
     The object returned by the application :term:`root factory`.
     Unlike the :term:`virtual root` of a request, it is not impacted by
     :ref:`vhosting_chapter`: it will always be the actual object returned by
     the root factory, never a subobject.

   physical path
     The path required by a traversal which resolve a :term:`resource` starting
     from the :term:`physical root`.  For example, the physical path of the
     ``abc`` subobject of the physical root object is ``/abc``.  Physical paths
     can also be specified as tuples where the first element is the empty
     string (representing the root), and every other element is a Unicode
     object, e.g. ``('', 'abc')``.  Physical paths are also sometimes called
     "traversal paths".

   lineage
     An ordered sequence of objects based on a ":term:`location` -aware"
     resource.  The lineage of any given :term:`resource` is composed of
     itself, its parent, its parent's parent, and so on.  The order of the
     sequence is resource-first, then the parent of the resource, then its
     parent's parent, and so on.  The parent of a resource in a lineage is
     available as its ``__parent__`` attribute.

   root factory
     The "root factory" of a :app:`Pyramid` application is called on every
     request sent to the application.  The root factory returns the traversal
     root of an application.  It is conventionally named ``get_root``.  An
     application may supply a root factory to :app:`Pyramid` during the
     construction of a :term:`Configurator`.  If a root factory is not
     supplied, the application creates a default root object using the
     :term:`default root factory`.  

   default root factory
     If an application does not register a :term:`root factory` at Pyramid
     configuration time, a *default* root factory is used to created the
     default root object.  Use of the default root object is useful in
     application which use :term:`URL dispatch` for all URL-to-view code
     mappings, and does not (knowingly) use traversal otherwise.

   SQLAlchemy
     `SQLAlchemy <http://www.sqlalchemy.org/>`_ is an object
     relational mapper used in tutorials within this documentation.

   JSON
     `JavaScript Object Notation <http://www.json.org/>`_ is a data
     serialization format.

   jQuery
     A popular `Javascript library <https://jquery.org>`_.

   renderer
     A serializer which converts non-:term:`Response` return values from a
     :term:`view` into a string, and ultimately into a response, usually
     through :term:`view configuration`. Using a renderer can make writing
     views that require templating or other serialization, like JSON, less
     tedious. See :ref:`views_which_use_a_renderer` for more information.

   renderer factory
     A factory which creates a :term:`renderer`.  See
     :ref:`adding_and_overriding_renderers` for more information.

   mod_wsgi
     `mod_wsgi <https://code.google.com/archive/p/modwsgi>`_ is an Apache
     module developed by Graham Dumpleton.  It allows :term:`WSGI` applications
     (such as applications developed using :app:`Pyramid`) to be served using
     the Apache web server.

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

   routes mapper
     An object which compares path information from a request to an
     ordered set of route patterns.  See :ref:`urldispatch_chapter`.

   predicate
     A test which returns ``True`` or ``False``.  Two different types
     of predicates exist in :app:`Pyramid`: a :term:`view predicate`
     and a :term:`route predicate`.  View predicates are attached to
     :term:`view configuration` and route predicates are attached to
     :term:`route configuration`.

   decorator
     A wrapper around a Python function or class which accepts the
     function or class as its first argument and which returns an
     arbitrary object.  :app:`Pyramid` provides several decorators,
     used for configuration and return value modification purposes.

     .. seealso::
     
        See also `PEP 318 <https://www.python.org/dev/peps/pep-0318/>`_.

   configuration declaration
     An individual method call made to a :term:`configuration directive`,
     such as registering a :term:`view configuration` (via the
     :meth:`~pyramid.config.Configurator.add_view` method of the
     configurator) or :term:`route configuration` (via the
     :meth:`~pyramid.config.Configurator.add_route` method of the
     configurator).  A set of configuration declarations is also implied by
     the :term:`configuration decoration` detected by a :term:`scan` of code
     in a package.

   configuration decoration
     Metadata implying one or more :term:`configuration declaration`
     invocations.  Often set by configuration Python :term:`decorator`
     attributes, such as :class:`pyramid.view.view_config`, aka
     ``@view_config``.

   scan
     The term used by :app:`Pyramid` to define the process of
     importing and examining all code in a Python package or module for
     :term:`configuration decoration`.

   configurator
     An object used to do :term:`configuration declaration` within an
     application.  The most common configurator is an instance of the
     :class:`pyramid.config.Configurator` class.

   imperative configuration
     The configuration mode in which you use Python to call methods on
     a :term:`Configurator` in order to add each :term:`configuration
     declaration` required by your application.

   declarative configuration
     The configuration mode in which you use the combination of
     :term:`configuration decoration` and a :term:`scan` to configure your
     Pyramid application.

   Not Found View
      An :term:`exception view` invoked by :app:`Pyramid` when the developer
      explicitly raises a :class:`pyramid.httpexceptions.HTTPNotFound`
      exception from within :term:`view` code or :term:`root factory` code,
      or when the current request doesn't match any :term:`view
      configuration`.  :app:`Pyramid` provides a default implementation of a
      Not Found View; it can be overridden.  See
      :ref:`changing_the_notfound_view`.

   Forbidden view
      An :term:`exception view` invoked by :app:`Pyramid` when the developer
      explicitly raises a :class:`pyramid.httpexceptions.HTTPForbidden`
      exception from within :term:`view` code or :term:`root factory` code,
      or when the :term:`view configuration` and :term:`authorization policy`
      found for a request disallows a particular view invocation.
      :app:`Pyramid` provides a default implementation of a forbidden view;
      it can be overridden.  See :ref:`changing_the_forbidden_view`.

   Exception view
      An exception view is a :term:`view callable` which may be
      invoked by :app:`Pyramid` when an exception is raised during
      request processing.  See :ref:`exception_views` for more
      information.

   HTTP Exception
      The set of exception classes defined in :mod:`pyramid.httpexceptions`.
      These can be used to generate responses with various status codes when
      raised or returned from a :term:`view callable`.

      .. seealso::

          See also :ref:`http_exceptions`.

   thread local
      A thread-local variable is one which is essentially a global variable
      in terms of how it is accessed and treated, however, each `thread
      <https://en.wikipedia.org/wiki/Thread_(computer_science)>`_ used by the
      application may have a different value for this same "global" variable.
      :app:`Pyramid` uses a small number of thread local variables, as
      described in :ref:`threadlocals_chapter`.

      .. seealso::

          See also the :class:`stdlib documentation <threading.local>`
          for more information.

   multidict
     An ordered dictionary that can have multiple values for each key. Adds
     the methods ``getall``, ``getone``, ``mixed``, ``add`` and
     ``dict_of_lists`` to the normal dictionary interface.  See
     :ref:`multidict_narr` and :class:`pyramid.interfaces.IMultiDict`.

   PyPI
     `The Python Package Index <https://pypi.python.org/pypi>`_, a collection
     of software available for Python.

   Agendaless Consulting
     A consulting organization formed by Paul Everitt, Tres Seaver,
     and Chris McDonough.

     .. seealso::

         See also `Agendaless Consulting <https://agendaless.com>`_.

   Jython
     A `Python implementation <http://www.jython.org/>`_ written for
     the Java Virtual Machine.

   Python
     The `programming language <https://www.python.org>`_ in which
     :app:`Pyramid` is written.

   CPython
     The C implementation of the Python language.  This is the
     reference implementation that most people refer to as simply
     "Python"; :term:`Jython`, Google's App Engine, and `PyPy
     <http://doc.pypy.org/en/latest/>`_ are examples of
     non-C based Python implementations.

   View Lookup
     The act of finding and invoking the "best" :term:`view callable`,
     given a :term:`request` and a :term:`context` resource.

   Resource Location
     The act of locating a :term:`context` resource given a :term:`request`.
     :term:`Traversal` and :term:`URL dispatch` are the resource location
     subsystems used by :app:`Pyramid`.

   Google App Engine
     `Google App Engine <https://cloud.google.com/appengine/>`_ (aka
     "GAE") is a Python application hosting service offered by Google.
     :app:`Pyramid` runs on GAE.

   Venusian
     :ref:`Venusian` is a library which
     allows framework authors to defer decorator actions.  Instead of
     taking actions when a function (or class) decorator is executed
     at import time, the action usually taken by the decorator is
     deferred until a separate "scan" phase.  :app:`Pyramid` relies
     on Venusian to provide a basis for its :term:`scan` feature.

   Translation String
     An instance of :class:`pyramid.i18n.TranslationString`, which
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
     translation domain is represented by a collection of ``.mo`` files
     within one or more :term:`translation directory` directories.

   Translation Context
     A string representing the "context" in which a translation was
     made within a given :term:`translation domain`. See the gettext
     documentation, `11.2.5 Using contexts for solving ambiguities
     <https://www.gnu.org/software/gettext/manual/gettext.html#Contexts>`_
     for more information.

   Translator
     A callable which receives a :term:`translation string` and returns a
     translated Unicode object for the purposes of internationalization.  A
     :term:`localizer` supplies a translator to a :app:`Pyramid` application
     accessible via its :class:`~pyramid.i18n.Localizer.translate` method.

   Translation Directory
     A translation directory is a :term:`gettext` translation
     directory.  It contains language folders, which themselves
     contain ``LC_MESSAGES`` folders, which contain ``.mo`` files.
     Each ``.mo`` file represents a set of translations for a language
     in a :term:`translation domain`.  The name of the ``.mo`` file
     (minus the .mo extension) is the translation domain name.

   Localizer
     An instance of the class :class:`pyramid.i18n.Localizer` which
     provides translation and pluralization services to an
     application.  It is retrieved via the
     :func:`pyramid.i18n.get_localizer` function.

   Locale Name
     A string like ``en``, ``en_US``, ``de``, or ``de_AT`` which
     uniquely identifies a particular locale.

   Default Locale Name
     The :term:`locale name` used by an application when no explicit
     locale name is set.  See :ref:`localization_deployment_settings`.

   Locale Negotiator
     An object supplying a policy determining which :term:`locale
     name` best represents a given :term:`request`.  It is used by the
     :func:`pyramid.i18n.get_locale_name`, and
     :func:`pyramid.i18n.negotiate_locale_name` functions, and
     indirectly by :func:`pyramid.i18n.get_localizer`.  The
     :func:`pyramid.i18n.default_locale_negotiator` function
     is an example of a locale negotiator.

   Gettext
     The GNU `gettext <http://www.gnu.org/software/gettext/>`_
     library, used by the :app:`Pyramid` translation machinery.

   Babel
     A `collection of tools <http://babel.pocoo.org/en/latest/>`_ for
     internationalizing Python applications. :app:`Pyramid` does not depend on
     Babel to operate, but if Babel is installed, additional locale
     functionality becomes available to your application.

   Lingua
     A package by Wichert Akkerman which provides the ``pot-create``
     command to extract translateable messages from Python sources
     and Chameleon ZPT template files.

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
     "internationalization" is I, 18 letters, then N).

     .. seealso::

         See also :term:`Localization`.

   Localization
     The process of displaying the user interface of an
     internationalized application in a particular language or
     cultural context.  Often shortened to "l10" (because the word
     "localization" is L, 10 letters, then N).

     .. seealso::
     
         See also :term:`Internationalization`.

   renderer globals
      Values injected as names into a renderer by a
      :class:`pyramid.event.BeforeRender` event.

   response callback
      A user-defined callback executed by the :term:`router` at a
      point after a :term:`response` object is successfully created.

      .. seealso::

          See also :ref:`using_response_callbacks`.

   finished callback
      A user-defined callback executed by the :term:`router`
      unconditionally at the very end of request processing .  See
      :ref:`using_finished_callbacks`.

   pregenerator
      A pregenerator is a function associated by a developer with a
      :term:`route`.  It is called by
      :meth:`~pyramid.request.Request.route_url` in order to adjust the set
      of arguments passed to it by the user for special purposes.  It will
      influence the URL returned by
      :meth:`~pyramid.request.Request.route_url`.  See
      :class:`pyramid.interfaces.IRoutePregenerator` for more information.

   session
      A namespace that is valid for some period of continual activity
      that can be used to represent a user's interaction with a web
      application.

   session factory
      A callable, which, when called with a single argument named ``request``
      (a :term:`request` object), returns a :term:`session` object.  See
      :ref:`using_the_default_session_factory`,
      :ref:`using_alternate_session_factories` and
      :meth:`pyramid.config.Configurator.set_session_factory` for more
      information.

   Mako
     `Mako <http://www.makotemplates.org/>`_ is a template language
     which refines the familiar ideas of componentized layout and inheritance
     using Python with Python scoping and calling semantics.

   View handler
     A view handler ties together
     :meth:`pyramid.config.Configurator.add_route` and
     :meth:`pyramid.config.Configurator.add_view` to make it more convenient
     to register a collection of views as a single class when using
     :term:`url dispatch`.  View handlers ship as part of the
     :term:`pyramid_handlers` add-on package.

   Deployment settings
     Deployment settings are settings passed to the :term:`Configurator` as a
     ``settings`` argument.  These are later accessible via a
     ``request.registry.settings`` dictionary in views or as
     ``config.registry.settings`` in configuration code.  Deployment settings
     can be used as global application values.

   WebTest
     `WebTest <http://webtest.pythonpaste.org/en/latest/>`_ is a package which can help
     you write functional tests for your WSGI application.

   view mapper
    A view mapper is a class which implements the
    :class:`pyramid.interfaces.IViewMapperFactory` interface, which performs
    view argument and return value mapping.  This is a plug point for
    extension builders, not normally used by "civilians".

   matchdict
    The dictionary attached to the :term:`request` object as
    ``request.matchdict`` when a :term:`URL dispatch` route has been matched.
    Its keys are names as identified within the route pattern; its values are
    the values matched by each pattern name.

   pyramid_zcml
     An add-on package to :app:`Pyramid` which allows applications to be
     configured via :term:`ZCML`.  It is available on :term:`PyPI`.  If you
     use :mod:`pyramid_zcml`, you can use ZCML as an alternative to
     :term:`imperative configuration` or :term:`configuration decoration`.

   ZCML
     `Zope Configuration Markup Language
     <http://muthukadan.net/docs/zca.html#zcml>`_, an XML dialect
     used by Zope and :term:`pyramid_zcml` for configuration tasks.

   pyramid_handlers
     An add-on package which allows :app:`Pyramid` users to create classes
     that are analogues of Pylons 1 "controllers".  See
     http://docs.pylonsproject.org/projects/pyramid_handlers/en/latest/.

   pyramid_jinja2
     :term:`Jinja2` templating system bindings for Pyramid, documented at
     http://docs.pylonsproject.org/projects/pyramid_jinja2/en/latest/.  This
     package also includes a scaffold named ``pyramid_jinja2_starter``, which
     creates an application package based on the Jinja2 templating system.

   Akhet
     `Akhet <http://docs.pylonsproject.org/projects/akhet/en/latest/>`_ is a 
     Pyramid library and demo application with a Pylons-like feel.
     It's most known for its former application scaffold, which helped 
     users transition from Pylons and those preferring a more Pylons-like API.
     The scaffold has been retired but the demo plays a similar role. 

   Pyramid Community Cookbook
     Additional, community-based documentation for Pyramid which presents
     topical, practical uses of Pyramid:
     :ref:`Pyramid Community Cookbook <cookbook:pyramid-cookbook>`

   distutils
     The standard system for packaging and distributing Python packages.  See
     https://docs.python.org/2/distutils/index.html for more information.
     :term:`setuptools` is actually an *extension* of the Distutils.

   exception response
     A :term:`response` that is generated as the result of a raised exception
     being caught by an :term:`exception view`.

   PyPy
     PyPy is an "alternative implementation of the Python
     language": http://pypy.org/

   tween
     A bit of code that sits between the Pyramid router's main request
     handling function and the upstream WSGI component that uses
     :app:`Pyramid` as its 'app'.  The word "tween" is a contraction of
     "between".  A tween may be used by Pyramid framework extensions, to
     provide, for example, Pyramid-specific view timing support, bookkeeping
     code that examines exceptions before they are returned to the upstream
     WSGI application, or a variety of other features.  Tweens behave a bit
     like :term:`WSGI` :term:`middleware` but they have the benefit of running in a
     context in which they have access to the Pyramid :term:`application
     registry` as well as the Pyramid rendering machinery.  See
     :ref:`registering_tweens`.

   pyramid_debugtoolbar
     A Pyramid add-on which displays a helpful debug toolbar "on top of" HTML
     pages rendered by your application, displaying request, routing, and
     database information.  :mod:`pyramid_debugtoolbar` is configured into
     the ``development.ini`` of all applications which use a Pyramid
     :term:`scaffold`.  For more information, see
     http://docs.pylonsproject.org/projects/pyramid_debugtoolbar/en/latest/.

   scaffold
     A project template that generates some of the major parts of a Pyramid
     application and helps users to quickly get started writing larger
     applications.  Scaffolds are usually used via the ``pcreate`` command.

   pyramid_exclog
     A package which logs Pyramid application exception (error) information
     to a standard Python logger.  This add-on is most useful when
     used in production applications, because the logger can be configured to
     log to a file, to UNIX syslog, to the Windows Event Log, or even to
     email. See its `documentation
     <http://docs.pylonsproject.org/projects/pyramid_exclog/en/latest/>`_.

   console script
     A script written to the ``bin`` (on UNIX, or ``Scripts`` on Windows)
     directory of a Python installation or :term:`virtual environment` as the
     result of running ``pip install`` or ``pip install -e .``.

   introspector
     An object with the methods described by
     :class:`pyramid.interfaces.IIntrospector` that is available in both
     configuration code (for registration) and at runtime (for querying) that
     allows a developer to introspect configuration statements and
     relationships between those statements.

   conflict resolution
     Pyramid attempts to resolve ambiguous configuration statements made by
     application developers via automatic conflict resolution.  Automatic
     conflict resolution is described in
     :ref:`automatic_conflict_resolution`.  If Pyramid cannot resolve
     ambiguous configuration statements, it is possible to manually resolve
     them as described in :ref:`manually_resolving_conflicts`.

   configuration directive
     A method of the :term:`Configurator` which causes a configuration action
     to occur.  The method :meth:`pyramid.config.Configurator.add_view` is a
     configuration directive, and application developers can add their own
     directives as necessary (see :ref:`add_directive`).

   action
     Represents a pending configuration statement generated by a call to a
     :term:`configuration directive`.  The set of pending configuration
     actions are processed when :meth:`pyramid.config.Configurator.commit` is
     called.

   discriminator
     The unique identifier of an :term:`action`.

   introspectable
      An object which implements the attributes and methods described in
      :class:`pyramid.interfaces.IIntrospectable`.  Introspectables are used
      by the :term:`introspector` to display configuration information about
      a running Pyramid application.  An introspectable is associated with a
      :term:`action` by virtue of the
      :meth:`pyramid.config.Configurator.action` method.

   asset descriptor
      An instance representing an :term:`asset specification` provided by the
      :meth:`pyramid.path.AssetResolver.resolve` method.  It supports the
      methods and attributes documented in
      :class:`pyramid.interfaces.IAssetDescriptor`.

   Waitress
      A :term:`WSGI` server that runs on UNIX and Windows under Python 2.6+
      and Python 3.2+.  Projects generated via Pyramid scaffolding use
      Waitress as a WGSI server.  See
      http://docs.pylonsproject.org/projects/waitress/en/latest/ for detailed
      information.

   Green Unicorn
      Aka ``gunicorn``, a fast :term:`WSGI` server that runs on UNIX under
      Python 2.6+ or Python 3.1+.  See http://gunicorn.org/ for detailed 
      information.

   predicate factory
      A callable which is used by a third party during the registration of a
      route, view, or subscriber predicates to extend the configuration
      system.  See :ref:`registering_thirdparty_predicates` for more
      information.

   add-on
      A Python :term:`distribution` that uses Pyramid's extensibility
      to plug into a Pyramid application and provide extra,
      configurable services.

   pyramid_redis_sessions
      A package by Eric Rasmussen which allows you to store Pyramid session 
      data in a Redis database.  See 
      https://pypi.python.org/pypi/pyramid_redis_sessions for more information.

   cache busting
      A technique used when serving a cacheable static asset in order to force
      a client to query the new version of the asset. See :ref:`cache_busting`
      for more information.

   view deriver
      A view deriver is a composable component of the view pipeline which is
      used to create a :term:`view callable`. A view deriver is a callable
      implementing the :class:`pyramid.interfaces.IViewDeriver` interface.
      Examples of built-in derivers including view mapper, the permission
      checker, and applying a renderer to a dictionary returned from the view.

   truthy string
      A string represeting a value of ``True``. Acceptable values are
      ``t``, ``true``, ``y``, ``yes``, ``on`` and ``1``.

   falsey string
      A string represeting a value of ``False``. Acceptable values are
      ``f``, ``false``, ``n``, ``no``, ``off`` and ``0``.

   pip
      The :term:`Python Packaging Authority`'s recommended tool for installing
      Python packages.

   pyvenv
      The :term:`Python Packaging Authority` formerly recommended using the
      ``pyvenv`` command for `creating virtual environments on Python 3.4 and
      3.5
      <https://packaging.python.org/en/latest/installing/#creating-virtual-environments>`_,
      but it was deprecated in 3.6 in favor of ``python3 -m venv`` on UNIX or
      ``python -m venv`` on Windows, which is backward compatible on Python
      3.3 and greater.

   virtual environment
      An isolated Python environment that allows packages to be installed for
      use by a particular application, rather than being installed system wide.

   venv
      The :term:`Python Packaging Authority`'s recommended tool for creating
      virtual environments on Python 3.3 and greater.

      Note: whenever you encounter commands prefixed with ``$VENV`` (Unix)
      or ``%VENV`` (Windows), know that that is the environment variable whose
      value is the root of the virtual environment in question.

   Python Packaging Authority
      The `Python Packaging Authority (PyPA) <https://www.pypa.io/en/latest/>`_
      is a working group that maintains many of the relevant projects in Python
      packaging.