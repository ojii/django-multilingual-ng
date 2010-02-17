from django.core.management.base import AppCommand
from django.db import models
from django.utils.importlib import import_module
from django.conf import settings
from multilingual.utils import is_multilingual_model
from multilingual.languages import get_language_choices
from inspect import isclass
from south.db import db
from django.db import connection


def get_code_by_id(lid):
    return settings.LANGUAGES[lid-1][0]

class Command(AppCommand):
    """
    Migrate the data from an id base translation table to a code based table.
    """
    def handle_app(self, app, **options):
        print 'handling app %s' % app.__name__
        for obj in [getattr(app, name) for name in dir(app)]:
            if not isclass(obj):
                continue
            if not issubclass(obj, models.Model):
                continue
            if not is_multilingual_model(obj):
                continue
            print 'altering model %s' % obj
            db.add_column(obj._meta.translation_model._meta.db_table, 
                'language_code',
                models.CharField(max_length=5, blank=True,
                    choices=get_language_choices(), db_index=True)
            )
            # migrate the model
            # This is TERRIBLE for performance, but whatever...
            print 'migrating data'
            tempfield = models.IntegerField(blank=False, null=False,
                choices=get_language_choices(), db_index=True)
            tempfield.contribute_to_class(obj._meta.translation_model, 'language_id')
            for row in obj.objects.all():
                for translation in row.translations.all():
                    translation.language_code = get_code_by_id(translation.language_id)
                    translation.save()