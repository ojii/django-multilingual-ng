"""
Support for models' internal Translation class.
"""

##TODO: this is messy and needs to be cleaned up

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import signals
from django.db.models.base import ModelBase
from multilingual.languages import *
from multilingual.exceptions import TranslationDoesNotExist
from multilingual.fields import TranslationForeignKey
from multilingual import manager
from multilingual.admin import install_multilingual_modeladmin_new

# TODO: remove this import.  It is here only because earlier versions
# of the library required importing TranslationModelAdmin from here
# instead of taking it directly from multilingual
from multilingual.admin import TranslationModelAdmin

from new import instancemethod

def translation_save_translated_fields(instance, **kwargs):
    """
    Save all the translations of instance in post_save signal handler.
    """
    if not hasattr(instance, '_translation_cache'):
        return
    for l_id, translation in instance._translation_cache.iteritems():
        # set the translation ID just in case the translation was
        # created while instance was not stored in the DB yet

        # note: we're using _get_pk_val here even though it is
        # private, since that's the most reliable way to get the value
        # on older Django (pk property did not exist yet)
        translation.master_id = instance._get_pk_val()
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
    def __init__(self, field_name, alias, field, language_id=None,
                 fallback=False):
        self.field_name = field_name
        self.field = field
        self.admin_order_field = alias
        self.language_id = language_id
        self.fallback = fallback

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        return getattr(obj, 'get_' + self.field_name)(self.language_id,
                                                      self.fallback)

    def __set__(self, obj, value):
        language_id = self.language_id

        return getattr(obj, 'set_' + self.field_name)(value, self.language_id)

    short_description = property(lambda self: self.field.short_description)

def getter_generator(field_name, short_description):
    """
    Generate get_'field name' method for field field_name.
    """
    def get_translation_field(self, language_id_or_code=None, fallback=False):
        try:
            return getattr(self.get_translation(language_id_or_code,
                                                fallback=fallback),
                           field_name)
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
                    create_if_necessary=False,
                    fallback=False):
    """
    Get a translation instance for the given `language_id_or_code`.

    If the translation does not exist:

    1. if `create_if_necessary` is True, this function will create one
    2. otherwise, if `fallback` is True, this function will search the
       list of languages looking for the first existing translation
    3. if all of the above fails to find a translation, raise the
    TranslationDoesNotExist exception
    """

    # fill the cache if necessary
    self.fill_translation_cache()

    language_id = get_language_id_from_id_or_code(language_id_or_code, False)
    if language_id is None:
        language_id = getattr(self, '_default_language', None)
    if language_id is None:
        language_id = get_default_language()

    if language_id in self._translation_cache:
        return self._translation_cache.get(language_id, None)

    if create_if_necessary:
        # case 1
        new_translation = self._meta.translation_model(master=self,
                                                       language_id=language_id)
        self._translation_cache[language_id] = new_translation
        return new_translation
    elif fallback:
        # case 2
        for fb_lang_id in FALLBACK_LANGUAGE_IDS:
            trans = self._translation_cache.get(fb_lang_id, None)
            if trans:
                return trans
        raise TranslationDoesNotExist(language_id)
    else:
        # case 3
        raise TranslationDoesNotExist(language_id)

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
        signals.class_prepared.connect(cls.finish_multilingual_class,
                sender=main_cls, weak=False)

        # connect the post_save signal on master class to a handler
        # that saves translations
        signals.post_save.connect(translation_save_translated_fields,
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

                # add the 'fname'_any fallback
                setattr(main_cls, fname + FALLBACK_FIELD_SUFFIX,
                        TranslatedFieldProxy(fname, fname, field, fallback=True))

                # create the 'fname'_'language_code' proxy properties
                for language_id in get_language_id_list():
                    language_code = get_language_code(language_id)
                    fname_lng = fname + '_' + language_code.replace('-', '_')
                    translated_fields[fname_lng] = (field, language_id)
                    setattr(main_cls, fname_lng,
                            TranslatedFieldProxy(fname, fname_lng, field,
                                                 language_id))
                    # add the 'fname'_'language_code'_any fallback proxy
                    setattr(main_cls, fname_lng + FALLBACK_FIELD_SUFFIX,
                            TranslatedFieldProxy(fname, fname_lng, field,
                                                 language_id, fallback=True))

        return translated_fields
    create_translation_attrs = classmethod(create_translation_attrs)

    def get_unique_fields(cls):
        """
        Return a list of fields with "unique" attribute, which needs to
        be augmented by the language.
        """
        unique_fields = []

        for fname, field in cls.__dict__.items():
            if isinstance(field, models.fields.Field):
                if getattr(field,'unique',False):
                    try:
                        field.unique = False
                    except AttributeError:
                        # newer Django defines unique as a property
                        # that uses _unique to store data.  We're
                        # jumping over the fence by setting _unique,
                        # so this sucks, but this happens early enough
                        # to be safe.
                        field._unique = False
                    unique_fields.append(fname)
        return unique_fields
    get_unique_fields = classmethod(get_unique_fields)

    def finish_multilingual_class(cls, *args, **kwargs):
        """
        Create a model with translations of a multilingual class.
        """

        main_cls = kwargs['sender']
        translation_model_name = main_cls.__name__ + "Translation"

        # create the model with all the translatable fields
        unique = [('language_id', 'master')]
        for f in cls.get_unique_fields():
            unique.append(('language_id',f))

        class TransMeta:
            pass

        try:
            meta = cls.Meta
        except AttributeError:
            meta = TransMeta

        meta.ordering = ('language_id',)
        meta.unique_together = tuple(unique)
        meta.app_label = main_cls._meta.app_label
        if not hasattr(meta, 'db_table'):
            meta.db_table = main_cls._meta.db_table + '_translation'

        trans_attrs = cls.__dict__.copy()
        trans_attrs['Meta'] = meta
        trans_attrs['language_id'] = models.IntegerField(blank=False, null=False,
                                                         choices=get_language_choices(),
                                                         db_index=True)

        edit_inline = True

        trans_attrs['master'] = TranslationForeignKey(main_cls, blank=False, null=False,
                                                      related_name='translations',)
        trans_attrs['__str__'] = lambda self: ("%s object, language_code=%s"
                                               % (translation_model_name,
                                                  get_language_code(self.language_id)))

        trans_model = ModelBase(translation_model_name, (models.Model,), trans_attrs)
        trans_model._meta.translated_fields = cls.create_translation_attrs(main_cls)

        _old_init_name_map = main_cls._meta.__class__.init_name_map
        def init_name_map(self):
            cache = _old_init_name_map(self)
            for name, field_and_lang_id in trans_model._meta.translated_fields.items():
                #import sys; sys.stderr.write('TM %r\n' % trans_model)
                cache[name] = (field_and_lang_id[0], trans_model, True, False)
            return cache
        main_cls._meta.init_name_map = instancemethod(init_name_map,
                                                      main_cls._meta,
                                                      main_cls._meta.__class__)

        main_cls._meta.translation_model = trans_model
        main_cls.Translation = trans_model
        main_cls.get_translation = get_translation
        main_cls.fill_translation_cache = fill_translation_cache

        # Note: don't fill the translation cache in post_init, as all
        # the extra values selected by QAddTranslationData will be
        # assigned AFTER init()
#        signals.post_init.connect(fill_translation_cache,
#                sender=main_cls)

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

        return _old_new(cls, name, bases, attrs)
    ModelBase.__new__ = staticmethod(multilingual_modelbase_new)
    ModelBase._multilingual_installed = True

    install_multilingual_modeladmin_new()

# install the library
install_translation_library()
