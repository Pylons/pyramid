.. _resources_chapter:

Resources
=========

A :term:`resource` is an object that represents a "place" in a tree related to
your application.  Every :app:`Pyramid` application has at least one resource
object: the :term:`root` resource.  Even if you don't define a root resource
manually, a default one is created for you.  The root resource is the root of a
:term:`resource tree`.  A resource tree is a set of nested dictionary-like
objects which you can use to represent your website's structure.

In an application which uses :term:`traversal` to map URLs to code, the
resource tree structure is used heavily to map each URL to a :term:`view
callable`.  When :term:`traversal` is used, :app:`Pyramid` will walk through
the resource tree by traversing through its nested dictionary structure in
order to find a :term:`context` resource.  Once a context resource is found,
the context resource and data in the request will be used to find a :term:`view
callable`.

In an application which uses :term:`URL dispatch`, the resource tree is only
used indirectly, and is often "invisible" to the developer.  In URL dispatch
applications, the resource "tree" is often composed of only the root resource
by itself.  This root resource sometimes has security declarations attached to
it, but is not required to have any.  In general, the resource tree is much
less important in applications that use URL dispatch than applications that use
traversal.

In "Zope-like" :app:`Pyramid` applications, resource objects also often store
data persistently, and offer methods related to mutating that persistent data.
In these kinds of applications, resources not only represent the site structure
of your website, but they become the :term:`domain model` of the application.

Also:

- The ``context`` and ``containment`` predicate arguments to
  :meth:`~pyramid.config.Configurator.add_view` (or a
  :func:`~pyramid.view.view_config` decorator) reference a resource class or
  resource :term:`interface`.

- A :term:`root factory` returns a resource.

- A resource is exposed to :term:`view` code as the :term:`context` of a view.

- Various helpful :app:`Pyramid` API methods expect a resource as an argument
  (e.g., :meth:`~pyramid.request.Request.resource_url` and others).

.. index::
   single: resource tree
   single: traversal tree
   single: object tree
   single: container resources
   single: leaf resources

Defining a Resource Tree
------------------------

When :term:`traversal` is used (as opposed to a purely :term:`URL dispatch`
based application), :app:`Pyramid` expects to be able to traverse a tree
composed of resources (the :term:`resource tree`).  Traversal begins at a root
resource, and descends into the tree recursively, trying each resource's
``__getitem__`` method to resolve a path segment to another resource object.
:app:`Pyramid` imposes the following policy on resource instances in the tree:

- A container resource (a resource which contains other resources) must supply
  a ``__getitem__`` method which is willing to resolve a Unicode name to a
  sub-resource.  If a sub-resource by a particular name does not exist in a
  container resource, the ``__getitem__`` method of the container resource must
  raise a :exc:`KeyError`.  If a sub-resource by that name *does* exist, the
  container's ``__getitem__`` should return the sub-resource.

- Leaf resources, which do not contain other resources, must not implement a
  ``__getitem__``, or if they do, their ``__getitem__`` method must always
  raise a :exc:`KeyError`.

See :ref:`traversal_chapter` for more information about how traversal works
against resource instances.

Here's a sample resource tree, represented by a variable named ``root``:

.. code-block:: python
    :linenos:

    class Resource(dict):
        pass

    root = Resource({'a':Resource({'b':Resource({'c':Resource()})})})

The resource tree we've created above is represented by a dictionary-like root
object which has a single child named ``'a'``.  ``'a'`` has a single child
named ``'b'``, and ``'b'`` has a single child named ``'c'``, which has no
children. It is therefore possible to access the ``'c'`` leaf resource like so:

.. code-block:: python
   :linenos:

   root['a']['b']['c']

If you returned the above ``root`` object from a :term:`root factory`, the path
``/a/b/c`` would find the ``'c'`` object in the resource tree as the result of
:term:`traversal`.

In this example, each of the resources in the tree is of the same class. This
is not a requirement.  Resource elements in the tree can be of any type. We
used a single class to represent all resources in the tree for the sake of
simplicity, but in a "real" app, the resources in the tree can be arbitrary.

Although the example tree above can service a traversal, the resource instances
in the above example are not aware of :term:`location`, so their utility in a
"real" application is limited.  To make best use of built-in :app:`Pyramid` API
facilities, your resources should be "location-aware". The next section details
how to make resources location-aware.

.. index::
   pair: location-aware; resource

.. _location_aware:

Location-Aware Resources
------------------------

In order for certain :app:`Pyramid` location, security, URL-generation, and
traversal APIs to work properly against the resources in a resource tree, all
resources in the tree must be :term:`location`-aware.  This means they must
have two attributes: ``__parent__`` and ``__name__``.

The ``__parent__`` attribute of a location-aware resource should be a reference
to the resource's parent resource instance in the tree.  The ``__name__``
attribute should be the name with which a resource's parent refers to the
resource via ``__getitem__``.

The ``__parent__`` of the root resource should be ``None`` and its ``__name__``
should be the empty string.  For instance:

.. code-block:: python
   :linenos:

   class MyRootResource(object):
       __name__ = ''
       __parent__ = None

A resource returned from the root resource's ``__getitem__`` method should have
a ``__parent__`` attribute that is a reference to the root resource, and its
``__name__`` attribute should match the name by which it is reachable via the
root resource's ``__getitem__``.  A container resource within the root resource
should have a ``__getitem__`` that returns resources with a ``__parent__``
attribute that points at the container, and these sub-objects should have a
``__name__`` attribute that matches the name by which they are retrieved from
the container via ``__getitem__``.  This pattern continues recursively "up" the
tree from the root.

The ``__parent__`` attributes of each resource form a linked list that points
"downwards" toward the root. This is analogous to the ``..`` entry in
filesystem directories. If you follow the ``__parent__`` values from any
resource in the resource tree, you will eventually come to the root resource,
just like if you keep executing the ``cd ..`` filesystem command, eventually
you will reach the filesystem root directory.

.. warning::

   If your root resource has a ``__name__`` argument that is not ``None`` or
   the empty string, URLs returned by the
   :func:`~pyramid.request.Request.resource_url` function, and paths generated
   by the :func:`~pyramid.traversal.resource_path` and
   :func:`~pyramid.traversal.resource_path_tuple` APIs, will be generated
   improperly.  The value of ``__name__`` will be prepended to every path and
   URL generated (as opposed to a single leading slash or empty tuple element).

.. sidebar:: For your convenience

  If you'd rather not manage the ``__name__`` and ``__parent__`` attributes of
  your resources "by hand", an add-on package named
  :mod:`pyramid_traversalwrapper` can help.

  In order to use this helper feature, you must first install the
  :mod:`pyramid_traversalwrapper` package (available via PyPI), then register
  its ``ModelGraphTraverser`` as the traversal policy, rather than the default
  :app:`Pyramid` traverser. The package contains instructions for doing so.

  Once :app:`Pyramid` is configured with this feature, you will no longer need
  to manage the ``__parent__`` and ``__name__`` attributes on resource objects
  "by hand".  Instead, as necessary during traversal, :app:`Pyramid` will wrap
  each resource (even the root resource) in a ``LocationProxy``, which will
  dynamically assign a ``__name__`` and a ``__parent__`` to the traversed
  resource, based on the last traversed resource and the name supplied to
  ``__getitem__``.  The root resource will have a ``__name__`` attribute of
  ``None`` and a ``__parent__`` attribute of ``None``.

Applications which use tree-walking :app:`Pyramid` APIs require location-aware
resources.  These APIs include (but are not limited to)
:meth:`~pyramid.request.Request.resource_url`,
:func:`~pyramid.traversal.find_resource`, :func:`~pyramid.traversal.find_root`,
:func:`~pyramid.traversal.find_interface`,
:func:`~pyramid.traversal.resource_path`,
:func:`~pyramid.traversal.resource_path_tuple`,
:func:`~pyramid.traversal.traverse`, :func:`~pyramid.traversal.virtual_root`,
and (usually) :meth:`~pyramid.request.Request.has_permission` and
:func:`~pyramid.security.principals_allowed_by_permission`.

In general, since so much :app:`Pyramid` infrastructure depends on
location-aware resources, it's a good idea to make each resource in your tree
location-aware.

.. index::
   single: resource_url
   pair: generating; resource url

.. _generating_the_url_of_a_resource:

Generating the URL of a Resource
--------------------------------

If your resources are :term:`location`-aware, you can use the
:meth:`pyramid.request.Request.resource_url` API to generate a URL for the
resource.  This URL will use the resource's position in the parent tree to
create a resource path, and it will prefix the path with the current
application URL to form a fully-qualified URL with the scheme, host, port, and
path.  You can also pass extra arguments to
:meth:`~pyramid.request.Request.resource_url` to influence the generated URL.

The simplest call to :meth:`~pyramid.request.Request.resource_url` looks like
this:

.. code-block:: python
   :linenos:

   url = request.resource_url(resource)

The ``request`` in the above example is an instance of a :app:`Pyramid`
:term:`request` object.

If the resource referred to as ``resource`` in the above example was the root
resource, and the host that was used to contact the server was ``example.com``,
the URL generated would be ``http://example.com/``. However, if the resource
was a child of the root resource named ``a``, the generated URL would be
``http://example.com/a/``.

A slash is appended to all resource URLs when
:meth:`~pyramid.request.Request.resource_url` is used to generate them in this
simple manner, because resources are "places" in the hierarchy, and URLs are
meant to be clicked on to be visited.  Relative URLs that you include on HTML
pages rendered as the result of the default view of a resource are more apt to
be relative to these resources than relative to their parent.

You can also pass extra elements to
:meth:`~pyramid.request.Request.resource_url`:

.. code-block:: python
   :linenos:

   url = request.resource_url(resource, 'foo', 'bar')

If the resource referred to as ``resource`` in the above example was the root
resource, and the host that was used to contact the server was ``example.com``,
the URL generated would be ``http://example.com/foo/bar``. Any number of extra
elements can be passed to :meth:`~pyramid.request.Request.resource_url` as
extra positional arguments. When extra elements are passed, they are appended
to the resource's URL.  A slash is not appended to the final segment when
elements are passed.

You can also pass a query string:

.. code-block:: python
   :linenos:

   url = request.resource_url(resource, query={'a':'1'})

If the resource referred to as ``resource`` in the above example was the root
resource, and the host that was used to contact the server was ``example.com``,
the URL generated would be ``http://example.com/?a=1``.

When a :term:`virtual root` is active, the URL generated by
:meth:`~pyramid.request.Request.resource_url` for a resource may be "shorter"
than its physical tree path.  See :ref:`virtual_root_support` for more
information about virtually rooting a resource.

For more information about generating resource URLs, see the documentation for
:meth:`pyramid.request.Request.resource_url`.

.. index::
   pair: resource URL generation; overriding

.. _overriding_resource_url_generation:

Overriding Resource URL Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a resource object implements a ``__resource_url__`` method, this method will
be called when :meth:`~pyramid.request.Request.resource_url` is called to
generate a URL for the resource, overriding the default URL returned for the
resource by :meth:`~pyramid.request.Request.resource_url`.

The ``__resource_url__`` hook is passed two arguments: ``request`` and
``info``.  ``request`` is the :term:`request` object passed to
:meth:`~pyramid.request.Request.resource_url`.  ``info`` is a dictionary with
the following keys:

``physical_path``
   A string representing the "physical path" computed for the resource, as
   defined by ``pyramid.traversal.resource_path(resource)``.  It will begin and
   end with a slash.

``virtual_path``
   A string representing the "virtual path" computed for the resource, as
   defined by :ref:`virtual_root_support`.  This will be identical to the
   physical path if virtual rooting is not enabled.  It will begin and end with
   a slash.

``app_url``
  A string representing the application URL generated during
  ``request.resource_url``.  It will not end with a slash.  It represents a
  potentially customized URL prefix, containing potentially custom scheme, host
  and port information passed by the user to ``request.resource_url``.  It
  should be preferred over use of ``request.application_url``.

The ``__resource_url__`` method of a resource should return a string
representing a URL.  If it cannot override the default, it should return
``None``.  If it returns ``None``, the default URL will be returned.

Here's an example ``__resource_url__`` method.

.. code-block:: python
   :linenos:

   class Resource(object):
       def __resource_url__(self, request, info):
           return info['app_url'] + info['virtual_path']

The above example actually just generates and returns the default URL, which
would have been what was generated by the default ``resource_url`` machinery,
but your code can perform arbitrary logic as necessary.  For example, your code
may wish to override the hostname or port number of the generated URL.

Note that the URL generated by ``__resource_url__`` should be fully qualified,
should end in a slash, and should not contain any query string or anchor
elements (only path elements) to work with
:meth:`~pyramid.request.Request.resource_url`.

.. index::
   single: resource path generation

Generating the Path To a Resource
---------------------------------

:func:`pyramid.traversal.resource_path` returns a string object representing
the absolute physical path of the resource object based on its position in the
resource tree.  Each segment of the path is separated with a slash character.

.. code-block:: python
   :linenos:

   from pyramid.traversal import resource_path
   url = resource_path(resource)

If ``resource`` in the example above was accessible in the tree as
``root['a']['b']``, the above example would generate the string ``/a/b``.

Any positional arguments passed in to :func:`~pyramid.traversal.resource_path`
will be appended as path segments to the end of the resource path.

.. code-block:: python
   :linenos:

   from pyramid.traversal import resource_path
   url = resource_path(resource, 'foo', 'bar')

If ``resource`` in the example above was accessible in the tree as
``root['a']['b']``, the above example would generate the string
``/a/b/foo/bar``.

The resource passed in must be :term:`location`-aware.

The presence or absence of a :term:`virtual root` has no impact on the behavior
of :func:`~pyramid.traversal.resource_path`.

.. index::
   pair: resource; finding by path

Finding a Resource by Path
--------------------------

If you have a string path to a resource, you can grab the resource from that
place in the application's resource tree using
:func:`pyramid.traversal.find_resource`.

You can resolve an absolute path by passing a string prefixed with a ``/`` as
the ``path`` argument:

.. code-block:: python
   :linenos:

   from pyramid.traversal import find_resource
   url = find_resource(anyresource, '/path')

Or you can resolve a path relative to the resource that you pass in to
:func:`pyramid.traversal.find_resource` by passing a string that isn't prefixed
by ``/``:

.. code-block:: python
   :linenos:

   from pyramid.traversal import find_resource
   url = find_resource(anyresource, 'path')

Often the paths you pass to :func:`~pyramid.traversal.find_resource` are
generated by the :func:`~pyramid.traversal.resource_path` API.  These APIs are
"mirrors" of each other.

If the path cannot be resolved when calling
:func:`~pyramid.traversal.find_resource` (if the respective resource in the
tree does not exist), a :exc:`KeyError` will be raised.

See the :func:`pyramid.traversal.find_resource` documentation for more
information about resolving a path to a resource.

.. index::
   pair: resource; lineage

Obtaining the Lineage of a Resource
-----------------------------------

:func:`pyramid.location.lineage` returns a generator representing the
:term:`lineage` of the :term:`location`-aware :term:`resource` object.

The :func:`~pyramid.location.lineage` function returns the resource that is
passed into it, then each parent of the resource in order.  For example, if the
resource tree is composed like so:

.. code-block:: python
   :linenos:

   class Thing(object): pass

   thing1 = Thing()
   thing2 = Thing()
   thing2.__parent__ = thing1

Calling ``lineage(thing2)`` will return a generator.  When we turn it into a
list, we will get:

.. code-block:: python
   :linenos:

   list(lineage(thing2))
   [ <Thing object at thing2>, <Thing object at thing1> ]

The generator returned by :func:`~pyramid.location.lineage` first returns
unconditionally the resource that was passed into it.  Then, if the resource
supplied a ``__parent__`` attribute, it returns the resource represented by
``resource.__parent__``.  If *that* resource has a ``__parent__`` attribute, it
will return that resource's parent, and so on, until the resource being
inspected either has no ``__parent__`` attribute or has a ``__parent__``
attribute of ``None``.

See the documentation for :func:`pyramid.location.lineage` for more
information.

Determining if a Resource is in the Lineage of Another Resource
---------------------------------------------------------------

Use the :func:`pyramid.location.inside` function to determine if one resource
is in the :term:`lineage` of another resource.

For example, if the resource tree is:

.. code-block:: python
   :linenos:

   class Thing(object): pass

   a = Thing()
   b = Thing()
   b.__parent__ = a

Calling ``inside(b, a)`` will return ``True``, because ``b`` has a lineage that
includes ``a``.  However, calling ``inside(a, b)`` will return ``False``
because ``a`` does not have a lineage that includes ``b``.

The argument list for :func:`~pyramid.location.inside` is ``(resource1,
resource2)``.  ``resource1`` is "inside" ``resource2`` if ``resource2`` is a
:term:`lineage` ancestor of ``resource1``.  It is a lineage ancestor if its
parent (or one of its parent's parents, etc.) is an ancestor.

See :func:`pyramid.location.inside` for more information.

.. index::
   pair: resource; finding root

Finding the Root Resource
-------------------------

Use the :func:`pyramid.traversal.find_root` API to find the :term:`root`
resource.  The root resource is the resource at the root of the :term:`resource
tree`. The API accepts a single argument: ``resource``.  This is a resource
that is :term:`location`-aware.  It can be any resource in the tree for which
you want to find the root.

For example, if the resource tree is:

.. code-block:: python
   :linenos:

   class Thing(object): pass

   a = Thing()
   b = Thing()
   b.__parent__ = a

Calling ``find_root(b)`` will return ``a``.

The root resource is also available as ``request.root`` within :term:`view
callable` code.

The presence or absence of a :term:`virtual root` has no impact on the behavior
of :func:`~pyramid.traversal.find_root`.  The root object returned is always
the *physical* root object.

.. index::
   single: resource interfaces

.. _resources_which_implement_interfaces:

Resources Which Implement Interfaces
------------------------------------

Resources can optionally be made to implement an :term:`interface`.  An
interface is used to tag a resource object with a "type" that later can be
referred to within :term:`view configuration` and by
:func:`pyramid.traversal.find_interface`.

Specifying an interface instead of a class as the ``context`` or
``containment`` predicate arguments within :term:`view configuration`
statements makes it possible to use a single view callable for more than one
class of resource objects.  If your application is simple enough that you see
no reason to want to do this, you can skip reading this section of the chapter.

For example, here's some code which describes a blog entry which also declares
that the blog entry implements an :term:`interface`.

.. code-block:: python
   :linenos:

   import datetime
   from zope.interface import implementer
   from zope.interface import Interface

   class IBlogEntry(Interface):
       pass

   @implementer(IBlogEntry)
   class BlogEntry(object):
       def __init__(self, title, body, author):
           self.title = title
           self.body = body
           self.author = author
           self.created = datetime.datetime.now()

This resource consists of two things: the class which defines the resource
constructor as the class ``BlogEntry``, and an :term:`interface` attached to
the class via an ``implementer`` class decorator using the ``IBlogEntry``
interface as its sole argument.

The interface object used must be an instance of a class that inherits from
:class:`zope.interface.Interface`.

A resource class may implement zero or more interfaces.  You specify that a
resource implements an interface by using the
:func:`zope.interface.implementer` function as a class decorator.  The above
``BlogEntry`` resource implements the ``IBlogEntry`` interface.

You can also specify that a particular resource *instance* provides an
interface as opposed to its class.  When you declare that a class implements an
interface, all instances of that class will also provide that interface.
However, you can also just say that a single object provides the interface. To
do so, use the :func:`zope.interface.directlyProvides` function:

.. code-block:: python
   :linenos:

   import datetime
   from zope.interface import directlyProvides
   from zope.interface import Interface

   class IBlogEntry(Interface):
       pass

   class BlogEntry(object):
       def __init__(self, title, body, author):
           self.title = title
           self.body = body
           self.author = author
           self.created = datetime.datetime.now()

   entry = BlogEntry('title', 'body', 'author')
   directlyProvides(entry, IBlogEntry)

:func:`zope.interface.directlyProvides` will replace any existing interface
that was previously provided by an instance.  If a resource object already has
instance-level interface declarations that you don't want to replace, use the
:func:`zope.interface.alsoProvides` function:

.. code-block:: python
   :linenos:

   import datetime
   from zope.interface import alsoProvides
   from zope.interface import directlyProvides
   from zope.interface import Interface

   class IBlogEntry1(Interface):
       pass

   class IBlogEntry2(Interface):
       pass

   class BlogEntry(object):
       def __init__(self, title, body, author):
           self.title = title
           self.body = body
           self.author = author
           self.created = datetime.datetime.now()

   entry = BlogEntry('title', 'body', 'author')
   directlyProvides(entry, IBlogEntry1)
   alsoProvides(entry, IBlogEntry2)

:func:`zope.interface.alsoProvides` will augment the set of interfaces directly
provided by an instance instead of overwriting them like
:func:`zope.interface.directlyProvides` does.

For more information about how resource interfaces can be used by view
configuration, see :ref:`using_resource_interfaces`.

.. index::
   pair: resource; finding by interface or class

Finding a Resource with a Class or Interface in Lineage
-------------------------------------------------------

Use the :func:`~pyramid.traversal.find_interface` API to locate a parent that
is of a particular Python class, or which implements some :term:`interface`.

For example, if your resource tree is composed as follows:

.. code-block:: python
   :linenos:

   class Thing1(object): pass
   class Thing2(object): pass

   a = Thing1()
   b = Thing2()
   b.__parent__ = a

Calling ``find_interface(a, Thing1)`` will return the ``a`` resource because
``a`` is of class ``Thing1`` (the resource passed as the first argument is
considered first, and is returned if the class or interface specification
matches).

Calling ``find_interface(b, Thing1)`` will return the ``a`` resource because
``a`` is of class ``Thing1`` and ``a`` is the first resource in ``b``'s lineage
of this class.

Calling ``find_interface(b, Thing2)`` will return the ``b`` resource.

The second argument to ``find_interface`` may also be a :term:`interface`
instead of a class.  If it is an interface, each resource in the lineage is
checked to see if the resource implements the specificed interface (instead of
seeing if the resource is of a class).

.. seealso::

    See also :ref:`resources_which_implement_interfaces`.

.. index::
   single: resource API functions
   single: url generation (traversal)

:app:`Pyramid` API Functions That Act Against Resources
-------------------------------------------------------

A resource object is used as the :term:`context` provided to a view.  See
:ref:`traversal_chapter` and :ref:`urldispatch_chapter` for more information
about how a resource object becomes the context.

The APIs provided by :ref:`traversal_module` are used against resource objects.
These functions can be used to find the "path" of a resource, the root resource
in a resource tree, or to generate a URL for a resource.

The APIs provided by :ref:`location_module` are used against resources. These
can be used to walk down a resource tree, or conveniently locate one resource
"inside" another.

Some APIs on the :class:`pyramid.request.Request` accept a resource object as a
parameter. For example, the :meth:`~pyramid.request.Request.has_permission` API
accepts a resource object as one of its arguments; the ACL is obtained from
this resource or one of its ancestors.  Other security related APIs on the
:class:`pyramid.request.Request` class also accept :term:`context` as an
argument, and a context is always a resource.
