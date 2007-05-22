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
from exceptions import TranslationDoesNotExist
from fields import TranslationForeignKey
from manipulators import add_multilingual_manipulators
import manager

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
    if not hasattr(instance, '_translation_cache'):
        return
    for l_id, translation in instance._translation_cache.iteritems():
        # set the translation ID just in case the translation was
        # created while instance was not stored in the DB yet
        translation.master_id = instance.id
        translation.save()

def translation_overwrite_previous(instance, **kwargs):
    """
    Delete previously existing translation with the same master and
    language_id values.  To be called by translation model's pre_save
    signal.

    This most probably means I am abusing something here trying to use
    Django inline editor.  Oh well, it will have to go anyway when we
    move to newforms.
    """
    qs = instance.__class__.objects
    qs = qs.filter(master=instance.master).filter(language_id=instance.language_id)
    qs.delete()

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
        field_alias = get_translated_field_alias('id', language_id)
        if getattr(instance, field_alias, None) is not None:
            field_names = [f.attname for f in instance._meta.translation_model._meta.fields]

            # if so, create a translation object and put it in the cache
            field_data = {}
            for fname in field_names:
                field_data[fname] = getattr(instance,
                                            get_translated_field_alias(fname, language_id))

            translation = instance._meta.translation_model(**field_data)
            instance._translation_cache[language_id] = translation

    # In some situations an (existing in the DB) object is loaded
    # without using the normal QuerySet.  In such case fallback to
    # loading the translations using a separate query.

    # Unfortunately, this is indistinguishable from the situation when
    # an object does not have any translations.  Oh well, we'll have
    # to live with this for the time being.
    if len(instance._translation_cache.keys()) == 0:
        for translation in instance.translations.all():
            instance._translation_cache[translation.language_id] = translation

class TranslatedFieldProxy(property):
    def __init__(self, field_name, alias, field, language_id=None):
        self.field_name = field_name
        self.field = field
        self.admin_order_field = alias
        self.language_id = language_id

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        return getattr(obj, 'get_' + self.field_name)(self.language_id)

    def __set__(self, obj, value):
        language_id = self.language_id

        return getattr(obj, 'set_' + self.field_name)(value, self.language_id)

    short_description = property(lambda self: self.field.short_description)

def getter_generator(field_name, short_description):
    """
    Generate get_'field name' method for field field_name.
    """
    def get_translation_field(self, language_id_or_code=None):
        try:
            return getattr(self.get_translation(language_id_or_code), field_name)
        except TranslationDoesNotExist:
            return None
    get_translation_field.short_description = short_description
    return get_translation_field

def setter_generator(field_name):
    """
    Generate set_'field name' method for field field_name.
    """
    def set_translation_field(self, value, language_id_or_code=None):
        setattr(self.get_translation(language_id_or_code, True),
                field_name, value)
    set_translation_field.short_description = "set " + field_name
    return set_translation_field

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

    language_id = get_language_id_from_id_or_code(language_id_or_code, False)
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

class Translation:
    """
    A superclass for translatablemodel.Translation inner classes.
    """

    def contribute_to_class(cls, main_cls, name):
        """
        Handle the inner 'Translation' class.
        """

        # delay the creation of the *Translation until the master model is
        # fully created
        connect(cls.finish_multilingual_class, signal=signals.class_prepared,
                sender=main_cls, weak=False)
    
        # connect the post_save signal on master class to a handler
        # that saves translations
        connect(translation_save_translated_fields, signal=signals.post_save,
                sender=main_cls)

    contribute_to_class = classmethod(contribute_to_class)

    def create_translation_attrs(cls, main_cls):
        """
        Creates get_'field name'(language_id) and set_'field
        name'(language_id) methods for all the translation fields.
        Adds the 'field name' properties too.

        Returns the translated_fields hash used in field lookups, see
        multilingual.query.  It maps field names to (field,
        language_id) tuples.
        """
        translated_fields = {}
    
        for fname, field in cls.__dict__.items():
            if isinstance(field, models.fields.Field):
                translated_fields[fname] = (field, None)
    
                # add get_'fname' and set_'fname' methods to main_cls
                getter = getter_generator(fname, getattr(field, 'verbose_name', fname))
                setattr(main_cls, 'get_' + fname, getter)
    
                setter = setter_generator(fname)
                setattr(main_cls, 'set_' + fname, setter)
    
                # add the 'fname' proxy property that allows reads
                # from and writing to the appropriate translation
                setattr(main_cls, fname,
                        TranslatedFieldProxy(fname, fname, field))
    
                # create the 'fname'_'language_code' proxy properties
                for language_id in get_language_id_list():
                    language_code = get_language_code(language_id)
                    fname_lng = fname + '_' + language_code
                    translated_fields[fname_lng] = (field, language_id)
                    setattr(main_cls, fname_lng,
                            TranslatedFieldProxy(fname, fname_lng, field,
                                                 language_id))
        return translated_fields
    create_translation_attrs = classmethod(create_translation_attrs)

    def finish_multilingual_class(cls, *args, **kwargs):
        """
        Create a model with translations of a multilingual class.
        """

        main_cls = kwargs['sender']
        translation_model_name = main_cls.__name__ + "Translation"

        # create the model with all the translatable fields
        class TransMeta:
            ordering = ('language_id',)
            unique_together = (('master', 'language_id'),)
            db_table = main_cls._meta.db_table + 'translation'
            app_label = main_cls._meta.app_label
    
        trans_attrs = cls.__dict__.copy()
        trans_attrs['Meta'] = TransMeta
        trans_attrs['language_id'] = models.IntegerField(blank=False, null=False, core=True,
                                                         choices=get_language_choices(),
                                                         db_index=True)
        trans_attrs['master'] = TranslationForeignKey(main_cls, blank=False, null=False,
                                                      edit_inline=TransBoundRelatedObject,
                                                      related_name='translations',
                                                      num_in_admin=get_language_count(),
                                                      min_num_in_admin=get_language_count(),
                                                      num_extra_on_change=0)
        trans_attrs['__str__'] = lambda self: ("%s object, language_code=%s"
                                               % (translation_model_name,
                                                  get_language_code(self.language_id)))
    
        trans_model = ModelBase(translation_model_name, (models.Model,), trans_attrs)
        trans_model._meta.translated_fields = cls.create_translation_attrs(main_cls)
    
        main_cls._meta.translation_model = trans_model
        main_cls.get_translation = get_translation
        main_cls.fill_translation_cache = fill_translation_cache

        # Note: don't fill the translation cache in post_init, as all
        # the extra values selected by QAddTranslationData will be
        # assigned AFTER init()
#        connect(fill_translation_cache, signal=signals.post_init,
#                sender=main_cls)

        # connect the pre_save signal on translation class to a
        # function removing previous translation entries.
        connect(translation_overwrite_previous, signal=signals.pre_save,
                sender=trans_model, weak=False)

    finish_multilingual_class = classmethod(finish_multilingual_class)

def install_translation_library():
    # modify ModelBase.__new__ so that it understands how to handle the
    # 'Translation' inner class

    if getattr(ModelBase, '_multilingual_installed', False):
        # don't install it twice
        return

    _old_new = ModelBase.__new__

    def multilingual_modelbase_new(cls, name, bases, attrs):
        if 'Translation' in attrs:
            if not issubclass(attrs['Translation'], Translation):
                raise ValueError, ("%s.Translation must be a subclass "
                                   + " of multilingual.Translation.") % (name,)
            
            # Make sure that if the class specifies objects then it is
            # a subclass of our Manager.
            #
            # Don't check other managers since someone might want to
            # have a non-multilingual manager, but assigning a
            # non-multilingual manager to objects would be a common
            # mistake.
            if ('objects' in attrs) and (not isinstance(attrs['objects'], manager.Manager)):
                raise ValueError, ("Model %s specifies translations, " +
                                   "so its 'objects' manager must be " +
                                   "a subclass of multilingual.Manager.") % (name,)

            # Change the default manager to multilingual.Manager.
            if not 'objects' in attrs:
                attrs['objects'] = manager.Manager()
    
            # Override the admin manager as well, or the admin views will
            # not see the translation data.
            if 'Admin' in attrs:
                attrs['Admin'].manager = attrs['objects']

            # Install a hack to let add_multilingual_manipulators know
            # this is a translatable model
            attrs['is_translation_model'] = lambda self: True
            
        return _old_new(cls, name, bases, attrs)

    ModelBase.__new__ = staticmethod(multilingual_modelbase_new)
    ModelBase._multilingual_installed = True

# install the library
install_translation_library()
