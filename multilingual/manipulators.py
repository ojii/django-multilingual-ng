"""
Automatic add and change manipulators for translatable models.
"""

import django.db.models.manipulators as django_manipulators
from languages import get_language_id_list

class MultilingualManipulatorMixin:
    def fix_translation_data(self, new_data):
        """
        Update data before save to include necessary fields for
        translations.

        This means adding language_id field for every translation.
        """
        trans_model = self.model._meta.translation_model
        lower_model_name = trans_model._meta.object_name.lower()
        language_id_list = get_language_id_list()
        for language_idx in range(0, len(language_id_list)):
            name = "%s.%s.language_id" % (lower_model_name,
                                          language_idx)
            new_data[name] = language_id_list[language_idx]

class MultilingualAddManipulator(django_manipulators.AutomaticAddManipulator,
                                 MultilingualManipulatorMixin):

    def do_html2python(self, new_data):
        self.fix_translation_data(new_data)
        super(MultilingualAddManipulator, self).do_html2python(new_data)

class MultilingualChangeManipulator(django_manipulators.AutomaticChangeManipulator,
                                    MultilingualManipulatorMixin):

    def do_html2python(self, new_data):
        self.fix_translation_data(new_data)
        super(MultilingualChangeManipulator, self).do_html2python(new_data)

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
