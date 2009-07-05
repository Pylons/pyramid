Models
======

A :term:`model` class is typically a simple Python class defined in a
module.  These classes are termed model *constructors*.  Model
*instances* make up the graph that :mod:`repoze.bfg` is willing to
traverse when :term:`traversal` is used.  A model instance is also
generated as a result of :term:`url dispatch`.  A model instance is
exposed to :term:`view` code as the :term:`context` of a view.

Defining a Model Constructor
----------------------------

An example of a model constructor, ``BlogEntry`` is presented below.
It is a class which, when instantiated, becomes a model instance.

.. code-block:: python
   :linenos:

   import datetime

   class BlogEntry(object):
       def __init__(self, title, body, author):
           self.title = title
           self.body =  body
           self.author = author
           self.created = datetime.datetime.now()

A model constructor may be essentially any Python object which is
callable, and which returns a model instance.  In the above example,
the ``BlogEntry`` class can be "called", returning a model instance.

Model Instances Which Implement Interfaces
------------------------------------------

Model instances can *optionally* be made to implement an
:term:`interface`.  This makes it possible to register views against
the interface itself instead of the *class* within :term:`view`
statements within the :term:`application registry`.  If your
application is simple enough that you see no reason to want to do
this, you can skip reading this section of the chapter.

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

This model consists of two things: the class which defines the model
constructor (above as the class ``BlogEntry``), and an
:term:`interface` attached to the class (via an ``implements``
statement at class scope using the ``IBlogEntry`` interface as its
sole argument).

An interface simply tags the model object with a "type" that can be
referred to within the :term:`application registry`.  A model object
can implement zero or more interfaces.  The interface must be an
instance of a class that inherits from ``zope.interface.Interface``.

You specify that a model *implements* an interface by using the
``zope.interface.implements`` function at class scope.  The above
``BlogEntry`` model implements the ``IBlogEntry`` interface.

You can also specify that a *particular* model instance provides an
interface (as opposed to its class).  To do so, use the
``zope.interface.directlyProvides`` API:

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

   entry = BlogEntry()
   directlyProvides(IBlogEntry, entry)

If a model object already has instance-level interface declarations
that you don't want to disturb, use the
``zope.interface.alsoProvides`` API:

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

   entry = BlogEntry()
   directlyProvides(IBlogEntry1, entry)
   alsoProvides(IBlogEntry2, entry)

See the :ref:`views_chapter` for more information about why providing
models with an interface can be an interesting thing to do with regard
to :term:`view` lookup.

Defining a Graph of Model Instances for Traversal
-------------------------------------------------

When :term:`traversal` is used (as opposed to a purely :term:`url
dispatch` based application), mod:`repoze.bfg` expects to be able to
traverse a graph of model instances.  Traversal begins at a root
model, and descends into the graph recursively via each found model's
``__getitem__`` method.  :mod:`repoze.bfg` imposes the following
policy on model instance nodes in the graph:

- Nodes which contain other nodes (aka "container" nodes) must supply
  a ``__getitem__`` method which is willing to resolve a unicode name
  to a subobject.  If a subobject by that name does not exist in the
  container, ``__getitem__`` must raise a ``KeyError``.  If a
  subobject by that name *does* exist, the container should return the
  subobject (another model instance).

- Nodes which do not contain other nodes (aka "leaf" nodes) must not
  implement a ``__getitem__``, or if they do, their ``__getitem__``
  method must raise a ``KeyError``.

See :ref:`traversal_chapter` for more information about how traversal
works against model instances.

.. _location_aware:

Location-Aware Model Instances
------------------------------

Applications which use :term:`traversal` to locate the :term:`context`
of a view must ensure that the model instances that make up the model
graph are "location aware".  In order for :mod:`repoze.bfg` location,
security, URL-generation, and traversal functions (such as the
functions exposed in :ref:`location_module`, :ref:`traversal_module`,
and :ref:`url_module` as well as certain functions in
:ref:`security_module` ) to work properly against a instances in a
model graph, all nodes in the graph must be "location-aware".  This
means they must have two attributes: ``__parent__`` and ``__name__``.
The ``__parent__`` attribute should be a reference to the node's
parent model instance in the graph.  The ``__name__`` attribute should
be the name that a node's parent refers to the node via
``__getitem__``.  The ``__parent__`` of the root object should be
``None`` and its ``__name__`` should be the empty string.  For
instance:

.. code-block:: python

   class MyRootObject(object):
       __name__ = ''
       __parent__ = None

.. warning:: If your root model object has a ``__name__`` argument
   that is not ``None`` or the empty string, URLs returned by the
   ``repoze.bfg.url.model_url`` function and paths generated by the
   ``repoze.bfg.traversal.model_path`` and
   ``repoze.bfg.traversal.model_path_tuple`` APIs will be generated
   improperly.  The value of ``__name__`` will be prepended to every
   path and URL generated (as opposed to a single leading slash or
   empty tuple element).

A node returned from the root item's ``__getitem__`` method should
have a ``__parent__`` attribute that is a reference to the root
object, and its ``__name__`` attribute should match the name by which
it is are reachable via the root object's ``__getitem__``.  *That*
object's ``__getitem__`` should return objects that have a
``__parent__`` attribute that points at that object, and
``__getitem__``-returned objects should have a ``__name__`` attribute
that matches the name by which they are retrieved via ``__getitem__``,
and so on.

.. note::

  If you'd rather not manage the ``__name__`` and ``__parent__``
  attributes of your models "by hand", an add-on package to
  :mod:`repoze.bfg`` named :mod:`repoze.bfg.traversalwrapper` can help
  you do this.

  In order to use this helper feature, you must first install the
  :mod:`repoze.bfg.traversalwrapper` package (available from
  `http://svn.repoze.org/repoze.bfg.traversalwrapper
  <http://svn.repoze.org/repoze.bfg.traversalwrapper>`_), then
  register its ``ModelGraphTraverser`` as the traversal policy, rather
  than the default BFG ``ModelGraphTraverser``. To register the
  :mod:`repoze.bfg.traversalwrapper` ``ModelGraphTraverser`` as the
  traversal policy, your application will need to have the following
  in its ``configure.zcml`` file:

  .. code-block:: xml

    <adapter
        factory="repoze.bfg.traversalwrapper.ModelGraphTraverser"
        provides="repoze.bfg.interfaces.ITraverserFactory"
        for="*"
    />

  If this statement is made in ZCML, you will no longer need to manage
  the ``__parent__`` and ``__name__`` attributes on graph objects "by
  hand".  Instead, as necessary, during traversal :mod:`repoze.bfg`
  will wrap each object (even the root object) in a ``LocationProxy``
  which will dynamically assign a ``__name__`` and a ``__parent__`` to
  the traversed object (based on the last traversed object and the
  name supplied to ``__getitem__``).  The root object will have a
  ``__name__`` attribute of ``None`` and a ``__parent__`` attribute
  of ``None``.

:mod:`repoze.bfg` API Functions That Act Against Models
-------------------------------------------------------

A model instance is used as the :term:`context` argument provided to a
view.  See :ref:`traversal_chapter` and :ref:`urldispatch_chapter` for
more information about how a model instance becomes the context.

The APIs provided by :ref:`traversal_module` are used against model
instances.  These functions can be used to find the "path" of a model,
find the URL of a model, the root model in a model graph, and so on.

The APIs provided by :ref:`location_module` are used against model
instances.  These can be used to walk down a model graph, or
conveniently locate one object "inside" another.

Some APIs in :ref:`security_module` accept a model object as a
parameter.  For example, the ``has_permission`` API accepts a
"context" (a model object) as one of its arguments; the ACL is
obtained from this model or one of its ancestors.  Other APIs in the
same module also accept :term:`context` as an argument, and a context
is always a model.
