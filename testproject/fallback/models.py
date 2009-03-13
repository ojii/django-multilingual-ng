"""
Unit tests for the translation fallback feature.
"""

from django.db import models
import multilingual

class Article(models.Model):
    class Translation(multilingual.Translation):
        title = models.CharField(max_length=250, null=False, blank=False)
        content = models.TextField(null=False, blank=True)
        signature = models.TextField(null=True, blank=True)

class Comment(models.Model):
    username = models.CharField(blank=True, max_length=100)
    class Translation(multilingual.Translation):
        body = models.TextField(null=True, blank=True)
