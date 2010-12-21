Resources
=========

A :term:`resource` is an object that represents a "place" in your
application.  Every :app:`Pyramid` application has at least one resource
object: the :term:`root` resource.  The root resource is the root of a
:term:`resource tree`.  A resource tree is a set of nested dictionary-like
objects which you can use to represent your website's structure.

In an application which uses :term:`traversal` to map URLs to code, the
resource tree structure is used heavily to map a URL to a :term:`view
callable`.  :app:`Pyramid` will walk "up" the resource tree by traversing
through the nested dictionary structure of the tree when :term:`traversal` is
used in order to find a :term:`context` resource.  Once a context resource is
found, the context resource and data in the request will be used to find a
:term:`view callable`.

In an application which uses :term:`URL dispatch`, the resource tree is only
used indirectly, and is often "invisible" to the developer.  In URL dispatch
applications, the resource "tree" is often composed of only the root resource
by itself.  This root resource sometimes has security declarations attached
to it, but is not required to have any.  In general, the resource tree is
much less important in applications that use URL dispatch than applications
that use traversal.

In "Zope-like" :app:`Pyramid` applications, resource objects also often store
data persistently and offer methods related to mutating that persistent data.
In these kinds of applications, resources not only represent the site
structure of your website, but they become the :term:`domain model` of the
application.

Also:

- The ``context`` and ``containment`` predicate arguments to
  :meth:`pyramid.config.Configurator.add_view` (or a
  :func:`pyramid.view.view_config` decorator) and reference a resource class
  or resource :term:`interface`.

- A :term:`root factory` returns a resource.

- A resource is exposed to :term:`view` code as the :term:`context` of a
  view.

- Various helpful :app:`Pyramid` API methods expect a resource as an
  argument (e.g. :func:`pyramid.url.resource_url` and others).

.. index::
   single: resource tree
   single: traversal tree
   single: object tree
   single: container resources
   single: leaf resources

Defining a Resource Tree
------------------------

When :term:`traversal` is used (as opposed to a purely :term:`url dispatch`
based application), :app:`Pyramid` expects to be able to traverse a tree
composed of resources (the :term:`resource tree`).  Traversal begins at a
root resource, and descends into the tree recursively, trying each resource's
``__getitem__`` method to resolve a path segment to another resource object.
:app:`Pyramid` imposes the following policy on resource instances in the
tree:

- A container resource (a resource which contains other resources) must
  supply a ``__getitem__`` method which is willing to resolve a unicode name
  to a sub-resource.  If a sub-resource by a particular name does not exist
  in a container resource, ``__getitem__`` method of the container resource
  must raise a :exc:`KeyError`.  If a sub-resource by that name *does* exist,
  the container's ``__getitem__`` should return the sub-resource.

- Leaf resources, which do not contain other resources, must not implement a
  ``__getitem__``, or if they do, their ``__getitem__`` method must raise a
  :exc:`KeyError`.

See :ref:`traversal_chapter` for more information about how traversal
works against resource instances.

Here's a sample resource tree, represented by a variable named ``root``:

.. code-block:: python
   :linenos:

    class Resource(dict):
        pass

    root = Resource({'a':Resource({'b':Resource({'c':Resource()})})})

The resource tree we've created above is represented by a dictionary-like
root object which has a single child named ``a``.  ``a`` has a single child
named ``b``, and ``b`` has a single child named ``c``, which has no children.
It is therefore possible to access ``c`` like so:

.. code-block:: python
   :linenos:

   root['a']['b']['c']

If you returned the above ``root`` object from a :term:`root factory`, the
path ``/a/b/c`` would find the ``c`` object in the resource tree as the
result of :term:`traversal`.

In this example, each of the resources in the tree is of the same class.
This is not a requirement.  Resource elements in the tree can be of any type.
We used a single class to represent all resources in the tree for the sake of
simplicity, but in a "real" app, the resources in the tree can be arbitrary.

Although the example tree above can service a traversal, the resource
instances in the above example are not aware of :term:`location`, so their
utility in a "real" application is limited.  To make best use of built-in
:app:`Pyramid` API facilities, your resources should be "location-aware".
The next section details how to make resources location-aware.

.. index::
   pair: location-aware; resource

.. _location_aware:

Location-Aware Resources
------------------------

In order for certain :app:`Pyramid` location, security, URL-generation, and
traversal APIs to work properly against the resources in a resource tree, all
resources in the tree must be :term:`location` -aware.  This means they must
have two attributes: ``__parent__`` and ``__name__``.

The ``__parent__`` attribute of a location-aware resource should be a
reference to the resource's parent resource instance in the tree.  The
``__name__`` attribute should be the name with which a resource's parent
refers to the resource via ``__getitem__``.

The ``__parent__`` of the root resource should be ``None`` and its
``__name__`` should be the empty string.  For instance:

.. code-block:: python
   :linenos:

   class MyRootResource(object):
       __name__ = ''
       __parent__ = None

A resource returned from the root resource's ``__getitem__`` method should
have a ``__parent__`` attribute that is a reference to the root resource, and
its ``__name__`` attribute should match the name by which it is reachable via
the root resource's ``__getitem__``.  A container resource within the root
resource should have a ``__getitem__`` that returns resources with a
``__parent__`` attribute that points at the container, and these subobjects
should have a ``__name__`` attribute that matches the name by which they are
retrieved from the container via ``__getitem__``.  This pattern continues
recursively "up" the tree from the root.

The ``__parent__`` attributes of each resource form a linked list that points
"upward" toward the root. This is analogous to the `..` entry in filesystem
directories. If you follow the ``__parent__`` values from any resource in the
resource tree, you will eventually come to the root resource, just like if
you keep executing the ``cd ..`` filesystem command, eventually you will
reach the filesystem root directory.

.. warning:: If your root resource has a ``__name__`` argument
   that is not ``None`` or the empty string, URLs returned by the
   :func:`pyramid.url.resource_url` function and paths generated by
   the :func:`pyramid.traversal.resource_path` and
   :func:`pyramid.traversal.resource_path_tuple` APIs will be
   generated improperly.  The value of ``__name__`` will be prepended
   to every path and URL generated (as opposed to a single leading
   slash or empty tuple element).

.. sidebar::  Using :mod:`pyramid_traversalwrapper`

  If you'd rather not manage the ``__name__`` and ``__parent__`` attributes
  of your resources "by hand", an add-on package named
  :mod:`pyramid_traversalwrapper` can help.

  In order to use this helper feature, you must first install the
  :mod:`pyramid_traversalwrapper` package (available via PyPI), then register
  its ``ModelGraphTraverser`` as the traversal policy, rather than the
  default :app:`Pyramid` traverser. The package contains instructions for
  doing so.

  Once :app:`Pyramid` is configured with this feature, you will no longer
  need to manage the ``__parent__`` and ``__name__`` attributes on resource
  objects "by hand".  Instead, as necessary, during traversal :app:`Pyramid`
  will wrap each resource (even the root resource) in a ``LocationProxy``
  which will dynamically assign a ``__name__`` and a ``__parent__`` to the
  traversed resrouce (based on the last traversed resource and the name
  supplied to ``__getitem__``).  The root resource will have a ``__name__``
  attribute of ``None`` and a ``__parent__`` attribute of ``None``.

Applications which use tree-walking :app:`Pyramid` APIs require
location-aware resources.  These APIs include (but are not limited to)
:func:`~pyramid.url.resource_url`, :func:`~pyramid.traversal.find_resource`,
:func:`~pyramid.traversal.find_root`,
:func:`~pyramid.traversal.find_interface`,
:func:`~pyramid.traversal.resource_path`,
:func:`~pyramid.traversal.resource_path_tuple`, or
:func:`~pyramid.traversal.traverse`, :func:`~pyramid.traversal.virtual_root`,
and (usually) :func:`~pyramid.security.has_permission` and
:func:`~pyramid.security.principals_allowed_by_permission`.

In general, since so much :app:`Pyramid` infrastructure depends on
location-aware resources, it's a good idea to make each resource in your tree
location-aware, even though location-awareness is not a prerequisite for
plain traversal.

.. index::
   single: resource interfaces

.. _resources_which_implement_interfaces:

Resources Which Implement Interfaces
------------------------------------

Resources can optionally be made to implement an :term:`interface`.  An
interface is used to tag a resource object with a "type" that can later be
referred to within :term:`view configuration`.

Specifying an interface instead of a class as the ``context`` or
``containment`` predicate arguments within :term:`view configuration`
statements effectively makes it possible to use a single view callable for
more than one class of resource object.  If your application is simple enough
that you see no reason to want to do this, you can skip reading this section
of the chapter.

For example, here's some code which describes a blog entry which also
declares that the blog entry implements an :term:`interface`.

.. code-block:: python
   :linenos:

   import datetime
   from zope.interface import implements
   from zope.interface import Interface

   class IBlogEntry(Interface):
       pass

   class BlogEntry(object):
       implements(IBlogEntry)
       def __init__(self, title, body, author):
           self.title = title
           self.body =  body
           self.author = author
           self.created = datetime.datetime.now()

This resource consists of two things: the class which defines the resource
constructor as the class ``BlogEntry``, and an :term:`interface` attached to
the class via an ``implements`` statement at class scope using the
``IBlogEntry`` interface as its sole argument.

The interface object used must be an instance of a class that inherits from
:class:`zope.interface.Interface`.

A resource class may implement zero or more interfaces.  You specify that a
resource implements an interface by using the
:func:`zope.interface.implements` function at class scope.  The above
``BlogEntry`` resource implements the ``IBlogEntry`` interface.

You can also specify that a particular resource *instance* provides an
interface, as opposed to its class.  When you declare that a class implements
an interface, all instances of that class will also provide that interface.
However, you can also just say that a single object provides the interface.
To do so, use the :func:`zope.interface.directlyProvides` function:

.. code-block:: python
   :linenos:

   from zope.interface import directlyProvides
   from zope.interface import Interface

   class IBlogEntry(Interface):
       pass

   class BlogEntry(object):
       def __init__(self, title, body, author):
           self.title = title
           self.body =  body
           self.author = author
           self.created = datetime.datetime.now()

   entry = BlogEntry('title', 'body', 'author')
   directlyProvides(entry, IBlogEntry)

:func:`zope.interface.directlyProvides` will replace any existing interface
that was previously provided by an instance.  If a resource object already
has instance-level interface declarations that you don't want to replace, use
the :func:`zope.interface.alsoProvides` function:

.. code-block:: python
   :linenos:

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
           self.body =  body
           self.author = author
           self.created = datetime.datetime.now()

   entry = BlogEntry('title', 'body', 'author')
   directlyProvides(entry, IBlogEntry1)
   alsoProvides(entry, IBlogEntry2)

:func:`zope.interface.alsoProvides` will augment the set of interfaces
directly provided by an instance instead of overwriting them like
:func:`zope.interface.directlyProvides` does.

For more information about how resource interfaces can be used by view
configuration, see :ref:`using_resource_interfaces`.

.. index::
   single: resource API functions
   single: url generation (traversal)

:app:`Pyramid` API Functions That Act Against Resources
-------------------------------------------------------

A resource object is used as the :term:`context` provided to a view.  See
:ref:`traversal_chapter` and :ref:`urldispatch_chapter` for more information
about how a resource object becomes the context.

The APIs provided by :ref:`traversal_module` are used against resource
objects.  These functions can be used to find the "path" of a resource, the
root resource in a resource tree, or to generate a URL for a resource.

The APIs provided by :ref:`location_module` are used against resources.
These can be used to walk down a resource tree, or conveniently locate one
resource "inside" another.

Some APIs in :ref:`security_module` accept a resource object as a parameter.
For example, the :func:`pyramid.security.has_permission` API accepts a
resource object as one of its arguments; the ACL is obtained from this
resource or one of its ancestors.  Other APIs in the :mod:`pyramid.security`
module also accept :term:`context` as an argument, and a context is always a
resource.

