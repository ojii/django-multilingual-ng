"""
Support for models' internal Translation class.
"""

## TO DO: this is messy and needs to be cleaned up

from django.db import models
from django.db.models.base import ModelBase
from django.dispatch.dispatcher import connect
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import signals
from languages import *
from manager import MultilingualModelManager
from exceptions import TranslationDoesNotExist

from django.contrib.admin.templatetags.admin_modify import StackedBoundRelatedObject

class TransBoundRelatedObject(StackedBoundRelatedObject):
    """
    This class changes the template for translation objects.
    """
    def template_name(self):
        return "admin/edit_inline_translations.html"

def translation_save_translated_fields(instance, **kwargs):
    """
    Save all the translations of instance in post_save signal handler.
    """
    instance.get_translation_set().all().delete()
    for translation in getattr(instance, '_translation_cache', {}).values():
        # set the translation ID just in case the translation was
        # created while instance was not stored in the DB yet
        translation.master_id = instance.id
        translation.save()

def fill_translation_cache(instance):
    """
    Fill the translation cache using information received in the
    instance objects as extra fields.

    You can not do this in post_init because the extra fields are
    assigned by QuerySet.iterator after model initialization.
    """

    if hasattr(instance, '_translation_cache'):
        # do not refill the cache
        return

    instance._translation_cache = {}
    for language_id in get_language_id_list():
        # see if translation for language_id was in the query
        if hasattr(instance, get_translated_field_alias('id', language_id)):
            field_names = [f.attname for f in instance._meta.translation_model._meta.fields]

            # if so, create a translation object and put it in the cache
            field_data = {}
            for fname in field_names:
                field_data[fname] = getattr(instance,
                                            get_translated_field_alias(fname, language_id))

            translation = instance._meta.translation_model(**field_data)
            instance._translation_cache[language_id] = translation

class TranslatedFieldProxy(object):
    def __init__(self, field_name, short_description,
                 language_id=None):
        self.field_name = field_name
        self.short_description = short_description
        self.admin_order_field = field_name
        self.language_id = language_id

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        return getattr(obj, 'get_' + self.field_name)(self.language_id)

    def __set__(self, obj, value):
        language_id = self.language_id

        return getattr(obj, 'set_' + self.field_name)(value, self.language_id)

def translation_contribute_to_class(cls, main_cls, name):
    """
    Handle the inner 'Translation' class.
    """

    def getter_generator(trans_name, field_name):
        """
        Generate get_'field name' method for model trans_name,
        field field_name.
        """
        def get_translation_field(self, language_id_or_code=None):
            try:
                return getattr(self.get_translation(language_id_or_code), field_name)
            except TranslationDoesNotExist:
                return "-translation-not-available-"
        get_translation_field.short_description = "get " + field_name
        return get_translation_field
    
    def setter_generator(trans_name, field_name):
        """
        Generate set_'field name' method for model trans_name,
        field field_name.
        """
        def set_translation_field(self, value, language_id_or_code=None):
            setattr(self.get_translation(language_id_or_code, True),
                    field_name, value)
        set_translation_field.short_description = "set " + field_name
        return set_translation_field

    def finish_multilingual_class(*args, **kwargs):
        """
        Create a model with translations of a multilingual class.
        """

        # trans_name is the name of the model with all translatable
        # fields.
        trans_name = main_cls.__name__ + name

        # The translated_fields hash is used in field lookups, see
        # multilingual.query.  It maps field names to (field,
        # language_id) tuples.
        translated_fields = {}

        # create get_'field name'(language_id) and set_'field
        # name'(language_id) methods for all the translation fields.
        # Add the 'field name' properties while you're at it, too.
        for fname, field in cls.__dict__.items():
            if isinstance(field, models.fields.Field):
                short_description = getattr(field, 'verbose_name', fname)
                translated_fields[fname] = (field, None)

                # add get_'fname' and set_'fname' methods to main_cls
                getter = getter_generator(trans_name, fname)
                getter.short_description = short_description
                setattr(main_cls, 'get_' + fname, getter)

                setter = setter_generator(trans_name, fname)
                setattr(main_cls, 'set_' + fname, setter)

                # add the 'fname' proxy property that allows reads
                # from and writing to the appropriate translation
                setattr(main_cls, fname,
                        TranslatedFieldProxy(fname, short_description))

                # create the 'fname'_'language_code' proxy properties
                for language_id in get_language_id_list():
                    language_code = get_language_code(language_id)
                    translated_fields[fname + '_' + language_code] = (field, language_id)
                    setattr(main_cls, fname + '_' + language_code,
                            TranslatedFieldProxy(fname, short_description,
                                          language_id))

        # create the model with all the translatable fields
        class TransMeta:
            ordering = ('language_id',)
            # TO DO: for some reason, unique_together does not work
            # for inline objects.
            unique_together = (('master', 'language_id'),)

        trans_attrs = cls.__dict__.copy()
        trans_attrs['Meta'] = TransMeta
        trans_attrs['language_id'] = models.IntegerField(blank=False, null=False, core=True,
                                                         choices=get_language_choices())
        trans_attrs['master'] = models.ForeignKey(main_cls, blank=False, null=False,
                                                  edit_inline=TransBoundRelatedObject,
                                                  num_in_admin=get_language_count(),
                                                  min_num_in_admin=get_language_count(),
                                                  num_extra_on_change=0)
        trans_attrs['__str__'] = lambda self: ("%s object, language_code=%s"
                                               % (trans_name,
                                                  get_language_code(self.language_id)))

        trans_model = ModelBase(trans_name, (models.Model,), trans_attrs)
        trans_model._meta.translated_fields = translated_fields

        def get_translation_set(self):
            """
            Return the manager for all translations of self.
            """
            return getattr(self, trans_name.lower() + '_set')

        def get_translation(self, language_id_or_code,
                            create_if_necessary=False):
            """
            Get a translation instance for the given language_id_or_code.

            If it does not exist, either create one or raise the
            TranslationDoesNotExist exception, depending on the
            create_if_necessary argument.
            """

            # fill the cache if necessary
            self.fill_translation_cache()

            language_id = get_language_id_from_id_or_code(language_id_or_code)
            if language_id is None:
                language_id = getattr(self, '_default_language', None)
            if language_id is None:
                language_id = get_default_language()

            if language_id not in self._translation_cache:
                if not create_if_necessary:
                    raise TranslationDoesNotExist
                new_translation = self._meta.translation_model(master=self,
                                                               language_id=language_id)
                self._translation_cache[language_id] = new_translation
            return self._translation_cache.get(language_id, None)

        main_cls._meta.translation_model = trans_model
        main_cls.get_translation = get_translation
        main_cls.get_translation_set = get_translation_set
        main_cls.fill_translation_cache = fill_translation_cache

    # delay the creation of the *Translation until the master model is
    # fully created
    connect(finish_multilingual_class, signal=signals.class_prepared,
            sender=main_cls, weak=False)

    # connect the post_save signal to a handler that saves translations
    connect(translation_save_translated_fields, signal=signals.post_save,
            sender=main_cls)

def install_translation_library():
    # modify ModelBase.__new__ so that it understands how to handle the
    # 'Translation' inner class

    _old_new = ModelBase.__new__

    def multilingual_modelbase_new(cls, name, bases, attrs):
        if 'Translation' in attrs:
            # make sure the class does not specify a custom manager.
            if 'objects' in attrs:
                raise ValueError, ("Model %s specifies both 'objects' and "
                                   + "'Translation'.") % (name,)
    
            # Change the default manager to one that knows how to handle
            # translation fields.  Ideally this should not be necessary, so
            # that it would still be possible to use a custom manager here.
            attrs['objects'] = MultilingualModelManager()
    
            # Override the admin manager as well, or the admin views will
            # not see the translation data.
            if 'Admin' in attrs:
                attrs['Admin'].manager = attrs['objects']
            
            attrs['Translation'].contribute_to_class = classmethod(translation_contribute_to_class)
        return _old_new(cls, name, bases, attrs)

    setattr(ModelBase, '__new__', staticmethod(multilingual_modelbase_new))

