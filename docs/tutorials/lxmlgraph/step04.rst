================================================
Step 4: Hierarchical Rendering With XSLT
================================================

Now that we have basic templating for our XML graph in place, let's
start doing some fun stuff with it.  As we walk through use cases and
build out patterns for implementing them, we'll get to leverage some
features available in XML processors.  For better or worse. [wink]

In this step we take a look at the following:

- Build a nested, folder-like website

- Render the HTML common to all pages, then render the part specific
  to a certain page

- Show contents of a folder when sitting on a folder, and content of a
  document when sitting on a document


Pre-Flight Cleanup
====================

In the last example, we had a default template that used ZPT.  We're
shifting the rest of the steps over to XSLT.  Thus, our
``configure.zcml`` is now simpler:

.. literalinclude:: step04/myapp/configure.zcml
   :linenos:
   :language: xml

We also remove the ZPT view function from ``views.py``, as we'll see
in a moment.

Design Change: Trees and Context IDs
========================================

In ``repoze.bfg``, the ``context`` variable that is passed into our
view function equates to the Python object that was grabbed on the
current hop in the URL.  For ``repoze.lxmlgraph``, that "context"
object is a node in the XML document, found by traversing node
children.

For the XSLT in Step 03, we passed in the context node.  From the
XSLT's perpective, the universe started at the context node.  It could
only see information in that node and the children beneath it.

If we could see the entire tree, however, we could put the other
information to use: showing the name of the site in a header, listing
the breadcrumbs to reach the document, and other portal-style boxes.

To enable this, we need the following:

#. A way to pass in the entire XML document tree.

#. A way to uniquely point at the item in the XML that we are
   currently sitting on, with the fastest performance possible.

We will thus make the following changes in our approach:

#. The XML document will support an ``xml:id`` attribute on each node
   that has a ``name`` attribute.  The ``xml:id`` uniquely identifies
   the resource within the document.  Moreover, it leverages built-in
   support for high-speed lookups in XPath.

#. We change the view function to pass in the root of the tree,
   instead of the context node.

#. We also pass in, via an XSLT parameter, the ``xml:id`` of the
   context node.

#. The XSLT will start at the top of the tree, generate the site-wide
   look and feel, then render the context node.

That's the big picture.  Each of these changes will be explained in
detail below.


File ``samplemodel.xml``
===================================

The XML document with the information for our website has quite a
number of changes:

.. literalinclude:: step04/myapp/samplemodel.xml
   :linenos:
   :language: xml

#. Line 3 shows that our ``<site>`` now gets a ``<title>``.

#. On Line 4 we make an index document at the root that contains a
   document-wide unique value for its ``@xml:id``.

#. In lines 5-11, our ``<document>`` gets some extra information: a
   ``<title>``, plus some HTML-namespaced markup content inside a
   ``<body>``.

#. 
