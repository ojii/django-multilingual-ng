from django.db import models
import multilingual

try:
    from django.utils.translation import ugettext as _
except:
    # if this fails then _ is a builtin
    pass

class Category(models.Model):
    parent = models.ForeignKey('self', verbose_name=_("Parent category"),
                               blank=True, null=True)

    class Translation(multilingual.Translation):
        name = models.CharField(verbose_name=_("The name"),
                                blank=True, null=False, max_length=250)

    class Meta:
        app_label = 'issue_16'
