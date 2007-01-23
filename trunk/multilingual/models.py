"""
Multilingual model support.
"""

from django.db import models
from django.db.models.base import ModelBase
from django.dispatch.dispatcher import connect
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import signals

# This is ugly, ideally languages should be taken from the DB or
# settings file.  Oh well, it is a prototype anyway.

# It is important that the language identifiers are consecutive
# numbers starting with 1.
LANGUAGES = [['en', 'English'], # id=1
             ['pl', 'Polish']]  # id=2

LANGUAGE_CNT = len(LANGUAGES)

from django.contrib.admin.templatetags.admin_modify import StackedBoundRelatedObject

class TransBoundRelatedObject(StackedBoundRelatedObject):
    """
    This class changes the template for translation objects.
    """
    def template_name(self):
        return "admin/edit_inline_translations.html"

def get_default_language():
    # you might take the ID from elsewhere, ie
    # cookies or threadlocals
    return 1

def translation_contribute_to_class(cls, main_cls, name):
    """
    Handle the inner 'Translation' class.
    """

    def getter_generator(trans_name, field_name):
        """
        Generate get_'field name' method for model trans_name,
        field field_name.
        """
        def get_translation_field(self, language_id=None):
            if language_id == None:
                language_id = get_default_language()
            try:
                return getattr(self.get_translation(language_id), field_name)
            except ObjectDoesNotExist:
                return "None"
        get_translation_field.short_description = "get " + field_name
        return get_translation_field
    
    def setter_generator(trans_name, field_name):
        """
        Generate set_'field name' method for model trans_name,
        field field_name.
        """
        def set_translation_field(self, value, language_id=None):
            if language_id == None:
                language_id = get_default_language()
            try:
                translation = self.get_translation(language_id)
                setattr(translation, field_name, value)
                translation.save()
            except ObjectDoesNotExist:
                return "None"
        set_translation_field.short_description = "set " + field_name
        return set_translation_field
    
    def finish_multilingual_class(*args, **kwargs):
        """
        Create a model with translations of a multilingual class.
        """
        class TransMeta:
            ordering = ('language',)

        trans_name = main_cls.__name__ + name

        # create get_'field name'(language) and set_'field
        # name'(language) methods for all the translation fields.
        # Add the 'field name' properties while you're at it, too.
        for fname, field in cls.__dict__.items():
            if isinstance(field, models.fields.Field):
                getter = getter_generator(trans_name, fname)
                setattr(main_cls, 'get_' + fname, getter)

                setter = setter_generator(trans_name, fname)
                setattr(main_cls, 'set_' + fname, setter)

                setattr(main_cls, fname, property(getter, setter, doc=fname))

        trans_attrs = cls.__dict__.copy()
        trans_attrs['Meta'] = TransMeta
        trans_attrs['language'] = models.IntegerField(blank=False, null=False, core=True)
        trans_attrs['master'] = models.ForeignKey(main_cls, blank=False, null=False,
                                                  edit_inline=TransBoundRelatedObject,
                                                  num_in_admin=LANGUAGE_CNT,
                                                  min_num_in_admin=LANGUAGE_CNT,
                                                  num_extra_on_change=0)

        trans_model = ModelBase(trans_name, (models.Model,), trans_attrs)

        def get_translation(self, language_id):
            return getattr(self, trans_name.lower() + '_set').get(language=language_id)
            
        main_cls.get_translation = get_translation

    # delay the creation of the *Translation until the master model is
    # fully created
    connect(finish_multilingual_class, signal=signals.class_prepared,
            sender=main_cls, weak=False)

# modify ModelBase.__new__ so that it understands how to handle the
# 'Translation' inner class
_old_new = ModelBase.__new__
def multilingual_modelbase_new(cls, name, bases, attrs):
    if 'Translation' in attrs:
        attrs['Translation'].contribute_to_class = classmethod(translation_contribute_to_class)
    return _old_new(cls, name, bases, attrs)
setattr(ModelBase, '__new__', staticmethod(multilingual_modelbase_new))
