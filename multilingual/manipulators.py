"""
Automatic add and change manipulators for translatable models.
"""

import django.db.models.manipulators as django_manipulators
from languages import get_language_id_list

class MultilingualManipulatorMixin:
    def multilingual_pre_save(self, new_data):
        """
        Update data before save to include necessary fields for
        translations.

        This means adding language_id field for every translation.
        """

        # TO do: add proper .id fields in the latter loop instead of
        # deleting translations
        original = getattr(self, 'original_object', None)
        if original:
            original.translations.all().delete()

        trans_model = self.model._meta.translation_model
        lower_model_name = trans_model._meta.object_name.lower()
        language_id_list = get_language_id_list()
        for language_idx in range(0, len(language_id_list)):
            name = "%s.%s.language_id" % (lower_model_name,
                                          language_idx)
            new_data[name] = language_id_list[language_idx]

class MultilingualAddManipulator(django_manipulators.AutomaticAddManipulator,
                                 MultilingualManipulatorMixin):
    def save(self, new_data):
        self.multilingual_pre_save(new_data)
        return super(MultilingualAddManipulator, self).save(new_data)

class MultilingualChangeManipulator(django_manipulators.AutomaticChangeManipulator,
                                    MultilingualManipulatorMixin):
    def save(self, new_data):
        self.multilingual_pre_save(new_data)
        return super(MultilingualChangeManipulator, self).save(new_data)

def add_multilingual_manipulators(sender):
    """
    A replacement for django.db.models.manipulators that installs
    multilingual manipulators for translatable models.

    It is supposed to be called from
    Translation.finish_multilingual_class.
    """
    cls = sender
    if hasattr(cls, 'is_translation_model'):
        cls.add_to_class('AddManipulator', MultilingualAddManipulator)
        cls.add_to_class('ChangeManipulator', MultilingualChangeManipulator)
    else:
        django_manipulators.add_manipulators(sender)

from django.dispatch import dispatcher
from django.db.models import signals

dispatcher.disconnect(django_manipulators.add_manipulators, signal=signals.class_prepared)
dispatcher.connect(add_multilingual_manipulators, signal=signals.class_prepared)
