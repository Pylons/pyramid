from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('hello_world')

def my_view(request):
    return {'project':'hello_world'}
