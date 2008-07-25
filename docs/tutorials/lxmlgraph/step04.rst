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

For the XSLT in Step 3, we passed in the context node.  From the
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


``samplemodel.xml``
=====================

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

#. Lines 13-32 show a nested XML hierarchy.  A ``<folder>`` gets an
   ``@name``, making the folder itself published as a possible URL.
   It also gets an ``@xml:id``, allowing it to be uniquely addressed
   within the entire document.  The ``<folder>`` gets a ``<title>``
   child node, but then gets two more ``__getitem__``-enabled child
   nodes of type ``<document>``.  ("Enabled", as in, has a ``@name``
   attribute.)

Thus the major changes:

- The root contains ``<folder>`` nodes which contain ``<document>``
  nodes.

- The root could contain documents too, and the folder could contain
  sub-folders.  There's nothing special about the arrangement.

- The only thing special is the presence of ``@name`` attributes,
  which allow ``__getitem__`` (via XPath) to traverse to that child.

- As we'll see in a second, the ``@xml:id`` allows jumping through the
  hierarchy directly to a node.

- Finally, for UI-framework-ish purposes, having a child ``<title>``
  allows us to show in a browser what we're looking at.

The ``models.py`` hasn't changed, so let's move to the small changes
in the ``views.py``.

``views.py``
============

As noted above, we removed the ZPT views, and thus ``views.py`` is
shorter, and focused only on a function that provides an XSLT
template.  Although there aren't many lines in that function, there
are some concepts to explain:

.. literalinclude:: step04/myapp/views.py
   :linenos:

#. We are going to be using a feature from XML called ``xml:id``,
   which we explained above in the ``samplemodel.xml`` section.  In
   lines 4 and 5, we make constants that point to the namespace
   needed.

#. As the comment says, line 9 grabs the "root" node of the site.
   Inside this function, we are traversing, node-by-node, through a
   hierarchy.  Thus our context node is an lxml Element object, which
   supports a method to grab the tree (and thus root) in which the
   context sits.

#. Next, to support the XSLT approach we show next, we want to let the
   XSLT know the ``xml:id`` that we are sitting on.  Since we are
   passing it in as an XSLT paramter, we need some special handling:

  - The *value* of the parameter is the ``@xml:id`` of the node we are
    sitting on.

  - Per lxml's needs, that value needs to be quoted.  Thus, the value
    of ``contextid`` will be something like ``"'n1'"``

#. Finally, on line 12, we call the XSLT processor, passing in keyword
   arguments that become XSLT parameters.  Unlike before, the node we
   pass in is the top of the tree, rather than the current (context)
   node.

In summary, we render the XSLT by handing it the root node of the
tree, plus a flag that says which node we are currently sitting on.

``xsltview.xsl``
=================

The XSLT template gets the most substantive changes, as we both have
to support this root-and-contextid idea, as well as some features that
put this to use:

- Having a common look-and-feel across all pages, along with "rules"
  that handle each content type

- Show the context's ``<title>`` in the same place

- Show some general information about the node

The following XSLT accomplishes these features:

.. literalinclude:: step04/myapp/xsltview.xsl
   :linenos:
   :language: xml

#. Line 3 accepts the ``@xml:id`` passed in as a parameter of the XSLT
   transformation.  This can differ between requests, as different
   nodes are traversed.

#. Line 4 jumps directly to the tree node that has that ``@xml:id`` by
   using XPath's ``id()`` function.  This is a high-speed lookup,
   similar to ``document.getElementById()`` in JavaScript.  We then
   assign the node to a global XSLT variable, to avoid paying that
   price again.

#. Line 5 gets into XSLT's rule-oriented mumbo-jumbo.  This template
   rule says: "Match on the root of the tree that was passed in, then
   do some work."  Think of this as a CSS rule that matches on ``body
   {}``.

#. Lines 7-11 output HTML for the document and ``<head>``.

#. Line 9 (and line 14) inserts the value of the context node's
   ``<title>`` using ``<xsl:value-of>``.

#. Line 16 does some XSLT mumbo jumbo.  It says "Find a rule that
   handles the context node, which might be a ``<folder>`` or might be
   a ``<document>``."  Control is then passed to an ``<xsl:template>``
   that meets the conditions.  Once that rule is finished, control
   returns to line 17.

#. Lines 17-42 then format some basic information about the context
   node.  The HTML generated for this, however, appears *after* the
   type-specific handler in the resulting HTML.

#. Line 46 is an ``<xsl:template>`` rule that handles ``<folder>``
   nodes.  It only gets control when something else hands control to it.

   In this case, the rule makes a paragraph then lists the contents of
   the folder.

#. Line 50 checks to see if the folder contains any "publishable"
   content.  We wouldn't want a heading to appear saying "Folder
   Contents" with empty space under it.

#. Line 53 then iterates over all the child nodes which have an
   ``@xml:id``.

#. Lines 55-57 make an ``<li>`` with an ``<a>`` for each item in the
   folder.  Inside the ``<xsl:for-each``, the "current" node is the
   current item in the iteration.  The ``@href`` uses what XSLT calls
   "attribute value template" (curly braces) to let the XSLT processor
   operate inside an attribute.

#. Line 63 handles ``<document>`` nodes when handed control.

#. Line 67 recursively copies the nodes in the ``<document>`` content.

To recap, this XSLT handles any node passed in, and generates a UI
that can handle the global styling, the navigational elements, and the
content for the current traversal hop.

Conclusion
=====================

Though not very much code, this is the basis for a useful amount of
features.  A hierarchical website with templating that can handle
global styling and navigation, as well as type-driven templating, all
at reasonable (albeit in-memory) performance.


