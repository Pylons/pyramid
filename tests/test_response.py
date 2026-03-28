from datetime import datetime, timezone
import io
import mimetypes
import os
from os.path import getmtime, getsize
import unittest
from unittest.mock import Mock

from pyramid import testing
from pyramid.request import Request


class TestResponse(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.response import Response

        return Response

    def test_implements_IResponse(self):
        from pyramid.interfaces import IResponse

        cls = self._getTargetClass()
        self.assertTrue(IResponse.implementedBy(cls))

    def test_provides_IResponse(self):
        from pyramid.interfaces import IResponse

        inst = self._getTargetClass()()
        self.assertTrue(IResponse.providedBy(inst))


class TestFileResponse(unittest.TestCase):
    def setUp(self):
        self.request = Request.blank('/')
        self.config = testing.setUp(request=self.request)

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, file, **kw):
        from pyramid.response import FileResponse

        return FileResponse(file, **kw)

    def _get_path(self, suffix='txt'):
        here = os.path.dirname(__file__)
        return os.path.join(here, 'fixtures', f'minimal.{suffix}')

    def _validate_content(self, r, suffix='txt'):
        path = self._get_path(suffix)
        with open(path, 'rb') as fh:
            expected = fh.read()
        self.assertEqual(r.body, expected, 'File contents do not match.')
        expected_dt = datetime.fromtimestamp(getmtime(path), timezone.utc)
        expected_dt = expected_dt.replace(microsecond=0)
        self.assertEqual(r.last_modified, expected_dt)
        self.assertEqual(r.content_length, getsize(path))

    def test_with_image_content_type(self):
        path = self._get_path('jpg')
        r = self._makeOne(path, content_type='image/jpeg')
        self.assertEqual(r.content_type, 'image/jpeg')
        self.assertEqual(r.headers['content-type'], 'image/jpeg')
        self._validate_content(r, 'jpg')

    def test_with_xml_content_type(self):
        path = self._get_path('xml')
        r = self._makeOne(path, content_type='application/xml')
        self.assertEqual(r.content_type, 'application/xml')
        self.assertEqual(
            r.headers['content-type'], 'application/xml; charset=UTF-8'
        )
        self._validate_content(r, 'xml')

    def test_with_pdf_content_type(self):
        path = self._get_path('xml')
        r = self._makeOne(path, content_type='application/pdf')
        self.assertEqual(r.content_type, 'application/pdf')
        self.assertEqual(r.headers['content-type'], 'application/pdf')
        self._validate_content(r, 'xml')

    def test_without_content_type(self):
        for suffix in ('txt', 'xml', 'pdf'):
            path = self._get_path(suffix)
            r = self._makeOne(path)
            self.assertEqual(
                r.headers['content-type'].split(';')[0],
                mimetypes.guess_type(path, strict=False)[0],
            )
            self._validate_content(r, suffix)

    def test_wsgi_file_wrapper(self):
        from pyramid.response import FileIter

        wrapper = Mock(side_effect=FileIter)
        request = Request.blank(
            '/',
            environ={
                'wsgi.file_wrapper': wrapper,
            },
        )

        path = self._get_path()
        r = self._makeOne(path, request=request)
        self._validate_content(r)

        wrapper.assert_called_once()


class TestFileIter(unittest.TestCase):
    def _makeOne(self, file, block_size):
        from pyramid.response import FileIter

        return FileIter(file, block_size)

    def test___iter__(self):
        f = io.BytesIO(b'abc')
        inst = self._makeOne(f, 1)
        self.assertEqual(inst.__iter__(), inst)

    def test_iteration(self):
        data = b'abcdef'
        f = io.BytesIO(b'abcdef')
        inst = self._makeOne(f, 1)
        r = b''
        for x in inst:
            self.assertEqual(len(x), 1)
            r += x
        self.assertEqual(r, data)

    def test_close(self):
        f = io.BytesIO(b'abc')
        inst = self._makeOne(f, 1)
        inst.close()
        self.assertTrue(f.closed)


class TestResponseAdapter(unittest.TestCase):
    def setUp(self):
        registry = Dummy()
        self.config = testing.setUp(registry=registry)

    def tearDown(self):
        self.config.end()

    def _makeOne(self, *types_or_ifaces, **kw):
        from pyramid.response import response_adapter

        return response_adapter(*types_or_ifaces, **kw)

    def test_register_single(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass

        dec = self._makeOne(IFoo)

        def foo():  # pragma: no cover
            pass

        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(config.adapters, [(foo, IFoo)])

    def test_register_multi(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        dec = self._makeOne(IFoo, IBar)

        def foo():  # pragma: no cover
            pass

        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(config.adapters, [(foo, IFoo), (foo, IBar)])

    def test___call__(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass

        dec = self._makeOne(IFoo)
        dummy_venusian = DummyVenusian()
        dec.venusian = dummy_venusian

        def foo():  # pragma: no cover
            pass

        dec(foo)
        self.assertEqual(
            dummy_venusian.attached, [(foo, dec.register, 'pyramid', 1)]
        )

    def test___call___with_venusian_args(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass

        dec = self._makeOne(IFoo, _category='foo', _depth=1)
        dummy_venusian = DummyVenusian()
        dec.venusian = dummy_venusian

        def foo():  # pragma: no cover
            pass

        dec(foo)
        self.assertEqual(
            dummy_venusian.attached, [(foo, dec.register, 'foo', 2)]
        )


class TestGetResponseFactory(unittest.TestCase):
    def test_get_factory(self):
        from pyramid.registry import Registry
        from pyramid.response import Response, _get_response_factory

        registry = Registry()
        response = _get_response_factory(registry)(None)
        self.assertTrue(isinstance(response, Response))


class Dummy:
    pass


class DummyConfigurator:
    def __init__(self):
        self.adapters = []

    def add_response_adapter(self, wrapped, type_or_iface):
        self.adapters.append((wrapped, type_or_iface))


class DummyVenusian:
    def __init__(self):
        self.attached = []

    def attach(self, wrapped, fn, category=None, depth=None):
        self.attached.append((wrapped, fn, category, depth))
