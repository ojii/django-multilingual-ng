"""
Django-multilingual: language-related settings and functions.
"""

# Note: this file did become a mess and will have to be refactored
# after the configuration changes get in place.

#retrieve language settings from settings.py
from multilingual import settings

from django.utils.translation import ugettext_lazy as _
from multilingual.exceptions import LanguageDoesNotExist

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

thread_locals = local()

def get_language_count():
    return len(settings.LANGUAGES)

def get_language_name(language_code):
    return settings.LANG_DICT[language_code]

def get_language_bidi(language_code):
    return language_code in settings.LANGUAGES_BIDI

def get_language_code_list():
    return settings.LANG_DICT.keys()

def get_language_choices():
    return settings.LANGUAGES

def set_default_language(language_code):
    """
    Set the default language for the whole translation mechanism.
    """
    thread_locals.DEFAULT_LANGUAGE = language_code

def get_default_language():
    """
    Return the language code set by set_default_language.
    """
    return getattr(thread_locals, 'DEFAULT_LANGUAGE',
                   settings.DEFAULT_LANGUAGE)
get_default_language_code = get_default_language

def _to_db_identifier(name):
    """
    Convert name to something that is usable as a field name or table
    alias in SQL.

    For the time being assume that the only possible problem with name
    is the presence of dashes.
    """
    return name.replace('-', '_')

def get_translation_table_alias(translation_table_name, language_code):
    """
    Return an alias for the translation table for a given language_code.
    Used in SQL queries.
    """
    return (translation_table_name
            + '_'
            + _to_db_identifier(language_code))

def get_language_idx(language_code):
    return get_language_code_list().index(language_code)

def get_translated_field_alias(field_name, language_code):
    """
    Return an alias for field_name field for a given language_code.
    Used in SQL queries.
    """
    return ('_trans_'
            + field_name
            + '_' + _to_db_identifier(language_code))
    
def get_fallbacks(language_code):
    fallbacks = settings.FALLBACK_LANGUAGES.get(language_code, [])
    if len(language_code) != 2 and settings.IMPLICIT_FALLBACK:
        if not language_code[:2] in fallbacks:
            fallbacks.insert(0, language_code[:2])
    if language_code is not None and language_code not in fallbacks:
        fallbacks.insert(0, language_code)
    return fallbacks

FALLBACK_FIELD_SUFFIX = '_any'