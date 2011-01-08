.. _forms_chapter:

.. index::
   single: unicode, views, and forms
   single: forms, views, and unicode
   single: views, forms, and unicode

Form Handling
=============

Handling Form Submissions in View Callables (Unicode and Character Set Issues)
------------------------------------------------------------------------------

Most web applications need to accept form submissions from web browsers and
various other clients.  In :app:`Pyramid`, form submission handling logic is
always part of a :term:`view`.  For a general overview of how to handle form
submission data using the :term:`WebOb` API, see :ref:`webob_chapter` and
`"Query and POST variables" within the WebOb documentation
<http://pythonpaste.org/webob/reference.html#query-post-variables>`_.
:app:`Pyramid` defers to WebOb for its request and response implementations,
and handling form submission data is a property of the request
implementation.  Understanding WebOb's request API is the key to
understanding how to process form submission data.

There are some defaults that you need to be aware of when trying to handle
form submission data in a :app:`Pyramid` view.  Having high-order (i.e.,
non-ASCII) characters in data contained within form submissions is
exceedingly common, and the UTF-8 encoding is the most common encoding used
on the web for character data. Since Unicode values are much saner than
working with and storing bytestrings, :app:`Pyramid` configures the
:term:`WebOb` request machinery to attempt to decode form submission values
into Unicode from UTF-8 implicitly.  This implicit decoding happens when view
code obtains form field values via the ``request.params``, ``request.GET``,
or ``request.POST`` APIs (see :ref:`request_module` for details about these
APIs).

.. note::

   Many people find the difference between Unicode and UTF-8 confusing.
   Unicode is a standard for representing text that supports most of the
   world's writing systems. However, there are many ways that Unicode data
   can be encoded into bytes for transit and storage. UTF-8 is a specific
   encoding for Unicode, that is backwards-compatible with ASCII. This makes
   UTF-8 very convenient for encoding data where a large subset of that data
   is ASCII characters, which is largely true on the web. UTF-8 is also the
   standard character encoding for URLs.

As an example, let's assume that the following form page is served up to a
browser client, and its ``action`` points at some :app:`Pyramid` view code:

.. code-block:: xml
   :linenos:

   <html xmlns="http://www.w3.org/1999/xhtml">
     <head>
       <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
     </head>
     <form method="POST" action="myview">
       <div>
         <input type="text" name="firstname"/>
       </div> 
       <div>
         <input type="text" name="lastname"/>
       </div>
       <input type="submit" value="Submit"/>
     </form>
   </html>

The ``myview`` view code in the :app:`Pyramid` application *must* expect that
the values returned by ``request.params`` will be of type ``unicode``, as
opposed to type ``str``. The following will work to accept a form post from
the above form:

.. code-block:: python
   :linenos:

   def myview(request):
       firstname = request.params['firstname']
       lastname = request.params['lastname']

But the following ``myview`` view code *may not* work, as it tries to decode
already-decoded (``unicode``) values obtained from ``request.params``:

.. code-block:: python
   :linenos:

   def myview(request):
       # the .decode('utf-8') will break below if there are any high-order
       # characters in the firstname or lastname
       firstname = request.params['firstname'].decode('utf-8')
       lastname = request.params['lastname'].decode('utf-8')

For implicit decoding to work reliably, you should ensure that every form you
render that posts to a :app:`Pyramid` view explicitly defines a charset
encoding of UTF-8. This can be done via a response that has a
``;charset=UTF-8`` in its ``Content-Type`` header; or, as in the form above,
with a ``meta http-equiv`` tag that implies that the charset is UTF-8 within
the HTML ``head`` of the page containing the form.  This must be done
explicitly because all known browser clients assume that they should encode
form data in the same character set implied by ``Content-Type`` value of the
response containing the form when subsequently submitting that form. There is
no other generally accepted way to tell browser clients which charset to use
to encode form data.  If you do not specify an encoding explicitly, the
browser client will choose to encode form data in its default character set
before submitting it, which may not be UTF-8 as the server expects.  If a
request containing form data encoded in a non-UTF8 charset is handled by your
view code, eventually the request code accessed within your view will throw
an error when it can't decode some high-order character encoded in another
character set within form data, e.g., when ``request.params['somename']`` is
accessed.

If you are using the :class:`pyramid.response.Response` class to generate a
response, or if you use the ``render_template_*`` templating APIs, the UTF-8
charset is set automatically as the default via the ``Content-Type`` header.
If you return a ``Content-Type`` header without an explicit charset, a
request will add a ``;charset=utf-8`` trailer to the ``Content-Type`` header
value for you, for response content types that are textual
(e.g. ``text/html``, ``application/xml``, etc) as it is rendered.  If you are
using your own response object, you will need to ensure you do this yourself.

.. note:: Only the *values* of request params obtained via
   ``request.params``, ``request.GET`` or ``request.POST`` are decoded
   to Unicode objects implicitly in the :app:`Pyramid` default
   configuration.  The keys are still (byte) strings.


