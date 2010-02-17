from django.core.exceptions import ImproperlyConfigured
from django.db import models

from multilingual.utils import is_multilingual_model


def get_field(cls, model, opts, label, field):
    """
    Just like django.contrib.admin.validation.get_field, but knows
    about translation models.
    """

    trans_model = model._meta.translation_model
    try:
        (f, lang_id) = trans_model._meta.translated_fields[field]
        return f
    except KeyError:
        # fall back to the old way -- see if model contains the field
        # directly
        pass

    try:
        return opts.get_field(field)
    except models.FieldDoesNotExist:
        raise ImproperlyConfigured("'%s.%s' refers to field '%s' that is " \
            "missing from model '%s'." \
            % (cls.__name__, label, field, model.__name__))


def validate_admin_registration(cls, model):
    """
    Validates a class specified as a model admin.

    Right now this means validating prepopulated_fields, as for
    multilingual models DM handles them by itself.
    """

    if not is_multilingual_model(model):
        return

    from django.contrib.admin.validation import check_isdict, check_isseq

    opts = model._meta

    # this is heavily based on django.contrib.admin.validation.
    if hasattr(cls, '_dm_prepopulated_fields'):
        check_isdict(cls, '_dm_prepopulated_fields', cls.prepopulated_fields)
        for field, val in cls._dm_prepopulated_fields.items():
            f = get_field(cls, model, opts, 'prepopulated_fields', field)
            if isinstance(f, (models.DateTimeField, models.ForeignKey,
                models.ManyToManyField)):
                raise ImproperlyConfigured("'%s.prepopulated_fields['%s']' "
                        "is either a DateTimeField, ForeignKey or "
                        "ManyToManyField. This isn't allowed."
                        % (cls.__name__, field))
            check_isseq(cls, "prepopulated_fields['%s']" % field, val)
            for idx, f in enumerate(val):
                get_field(cls, model,
                        opts, "prepopulated_fields['%s'][%d]"
                        % (f, idx), f)
