Templates
=========

A *template* is a file on disk which can be used to render data
provided by a *view*.

Default Templating With z3c.pt Page Templates
------------------------------------------------

Like Zope, :mod:`repoze.bfg` uses Zope Page Templates (ZPT) as its
default templating language. However, :mod:`repoze.bfg` uses a
different implementation of the ZPT specification: the :term:`z3c.pt`
templating engine. This templating engine complies with the `Zope Page
Template <http://wiki.zope.org/ZPT/FrontPage>`_ template
specification. While :term:`z3c.pt` doesn't implement the *METAL*
specification (feature or drawback, depending on your viewpoint), it
is significantly faster.

Given a template named ``foo.html`` in a directory in your application
named "templates", you can render the template in a view via::

  from repoze.bfg.template import render_template_to_response
  return render_template_to_response('templates/foo.html', foo=1, bar=2)

You associate a view with a URL by adding information to your ZCML.

.. sourcecode:: xml

  <bfg:view
      for=".models.IMapping"
      view=".views.contents_view"
      name="contents.html"
      />

:mod:`repoze.bfg` loads the template and keeps it in memory between
requests. This means that modifications to the ZPT require a restart
before you can see the changes.

Templating with XSLT
------------------------

:mod:`repoze.bfg` also supports XSLT as an optional templating
language.  Like ZPT, an XSLT template is loaded once and re-used
between requests.

Given a template ``foo.xsl`` in the templates directory, you can render
an XSLT as follows::

  from repoze.bfg.template import render_transform_to_response
  from lxml import etree
  node = etree.Element("root")  
  return render_transform_to_response('templates/foo.xsl', node)

As shown, the second argument to ``render_transform_to_response`` is
the element (and children) that you want as the top of the data for
the XSLT.

You can also pass XSLT parameters in as keyword arguments::

  from repoze.bfg.template import render_transform_to_response
  from lxml import etree
  node = etree.Element("root")
  value1 = "'app1'"
  return render_transform_to_response('templates/foo.xsl', node, param1=value1)

This would then assign 'app1' as the value of an ``<xsl:param
name="param1"/>`` parameter in the XSLT template.
