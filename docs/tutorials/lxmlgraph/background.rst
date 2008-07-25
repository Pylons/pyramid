Background
====================

This demo application presumes that you have an interest in XML
technologies and might want to leverage them for a fast, but rich and
dynamic, website.  In this demo application, we build up, bit-by-bit,
the functionality.  Thus, you don't have to know squatola about XML to
follow along.

In fact, the real purpose of this demo app is to teach its author how
to use the stack (repoze.bfg, Paster, eggs, etc.)

In summary:

  - Represent a hierarchical site as hierarchical XML

  - Inject ``repoze.bfg`` semantics into elements using :term:`lxml`

  - Support flexible-but-fast rendering with XSLT

.. warning::

  If you dislike XML and related technologies such as XPath and XSLT,
  you'll thoroughly detest this sample application.  Just to be
  stupendously clear, ``repoze.bfg`` is in no way dependent on XML.
  On the other hand, ``repoze.bfg`` happens to make XML publishing
  kinda fun.

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

Using ``repoze.bfg``, of course.  More specifically, with an XML file
that models that hierarchy:

.. literalinclude:: step00/simplemodel.xml
	:language: xml

How It Works
-------------------

To coerce ``repoze.bfg`` into publishing this model, I just need to
sprinkle in some Python behavior.  For example, ``repoze.bfg`` uses
``__getitem__`` to traverse the model.  I need my XML data to support
this method.  Moreover, I want some specific behavior: run an XPath
express on the node to get the child with the ``@name`` attribute
matching the URL hop.

Fortunately :term:`lxml` makes this easy.  I can inject my nodes with a
class that I write, thus providing my own ``__getitem__`` behavior.

That class can also assert that my XML nodes provide an interface.
The interface then lets me glue back into the standard ``repoze.bfg``
machinery, such as associating views and permissions into the model.

Neato torpedo.  And stinking fast.

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

What It Might Do
--------------------

This demo application has the potential to show some other interesting
investigations:

#. **Authorization**.  By hooking up support for an ``__acl__``
   property, I can store ACL information on a single node, on an
   ancestor, on the ``<site>`` root, on the Python class, or any
   combination thereof.  Additionally, I can wire up the
   ``__parent__`` attribute as a property that makes an :term:`lxml`
   ``node.getparent()`` call.

#. **Multiple views**.  Instead of just having a single default view
   on a node, I can allow other view names, all pointing at the same
   view function and XSLT.  I simple grab that name and pass it in as
   a paramter to the XSLT, which will run a different rule for
   rendering.  Adding a view would no longer required editing ZCML and
   adding a function.

#. **Forms**.  To edit data in the model, I need to render a form,
   then handle post data on the way back in.  For the former, it's
   *really* easy in XSLT to make a very powerful, flexible, and
   extensisible form rendering system.  For the latter, I'll have to
   learn more about POST handlers in ``repoze.bfg``.
