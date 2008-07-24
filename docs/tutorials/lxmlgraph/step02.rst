================================================
Step 02: Hello World as XML
================================================

We now have a website with ``/a`` and ``/b`` URLs.  Each has a default
view that returns a teensy weensy response.

In this step we will do the exact some scope, but using an XML
document as our model data.  We will leverage the same ``repoze.bfg``
machinery:

  - Model data with interfaces that define "types"

  - ZCML configuration to provide type-specific views

We do, however, need to do some things differently:

  - Our model class needs to use lxml to inject itelf into the XML
    nodes

  - That model class needs to implement the "handshake"

Let's look at what changed.

File ``myapp/samplemodel.xml``
--------------------------------

Our hierarchy in Step 01 was very simple.  Mimicking it in XML is,
thus, also very simple:

.. literalinclude:: step02/myapp/samplemodel.xml
   :linenos:
   :language: xml

#. Line 2 provides the root of the model as an XML ``<site>`` node.
   The element name doesn't have to be ``<site>``.

#. In lines 3-4, the ``<site>`` contains 2 top-level children: a and
   b.  These are provided as an element name ``<document>``.  This,
   also, is meaningfless as far as ``repoze.bfg`` is concerned.
   However, this is where you compose th information model you are
   publishing.

The only special constraint is that a node that wants to be "found" by
``repoze.bfg`` in during traversal *must* have an ``name`` attribute.
(The use of ``@name`` corresponds to ``__name__`` in the
``repoze.bfg`` handshake.)  Each hop in the URL tries to grab a child
with an attribute matching the next hop.  Also, the value of the
``@name`` should be unique in its containing node.


Module ``myapp/models.py``
------------------------------

Here is the serious change: we have made an XML-aware model.  Or is it
a model-aware XML document?  Such questions, harrumph.

At a high level, we make write a class that "extends" lxml Element
nodes, create an lxml parser, and register the custom class with the
parser.

.. literalinclude:: step02/myapp/models.py
   :linenos:

#. Line 4 imports lxml.

#. Line 9 creates the custom class we are going to use to extend
   etree.ElementBase.  The lxml website has great documentation on the
   various ways to inject custom Python behavior into XML.

#. Just as before, line 12 says that instances of this class support a
   certain content type (interface.)  In our case, instances will be
   XML nodes.

#. ``repoze.bfg`` has a "protocol" where model data should have an
   ``__name__`` attribute.  Lines 14-16 implement this by grabbing the
   ``@name`` attribute of the current node.

#. URL traversal in ``repoze.bfg`` works via the ``__getitem__``
   protocol.  Thus, we need a method that implements this.  Lines
   18-26 use XPath to look for a direct child that has an ``@name``
   matching the item name that's being traversed to.  If it finds it,
   return it.  If not, or if more than one is found, raise an error.

#. As before, ``get_root`` is the function that is expected to return
   the top of the model.  In lines 30-32 we do the lxml magic to get
   the custom Python class registered.  We then load some XML and
   return the top of the tree.


Module `myapp/views.py``
--------------------------

We only made two changes here.

.. literalinclude:: step02/myapp/views.py
   :linenos:

#. Line 5 grabs the element name (tag name) of the ``context``, which
   is the current XML node that we're traversing through.

#. Line 6 uses the special property we defined in our custom Python
   class to get the ``__name__`` of the context.


Browsing the Model
------------------------

We can use the same URLs from Step 01 to browser the model and see
results::

  http://localhost:5432/a
  http://localhost:5432/b
  http://localhost:5432/c (Not Found)

In this case, each request grabs a node in the XML and uses it as the
data for the view.  ``repoze.bfg`` doesn't really know that, unlike
Step 01, we no longer have "real" Python data.