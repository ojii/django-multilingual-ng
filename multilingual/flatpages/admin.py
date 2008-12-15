from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from multilingual.flatpages.models import MultilingualFlatPage
import multilingual

class MultilingualFlatPageAdmin(multilingual.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'sites')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
    list_filter = ('sites',)
    search_fields = ('url', 'title')

admin.site.register(MultilingualFlatPage, MultilingualFlatPageAdmin)
