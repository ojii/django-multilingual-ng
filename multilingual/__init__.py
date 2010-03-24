"""
Django-multilingual-ng: multilingual model support for Django 1.2.

Note about version numbers:
    - uneven minor versions are considered unstable releases
    - even minor versions are considered stable releases
"""
VERSION = ('0', '1', '20')
__version__ = '.'.join(VERSION)

try:
    """
    WARNING: All these names imported here WILL BE DEPRECATED!
    """
    from multilingual import models
    from multilingual.exceptions import TranslationDoesNotExist, LanguageDoesNotExist
    from multilingual.languages import (set_default_language, get_default_language,
                                        get_language_code_list)
    from multilingual.settings import FALLBACK_LANGUAGES
    from multilingual.translation import Translation
    from multilingual.admin import MultilingualModelAdmin, MultilingualInlineAdmin
    from multilingual.manager import Manager
    ModelAdmin = MultilingualModelAdmin
except ImportError:
    pass
