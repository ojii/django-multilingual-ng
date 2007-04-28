from django.db import models
import multilingual

class Category(models.Model):
    parent = models.ForeignKey('self', verbose_name=_("Parent category"),
                               blank=True, null=True)

    class Translation(multilingual.Translation):
        name = models.CharField(verbose_name=_("The name"),
                                blank=True, null=False, maxlength=250)

    class Meta:
        app_label = 'issue_16'
