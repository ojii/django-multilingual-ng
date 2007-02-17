from django.db import models
from query import MultilingualModelQuerySet, QAddTranslationData
from languages import *

class Manager(models.Manager):
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

        return MultilingualModelQuerySet(self.model).filter(QAddTranslationData()).extra(select=select)

