def is_multilingual_model(model):
    """
    Return True if `model` is a multilingual model.
    """
    return hasattr(model._meta, 'translation_model')

class GlobalLanguageLock(object):
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