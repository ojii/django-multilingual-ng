from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

LANGUAGES = settings.LANGUAGES

LANG_DICT = dict(LANGUAGES)

def get_fallback_languages():
    fallbacks = {}
    for lang in LANG_DICT:
        fallbacks[lang] = [lang]
        for other in LANG_DICT:
            if other != lang:
                fallbacks[lang].append(other)
    return fallbacks

FALLBACK_LANGUAGES = getattr(settings, 'MULTILINGUAL_FALLBACK_LANGUAGES',
                             get_fallback_languages())
    
IMPLICIT_FALLBACK = getattr(settings, 'MULTILINGUAL_IMPLICIT_FALLBACK', True)

DEFAULT_LANGUAGE = getattr(settings, 'MULTILINGUAL_DEFAULT_LANGUAGE', LANGUAGES[0][0])

mcp = "multilingual.context_processors.multilingual"
if mcp not in settings.TEMPLATE_CONTEXT_PROCESSORS:
    found = ','.join(settings.TEMPLATE_CONTEXT_PROCESSORS)
    raise ImproperlyConfigured(
        "django-multilingual-ng requires the '%s' context processor. "
        "Only found: %s" % (mcp, found)
    )