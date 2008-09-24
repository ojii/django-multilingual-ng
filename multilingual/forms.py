"""TODO: this will probably be removed because DM seems to work correctly without 
manipulators.
"""
from django.forms.models import ModelForm
from django.forms.models import ErrorList

from multilingual.languages import get_language_id_list

def multilingual_init(self, data=None, files=None, auto_id='id_%s', prefix=None,
    initial=None, error_class=ErrorList, label_suffix=':',
    empty_permitted=False, instance=None):
    if data and hasattr(self._meta.model, 'translation_model'):
        trans_model = self._meta.model._meta.translation_model
        lower_model_name = trans_model._meta.object_name.lower()
        language_id_list = get_language_id_list()
        for language_idx in range(0, len(language_id_list)):
            name = "%s.%s.language_id" % (lower_model_name,
                                          language_idx)
            data[name] = language_id_list[language_idx]
    super(ModelForm, self).__init__(data, files, auto_id, prefix, initial,
        error_class, label_suffix, empty_permitted, instance)

#NOTE: leave commented
#ModelForm.__init__ = multilingual_init
