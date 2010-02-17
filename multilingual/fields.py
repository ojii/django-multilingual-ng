from django.db import models


class TranslationForeignKey(models.ForeignKey):
    """
    """
    def south_field_triple(self):
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.related.ForeignKey"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)