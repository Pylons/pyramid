Models
======

*Models* are typically simple Python classes defined in a module.
 Model *instances* make up the graph that ``repoze.bfg`` is willing to
 traverse.

Defining a Model
----------------

An example of a model describing a blog entry::

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

A model consists of basically two things: the object which defines the
model (above as the class ``IBlogEntry``), and an *interface* attached
to the model object.  An interface simply tags the model object with a
"type" that can be referred to within view configuration.  A model
object can implement zero or more interfaces.

Defining a Graph of Model Instances
-----------------------------------

``repoze.bfg`` expects to be able to traverse a graph of model
instances.  ``repoze.bfg`` imposes the following policy on model
instance nodes in the graph:

 - Nodes which contain other nodes (aka "container" nodes) must supply
   a ``__getitem__`` method which is willing to resolve a string or
   unicode name to a subobject.  If a subobject by that name does not
   exist in the container, ``__getitem__`` must raise a KeyError.  If
   a subobject by that name *does* exist, the container should return
   the subobject (another model instance).  

 - Nodes which do not contain other nodes (aka "leaf" nodes) must not
   implement ``__getitem__``.

Location-Aware Model Instances
------------------------------

 - For ``repoze.bfg`` security and convenience URL-generation
   functions to work properly against a model instance graph, all
   nodes in the graph should have two attributes:: ``__parent__`` and
   ``__name__``.  The ``__parent__`` attribute should be a reference
   to the node's parent model instance in the graph.  The ``__name__``
   attribute should be the name that a node's parent refers to the
   node by via ``__getitem__``.

