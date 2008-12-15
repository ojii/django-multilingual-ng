from django.contrib import admin
from testproject.issue_23.models import ArticleWithSlug
import multilingual
from multilingual.languages import get_language_count

class TranslationAdmin(multilingual.TranslationModelAdmin):
#    prepopulated_fields = {'slug_local': ('title',)}
    model = ArticleWithSlug._meta.translation_model

class ArticleWithSlugAdmin(multilingual.ModelAdmin):
    inlines = [TranslationAdmin]
    prepopulated_fields = {'slug_global': ('title_en',)}

admin.site.register(ArticleWithSlug, ArticleWithSlugAdmin)
