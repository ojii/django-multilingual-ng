"""
Django-multilingual: a QuerySet subclass for models with translatable
fields.

This file contains the implementation for QSRF Django.

Huge thanks to hubscher.remy for writing this!
"""
from django.db.models.sql.compiler import SQLCompiler

from multilingual.languages import (
    get_translation_table_alias,
    get_language_code_list,
    get_default_language,
    get_translated_field_alias)

__ALL__ = ['MultilingualSQLCompiler']

class MultilingualSQLCompiler(SQLCompiler):

    def pre_sql_setup(self):
        """
        Adds the JOINS and SELECTS for fetching multilingual data.
        """
        super(MultilingualSQLCompiler, self).pre_sql_setup()

        if not self.query.include_translation_data:
            return

        opts = self.query.model._meta
        qn = self.quote_name_unless_alias
        qn2 = self.connection.ops.quote_name

        if hasattr(opts, 'translation_model'):
            master_table_name = self.query.join((None, opts.db_table, None, None))
            translation_opts = opts.translation_model._meta
            trans_table_name = translation_opts.db_table
            for language_code in get_language_code_list():
                table_alias = get_translation_table_alias(trans_table_name,
                                                          language_code)
                trans_join = ("LEFT JOIN %s AS %s ON ((%s.master_id = %s.%s) AND (%s.language_code = '%s'))"
                           % (qn2(translation_opts.db_table),
                           qn2(table_alias),
                           qn2(table_alias),
                           qn(master_table_name),
                           qn2(opts.pk.column),
                           qn2(table_alias),
                           language_code))
                self.query.extra_join[table_alias] = trans_join

    
    def get_from_clause(self):
        """
        Add the JOINS for related multilingual fields filtering.
        """
        result = super(MultilingualSQLCompiler, self).get_from_clause()

        if not self.query.include_translation_data:
            return result

        from_ = result[0]
        for join in self.query.extra_join.values():
            from_.append(join)
        return (from_, result[1])
