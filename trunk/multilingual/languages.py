"""
Django-multilingual: language-related settings and functions.
"""

# This is ugly, ideally languages should be taken from the DB or
# settings file.  Oh well, it is a prototype anyway.

# It is important that the language identifiers are consecutive
# numbers starting with 1.
LANGUAGES = [['en', 'English'], # id=1
             ['pl', 'Polish']]  # id=2

DEFAULT_LANGUAGE = 1

def get_language_count():
    return len(LANGUAGES)

def get_language_code(language_id):
    return LANGUAGES[(language_id or DEFAULT_LANGUAGE) - 1][0]

def get_language_name(language_id):
    return LANGUAGES[(language_id or DEFAULT_LANGUAGE) - 1][1]

def get_language_id_list():
    return range(1, get_language_count() + 1)

def set_default_language(language_id):
    """
    Set the default language for the whole translation mechanism.

    To do: find a better place to store the value.
    """
    import multilingual.languages
    multilingual.languages.DEFAULT_LANGUAGE = language_id

def get_default_language():
    # you might take the ID from elsewhere, ie
    # cookies or threadlocals
    return DEFAULT_LANGUAGE

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

