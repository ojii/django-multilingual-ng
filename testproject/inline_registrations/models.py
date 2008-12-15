from django.db import models
import multilingual

class ArticleWithSimpleRegistration(models.Model):
    """
    This model will be registered without specifying a ModelAdmin.
    """
    slug_global = models.SlugField(blank=True, null=False)

    class Translation(multilingual.Translation):
        slug_local = models.SlugField(blank=True, null=False)
        title = models.CharField(blank=True, null=False, max_length=250)
        contents = models.TextField(blank=True, null=False)

class ArticleWithExternalInline(models.Model):
    """
    This model will be registered with a ModelAdmin and an
    externally-defined TranslationModelAdmin class.
    """
    slug_global = models.SlugField(blank=True, null=False)

    class Translation(multilingual.Translation):
        slug_local = models.SlugField(blank=True, null=False)
        title = models.CharField(blank=True, null=False, max_length=250)
        contents = models.TextField(blank=True, null=False)

class ArticleWithInternalInline(models.Model):
    """
    This model will be registered with a ModelAdmin having an inner
    Translation class.
    """
    slug_global = models.SlugField(blank=True, null=False)

    class Translation(multilingual.Translation):
        slug_local = models.SlugField(blank=True, null=False)
        title = models.CharField(blank=True, null=False, max_length=250)
        contents = models.TextField(blank=True, null=False)

