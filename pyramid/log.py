import logging

def make_stream_logger(
    name, stream, levelname='DEBUG', fmt='%(asctime)s %(message)s'):
    """ Return an object which implements
    ``repoze.bfg.interfaces.IDebugLogger`` (ie. a Python PEP 282 logger
    instance) with the name ``name`` using the stream (or open
    filehandle) ``stream``, logging at ``levelname`` log level or
    above with format ``fmt``. """
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger = logging.Logger(name)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, levelname))
    return logger
