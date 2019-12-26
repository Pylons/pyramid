# package
from functools import partial
from zope.interface import Interface, implementer


class IFactory(Interface):
    pass


def dummy_tween_factory(handler, registry):  # pragma: no cover
    pass


def dummy_tween_factory2(handler, registry):  # pragma: no cover
    pass


def dummy_include(config):
    config.registry.included = True
    config.action('discrim', None, config.package)


def dummy_include2(config):
    config.registry.also_included = True
    config.action('discrim', None, config.package)


includeme = dummy_include


class DummyContext:
    pass


@implementer(IFactory)
class DummyFactory(object):
    def __call__(self):
        """ """


def dummyfactory(request):
    """ """


class IDummy(Interface):
    pass


def dummy_view(request):
    return 'OK'


def dummy_extend(config, discrim):
    config.action(discrim, None, config.package)


def dummy_extend2(config, discrim):
    config.action(discrim, None, config.registry)


dummy_partial = partial(dummy_extend, discrim='partial')


class DummyCallable(object):
    def __call__(self, config, discrim):
        config.action(discrim, None, config.package)


dummy_callable = DummyCallable()
