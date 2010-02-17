"""
Django-multilingual: multilingual model support for Django.
"""

VERSION = (0,1,0,'b1')
__version__ = '0.1.0b1'

from multilingual import models
from multilingual.exceptions import TranslationDoesNotExist, LanguageDoesNotExist
from multilingual.languages import (set_default_language, get_default_language,
                                    get_language_code_list, FALLBACK_LANGUAGES)
from multilingual.translation import Translation
from multilingual.admin import ModelAdmin, MultilingualInlineAdmin
from multilingual.manager import Manager

MultilingualModelAdmin = ModelAdmin