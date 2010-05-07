from multilingual.languages import get_default_language
try:
    from django.utils.decorators import auto_adapt_to_methods as method_decorator
except ImportError:
    from django.utils.decorators import method_decorator
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()
_thread_locals.gll_language_code = None

def is_multilingual_model(model):
    """
    Return True if `model` is a multilingual model.
    """
    return hasattr(model._meta, 'translation_model')


def _get_language_code():
    return getattr(_thread_locals, 'gll_language_code', None)

def _set_language_code(lang):
    setattr(_thread_locals, 'gll_language_code', lang)


class GLLError(Exception): pass


class GlobalLanguageLock(object):
    """
    The Global Language Lock can be used to force django-multilingual-ng to use
    a specific language and not try to fall back.
    """
    def lock(self, language_code):
        _set_language_code(language_code)
        
    def release(self):
        _set_language_code(None)
        
    @property
    def language_code(self):
        lang_code = _get_language_code()
        if lang_code is not None:
            return lang_code
        raise GLLError("The Global Language Lock is not active")
        
    @property
    def is_active(self):
        return _get_language_code() is not None
        
GLL = GlobalLanguageLock()


def gll_unlock_decorator(func):
    def _decorated(*args, **kwargs):
        if not GLL.is_active:
            return func(*args, **kwargs)
        language_code = GLL.language_code
        GLL.release()
        result = func(*args, **kwargs)
        GLL.lock(language_code)
        return result
    _decorated.__name__ = func.__name__
    _decorated.__doc__ = func.__doc__
    return _decorated
gll_unlock = method_decorator(gll_unlock_decorator)