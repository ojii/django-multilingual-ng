from django import forms
from django.contrib import admin
from multilingual import translation
from articles import models

class CategoryAdmin(admin.ModelAdmin):
    # Field names would just work here, but if you need
    # correct list headers (from field.verbose_name) you have to
    # use the get_'field_name' functions here.
    list_display = ('id', 'creator', 'created', 'name', 'description')
    search_fields = ('name', 'description')

class ArticleAdmin(admin.ModelAdmin):
    class Translation(translation.TranslationModelAdmin):
        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(translation.TranslationModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            if db_field.name == 'contents':
                field.widget = forms.Textarea(attrs={'cols': 50})
            return field

admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.Category, CategoryAdmin)
