from django.db import models
from django.db.models.related import RelatedObject
from languages import get_language_id_list

def get_list(self, parent_instance=None):
    """
    An ugly way to override RelatedObject.get_list for some objects.
    This is the only way to do it right now because a reference to
    RelatedObject class is hardcoded in db.models.options, but ideally
    there should be a way to specify your own RelatedObject subclass.
    """
    the_list = _old_get_list(self, parent_instance)

    # this check is ugly, will be changed
    if not hasattr(self.model._meta, 'translated_fields'):
        return the_list
    
    # 1. find corresponding language for each entry
    
    entries_with_lang = {}
    entries_without_lang = []
    for entry in the_list:
        if entry is None:
            entries_without_lang.append(entry)
        else:
            entries_with_lang[entry.language_id] = entry

    # 2. reorder the entries according to what you found in #1

    new_list = []
    for language_id in get_language_id_list():
        entry = entries_with_lang.get(language_id, None)
        if entry is None:
            entry = entries_without_lang.pop(0)
        new_list.append(entry)
    return new_list

_old_get_list = RelatedObject.get_list
RelatedObject.get_list = get_list
    
class TranslationForeignKey(models.ForeignKey):
    """
    """
    pass
