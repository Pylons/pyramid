================================================
Step 3: Basic Rendering With ZPT and XSLT
================================================

Our XML-based model is now usable.  However, we're using Python to
generate the HTML, instead of a template.  In this step, we'll look at
wiring up some templates, using both ZPT and XSLT.

In a nutshell, this means:

  - Slight changes to the ZCML

  - View functions that assemble information and call the template

ZPT Templates
========================

Let's start with a ZPT-based default view for the nodes in the XML.
The ZCML for this would look like this:

.. code-block:: xml

  <bfg:view
     for=".models.IMyModel"
     view=".views.zpt_default_view"
     />

Here we point to a function in ``views.py`` that looks like the
following:

.. code-block:: python
   :linenos:

   from repoze.bfg.template import render_template_to_response
   def zpt_default_view(context, request):
      fn = "default.pt"
      return render_template_to_response(fn, name=context.__name__, node=context)

This function is relatively simple:

#. Line 1 imports a ``repoze.bfg`` function that renders ZPT
   templates.  ``repoze.bfg`` uses the ``z3c.pt`` ZPT engine.

#. Line 2, like our other view functions, gets passed a ``context``
   (the current hop in the URL) and WebOb ``request`` object.

#. Line 3 points at the filename of the ZPT.

#. Line 4 calls the ``render_template_to_response`` function, passing in the
   filename for the ZPT and two top-level variables that can be used
   in the ZPT.  The first is the name of the current URL hop
   (context).  The second is the XML node object for that hop
   (context).

In Step 02, we returned a WebOb Response object that we created.
``render_template_to_response`` makes a Response itself.  The
response's status is always ``200 OK`` if you use this shortcut
function.

Here's what the ZPT looks like:

.. literalinclude:: step03/myapp/default.pt
   :linenos:
   :language: xml

Look, a template!  Life is better with templating:

#. Lines 1-2 make an ``<html>`` node with a namespace for TAL.

#. Line 5 inserts the value of the ``name`` that we passed into
   ``render_template_to_response``.

#. Line 6 sure looks interesting.  It uses the ``node`` that we passed
   in via ``render_template_to_response``.  Since ``z3c.pt`` uses
   Python as its expession language, we can put anything Python-legal
   between the braces.  And since ``node`` is an ``lxml`` ``Element``
   object, we just ask for its ``.tag``, like regular Python ``lxml``
   code.

Viewing the ZPT
------------------

With all of that in place, going to ``http://localhost:5432/a`` now
generates, via the ZPT, the following::

  My template is viewing item: a

  The node has a tag name of: document.


XSLT Templates
====================

So that's the ZPT way of rendering HTML for an XML document.  How
might XSLT look?

.. note::

  For the following, we'll switch back to showing the complete module
  code, rather than snippets.  You can then follow along by looking at
  the files in ``docs/step03/myapp``.

File ``configure.zcml``
----------------------------------

The ZCML statement for the XSLT template looks almost exactly the same
as the ZPT template:

.. literalinclude:: step03/myapp/configure.zcml
   :linenos:
   :language: xml

#. Lines 10-14 wire up a new view, in addition to the default view.

#. Line 13 provides the difference: ``name="xsltview.html"`` means
   that all our URLs now can have ``/xsltview.xml`` appended to them.

In the ZCML, there is no distinction between a ZPT view and an XSLT
view.  The difference is only in the function that is pointed to by
the ``view=`` attribute.


Module ``views.py``
--------------------------------

The ZCML says that our XSLT view (``xsltview.html`` on the URL) comes
from the ``lxmlgraph.views.xslt_view`` function:

.. literalinclude:: step03/myapp/views.py
   :linenos:

#. Line 9 starts the Python function which serves as the view for this
   template.  The function has the same signature as the
   ``zpt_default_view`` function we defined for the ZPT template's
   view.

#. Line 10 implements the difference.  We call
   ``render_transform_to_response`` instead of
   ``render_template_to_response``.  This tells ``repoze.bfg`` to make
   an XSLT processor for this template, instead of a ZPT.  The second
   argument passes in ``context`` to the XSLT transform.  ``context```
   is an instance of an Element node.  Namely, a node from the XML
   document that corresponds to the current hop in the URL.


File ``xsltview.xsl``
--------------------------------

How different does the XSLT itself look?  At this stage, not too different:

.. literalinclude:: step03/myapp/xsltview.xsl
   :linenos:
   :language: xml

#. Lines 1 and 2 are typical XSLT setup.

#. Line 3 defines a rule to match on the node that is passed in.  In
   our case, a ``<document>`` node.

#. Line 7 inserts the value of the ``@id`` attribute from the
   "current" node at that point in the rule.  We're sitting on the
   ``<document>`` node (thanks to line 3).  Thus, ``<xsl:value of
   select="@id"/>`` inserts ``a`` or ``b``, depending on which
   document we are sitting on.

#. Line 8 shows the element name of the current node.


Viewing the XSLT
--------------------

With this in place, runnning the application provides a URL such as
``http://localhost:5432/a/xsltview.html``.  Going to that URL should
show::

  My template is viewing item: a

  The node has a name of: document.
