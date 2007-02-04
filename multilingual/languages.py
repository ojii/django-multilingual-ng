"""
Django-multilingual: language-related settings and functions.
"""

#retrieve language settings from settings.py
from django.conf import settings
LANGUAGES = settings.LANGUAGES

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

thread_locals = local()

#dev-note: it might be nice to define the default language per-model
thread_locals.DEFAULT_LANGUAGE = settings.DEFAULT_LANGUAGE

def get_language_count():
    return len(LANGUAGES)

def get_language_code(language_id):
    return LANGUAGES[(int(language_id or thread_locals.DEFAULT_LANGUAGE)) - 1][0]

def get_language_name(language_id):
    return LANGUAGES[(int(language_id or thread_locals.DEFAULT_LANGUAGE)) - 1][1]

def get_language_id_list():
    return range(1, get_language_count() + 1)

def get_language_choices():
    return [(language_id, get_language_code(language_id))
            for language_id in get_language_id_list()]

def get_language_id_from_id_or_code(language_id_or_code):
    if language_id_or_code is None:
        return None
    
    if isinstance(language_id_or_code, int):
        return language_id_or_code

    i = 0
    for (code, desc) in LANGUAGES:
        i += 1
        if code == language_id_or_code:
            return i
    raise LanguageDoesNotExist()

def set_default_language(language_id_or_code):
    """
    Set the default language for the whole translation mechanism.

    To do: find a better place to store the value.
    """
    language_id = get_language_id_from_id_or_code(language_id_or_code)
    thread_locals.DEFAULT_LANGUAGE = language_id

def get_default_language():
    # you might take the ID from elsewhere, ie
    # cookies or threadlocals
    return thread_locals.DEFAULT_LANGUAGE

def get_translation_table_alias(translation_table_name, language_id):
    """
    Return an alias for the translation table for a given language_id.
    Used in SQL queries.
    """
    return translation_table_name + '_' + get_language_code(language_id)

def get_translated_field_alias(field_name, language_id=None):
    """
    Return an alias for field_name field for a given language_id.
    Used in SQL queries.
    """
    return '_trans_' + field_name + '_' + get_language_code(language_id)

