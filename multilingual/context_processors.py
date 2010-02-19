from multilingual.languages import get_language_code_list, get_default_language_code
from multilingual.settings import LANG_DICT
from django.conf import settings


def multilingual(request):
    """
    Returns context variables containing information about available languages.
    """
    codes = sorted(get_language_code_list())
    return {'LANGUAGE_CODES': codes,
            'LANGUAGE_CODES_AND_NAMES': [(c, LANG_DICT.get(c, c)) for c in codes], 
            'DEFAULT_LANGUAGE_CODE': get_default_language_code(),
            'ADMIN_MEDIA_URL': settings.ADMIN_MEDIA_PREFIX}
