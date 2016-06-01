.. index::
   single: Bicking, Ian
   single: WebOb

.. _webob_chapter:

Request and Response Objects
============================

.. note:: This chapter is adapted from a portion of the :term:`WebOb`
   documentation, originally written by Ian Bicking.

:app:`Pyramid` uses the :term:`WebOb` package as a basis for its
:term:`request` and :term:`response` object implementations.  The
:term:`request` object that is passed to a :app:`Pyramid` :term:`view` is an
instance of the :class:`pyramid.request.Request` class, which is a subclass of
:class:`webob.Request`.  The :term:`response` returned from a :app:`Pyramid`
:term:`view` :term:`renderer` is an instance of the
:mod:`pyramid.response.Response` class, which is a subclass of the
:class:`webob.Response` class.  Users can also return an instance of
:class:`pyramid.response.Response` directly from a view as necessary.

WebOb is a project separate from :app:`Pyramid` with a separate set of authors
and a fully separate `set of documentation
<http://docs.webob.org/en/latest/index.html>`_.  :app:`Pyramid` adds some
functionality to the standard WebOb request, which is documented in the
:ref:`request_module` API documentation.

WebOb provides objects for HTTP requests and responses.  Specifically it does
this by wrapping the `WSGI <http://wsgi.readthedocs.org/en/latest/>`_ request
environment and response status, header list, and app_iter (body) values.

WebOb request and response objects provide many conveniences for parsing WSGI
requests and forming WSGI responses.  WebOb is a nice way to represent "raw"
WSGI requests and responses.  However, we won't cover that use case in this
document, as users of :app:`Pyramid` don't typically need to use the
WSGI-related features of WebOb directly.  The `reference documentation
<http://docs.webob.org/en/latest/reference.html>`_ shows many examples of
creating requests and using response objects in this manner, however.

.. index::
   single: request object
   single: request attributes

Request
~~~~~~~

The request object is a wrapper around the `WSGI environ dictionary
<https://www.python.org/dev/peps/pep-0333/#environ-variables>`_.  This
dictionary contains keys for each header, keys that describe the request
(including the path and query string), a file-like object for the request body,
and a variety of custom keys.  You can always access the environ with
``req.environ``.

Some of the most important and interesting attributes of a request object are
below.

``req.method``
    The request method, e.g., ``GET``, ``POST``

``req.GET``
    A :term:`multidict` with all the variables in the query string.

``req.POST``
    A :term:`multidict` with all the variables in the request body.  This only
    has variables if the request was a ``POST`` and it is a form submission.

``req.params``
    A :term:`multidict` with a combination of everything in ``req.GET`` and
    ``req.POST``.

``req.body``
    The contents of the body of the request.  This contains the entire request
    body as a string.  This is useful when the request is a ``POST`` that is
    *not* a form submission, or a request like a ``PUT``.  You can also get
    ``req.body_file`` for a file-like object.

``req.json_body``
    The JSON-decoded contents of the body of the request. See
    :ref:`request_json_body`.

``req.cookies``
    A simple dictionary of all the cookies.

``req.headers``
    A dictionary of all the headers.  This dictionary is case-insensitive.

``req.urlvars`` and ``req.urlargs``
    ``req.urlvars`` are the keyword parameters associated with the request URL.
    ``req.urlargs`` are the positional parameters. These are set by products
    like `Routes <http://routes.readthedocs.org/en/latest/>`_ and `Selector
    <https://github.com/lukearno/selector>`_.

Also for standard HTTP request headers, there are usually attributes such as
``req.accept_language``, ``req.content_length``, and ``req.user_agent``.  These
properties expose the *parsed* form of each header, for whatever parsing makes
sense.  For instance, ``req.if_modified_since`` returns a :mod:`datetime`
object (or None if the header is was not provided).

.. note:: Full API documentation for the :app:`Pyramid` request object is
   available in :ref:`request_module`.

.. index::
   single: request attributes (special)

.. _special_request_attributes:

Special Attributes Added to the Request by :app:`Pyramid`
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

In addition to the standard :term:`WebOb` attributes, :app:`Pyramid` adds
special attributes to every request: ``context``, ``registry``, ``root``,
``subpath``, ``traversed``, ``view_name``, ``virtual_root``,
``virtual_root_path``, ``session``, ``matchdict``, and ``matched_route``. These
attributes are documented further within the :class:`pyramid.request.Request`
API documentation.

.. index::
   single: request URLs

URLs
++++

In addition to these attributes, there are several ways to get the URL of the
request and its parts.  We'll show various values for an example URL
``http://localhost/app/blog?id=10``, where the application is mounted at
``http://localhost/app``.

``req.url``
    The full request URL with query string, e.g.,
    ``http://localhost/app/blog?id=10``

``req.host``
    The host information in the URL, e.g., ``localhost``

``req.host_url``
    The URL with the host, e.g., ``http://localhost``

``req.application_url``
    The URL of the application (just the ``SCRIPT_NAME`` portion of the path,
    not ``PATH_INFO``), e.g., ``http://localhost/app``

``req.path_url``
    The URL of the application including the ``PATH_INFO``, e.g.,
    ``http://localhost/app/blog``

``req.path``
    The URL including ``PATH_INFO`` without the host or scheme, e.g.,
    ``/app/blog``

``req.path_qs``
    The URL including ``PATH_INFO`` and the query string, e.g,
    ``/app/blog?id=10``

``req.query_string``
    The query string in the URL, e.g., ``id=10``

``req.relative_url(url, to_application=False)``
    Gives a URL relative to the current URL.  If ``to_application`` is True,
    then resolves it relative to ``req.application_url``.

.. index::
   single: request methods

Methods
+++++++

There are methods of request objects documented in
:class:`pyramid.request.Request` but you'll find that you won't use very many
of them.  Here are a couple that might be useful:

``Request.blank(base_url)``
    Creates a new request with blank information, based at the given URL.  This
    can be useful for subrequests and artificial requests.  You can also use
    ``req.copy()`` to copy an existing request, or for subrequests
    ``req.copy_get()`` which copies the request but always turns it into a GET
    (which is safer to share for subrequests).

``req.get_response(wsgi_application)``
    This method calls the given WSGI application with this request, and returns
    a :class:`pyramid.response.Response` object.  You can also use this for
    subrequests or testing.

.. index::
   single: request (and text/unicode)
   single: unicode and text (and the request)

Text (Unicode)
++++++++++++++

Many of the properties of the request object will be text values (``unicode``
under Python 2 or ``str`` under Python 3) if the request encoding/charset is
provided.  If it is provided, the values in ``req.POST``, ``req.GET``,
``req.params``, and ``req.cookies`` will contain text.  The client *can*
indicate the charset with something like ``Content-Type:
application/x-www-form-urlencoded; charset=utf8``, but browsers seldom set
this.  You can reset the charset of an existing request with ``newreq =
req.decode('utf-8')``, or during instantiation with ``Request(environ,
charset='utf8')``.

.. index::
   single: multidict (WebOb)

.. _multidict_narr:

Multidict
+++++++++

Several attributes of a WebOb request are multidict structures (such as
``request.GET``, ``request.POST``, and ``request.params``).  A multidict is a
dictionary where a key can have multiple values.  The quintessential example is
a query string like ``?pref=red&pref=blue``; the ``pref`` variable has two
values: ``red`` and ``blue``.

In a multidict, when you do ``request.GET['pref']``, you'll get back only
``"blue"`` (the last value of ``pref``).  This returned result might not be
expected—sometimes returning a string, and sometimes returning a list—and may
be cause of frequent exceptions.  If you want *all* the values back, use
``request.GET.getall('pref')``.  If you want to be sure there is *one and only
one* value, use ``request.GET.getone('pref')``, which will raise an exception
if there is zero or more than one value for ``pref``.

When you use operations like ``request.GET.items()``, you'll get back something
like ``[('pref', 'red'), ('pref', 'blue')]``.  All the key/value pairs will
show up.  Similarly ``request.GET.keys()`` returns ``['pref', 'pref']``. 
Multidict is a view on a list of tuples; all the keys are ordered, and all the
values are ordered.

API documentation for a multidict exists as
:class:`pyramid.interfaces.IMultiDict`.

.. index::
   pair: json_body; request

.. _request_json_body:

Dealing with a JSON-Encoded Request Body
++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 1.1

:attr:`pyramid.request.Request.json_body` is a property that returns a
:term:`JSON`-decoded representation of the request body.  If the request does
not have a body, or the body is not a properly JSON-encoded value, an exception
will be raised when this attribute is accessed.

This attribute is useful when you invoke a :app:`Pyramid` view callable via,
for example, jQuery's ``$.ajax`` function, which has the potential to send a
request with a JSON-encoded body.

Using ``request.json_body`` is equivalent to:

.. code-block:: python

   from json import loads
   loads(request.body, encoding=request.charset)

Here's how to construct an AJAX request in JavaScript using :term:`jQuery` that
allows you to use the ``request.json_body`` attribute when the request is sent
to a :app:`Pyramid` application:

.. code-block:: javascript

    jQuery.ajax({type:'POST',
                 url: 'http://localhost:6543/', // the pyramid server
                 data: JSON.stringify({'a':1}),
                 contentType: 'application/json; charset=utf-8'});

When such a request reaches a view in your application, the
``request.json_body`` attribute will be available in the view callable body.

.. code-block:: python

    @view_config(renderer='string')
    def aview(request):
        print(request.json_body)
        return 'OK'

For the above view, printed to the console will be:

.. code-block:: python

    {u'a': 1}

For bonus points, here's a bit of client-side code that will produce a request
that has a body suitable for reading via ``request.json_body`` using Python's
``urllib2`` instead of a JavaScript AJAX request:

.. code-block:: python

    import urllib2
    import json

    json_payload = json.dumps({'a':1})
    headers = {'Content-Type':'application/json; charset=utf-8'}
    req = urllib2.Request('http://localhost:6543/', json_payload, headers)
    resp = urllib2.urlopen(req)

If you are doing Cross-origin resource sharing (CORS), then the standard
requires the browser to do a pre-flight HTTP OPTIONS request. The easiest way
to handle this is to add an extra ``view_config`` for the same route, with
``request_method`` set to ``OPTIONS``, and set the desired response header
before returning. You can find examples of response headers `Access control
CORS, Preflighted requests
<https://developer.mozilla.org/en-US/docs/Web/HTTP/Access_control_CORS#Preflighted_requests>`_.

.. index::
   single: cleaning up after request

.. _cleaning_up_after_a_request:

Cleaning up after a Request
+++++++++++++++++++++++++++

Sometimes it's required to perform some cleanup at the end of a request when a
database connection is involved.

For example, let's say you have a ``mypackage`` :app:`Pyramid` application
package that uses SQLAlchemy, and you'd like the current SQLAlchemy database
session to be removed after each request.  Put the following in the
``mypackage.__init__`` module:

.. code-block:: python
   :linenos:

   from mypackage.models import DBSession

   from pyramid.events import subscriber
   from pyramid.events import NewRequest

   def cleanup_callback(request):
       DBSession.remove()

   @subscriber(NewRequest)
   def add_cleanup_callback(event):
       event.request.add_finished_callback(cleanup_callback)

Registering the ``cleanup_callback`` finished callback at the start of a
request (by causing the ``add_cleanup_callback`` to receive a
:class:`pyramid.events.NewRequest` event at the start of each request) will
cause the DBSession to be removed whenever request processing has ended. Note
that in the example above, for the :class:`pyramid.events.subscriber` decorator
to work, the :meth:`pyramid.config.Configurator.scan` method must be called
against your ``mypackage`` package during application initialization.

.. note::
   This is only an example.  In particular, it is not necessary to cause
   ``DBSession.remove`` to be called in an application generated from any
   :app:`Pyramid` scaffold, because these all use the ``pyramid_tm`` package.
   The cleanup done by ``DBSession.remove`` is unnecessary when ``pyramid_tm``
   :term:`middleware` is configured into the application.

More Details
++++++++++++

More detail about the request object API is available as follows.

- :class:`pyramid.request.Request` API documentation

- `WebOb documentation <http://docs.webob.org/en/latest/index.html>`_.  All
  methods and attributes of a ``webob.Request`` documented within the WebOb
  documentation will work with request objects created by :app:`Pyramid`.

.. index::
   single: response object

Response
~~~~~~~~

The :app:`Pyramid` response object can be imported as
:class:`pyramid.response.Response`.  This class is a subclass of the
``webob.Response`` class.  The subclass does not add or change any
functionality, so the WebOb Response documentation will be completely relevant
for this class as well.

A response object has three fundamental parts:

``response.status``
    The response code plus reason message, like ``200 OK``.  To set the code
    without a message, use ``status_int``, i.e., ``response.status_int = 200``.

``response.headerlist``
    A list of all the headers, like ``[('Content-Type', 'text/html')]``.
    There's a case-insensitive :term:`multidict` in ``response.headers`` that
    also allows you to access these same headers.

``response.app_iter``
    An iterable (such as a list or generator) that will produce the content of
    the response.  This is also accessible as ``response.body`` (a string),
    ``response.text`` (a unicode object, informed by ``response.charset``), and
    ``response.body_file`` (a file-like object; writing to it appends to
    ``app_iter``).

Everything else in the object typically derives from this underlying state.
Here are some highlights:

``response.content_type``
    The content type *not* including the ``charset`` parameter.
    
    Typical use: ``response.content_type = 'text/html'``.

    Default value: ``response.content_type = 'text/html'``.

``response.charset``
    The ``charset`` parameter of the content-type, it also informs encoding in
    ``response.text``. ``response.content_type_params`` is a dictionary of all
    the parameters.

``response.set_cookie(key, value, max_age=None, path='/', ...)``
    Set a cookie.  The keyword arguments control the various cookie parameters.
    The ``max_age`` argument is the length for the cookie to live in seconds
    (you may also use a timedelta object).  The ``Expires`` key will also be
    set based on the value of ``max_age``.

``response.delete_cookie(key, path='/', domain=None)``
    Delete a cookie from the client.  This sets ``max_age`` to 0 and the cookie
    value to ``''``.

``response.cache_expires(seconds=0)``
    This makes the response cacheable for the given number of seconds, or if
    ``seconds`` is ``0`` then the response is uncacheable (this also sets the
    ``Expires`` header).

``response(environ, start_response)``
    The response object is a WSGI application.  As an application, it acts
    according to how you create it.  It *can* do conditional responses if you
    pass ``conditional_response=True`` when instantiating (or set that
    attribute later).  It can also do HEAD and Range requests.

.. index::
   single: response headers

Headers
+++++++

Like the request, most HTTP response headers are available as properties. These
are parsed, so you can do things like ``response.last_modified =
os.path.getmtime(filename)``.

The details are available in the :mod:`webob.response` API documentation.

.. index::
   single: response (creating)

Instantiating the Response
++++++++++++++++++++++++++

Of course most of the time you just want to *make* a response.  Generally any
attribute of the response can be passed in as a keyword argument to the class,
e.g.:

.. code-block:: python
  :linenos:

  from pyramid.response import Response
  response = Response(body='hello world!', content_type='text/plain')

The status defaults to ``'200 OK'``.

The value of ``content_type`` defaults to
``webob.response.Response.default_content_type``, which is ``text/html``. You
can subclass :class:`pyramid.response.Response` and set
``default_content_type`` to override this behavior.

.. index::
   single: exception responses

Exception Responses
+++++++++++++++++++

To facilitate error responses like ``404 Not Found``, the module
:mod:`pyramid.httpexceptions` contains classes for each kind of error response.
These include boring but appropriate error bodies.  The exceptions exposed by
this module, when used under :app:`Pyramid`, should be imported from the
:mod:`pyramid.httpexceptions` module.  This import location contains subclasses
and replacements that mirror those in the ``webob.exc`` module.

Each class is named ``pyramid.httpexceptions.HTTP*``, where ``*`` is the reason
for the error.  For instance, :class:`pyramid.httpexceptions.HTTPNotFound`
subclasses :class:`pyramid.response.Response`, so you can manipulate the
instances in the same way.  A typical example is:

.. code-block:: python
    :linenos:

    from pyramid.httpexceptions import HTTPNotFound
    from pyramid.httpexceptions import HTTPMovedPermanently

    response = HTTPNotFound('There is no such resource')
    # or:
    response = HTTPMovedPermanently(location=new_url)

More Details
++++++++++++

More details about the response object API are available in the
:mod:`pyramid.response` documentation.  More details about exception responses
are in the :mod:`pyramid.httpexceptions` API documentation.  The `WebOb
documentation <http://docs.webob.org/en/latest/index.html>`_ is also useful.
