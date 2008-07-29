Models
======

A :term:`model` is typically a simple Python class defined in a
module.  Model *instances* make up the graph that :mod:`repoze.bfg` is
willing to traverse.

Defining a Model
----------------

An example of a model describing a blog entry:

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

A model consists of two things: the object which defines the model
(above as the class ``BlogEntry``), and an :term:`interface` attached
to the model object (above as the class ``IBlogEntry``).  An interface
simply tags the model object with a "type" that can be referred to
within the :term:`application registry`.  A model object can implement
zero or more interfaces.  The interface must be an instance of a class
that inherits from ``zope.interface.Interface``.

You specify that a model *implements* an interface by using the
``zope.interface.implements`` function at class scope.  The above
``BlogEntry`` model implements the ``IBlogEntry`` interface.

Defining a Graph of Model Instances
-----------------------------------

:mod:`repoze.bfg` expects to be able to traverse a graph of model
instances.  :mod:`repoze.bfg` imposes the following policy on model
instance nodes in the graph:

- Nodes which contain other nodes (aka "container" nodes) must supply
  a ``__getitem__`` method which is willing to resolve a string or
  unicode name to a subobject.  If a subobject by that name does not
  exist in the container, ``__getitem__`` must raise a ``KeyError``.
  If a subobject by that name *does* exist, the container should
  return the subobject (another model instance).

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
interface ``zope.location.interfaces.ILocation``, you don't need to
manage these attributes by hand.  During :term:`traversal`, if the
root node says it implements the ``ILocation`` :term:`interface`,
:mod:`repoze.bfg` will wrap each child in a ``LocationProxy`` which
will dynamically assign a ``__name__`` and a ``__parent__`` to it,
recursively.

If you choose to make use of the location-based dynamic assignment of
``__parent__`` and ``__name__``, the root node must have a
``__parent__`` and a ``__name__`` that are both ``None``, and it must
provide the ``ILocation`` interface.  The easiest way to do this is to
claim that the class representing the root node
``implements(ILocation)``, as above.

