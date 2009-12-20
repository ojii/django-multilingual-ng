from django.utils.translation import get_language

from multilingual.exceptions import LanguageDoesNotExist
from multilingual.languages import set_default_language


class DefaultLanguageMiddleware(object):
    """
    Binds DEFAULT_LANGUAGE_CODE to django's currently selected language.

    The effect of enabling this middleware is that translated fields can be
    accessed by their name; i.e. model.field instead of model.field_en.
    """

    def process_request(self, request):
        assert hasattr(request, 'session'), "The DefaultLanguageMiddleware \
            middleware requires session middleware to be installed. Edit your \
            MIDDLEWARE_CLASSES setting to insert \
            'django.contrib.sessions.middleware.SessionMiddleware'."
        try:
            set_default_language(get_language())
        except LanguageDoesNotExist:
            # Try without the territory suffix
            set_default_language(get_language()[:2])
