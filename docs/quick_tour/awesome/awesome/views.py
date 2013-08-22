from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('awesome')

def my_view(request):
    return {'project':'awesome'}
