from django.contrib import admin
from testproject.issue_23.models import ArticleWithSlug
import multilingual

class ArticleWithSlugAdmin(multilingual.ModelAdmin):
    prepopulated_fields = {'slug_global': ('title', 'title_pl')}

admin.site.register(ArticleWithSlug, ArticleWithSlugAdmin)
