from django.contrib import admin
from testproject.inline_registrations.models import (ArticleWithSimpleRegistration,
                                                     ArticleWithExternalInline,
                                                     ArticleWithInternalInline)
import multilingual

##########################################
# for ArticleWithSimpleRegistration

admin.site.register(ArticleWithSimpleRegistration)

########################################
# for ArticleWithExternalInline

class TranslationAdmin(multilingual.TranslationModelAdmin):
    model = ArticleWithExternalInline._meta.translation_model
    prepopulated_fields = {'slug_local': ('title',)}

class ArticleWithExternalInlineAdmin(multilingual.ModelAdmin):
    inlines = [TranslationAdmin]

admin.site.register(ArticleWithExternalInline, ArticleWithExternalInlineAdmin)

########################################
# for ArticleWithInternalInline

class ArticleWithInternalInlineAdmin(multilingual.ModelAdmin):
    class Translation(multilingual.TranslationModelAdmin):
        prepopulated_fields = {'slug_local': ('title',)}

admin.site.register(ArticleWithInternalInline, ArticleWithInternalInlineAdmin)
