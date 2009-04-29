Models
======

A :term:`model` is typically a simple Python class defined in a
module.  Model *instances* make up the graph that :mod:`repoze.bfg` is
willing to traverse.

Defining a Model
----------------

Here's an example of a model describing a blog entry:

.. code-block:: python
   :linenos:

   import datetime

   class BlogEntry(object):
       def __init__(self, title, body, author):
           self.title = title
           self.body =  body
           self.author = author
           self.created = datetime.datetime.now()

A model may be essentially any Python object.  In the above example,
an instance of the ``BlogEntry`` class can be created and used as a
model.

Models Which Implement Interfaces
---------------------------------

Models can optionally be made to implement an :term:`interface`.  This
makes it possible to register views against the interface itself
instead of the *class* within view statement in the application
registry.  For example, here's some code which describes a blog entry
whicg also declares that the blog entry implements an
:term:`interface`.

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

This model consists of two things: the object which defines the model
(above as the class ``BlogEntry``), and an :term:`interface` attached
to the model object (above as the class ``IBlogEntry``).  An interface
simply tags the model object with a "type" that can be referred to
within the :term:`application registry`.  A model object can implement
zero or more interfaces.  The interface must be an instance of a class
that inherits from ``zope.interface.Interface``.

You specify that a model *implements* an interface by using the
``zope.interface.implements`` function at class scope.  The above
``BlogEntry`` model implements the ``IBlogEntry`` interface.

See the :ref:`views_chapter` for more information about why providing
models with an interface can be an interesing thing to do.

Defining a Graph of Model Instances
-----------------------------------

:mod:`repoze.bfg` expects to be able to traverse a graph of model
instances.  :mod:`repoze.bfg` imposes the following policy on model
instance nodes in the graph:

- Nodes which contain other nodes (aka "container" nodes) must supply
  a ``__getitem__`` method which is willing to resolve a unicode name
  to a subobject.  If a subobject by that name does not exist in the
  container, ``__getitem__`` must raise a ``KeyError``.  If a
  subobject by that name *does* exist, the container should return the
  subobject (another model instance).

- Nodes which do not contain other nodes (aka "leaf" nodes) must not
  implement a ``__getitem__``, or if they do, their ``__getitem__``
  method must raise a ``KeyError``.

.. _location_aware:

Location-Aware Model Instances
------------------------------

For :mod:`repoze.bfg` security and convenience URL-generation
functions to work properly against a model instance graph, all nodes
in the graph should have two attributes:: ``__parent__`` and
``__name__``.  The ``__parent__`` attribute should be a reference to
the node's parent model instance in the graph.  The ``__name__``
attribute should be the name that a node's parent refers to the node
by via ``__getitem__``.

If you choose not to manage the ``__name__`` and ``__parent__``
attributes of your models "by hand", :mod:`repoze.bfg`` is willing to
help you do this.  If your "root" node claims it implements the
interface ``repoze.bfg.interfaces.ILocation``, you don't need to
manage these attributes by hand.  During :term:`traversal`, if the
root node says it implements the ``ILocation`` :term:`interface`,
:mod:`repoze.bfg` will wrap each child in a ``LocationProxy`` which
will dynamically assign a ``__name__`` and a ``__parent__`` to it,
recursively.

.. note::
   In order to use this feature, you must register the
   ``WrappingModelGraphTraverser`` as the traversal policy, rather
   than the standard ``ModelGraphTraverser``.  E.g., your application
   will need to have the following in its ``configure.zcml``::

    <adapter
        factory="repoze.bfg.traversal.WrappingModelGraphTraverser"
        provides="repoze.bfg.interfaces.ITraverserFactory"
        for="*"
    />


If you choose to make use of the location-based dynamic assignment of
``__parent__`` and ``__name__``, the root node must have a
``__parent__`` that is ``None``, a ``__name__`` with any value, and it
must provide the ``repoze.bfg.interfaces.ILocation`` interface.  The
easiest way to do this is to claim that the class representing the
root node ``implements(ILocation)``:

.. code-block:: python
   :linenos:

   from repoze.bfg.interfaces import ILocation
   from zope.interface import implements

   class MyRootObject(object):
       implements(ILocation)
       __parent__ = None
       __name__ = ''

:mod:`repoze.bfg` API Functions That Act Against Models
-------------------------------------------------------

A model instance is used as the :term:`context` argument provided to a
view.  See :ref:`traversal_chapter` for more information about how a
model becomes the context.

The APIs provided by :ref:`traversal_module` are used against model
instances.  These functions can be used to find the "path" of a model,
find the URL of a model, the root model in a model graph, and so on.

The APIs provided by :ref:`location_module` are used against model
instances.  These can be used to walk down a model graph, or
conveniently locate one object "inside" another.

Some APIs in :ref:`security_module` accept a model object as a
parameter.  For example, the ``has_permission`` API accepts a
"context" (a model object) as one of its arguments; the "acl" is
obtained from this model or one of its ancestors.  Other APIs in the
same module also accept :term:`context` as an argument, and a context
is always a model.
