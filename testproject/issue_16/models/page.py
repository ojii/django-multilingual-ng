from django.db import models
from issue_16.models.category import Category
import multilingual

try:
    from django.utils.translation import ugettext as _
except:
    # if this fails then _ is a builtin
    pass

class Page(models.Model):
    category = models.ForeignKey(Category, verbose_name=_("Parent category"),
                                 blank=True, null=True)

    class Translation(multilingual.Translation):
        title = models.CharField(verbose_name=_("The title"),
                                 blank=True, null=False, max_length=250)
        contents = models.TextField(verbose_name=_("The contents"),
                                    blank=True, null=False)

    class Meta:
        app_label = 'issue_16'
