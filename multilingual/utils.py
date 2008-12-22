def is_multilingual_model(model):
    """
    Return True if `model` is a multilingual model.
    """
    return hasattr(model._meta, 'translation_model')
