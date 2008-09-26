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
Change your project's ``configure.zcml`` so that it looks like this:

.. code-block:: xml

  <configure xmlns="http://namespaces.zope.org/zope"
	     xmlns:bfg="http://namespaces.repoze.org/bfg"
	     i18n_domain="repoze.bfg">

    <!-- this must be included for the view declarations to work -->
    <include package="repoze.bfg" />

    <bfg:view
       for=".models.IMyModel"
       view=".views.zpt_view"
       />

  </configure>

In other words, replace the default view function with
``.views.zpt_view``.  This view stanza indicates that the *default
view* for a model that implements ``lxmlgraph.models.IMyModel`` should
be the ``lxmlgraph.views.zpt_view`` function.  It is the *default*
view because this stanza does not have a ``name`` attribute.

Additonally, add a template to your project's ``templates`` directory
named ``default.pt`` with this content:

.. literalinclude:: step03/myapp/templates/default.pt
   :linenos:
   :language: xml

Also add a function in ``views.py`` that looks like the following:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template_to_response
   def zpt_view(context, request):
      return render_template_to_response('templates/default.pt', 
                                         name=context.__name__, 
                                         node=context)

This function is relatively simple:

#. Line 1 imports a :mod:`repoze.bfg` function that renders ZPT
   templates to a response.  :mod:`repoze.bfg` uses the
   :term:`chameleon.zpt` ZPT engine.

#. Line 2, like our other view functions, gets passed a ``context``
   (the current hop in the URL) and WebOb ``request`` object.

#. Line 3 calls the ``render_template_to_response`` function, passing
   in the filename for the ZPT and two top-level variables that can be
   used in the ZPT.  The first is the name of the current URL hop
   (context).  The second is the XML node object for that hop
   (context).

In Step 02, we returned a :term:`WebOb` Response object that we
created.  ``render_template_to_response`` makes a Response itself.
The response's status is always ``200 OK`` and the content-type is
always ``text/html`` if you use this shortcut function.

Here's what the ZPT looks like again:

.. literalinclude:: step03/myapp/templates/default.pt
   :linenos:
   :language: xml

Life is better with templating:

#. Lines 1-2 make an ``<html>`` node with a namespace for TAL.

#. Line 5 inserts the value of the ``name`` that we passed into
   ``render_template_to_response``.

#. Line 6 looks interesting.  It uses the ``node`` that we passed in
   via ``render_template_to_response``.  Since :term:`chameleon.zpt`
   uses Python as its expession language, we can put anything
   Python-legal between the braces.  And since ``node`` is an ``lxml``
   ``Element`` object, we just ask for its ``.tag``, like regular
   Python ``lxml`` code.

Viewing the ZPT
------------------

With all of that in place, restarting the application and visiting
``http://localhost:5432/a`` now generates, via the ZPT, the
following::

  My template is viewing item: a

  The node has a tag name of: document.

If you visit ``http://localhost:5432/`` you will see::

  My template is viewing item: site

  The node has a tag name of: site.

We've successfully rendered a view that uses a template against a
model using the ZPT templating language.


XSLT Templates
==============

So that's the ZPT way of rendering HTML for an XML document.  We can
additonally use XSLT to do templating.  How might XSLT look?

``configure.zcml``
----------------------------------

Make your ``configure.zcml`` look like so:

.. literalinclude:: step03/myapp/configure.zcml
   :linenos:
   :language: xml

#. Lines 10-14 wire up a new view, in addition to the default view.

#. Line 13 provides the difference: ``name="xsltview.html"`` means
   that URLs invoked against our model can have ``/xsltview.html``
   appended to them, which will invoke our XSLT view.

In the ZCML, there is no distinction between a ZPT view and an XSLT
view.  The difference is only in the function that is pointed to by
the ``view=`` attribute.  The view itself controls which templating
language is in use.

``views.py``
--------------------------------

The ZCML says that our XSLT view (``xsltview.html`` on the URL) comes
from the ``lxmlgraph.views.xslt_view`` function, which you should add
to your ``views.py`` file:

.. literalinclude:: step03/myapp/views.py
   :linenos:

#. Line 9 starts the Python function which serves as the view for this
   template.  The function has the same signature as the
   ``zpt_default_view`` function we defined for the ZPT template's
   view.

#. Line 10 implements the difference.  We call
   ``render_transform_to_response`` instead of
   ``render_template_to_response``.  This tells :mod:`repoze.bfg` to
   make an XSLT processor for this template, instead of a ZPT.  The
   second argument passes in ``context`` to the XSLT transform.
   ``context``` is an instance of an Element node.  Namely, a node
   from the XML document that corresponds to the current hop in the
   URL.


``xsltview.xsl``
--------------------------------

Add a file named ``xsltview.xsl`` to your application's ``templates``
directory and give it the following contents:

.. literalinclude:: step03/myapp/templates/xsltview.xsl
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

With those changes in place, restart the application.  Visiting to the
``http://localhost:5432/a/xsltview.html`` URL should show::

  My template is viewing item: a

  The node has a name of: document.

We've successfully run an XSL template against our model object.

We've now seen how to use ZPT and XSL templates against model objects
created via an XML tree.


