"""
Django-multilingual-ng: multilingual model support for Django 1.2.
"""
import warnings

VERSION = (0,1,0,'b2')
__version__ = '0.1.0b2' 

def get_full(obj):
    return '%s.%s' % (obj.__module__, obj.__name__)

class BackwardsCompatibility(object):
    def __init__(self):
        try:
            from multilingual import models
            from multilingual.exceptions import TranslationDoesNotExist, LanguageDoesNotExist
            from multilingual.languages import (set_default_language, get_default_language,
                                                get_language_code_list)
            from multilingual.settings import FALLBACK_LANGUAGES
            from multilingual.translation import Translation
            from multilingual.admin import ModelAdmin, MultilingualInlineAdmin
            from multilingual.manager import Manager
            MultilingualModelAdmin = ModelAdmin
        except ImportError:
            pass
        for key, value in locals().items():
            if key == 'self':
                continue
            setattr(self, key, value)
    
    def __getattribute__(self, attr):
        obj = super(BackwardsCompatibility, self).__getattribute__(attr)
        if not attr.startswith('__'):
            warnings.warn("multilingual.%s is deprecated, use %s instead" % (attr, get_full(obj)), DeprecationWarning)
        return obj

b = BackwardsCompatibility()

for key, value in b.__dict__.items():
    globals()[key] = value