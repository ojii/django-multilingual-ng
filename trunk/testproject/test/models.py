from django.db import models
from django.contrib.auth.models import User
from multilingual.models import *

class Category(models.Model):
    """
    Test model for multilingual content.
    """
    
    # First, some fields that do not need translations
    creator = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', blank=True, null=True)

    # And now the translatable fields
    class Translation:
        """
        The definition of translation model.

        The multilingual machinery will automatically add these to the
        Category class:
        
         * get_name(language_id=None)
         * set_name(value, language_id=None)
         * get_description(language_id=None)
         * set_description(value, language_id=None)
         * name and description properties using the methods above
        """

        name = models.CharField(blank=True, null=False, maxlength=250)
        description = models.TextField(blank=True, null=False)

    def __str__(self):
        # note that you can use name and description fields as usual
        return self.name
    
    class Admin:
        # again, field names just work
        list_display = ('name', 'description')

    class Meta:
        verbose_name_plural = 'categories'
    
