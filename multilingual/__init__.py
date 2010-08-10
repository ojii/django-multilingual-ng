"""
Django-multilingual-ng: multilingual model support for Django 1.2.

Note about version numbers:
    - uneven minor versions are considered unstable releases
    - even minor versions are considered stable releases
"""
#VERSION = ('0', '1', '44')
#__version__ = '.'.join(VERSION)

import warnings

class LazyInit(object):
    VERSION = ('0', '1', '45')
    __version__ = '.'.join(VERSION)
    
    __deprecated__ = {
        'models': ('multilingual.models', None),
        'TranslationDoesNotExist': ('multilingual.exceptions', 'TranslationDoesNotExist'),
        'LanguageDoesNotExist': ('multilingual.exceptions', 'LanguageDoesNotExist'),
        'set_default_language': ('multilingual.languages', 'set_default_language'),
        'get_default_language': ('multilingual.languages', 'get_default_language'),
        'get_language_code_list': ('multilingual.languages', 'get_language_code_list'),
        'FALLBACK_LANGUAGES': ('multilingual.settings', 'FALLBACK_LANGUAGES'),
        'Translation': ('multilingual.translation', 'TranslationModel'),
        'MultilingualModelAdmin': ('multilingual.admin', 'MultilingualModelAdmin'),
        'MultilingualInlineAdmin': ('multilingual.admin', 'MultilingualInlineAdmin'),
        'ModelAdmin': ('multilingual.admin', 'MultilingualModelAdmin'),
        'Manager': ('multilingual.manager', 'MultilingualManager'),
    }
    
    __newnames__ = {
        'Translation': 'TranslationModel',
        'ModelAdmin': 'MultilingualModelAdmin',
        'Manager': 'MultilingualManager',
    }
    
    __modules_cache__ = {}
    __objects_cache__ = {}
    
    def __init__(self, real):
        self.__real__ = real
    
    def __getattr__(self, attr):
        if not attr in self.__deprecated__:
            return getattr(self.__real__, attr)
        if attr in self.__objects_cache__:
            return self.__objects_cache__[attr]
        return self._load(attr)
    
    def _import(self, modname):
        if not hasattr(self, '_importlib'):
            mod = __import__('django.utils.importlib', fromlist=['django', 'utils'])
            self._importlib = mod
        return self._importlib.import_module(modname)

    def _load(self, attr):
        modname, objname = self.__deprecated__[attr]
        if not modname in self.__modules_cache__:
            self.__modules_cache__[modname] = self._import(modname)
        obj = self.__modules_cache__[modname]
        if objname is not None:
            obj = getattr(obj, objname)
        if attr in self.__newnames__:
            self._warn_newname(attr)
        self._warn_deprecated(attr, modname, objname)
        self.__objects_cache__[attr] = obj
        return obj
    
    def _warn_newname(self, attr):
        new = self.__newnames__[attr]
        warnings.warn("The name '%s' is deprecated in favor of '%s'" % (attr, new), DeprecationWarning)
        
    def _warn_deprecated(self, attr, modname, objname):
        if objname:
            msg = "'multilingual.%s' is deprecated in favor of '%s.%s'" % (attr, modname, objname)
        else:
            msg = "'multilingual.%s' is deprecated in favor of '%s'" % (attr, modname)
        warnings.warn(msg, DeprecationWarning)

import sys
sys.modules[__name__] = LazyInit(sys.modules[__name__])
#
#try:
#    """
#    WARNING: All these names imported here WILL BE DEPRECATED!
#    """
#    from multilingual import models
#    from multilingual.exceptions import TranslationDoesNotExist, LanguageDoesNotExist
#    from multilingual.languages import (set_default_language, get_default_language,
#                                        get_language_code_list)
#    from multilingual.settings import FALLBACK_LANGUAGES
#    from multilingual.translation import Translation
#    from multilingual.admin import MultilingualModelAdmin, MultilingualInlineAdmin
#    from multilingual.manager import Manager
#    ModelAdmin = MultilingualModelAdmin
#except ImportError:
#    pass
