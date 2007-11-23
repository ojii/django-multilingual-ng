from multilingual.languages import get_language_code_list, get_default_language_code

def multilingual(request):
    """
    Returns context variables containing information about available languages.
    """
    return {'LANGUAGE_CODES': get_language_code_list(),
            'DEFAULT_LANGUAGE_CODE': get_default_language_code()}
