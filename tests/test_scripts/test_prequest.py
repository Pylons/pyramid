from io import StringIO
import unittest

from . import dummy


class TestPRequestCommand(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.scripts.prequest import PRequestCommand

        return PRequestCommand

    def _makeOne(self, argv, headers=None):
        cmd = self._getTargetClass()(argv)

        def helloworld(environ, start_request):
            self._environ = environ
            self._path_info = environ['PATH_INFO']
            start_request('200 OK', headers or [])
            return [b'abc']

        self.loader = dummy.DummyLoader(app=helloworld)
        self._out = []
        cmd._get_config_loader = self.loader
        cmd.out = self.out
        return cmd

    def out(self, msg):
        self._out.append(msg)

    def test_command_not_enough_args(self):
        command = self._makeOne([])
        command.run()
        self.assertEqual(
            self._out, ['You must provide at least two arguments']
        )

    def test_command_two_args(self):
        command = self._makeOne(
            ['', 'development.ini', '/'],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        command.run()
        self.assertEqual(self._path_info, '/')
        self.assertEqual(self.loader.uri.path, 'development.ini')
        self.assertEqual(self.loader.calls[0]['op'], 'logging')
        self.assertEqual(self.loader.calls[1]['op'], 'app')
        self.assertEqual(self.loader.calls[1]['name'], None)
        self.assertEqual(self._out, ['abc'])

    def test_command_path_doesnt_start_with_slash(self):
        command = self._makeOne(
            ['', 'development.ini', 'abc'],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        command.run()
        self.assertEqual(self._path_info, '/abc')
        self.assertEqual(self.loader.uri.path, 'development.ini')
        self.assertEqual(self._out, ['abc'])

    def test_command_has_bad_config_header(self):
        command = self._makeOne(['', '--header=name', 'development.ini', '/'])
        command.run()
        self.assertEqual(
            self._out[0],
            (
                "Bad --header=name option, value must be in the form "
                "'name:value'"
            ),
        )

    def test_command_has_good_header_var(self):
        command = self._makeOne(
            ['', '--header=name:value', 'development.ini', '/'],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        command.run()
        self.assertEqual(self._environ['HTTP_NAME'], 'value')
        self.assertEqual(self._path_info, '/')
        self.assertEqual(self._out, ['abc'])

    def test_command_w_basic_auth(self):
        command = self._makeOne(
            [
                '',
                '--login=user:password',
                '--header=name:value',
                'development.ini',
                '/',
            ],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        command.run()
        self.assertEqual(self._environ['HTTP_NAME'], 'value')
        self.assertEqual(
            self._environ['HTTP_AUTHORIZATION'], 'Basic dXNlcjpwYXNzd29yZA=='
        )
        self.assertEqual(self._path_info, '/')
        self.assertEqual(self._out, ['abc'])

    def test_command_has_content_type_header_var(self):
        command = self._makeOne(
            ['', '--header=content-type:app/foo', 'development.ini', '/'],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        command.run()
        self.assertEqual(self._environ['CONTENT_TYPE'], 'app/foo')
        self.assertEqual(self._path_info, '/')
        self.assertEqual(self._out, ['abc'])

    def test_command_has_multiple_header_vars(self):
        command = self._makeOne(
            [
                '',
                '--header=name:value',
                '--header=name2:value2',
                'development.ini',
                '/',
            ],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        command.run()
        self.assertEqual(self._environ['HTTP_NAME'], 'value')
        self.assertEqual(self._environ['HTTP_NAME2'], 'value2')
        self.assertEqual(self._path_info, '/')
        self.assertEqual(self._out, ['abc'])

    def test_command_method_get(self):
        command = self._makeOne(
            ['', '--method=GET', 'development.ini', '/'],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        command.run()
        self.assertEqual(self._environ['REQUEST_METHOD'], 'GET')
        self.assertEqual(self._path_info, '/')
        self.assertEqual(self._out, ['abc'])

    def test_command_method_post(self):
        command = self._makeOne(
            ['', '--method=POST', 'development.ini', '/'],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        stdin = StringIO()
        command.stdin = stdin
        command.run()
        self.assertEqual(self._environ['REQUEST_METHOD'], 'POST')
        self.assertEqual(self._environ['CONTENT_LENGTH'], '-1')
        self.assertEqual(self._environ['wsgi.input'], stdin)
        self.assertEqual(self._path_info, '/')
        self.assertEqual(self._out, ['abc'])

    def test_command_method_put(self):
        command = self._makeOne(
            ['', '--method=PUT', 'development.ini', '/'],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        stdin = StringIO()
        command.stdin = stdin
        command.run()
        self.assertEqual(self._environ['REQUEST_METHOD'], 'PUT')
        self.assertEqual(self._environ['CONTENT_LENGTH'], '-1')
        self.assertEqual(self._environ['wsgi.input'], stdin)
        self.assertEqual(self._path_info, '/')
        self.assertEqual(self._out, ['abc'])

    def test_command_method_patch(self):
        command = self._makeOne(
            ['', '--method=PATCH', 'development.ini', '/'],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        stdin = StringIO()
        command.stdin = stdin
        command.run()
        self.assertEqual(self._environ['REQUEST_METHOD'], 'PATCH')
        self.assertEqual(self._environ['CONTENT_LENGTH'], '-1')
        self.assertEqual(self._environ['wsgi.input'], stdin)
        self.assertEqual(self._path_info, '/')
        self.assertEqual(self._out, ['abc'])

    def test_command_method_propfind(self):
        command = self._makeOne(
            ['', '--method=PROPFIND', 'development.ini', '/'],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        stdin = StringIO()
        command.stdin = stdin
        command.run()
        self.assertEqual(self._environ['REQUEST_METHOD'], 'PROPFIND')
        self.assertEqual(self._path_info, '/')
        self.assertEqual(self._out, ['abc'])

    def test_command_method_options(self):
        command = self._makeOne(
            ['', '--method=OPTIONS', 'development.ini', '/'],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        stdin = StringIO()
        command.stdin = stdin
        command.run()
        self.assertEqual(self._environ['REQUEST_METHOD'], 'OPTIONS')
        self.assertEqual(self._path_info, '/')
        self.assertEqual(self._out, ['abc'])

    def test_command_with_query_string(self):
        command = self._makeOne(
            ['', 'development.ini', '/abc?a=1&b=2&c'],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        command.run()
        self.assertEqual(self._environ['QUERY_STRING'], 'a=1&b=2&c')
        self.assertEqual(self._path_info, '/abc')
        self.assertEqual(self._out, ['abc'])

    def test_command_display_headers(self):
        command = self._makeOne(
            ['', '--display-headers', 'development.ini', '/'],
            [('Content-Type', 'text/html; charset=UTF-8')],
        )
        command.run()
        self.assertEqual(self._path_info, '/')
        self.assertEqual(
            self._out,
            ['200 OK', 'Content-Type: text/html; charset=UTF-8', 'abc'],
        )

    def test_command_response_has_no_charset(self):
        command = self._makeOne(
            ['', '--method=GET', 'development.ini', '/'],
            headers=[('Content-Type', 'image/jpeg')],
        )
        command.run()
        self.assertEqual(self._path_info, '/')

        self.assertEqual(self._out, [b'abc'])

    def test_command_method_configures_logging(self):
        command = self._makeOne(['', '--method=GET', 'development.ini', '/'])
        command.run()
        self.assertEqual(self.loader.calls[0]['op'], 'logging')

    def test_command_script_name(self):
        command = self._makeOne(['', '--method=GET', 'development.ini', '/'])
        command.run()
        self.assertEqual(
            self.loader.calls[0]['defaults']['__script__'], 'prequest'
        )


class Test_main(unittest.TestCase):
    def _callFUT(self, argv):
        from pyramid.scripts.prequest import main

        return main(argv, True)

    def test_it(self):
        result = self._callFUT(['prequest'])
        self.assertEqual(result, 2)
