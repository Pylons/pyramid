Templates
=========

A *template* is a file on disk which can be used to render data
provided by a *view* in a form that is meaningful for a particular
*context*.

The ``repoze.bfg`` Default Templating Systems
---------------------------------------------

``repoze.bfg`` uses the `z3c.pt
<http://pypi.python.org/pypi/z3c.pt>`_
templating engine as its default
engine.  This templating engine
complies with the `Zope Page
Template
<http://wiki.zope.org/ZPT/FrontPage>`_
template specification.

``repoze.bfg`` also allows `XSL
Templates
<http://www.w3.org/TR/xslt>`_
to be used for templating.


Rendering a ``z3c.pt`` Template
-------------------------------

Given a template named ``foo.html``
in a directory in your application
named "templates", you can render
the template in a view via::

  from repoze.bfg.template import render template
  render_template('templates/foo.html', foo=1, bar=2)
