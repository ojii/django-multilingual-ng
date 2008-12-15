from django.db import models
import multilingual

class ArticleWithSlug(models.Model):
    slug_global = models.SlugField(blank=True, null=False)

    class Translation(multilingual.Translation):
        title = models.CharField(blank=True, null=False, max_length=250)
        contents = models.TextField(blank=True, null=False)
        slug_local = models.SlugField(blank=True, null=False)
