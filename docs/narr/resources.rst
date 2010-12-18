Resources
=========

A :term:`resource` is an object that represents a "place" in your
application.  Every :app:`Pyramid` application has at least one resource
object: the :term:`root resource`.  The root resource is the root of a
:term:`resource tree`.  A resource tree is a set of nested dictionary-like
objects which you may use to represent your website's structure.

In an application which uses :term:`traversal` to map URLs to code, the
resource tree structure is used heavily to map a URL to a :term:`view
callable`.  :app:`Pyramid` will walk "up" the resource tree when
:term:`traversal` is used in order to find a :term:`context`.  Once a context
is found, the resource represented by the context combined with data in the
request will be used to find a :term:`view callable`.

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
structure of your website, but they become the :term:`model` of the
application.

Also:

- The ``context`` and ``containment`` predicate arguments to
  :meth:`pyramid.config.Configurator.add_view` (or a
  :func:`pyramid.view.view_config` decorator) and reference a resource class
  or resource :term:`interface`.

- A :term:`root factory` returns a resource.

- A resource is exposed to :term:`view` code as the :term:`context` of a
  view.

.. index::
   single: resource constructor

Defining a Resource Constructor
-------------------------------

An example of a resource constructor, ``BlogEntry`` is presented below.  It
is implemented as a class which, when instantiated, becomes a resource
instance.

.. code-block:: python
   :linenos:

   import datetime

   class BlogEntry(object):
       def __init__(self, title, body, author):
           self.title = title
           self.body =  body
           self.author = author
           self.created = datetime.datetime.now()

A resource constructor may be any Python object which is callable, and which
returns a resource instance.  In the above example, the ``BlogEntry`` class
can be "called", returning a resource instance.

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
root resource, and descends into the tree recursively via each resource's
``__getitem__`` method.  :app:`Pyramid` imposes the following policy on
resource instances in the tree:

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

.. index::
   pair: location-aware; resource

.. _location_aware:

Location-Aware Resources
------------------------

Applications which use :term:`traversal` to locate the :term:`context`
resource of a view must ensure that the resources that make up the
resource tree are "location aware".

In order for :app:`Pyramid` location, security, URL-generation, and traversal
functions (i.e., functions in :ref:`location_module`,
:ref:`traversal_module`, :ref:`url_module` and some in :ref:`security_module`
) to work properly against the resources in a resource tree, all resources in
the tree must be :term:`location` -aware.  This means they must have two
attributes: ``__parent__`` and ``__name__``.

The ``__parent__`` attribute should be a reference to the resource's parent
resource instance in the tree.  The ``__name__`` attribute should be the name
with which a resource's parent refers to the resource via ``__getitem__``.

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

