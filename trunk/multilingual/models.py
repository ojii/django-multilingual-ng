"""
Multilingual model support.
"""

from django.db import models
from django.db.models.base import ModelBase
from django.dispatch.dispatcher import connect
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import signals
from django.db.models.query import QuerySet

# This is ugly, ideally languages should be taken from the DB or
# settings file.  Oh well, it is a prototype anyway.

# It is important that the language identifiers are consecutive
# numbers starting with 1.
LANGUAGES = [['en', 'English'], # id=1
             ['pl', 'Polish']]  # id=2

LANGUAGE_CNT = len(LANGUAGES)

DEFAULT_LANGUAGE = 1

class TranslationDoesNotExist(Exception):
    "The requested translation does not exist"
    pass

def get_language_code(language_id):
    return LANGUAGES[language_id - 1][0]

def get_language_name(language_id):
    return LANGUAGES[language_id - 1][1]

def get_language_id_list():
    return range(1, LANGUAGE_CNT + 1)

from django.contrib.admin.templatetags.admin_modify import StackedBoundRelatedObject

class TransBoundRelatedObject(StackedBoundRelatedObject):
    """
    This class changes the template for translation objects.
    """
    def template_name(self):
        return "admin/edit_inline_translations.html"

from django.utils.datastructures import SortedDict

class QAddTranslationData(object):
    """
    Extend a queryset with joins and contitions necessary to pull all
    the ML data.
    """
    def __init__(self, inner_queryset = None):
        self.inner_queryset = inner_queryset

    def get_sql(self, opts):
        joins, where, params = SortedDict(), [], []
        if self.inner_queryset:
            joins2, where2, params2 = self.inner_queryset.get_sql(opts)
            joins.update(joins2)
            where.extend(where2)
            params.extend(params2)

        # create all the LEFT JOINS needed to read all the
        # translations in one row
        master_table_name = opts.db_table
        trans_table_name = opts.translation_model._meta.db_table
        for language_id in get_language_id_list():
            table_alias = get_translation_table_alias(trans_table_name,
                                                      language_id)
            condition = ('((%s.master_id = %s.id) AND (%s.language_id = %%s))'
                         % (table_alias, master_table_name, table_alias))
            joins[table_alias] = (trans_table_name, 'LEFT JOIN', condition)
            params.append(language_id)
        return joins, where, params

class MultilingualModelManager(models.Manager):
    """
    A manager for multilingual models.

    TO DO: turn this into a proxy manager that would allow developers
    to use any manager they need.  It should be sufficient to extend
    and additionaly filter or order querysets returned by that manager.
    """

    def get_query_set(self):
        translation_model = self.model._meta.translation_model
        select = {}
        for language_id in get_language_id_list():
            for fname in [f.attname for f in translation_model._meta.fields]:
                trans_table_name = translation_model._meta.db_table
                table_alias = get_translation_table_alias(trans_table_name, language_id)
                field_alias = get_translated_field_alias(fname, language_id)

                select[field_alias] = table_alias + '.' + fname

        return QuerySet(self.model).filter(QAddTranslationData()).extra(select=select)

def set_default_language(language_id):
    """
    Set the default language for the whole translation mechanism.

    To do: find a better place to store the value.
    """
    import multilingual.models
    multilingual.models.DEFAULT_LANGUAGE = language_id

def get_default_language():
    # you might take the ID from elsewhere, ie
    # cookies or threadlocals
    return DEFAULT_LANGUAGE

def get_translation_table_alias(translation_table_name, language_id):
    return translation_table_name + '_' + get_language_code(language_id)

def get_translated_field_alias(field_name, language_id):
    return field_name + '_' + get_language_code(language_id)



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
            except TranslationDoesNotExist:
                return "-translation-not-available-"
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
            setattr(self.get_translation(language_id, True),
                    field_name, value)
        set_translation_field.short_description = "set " + field_name
        return set_translation_field

    def finish_multilingual_class(*args, **kwargs):
        """
        Create a model with translations of a multilingual class.
        """
        class TransMeta:
            ordering = ('language_id',)

        trans_name = main_cls.__name__ + name
        translated_fields = []

        # create get_'field name'(language_id) and set_'field
        # name'(language_id) methods for all the translation fields.
        # Add the 'field name' properties while you're at it, too.
        for fname, field in cls.__dict__.items():
            if isinstance(field, models.fields.Field):
                translated_fields.append(fname)
                
                getter = getter_generator(trans_name, fname)
                setattr(main_cls, 'get_' + fname, getter)

                setter = setter_generator(trans_name, fname)
                setattr(main_cls, 'set_' + fname, setter)

                setattr(main_cls, fname, property(getter, setter, doc=fname))

        trans_attrs = cls.__dict__.copy()
        trans_attrs['Meta'] = TransMeta
        trans_attrs['language_id'] = models.IntegerField(blank=False, null=False, core=True)
        trans_attrs['master'] = models.ForeignKey(main_cls, blank=False, null=False,
                                                  edit_inline=TransBoundRelatedObject,
                                                  num_in_admin=LANGUAGE_CNT,
                                                  min_num_in_admin=LANGUAGE_CNT,
                                                  num_extra_on_change=0)

        def translation_str(self):
            return ("%s object, master_id=%s, language_id=%s"
                    % (trans_name, self.master_id, self.language_id))
        trans_attrs['__str__'] = translation_str

        trans_model = ModelBase(trans_name, (models.Model,), trans_attrs)
        trans_model._meta.translated_fields = translated_fields

        def get_translation_set(self):
            return getattr(self, trans_name.lower() + '_set')

        def get_translation(self, language_id,
                            create_if_necessary=False):
            # fill the cache if necessary
            self.fill_translation_cache()

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
        
        attrs['Translation'].contribute_to_class = classmethod(translation_contribute_to_class)
    return _old_new(cls, name, bases, attrs)
setattr(ModelBase, '__new__', staticmethod(multilingual_modelbase_new))

