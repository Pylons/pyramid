Background
====================

In this demo application, we build up, bit-by-bit, the functionality
for a website based on a single XML document.  You don't have to know
much about XML to follow along.  In fact, the real purpose of this
demo app is to teach its author how to use the stack
(:mod:`repoze.bfg`, ``paster``, eggs, etc.)

.. warning::

  If you dislike XML and related technologies such as XPath and XSLT,
  you'll thoroughly detest this sample application.  Just to be
  stupendously clear, :mod:`repoze.bfg` is in no way dependent on XML.
  On the other hand, :mod:`repoze.bfg` happens to make XML publishing
  kinda fun.

In summary:

  - Represent a hierarchical website as an XML document

  - Inject :mod:`repoze.bfg` semantics into elements using
    :term:`lxml`

  - Support rendering with :term:`XSLT`

What It Does
-------------------

Imagine you have a website that looks like this::

  /
    folder1/
      doc1
      doc2
      image1
    folder2/
      doc2

Meaning, a heterogenous, nested folder structure, just like your hard
drive.  (Unless you're one of those folks that uses your Windows
Desktop as a flat filing system.)  How might I get that information
into a website?

Using :mod:`repoze.bfg`, of course.  More specifically, with an XML file
that models that hierarchy:

.. literalinclude:: step00/simplemodel.xml
	:language: xml

How It Works
-------------------

To coerce :mod:`repoze.bfg` into publishing this model, I just need to
sprinkle in some Python behavior.  For example, :mod:`repoze.bfg` uses
``__getitem__`` to traverse the model.  I need my XML data to support
this method.  Moreover, I want some specific behavior: run an XPath
express on the node to get the child with the ``@name`` attribute
matching the URL hop.

Fortunately :term:`lxml` makes this easy.  I can inject my nodes with a
class that I write, thus providing my own ``__getitem__`` behavior.

That class can also assert that my XML nodes provide an interface.
The interface then lets me glue back into the standard :mod:`repoze.bfg`
machinery, such as associating views and permissions into the model.

Next up, I need to provide views for the elements in the model.  I
could, for example, use ZPT and manipulate the XML data using Python
expressions against the :term:`lxml` API.  Or, I could use XSLT.

For the latter, I could register a different XSLT for every "view" on
every interface.  Or, I could write one big XSLT, and let its template
matching machinery decide who to render in a certain context.

And finally, I could pass in just a single node and render it, or pass
in the entire tree with a parameter identifying the context node.

In the course of this writeup, we'll build ``repoze.lxmlgraph``
step-by-step, starting with no XML.  Each of those decisions will be
analyzed an implemented.  At the end, you'll see both the resulting
demo application, plus the thought process that went along with it.

