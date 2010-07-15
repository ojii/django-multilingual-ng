"""
Django-multilingual: a QuerySet subclass for models with translatable
fields.

This file contains the implementation for QSRF Django.
"""

import datetime
from copy import deepcopy

from django.core.exceptions import FieldError
from django.db import connection
from django.db.models.fields import FieldDoesNotExist
from django.db.models.query import QuerySet, Q
from django.db.models.sql.query import Query
from django.db import connections, DEFAULT_DB_ALIAS
from django.db.models.sql.datastructures import (
    EmptyResultSet,
    Empty,
    MultiJoin)
from django.db.models.sql.constants import *
from django.db.models.sql.where import WhereNode, EverythingNode, AND, OR

try:
    # handle internal API changes in Django rev. 9700
    from django.db.models.sql.where import Constraint

    def constraint_tuple(alias, col, field, lookup_type, value):
        return (Constraint(alias, col, field), lookup_type, value)
except ImportError:
    # backwards compatibility, for Django versions 1.0 to rev. 9699
    def constraint_tuple(alias, col, field, lookup_type, value):
        return (alias, col, field, lookup_type, value)

from multilingual.languages import (
    get_translation_table_alias,
    get_language_code_list,
    get_default_language,
    get_translated_field_alias)

from compiler import MultilingualSQLCompiler

__ALL__ = ['MultilingualModelQuerySet']


class MultilingualQuery(Query):

    def __init__(self, model, where=WhereNode):
        self.extra_join = {}
        self.include_translation_data = True
        extra_select = {}
        super(MultilingualQuery, self).__init__(model, where=where)
        opts = self.model._meta
        qn = self.get_compiler(DEFAULT_DB_ALIAS).quote_name_unless_alias
        qn2 = self.get_compiler(DEFAULT_DB_ALIAS).connection.ops.quote_name
        master_table_name = opts.db_table
        translation_opts = opts.translation_model._meta
        trans_table_name = translation_opts.db_table
        if hasattr(opts, 'translation_model'):
            master_table_name = opts.db_table
            for language_code in get_language_code_list():
                for fname in [f.attname for f in translation_opts.fields]:
                    table_alias = get_translation_table_alias(trans_table_name,
                        language_code)
                    field_alias = get_translated_field_alias(fname,
                        language_code)
                    extra_select[field_alias] = qn2(table_alias) + '.' + qn2(fname)
            self.add_extra(extra_select, None, None, None, None, None)
            self._trans_extra_select_count = len(self.extra_select)

    def clone(self, klass=None, **kwargs):
        defaults = {
            'extra_join': self.extra_join,
            'include_translation_data': self.include_translation_data,
            }
        defaults.update(kwargs)
        return super(MultilingualQuery, self).clone(klass=klass, **defaults)

    def add_filter(self, filter_expr, connector=AND, negate=False, trim=False,
            can_reuse=None, process_extras=True):
        """
        Copied from add_filter to generate WHERES for translation fields.
        """
        arg, value = filter_expr
        parts = arg.split(LOOKUP_SEP)
        if not parts:
            raise FieldError("Cannot parse keyword query %r" % arg)

        # Work out the lookup type and remove it from 'parts', if necessary.
        if len(parts) == 1 or parts[-1] not in self.query_terms:
            lookup_type = 'exact'
        else:
            lookup_type = parts.pop()

        # Interpret '__exact=None' as the sql 'is NULL'; otherwise, reject all
        # uses of None as a query value.
        if value is None:
            if lookup_type != 'exact':
                raise ValueError("Cannot use None as a query value")
            lookup_type = 'isnull'
            value = True
        elif (value == '' and lookup_type == 'exact' and
              self.get_compiler(DEFAULT_DB_ALIAS).connection.features.interprets_empty_strings_as_nulls):
            lookup_type = 'isnull'
            value = True
        elif callable(value):
            value = value()

        opts = self.get_meta()
        alias = self.get_initial_alias()
        allow_many = trim or not negate

        try:
            field, target, opts, join_list, last, extra_filters = self.setup_joins(
                    parts, opts, alias, True, allow_many, can_reuse=can_reuse,
                    negate=negate, process_extras=process_extras)
        except MultiJoin, e:
            self.split_exclude(filter_expr, LOOKUP_SEP.join(parts[:e.level]),
                    can_reuse)
            return

        #=======================================================================
        # Django Mulitlingual NG Specific Code START
        #=======================================================================
        if hasattr(opts, 'translation_model'):
            field_name = parts[-1]
            if field_name == 'pk':
                field_name = opts.pk.name
            translation_opts = opts.translation_model._meta
            if field_name in translation_opts.translated_fields.keys():
                field, model, direct, m2m = opts.get_field_by_name(field_name)
                if model == opts.translation_model:
                    language_code = translation_opts.translated_fields[field_name][1]
                    if language_code is None:
                        language_code = get_default_language()
                    master_table_name = opts.db_table
                    trans_table_alias = get_translation_table_alias(
                        model._meta.db_table, language_code)
                    new_table = (master_table_name + "__" + trans_table_alias)
                    self.where.add(constraint_tuple(new_table, field.column, field, lookup_type, value), connector)
                    return
        #=======================================================================
        # Django Mulitlingual NG Specific Code END
        #=======================================================================
        final = len(join_list)
        penultimate = last.pop()
        if penultimate == final:
            penultimate = last.pop()
        if trim and len(join_list) > 1:
            extra = join_list[penultimate:]
            join_list = join_list[:penultimate]
            final = penultimate
            penultimate = last.pop()
            col = self.alias_map[extra[0]][LHS_JOIN_COL]
            for alias in extra:
                self.unref_alias(alias)
        else:
            col = target.column
        alias = join_list[-1]

        while final > 1:
            # An optimization: if the final join is against the same column as
            # we are comparing against, we can go back one step in the join
            # chain and compare against the lhs of the join instead (and then
            # repeat the optimization). The result, potentially, involves less
            # table joins.
            join = self.alias_map[alias]
            if col != join[RHS_JOIN_COL]:
                break
            self.unref_alias(alias)
            alias = join[LHS_ALIAS]
            col = join[LHS_JOIN_COL]
            join_list = join_list[:-1]
            final -= 1
            if final == penultimate:
                penultimate = last.pop()

        if (lookup_type == 'isnull' and value is True and not negate and
                final > 1):
            # If the comparison is against NULL, we need to use a left outer
            # join when connecting to the previous model. We make that
            # adjustment here. We don't do this unless needed as it's less
            # efficient at the database level.
            self.promote_alias(join_list[penultimate])

        if connector == OR:
            # Some joins may need to be promoted when adding a new filter to a
            # disjunction. We walk the list of new joins and where it diverges
            # from any previous joins (ref count is 1 in the table list), we
            # make the new additions (and any existing ones not used in the new
            # join list) an outer join.
            join_it = iter(join_list)
            table_it = iter(self.tables)
            join_it.next(), table_it.next()
            table_promote = False
            join_promote = False
            for join in join_it:
                table = table_it.next()
                if join == table and self.alias_refcount[join] > 1:
                    continue
                join_promote = self.promote_alias(join)
                if table != join:
                    table_promote = self.promote_alias(table)
                break
            self.promote_alias_chain(join_it, join_promote)
            self.promote_alias_chain(table_it, table_promote)

        self.where.add(constraint_tuple(alias, col, field, lookup_type, value), connector)

        if negate:
            self.promote_alias_chain(join_list)
            if lookup_type != 'isnull':
                if final > 1:
                    for alias in join_list:
                        if self.alias_map[alias][JOIN_TYPE] == self.LOUTER:
                            j_col = self.alias_map[alias][RHS_JOIN_COL]
                            entry = self.where_class()
                            entry.add(constraint_tuple(alias, j_col, None, 'isnull', True), AND)
                            entry.negate()
                            self.where.add(entry, AND)
                            break
                elif not (lookup_type == 'in' and not value) and field.null:
                    # Leaky abstraction artifact: We have to specifically
                    # exclude the "foo__in=[]" case from this handling, because
                    # it's short-circuited in the Where class.
                    entry = self.where_class()
                    entry.add(constraint_tuple(alias, col, None, 'isnull', True), AND)
                    entry.negate()
                    self.where.add(entry, AND)

        if can_reuse is not None:
            can_reuse.update(join_list)
        if process_extras:
            for filter in extra_filters:
                self.add_filter(filter, negate=negate, can_reuse=can_reuse,
                        process_extras=False)

    def _setup_joins_with_translation(self, names, opts, alias,
                                      dupe_multis, allow_many=True,
                                      allow_explicit_fk=False, can_reuse=None,
                                      negate=False, process_extras=True):
        """
        This is based on a full copy of Query.setup_joins because
        currently I see no way to handle it differently.

        TO DO: there might actually be a way, by splitting a single
        multi-name setup_joins call into separate calls.  Check it.

        -- marcin@elksoft.pl

        Compute the necessary table joins for the passage through the fields
        given in 'names'. 'opts' is the Options class for the current model
        (which gives the table we are joining to), 'alias' is the alias for the
        table we are joining to. If dupe_multis is True, any many-to-many or
        many-to-one joins will always create a new alias (necessary for
        disjunctive filters).

        Returns the final field involved in the join, the target database
        column (used for any 'where' constraint), the final 'opts' value and the
        list of tables joined.
        """
        joins = [alias]
        last = [0]
        dupe_set = set()
        exclusions = set()
        extra_filters = []
        for pos, name in enumerate(names):
            try:
                exclusions.add(int_alias)
            except NameError:
                pass
            exclusions.add(alias)
            last.append(len(joins))
            if name == 'pk':
                name = opts.pk.name
            try:
                field, model, direct, m2m = opts.get_field_by_name(name)
            except FieldDoesNotExist:
                for f in opts.fields:
                    if allow_explicit_fk and name == f.attname:
                        # XXX: A hack to allow foo_id to work in values() for
                        # backwards compatibility purposes. If we dropped that
                        # feature, this could be removed.
                        field, model, direct, m2m = opts.get_field_by_name(f.name)
                        break
                else:
                    names = opts.get_all_field_names() + self.aggregate_select.keys()
                    raise FieldError("Cannot resolve keyword %r into field. "
                            "Choices are: %s" % (name, ", ".join(names)))

            if not allow_many and (m2m or not direct):
                for alias in joins:
                    self.unref_alias(alias)
                raise MultiJoin(pos + 1)
            #===================================================================
            # Django Multilingual NG Specific Code START
            #===================================================================
            if hasattr(opts, 'translation_model'):
                translation_opts = opts.translation_model._meta
                if model == opts.translation_model:
                    language_code = translation_opts.translated_fields[name][1]
                    if language_code is None:
                        language_code = get_default_language()
                    #TODO: check alias
                    master_table_name = opts.db_table
                    trans_table_alias = get_translation_table_alias(
                        model._meta.db_table, language_code)
                    new_table = (master_table_name + "__" + trans_table_alias)
                    qn = self.get_compiler(DEFAULT_DB_ALIAS).quote_name_unless_alias
                    qn2 = self.get_compiler(DEFAULT_DB_ALIAS).connection.ops.quote_name
                    trans_join = ("JOIN %s AS %s ON ((%s.master_id = %s.%s) AND (%s.language_code = '%s'))"
                                 % (qn2(model._meta.db_table),
                                 qn2(new_table),
                                 qn2(new_table),
                                 qn(master_table_name),
                                 qn2(model._meta.pk.column),
                                 qn2(new_table),
                                 language_code))
                    self.extra_join[new_table] = trans_join
                    target = field
                    continue
            #===================================================================
            # Django Multilingual NG Specific Code END
            #===================================================================
            elif model:
                # The field lives on a base class of the current model.
                # Skip the chain of proxy to the concrete proxied model
                proxied_model = get_proxied_model(opts)

                for int_model in opts.get_base_chain(model):
                    if int_model is proxied_model:
                        opts = int_model._meta
                    else:
                        lhs_col = opts.parents[int_model].column
                        dedupe = lhs_col in opts.duplicate_targets
                        if dedupe:
                            exclusions.update(self.dupe_avoidance.get(
                                    (id(opts), lhs_col), ()))
                            dupe_set.add((opts, lhs_col))
                        opts = int_model._meta
                        alias = self.join((alias, opts.db_table, lhs_col,
                                opts.pk.column), exclusions=exclusions)
                        joins.append(alias)
                        exclusions.add(alias)
                        for (dupe_opts, dupe_col) in dupe_set:
                            self.update_dupe_avoidance(dupe_opts, dupe_col,
                                    alias)
            cached_data = opts._join_cache.get(name)
            orig_opts = opts
            dupe_col = direct and field.column or field.field.column
            dedupe = dupe_col in opts.duplicate_targets
            if dupe_set or dedupe:
                if dedupe:
                    dupe_set.add((opts, dupe_col))
                exclusions.update(self.dupe_avoidance.get((id(opts), dupe_col),
                        ()))

            if process_extras and hasattr(field, 'extra_filters'):
                extra_filters.extend(field.extra_filters(names, pos, negate))
            if direct:
                if m2m:
                    # Many-to-many field defined on the current model.
                    if cached_data:
                        (table1, from_col1, to_col1, table2, from_col2,
                                to_col2, opts, target) = cached_data
                    else:
                        table1 = field.m2m_db_table()
                        from_col1 = opts.pk.column
                        to_col1 = field.m2m_column_name()
                        opts = field.rel.to._meta
                        table2 = opts.db_table
                        from_col2 = field.m2m_reverse_name()
                        to_col2 = opts.pk.column
                        target = opts.pk
                        orig_opts._join_cache[name] = (table1, from_col1,
                                to_col1, table2, from_col2, to_col2, opts,
                                target)

                    int_alias = self.join((alias, table1, from_col1, to_col1),
                            dupe_multis, exclusions, nullable=True,
                            reuse=can_reuse)
                    if int_alias == table2 and from_col2 == to_col2:
                        joins.append(int_alias)
                        alias = int_alias
                    else:
                        alias = self.join(
                                (int_alias, table2, from_col2, to_col2),
                                dupe_multis, exclusions, nullable=True,
                                reuse=can_reuse)
                        joins.extend([int_alias, alias])
                elif field.rel:
                    # One-to-one or many-to-one field
                    if cached_data:
                        (table, from_col, to_col, opts, target) = cached_data
                    else:
                        opts = field.rel.to._meta
                        target = field.rel.get_related_field()
                        table = opts.db_table
                        from_col = field.column
                        to_col = target.column
                        orig_opts._join_cache[name] = (table, from_col, to_col,
                                opts, target)

                    alias = self.join((alias, table, from_col, to_col),
                            exclusions=exclusions, nullable=field.null)
                    joins.append(alias)
                else:
                    # Non-relation fields.
                    target = field
                    break
            else:
                orig_field = field
                field = field.field
                if m2m:
                    # Many-to-many field defined on the target model.
                    if cached_data:
                        (table1, from_col1, to_col1, table2, from_col2,
                                to_col2, opts, target) = cached_data
                    else:
                        table1 = field.m2m_db_table()
                        from_col1 = opts.pk.column
                        to_col1 = field.m2m_reverse_name()
                        opts = orig_field.opts
                        table2 = opts.db_table
                        from_col2 = field.m2m_column_name()
                        to_col2 = opts.pk.column
                        target = opts.pk
                        orig_opts._join_cache[name] = (table1, from_col1,
                                to_col1, table2, from_col2, to_col2, opts,
                                target)

                    int_alias = self.join((alias, table1, from_col1, to_col1),
                            dupe_multis, exclusions, nullable=True,
                            reuse=can_reuse)
                    alias = self.join((int_alias, table2, from_col2, to_col2),
                            dupe_multis, exclusions, nullable=True,
                            reuse=can_reuse)
                    joins.extend([int_alias, alias])
                else:
                    # One-to-many field (ForeignKey defined on the target model)
                    if cached_data:
                        (table, from_col, to_col, opts, target) = cached_data
                    else:
                        local_field = opts.get_field_by_name(
                                field.rel.field_name)[0]
                        opts = orig_field.opts
                        table = opts.db_table
                        from_col = local_field.column
                        to_col = field.column
                        target = opts.pk
                        orig_opts._join_cache[name] = (table, from_col, to_col,
                                opts, target)

                    alias = self.join((alias, table, from_col, to_col),
                            dupe_multis, exclusions, nullable=True,
                            reuse=can_reuse)
                    joins.append(alias)

            for (dupe_opts, dupe_col) in dupe_set:
                try:
                    self.update_dupe_avoidance(dupe_opts, dupe_col, int_alias)
                except NameError:
                    self.update_dupe_avoidance(dupe_opts, dupe_col, alias)

        if pos != len(names) - 1:
            if pos == len(names) - 2:
                raise FieldError("Join on field %r not permitted. Did you misspell %r for the lookup type?" % (name, names[pos + 1]))
            else:
                raise FieldError("Join on field %r not permitted." % name)

        return field, target, opts, joins, last, extra_filters

    def setup_joins(self, names, opts, alias, dupe_multis, allow_many=True,
            allow_explicit_fk=False, can_reuse=None, negate=False,
            process_extras=True):
        if not self.include_translation_data:
            return super(MultilingualQuery, self).setup_joins(names, opts, alias,
                                                              dupe_multis, allow_many,
                                                              allow_explicit_fk,
                                                              can_reuse, negate,
                                                              process_extras)
        else:
            return self._setup_joins_with_translation(names, opts, alias, dupe_multis,
                                                      allow_many, allow_explicit_fk,
                                                      can_reuse, negate, process_extras)

    def get_count(self, using=None):
        # optimize for the common special case: count without any
        # filters
        if ((not (self.select or self.where ))#or self.extra_where))
            and self.include_translation_data):
            obj = self.clone(extra_select = {},
                             extra_join = {},
                             include_translation_data = False)
            return obj.get_count(using)
        else:
            return super(MultilingualQuery, self).get_count(using)

    def get_compiler(self, using=None, connection=None):
        if using is None and connection is None:
            raise ValueError("Need either using or connection")
        if using:
            connection = connections[using]
        return MultilingualSQLCompiler(self, connection, using)


class MultilingualModelQuerySet(QuerySet):
    """
    A specialized QuerySet that knows how to handle translatable
    fields in ordering and filtering methods.
    """

    def __init__(self, model=None, query=None, using=None):
        query = query or MultilingualQuery(model)
        super(MultilingualModelQuerySet, self).__init__(model, query, using)
        self._field_name_cache = None
        
    def __deepcopy__(self, memo):
        """
        Deep copy of a QuerySet doesn't populate the cache
        """
        obj_dict = deepcopy(self.__dict__, memo)
        obj_dict['_iter'] = None
        #=======================================================================
        # Django Multilingual NG Specific Code START
        #=======================================================================
        obj = self.__class__(self.model) # add self.model as first argument
        #=======================================================================
        # Django Multilingual NG Specific Code END
        #=======================================================================
        obj.__dict__.update(obj_dict)
        return obj

    def for_language(self, language_code):
        """
        Set the default language for all objects returned with this
        query.
        """
        clone = self._clone()
        clone._default_language = language_code
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

    def order_by(self, *field_names):
        if hasattr(self.model._meta, 'translation_model'):
            trans_opts = self.model._meta.translation_model._meta
            new_field_names = []
            for field_name in field_names:
                prefix = ''
                if field_name[0] == '-':
                    prefix = '-'
                    field_name = field_name[1:]
                field_and_lang = trans_opts.translated_fields.get(field_name)
                if field_and_lang:
                    field, language_code = field_and_lang
                    if language_code is None:
                        language_code = getattr(self, '_default_language', None)
                    real_name = get_translated_field_alias(field.attname,
                                                           language_code)
                    new_field_names.append(prefix + real_name)
                else:
                    new_field_names.append(prefix + field_name)
            return super(MultilingualModelQuerySet, self).extra(order_by=new_field_names)
        else:
            return super(MultilingualModelQuerySet, self).order_by(*field_names)
        
    def _get_all_field_names(self):
        if self._field_name_cache is None:
            self._field_name_cache = self.model._meta.get_all_field_names() + ['pk']
        return self._field_name_cache

    def values(self, *fields):
        for field in fields:
            if field not in self._get_all_field_names():
                raise NotImplementedError("Multilingual fields cannot be queried using queryset.values(...)")
        return super(MultilingualModelQuerySet, self).values(*fields)

    def values_list(self, *fields, **kwargs):
        for field in fields:
            if field not in self._get_all_field_names():
                raise NotImplementedError("Multilingual fields cannot be queried using queryset.values(...)")
        return super(MultilingualModelQuerySet, self).values_list(*fields, **kwargs)