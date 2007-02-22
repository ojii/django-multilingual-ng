"""
Django-multilingual: a QuerySet subclass for models with translatable
fields.

Also, a wrapper for lookup_inner that makes it possible to lookup via
translatable fields.
"""

from django.db import models, backend
from django.db.models.query import QuerySet, get_where_clause
from django.utils.datastructures import SortedDict
from languages import *

old_lookup_inner = models.query.lookup_inner

def new_lookup_inner(path, lookup_type, value, opts, table, column):
    """
    Patch django.db.models.query.lookup_inner from the outside
    to recognize the translation fields.

    Ideally this should go into lookup_inner.
    """

    # check if there is anything to do for us here.  If not, send it
    # all back to the original lookup_inner.

    if not hasattr(opts, 'translation_model'):
        return old_lookup_inner(path, lookup_type, value, opts, table, column)

    translation_opts = opts.translation_model._meta
    if path[0] not in translation_opts.translated_fields:
        return old_lookup_inner(path, lookup_type, value, opts, table, column)

    # If we got here then path[0] _is_ a translatable field (or a
    # localised version of one) in a model with translations.

    joins, where, params = SortedDict(), [], []

    name = path.pop(0)
    current_table = table
    field, language_id = translation_opts.translated_fields[name]
    if language_id is None:
        language_id = get_default_language()
    translation_table = get_translation_table_alias(translation_opts.db_table,
                                                    language_id)
    new_table = (current_table + "__" + translation_table)

    # add the join necessary for the current step
    qn = backend.quote_name
    condition = ('((%s.master_id = %s.id) AND (%s.language_id = %s))'
                 % (new_table, current_table, new_table, language_id))
    joins[qn(new_table)] = (qn(translation_opts.db_table), 'LEFT JOIN', condition)

    if path:
        joins2, where2, params2 = \
                models.query.lookup_inner(path, lookup_type,
                                          value,
                                          translation_opts,
                                          new_table,
                                          translation_opts.pk.column)
        joins.update(joins2)
        where.extend(where2)
        params.extend(params2)
    else:
        trans_table_name = opts.translation_model._meta.db_table
        where.append(get_where_clause(lookup_type, new_table + '.', field.attname, value))
        params.extend(field.get_db_prep_lookup(lookup_type, value))

    return joins, where, params

models.query.lookup_inner = new_lookup_inner

class QAddTranslationData(object):
    """
    Extend a queryset with joins and contitions necessary to pull all
    the ML data.
    """
    def get_sql(self, opts):
        joins, where, params = SortedDict(), [], []

        # create all the LEFT JOINS needed to read all the
        # translations in one row
        master_table_name = opts.db_table
        trans_table_name = opts.translation_model._meta.db_table
        for language_id in get_language_id_list():
            table_alias = get_translation_table_alias(trans_table_name,
                                                      language_id)
            condition = ('((%s.master_id = %s.id) AND (%s.language_id = %s))'
                         % (table_alias, master_table_name, table_alias,
                            language_id))
            joins[table_alias] = (trans_table_name, 'LEFT JOIN', condition)
        return joins, where, params

class MultilingualModelQuerySet(QuerySet):
    """
    A specialized QuerySet that knows how to handle translatable
    fields in ordering and filtering methods.
    """

    def order_by(self, *field_names):
        """
        Override order_by to rename some of the arguments
        """
        translated_fields = self.model._meta.translation_model._meta.translated_fields

        new_field_names = []
        for field_name in field_names:
            prefix = ''
            if field_name[0] == '-':
                prefix = '-'
                field_name = field_name[1:]
                
            if field_name in translated_fields:
                field, language_id = translated_fields[field_name]
                if language_id is None:
                    language_id = getattr(self, '_default_language', None)
                real_name = get_translated_field_alias(field.attname,
                                                       language_id)
                new_field_names.append(prefix + real_name)
            else:
                new_field_names.append(prefix + field_name)
        return super(MultilingualModelQuerySet, self).order_by(*new_field_names)

    def for_language(self, language_id_or_code):
        """
        Set the default language for all objects returned with this
        query.
        """
        clone = self._clone()
        clone._default_language = get_language_id_from_id_or_code(language_id_or_code)
        return clone

    def iterator(self):
        """
        Add the default language information to all returned objects.
        """
        default_language = getattr(self, '_default_language', None)

        for obj in super(MultilingualModelQuerySet, self).iterator():
            obj._default_language = default_language
            yield obj

    def _clone(self, klass=None, **kwargs):
        """
        Override _clone to preserve additional information needed by
        MultilingualModelQuerySet.
        """
        clone = super(MultilingualModelQuerySet, self)._clone(klass, **kwargs)
        clone._default_language = getattr(self, '_default_language', None)
        return clone
