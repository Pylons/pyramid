import email.message
import unittest


class TestPDistReportCommand(unittest.TestCase):
    def _callFUT(self, **kw):
        argv = []
        from pyramid.scripts.pdistreport import main

        return main(argv, **kw)

    def test_no_dists(self):
        def platform():
            return 'myplatform'

        importlib_metadata = DummyImportlibMetadata()
        L = []

        def out(*args):
            L.extend(args)

        result = self._callFUT(
            importlib_metadata=importlib_metadata, platform=platform, out=out
        )
        self.assertEqual(result, None)
        self.assertEqual(
            L,
            ['Pyramid version:', '1', 'Platform:', 'myplatform', 'Packages:'],
        )

    def test_with_dists(self):
        def platform():
            return 'myplatform'

        working_set = (DummyDistribution('abc'), DummyDistribution('def'))
        importlib_metadata = DummyImportlibMetadata(working_set)
        L = []

        def out(*args):
            L.extend(args)

        result = self._callFUT(
            importlib_metadata=importlib_metadata, platform=platform, out=out
        )
        self.assertEqual(result, None)
        self.assertEqual(
            L,
            [
                'Pyramid version:',
                '1',
                'Platform:',
                'myplatform',
                'Packages:',
                ' ',
                'abc',
                '1',
                '   ',
                'summary for name=\'abc\'',
                ' ',
                'def',
                '1',
                '   ',
                'summary for name=\'def\'',
            ],
        )


class DummyImportlibMetadata:
    def __init__(self, distributions=()):
        self._distributions = distributions

    def distribution(self, name):
        return DummyDistribution(name)

    def distributions(self):
        return iter(self._distributions)


class DummyDistribution:
    def __init__(self, name):
        self.version = '1'
        self.metadata = email.message.Message()
        self.metadata['Name'] = name
        self.metadata['Summary'] = f'summary for {name=}'
