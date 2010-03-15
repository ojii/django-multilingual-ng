from multilingual.languages import get_default_language

def is_multilingual_model(model):
    """
    Return True if `model` is a multilingual model.
    """
    return hasattr(model._meta, 'translation_model')

class GlobalLanguageLock(object):
    """
    The Global Language Lock can be used to force django-multilingual-ng to use
    a specific language and not try to fall back.
    """
    def __init__(self):
        self.language_code = None
    
    def lock(self, language_code):
        self.language_code = language_code
        
    def release(self):
        self.language_code = None
        
    @property
    def is_active(self):
        return self.language_code is not None
        
GLL = GlobalLanguageLock()