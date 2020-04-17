class NotAnException:
    pass


class AnException(Exception):
    pass


class RouteContext:
    pass


class RouteContext2:
    pass


def route_factory(*arg):
    return RouteContext()


def route_factory2(*arg):
    return RouteContext2()
