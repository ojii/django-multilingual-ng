"""
Django-multilingual: language-related settings and functions.
"""

# Note: this file did become a mess and will have to be refactored
# after the configuration changes get in place.

#retrieve language settings from settings.py
from django.conf import settings
LANGUAGES = settings.LANGUAGES

try:
    FALLBACK_LANGUAGES = settings.MULTILINGUAL_FALLBACK_LANGUAGES
except AttributeError:
    FALLBACK_LANGUAGES = [lang[0] for lang in settings.LANGUAGES]

from django.utils.translation import ugettext_lazy as _
from multilingual.exceptions import LanguageDoesNotExist

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

thread_locals = local()

def get_language_count():
    return len(LANGUAGES)

def get_language_code(language_id):
    return LANGUAGES[(int(language_id or get_default_language())) - 1][0]

def get_language_name(language_id):
    return _(LANGUAGES[(int(language_id or get_default_language())) - 1][1])

def get_language_bidi(language_id):
    return get_language_code(language_id) in settings.LANGUAGES_BIDI

def get_language_id_list():
    return range(1, get_language_count() + 1)

def get_language_code_list():
    return [lang[0] for lang in LANGUAGES]

def get_language_choices():
    return [(language_id, get_language_code(language_id))
            for language_id in get_language_id_list()]

def get_language_id_from_id_or_code(language_id_or_code, use_default=True):
    if language_id_or_code is None:
        if use_default:
            return get_default_language()
        else:
            return None

    if isinstance(language_id_or_code, int):
        return language_id_or_code

    i = 0
    for (code, desc) in LANGUAGES:
        i += 1
        if code == language_id_or_code:
            return i
        if language_id_or_code.startswith("%s-" % code):
            return i
    raise LanguageDoesNotExist(language_id_or_code)

def get_language_idx(language_id_or_code):
    # to do: optimize
    language_id = get_language_id_from_id_or_code(language_id_or_code)
    return get_language_id_list().index(language_id)

def set_default_language(language_id_or_code):
    """
    Set the default language for the whole translation mechanism.

    Accepts language codes or IDs.
    """
    language_id = get_language_id_from_id_or_code(language_id_or_code)
    thread_locals.DEFAULT_LANGUAGE = language_id

def get_default_language():
    """
    Return the language ID set by set_default_language.
    """
    return getattr(thread_locals, 'DEFAULT_LANGUAGE',
                   settings.DEFAULT_LANGUAGE)

def get_default_language_code():
    """
    Return the language code of language ID set by set_default_language.
    """
    language_id = get_language_id_from_id_or_code(get_default_language())
    return get_language_code(language_id)

def _to_db_identifier(name):
    """
    Convert name to something that is usable as a field name or table
    alias in SQL.

    For the time being assume that the only possible problem with name
    is the presence of dashes.
    """
    return name.replace('-', '_')

def get_translation_table_alias(translation_table_name, language_id):
    """
    Return an alias for the translation table for a given language_id.
    Used in SQL queries.
    """
    return (translation_table_name
            + '_'
            + _to_db_identifier(get_language_code(language_id)))

def get_translated_field_alias(field_name, language_id=None):
    """
    Return an alias for field_name field for a given language_id.
    Used in SQL queries.
    """
    return ('_trans_'
            + field_name
            + '_' + _to_db_identifier(get_language_code(language_id)))

FALLBACK_LANGUAGE_IDS = [get_language_id_from_id_or_code(lang_code) for lang_code in FALLBACK_LANGUAGES]

FALLBACK_FIELD_SUFFIX = '_any'

