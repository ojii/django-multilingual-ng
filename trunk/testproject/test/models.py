"""
Test models for the multilingual library.

>>> from multilingual.models import set_default_language
>>> set_default_language(1)

### Create the test data

>>> c = Category()
>>> c.set_name('category 1', 1)
>>> c.set_name('kategoria 1', 2)
>>> c.save()

>>> c = Category()
>>> c.set_name('category 2', 1)
>>> c.set_name('kategoria 2', 2)
>>> c.save()

### See if the test data was saved correctly

>>> c = Category.objects.all().order_by('id')[0]
>>> (c.name, c.get_name(1), c.get_name(2))
('category 1', 'category 1', 'kategoria 1')
>>> c = Category.objects.all().order_by('id')[1]
>>> (c.name, c.get_name(1), c.get_name(2))
('category 2', 'category 2', 'kategoria 2')

### Check translation changes.
### Make sure the name and description properties obey
### set_default_language.

>>> c = Category.objects.all().order_by('id')[0]

# set language: pl
>>> set_default_language(2)
>>> (c.name, c.get_name(1), c.get_name(2))
('kategoria 1', 'category 1', 'kategoria 1')
>>> c.name = 'kat 1'
>>> (c.name, c.get_name(1), c.get_name(2))
('kat 1', 'category 1', 'kat 1')

# set language: en
>>> set_default_language(1)
>>> c.name = 'cat 1'
>>> (c.name, c.get_name(1), c.get_name(2))
('cat 1', 'cat 1', 'kat 1')
>>> c.save()

# Read the entire Category objects from the DB again to see if
# everything was saved correctly.
>>> c = Category.objects.all().order_by('id')[0]
>>> (c.name, c.get_name(1), c.get_name(2))
('cat 1', 'cat 1', 'kat 1')
>>> c = Category.objects.all().order_by('id')[1]
>>> (c.name, c.get_name(1), c.get_name(2))
('category 2', 'category 2', 'kategoria 2')

### Check ordering

>>> set_default_language(1)
>>> [c.name for c in  Category.objects.all().order_by('name_en')]
['cat 1', 'category 2']

"""

from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """
    Test model for multilingual content.
    """
    
    # First, some fields that do not need translations
    creator = models.ForeignKey(User, blank=True, null=True)
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
        try:
            return self.name
        except TranslationDoesNotExist:
            return "-not-available-"
    
    class Admin:
        # again, field names just work
        list_display = ('name', 'description')

    class Meta:
        verbose_name_plural = 'categories'
