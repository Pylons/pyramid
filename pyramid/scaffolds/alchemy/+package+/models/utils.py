import venusian

def scan(pkg, registry=None):
    if registry is None:
        registry = {}
    scanner = venusian.Scanner(registry=registry)
    scanner.scan(pkg)
    return registry

def expose(wrapped):
    def callback(scanner, name, obj):
        registry = getattr(scanner, 'registry', None)
        if registry is not None:
            registry[name] = wrapped
    venusian.attach(wrapped, callback)
    return wrapped

def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses
