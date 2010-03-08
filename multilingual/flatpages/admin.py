from django import forms
from django.contrib import admin
from multilingual.flatpages.models import MultilingualFlatPage
from django.utils.translation import ugettext_lazy as _
from multilingual.admin import MultilingualModelAdmin, MultilingualModelAdminForm


class MultilingualFlatpageForm(MultilingualModelAdminForm):
    url = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/]+$',
        help_text = _("Example: '/about/contact/'. Make sure to have leading"
                      " and trailing slashes."),
        error_message = _("This value must contain only letters, numbers,"
                          " underscores, dashes or slashes."))

    class Meta:
        model = MultilingualFlatPage


class MultilingualFlatPageAdmin(MultilingualModelAdmin):
    form = MultilingualFlatpageForm
    use_fieldsets = (
        (None, {'fields': ('title', 'url', 'sites', 'content')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
    list_display = ('url', 'title')
    list_filter = ('sites', 'enable_comments', 'registration_required')
    search_fields = ('url', 'title')

admin.site.register(MultilingualFlatPage, MultilingualFlatPageAdmin)
