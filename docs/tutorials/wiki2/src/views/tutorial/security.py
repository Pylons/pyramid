from pyramid.csrf import CookieCSRFStoragePolicy


def includeme(config):
    config.set_csrf_storage_policy(CookieCSRFStoragePolicy())
    config.set_default_csrf_options(require_csrf=True)
