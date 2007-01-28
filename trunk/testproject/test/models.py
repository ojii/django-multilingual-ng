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

### Check ordering

# start with renaming one of the categories so that the order actually
# depends on the default language

>>> set_default_language(1)
>>> c = Category.objects.get(name='cat 1')
>>> c.name = 'zzz cat 1'
>>> c.save()

>>> [c.name for c in  Category.objects.all().order_by('name_en')]
['category 2', 'zzz cat 1']
>>> [c.name for c in  Category.objects.all().order_by('name')]
['category 2', 'zzz cat 1']
>>> [c.name for c in  Category.objects.all().order_by('-name')]
['zzz cat 1', 'category 2']

>>> set_default_language(2)
>>> [c.name for c in  Category.objects.all().order_by('name')]
['kat 1', 'kategoria 2']
>>> [c.name for c in  Category.objects.all().order_by('-name')]
['kategoria 2', 'kat 1']

### Check filtering

>>> set_default_language(1)
>>> [c.name for c in  Category.objects.all().filter(name__contains='2')]
['category 2']

>>> set_default_language(1)
>>> [c.name for c in  Category.objects.all().filter(name_en__contains='2')]
['category 2']

>>> set_default_language(1)
>>> [c.name for c in  Category.objects.all().filter(name_pl__contains='kat')]
['zzz cat 1', 'category 2']

>>> set_default_language(2)
>>> [c.name for c in  Category.objects.all().filter(name__contains='k')]
['kat 1', 'kategoria 2']

>>> set_default_language(2)
>>> [c.name for c in  Category.objects.all().filter(name__contains='kategoria')]
['kategoria 2']

"""

from django.db import models
from django.contrib.auth.models import User
from multilingual.models import TranslationDoesNotExist

class Category(models.Model):
    """
    Test model for multilingual content.
    """
    
    # First, some fields that do not need translations
    creator = models.ForeignKey(User, verbose_name=_("Created by"),
                                blank=True, null=True)
    created = models.DateTimeField(verbose_name=_("Created at"),
                                   auto_now_add=True)
    parent = models.ForeignKey('self', verbose_name=_("Parent category"),
                               blank=True, null=True)

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

        name = models.CharField(verbose_name=_("The name"),
                                blank=True, null=False, maxlength=250)
        description = models.TextField(verbose_name=_("The description"),
                                       blank=True, null=False)

    def __str__(self):
        # note that you can use name and description fields as usual
        try:
            return str(self.name)
        except TranslationDoesNotExist:
            return "-not-available-"
    
    class Admin:
        # Again, field names would just work here, but if you need
        # correct list headers (from field.verbose_name) you have to
        # use the get_'field_name' functions here.
        list_display = ('creator', 'created', 'get_name', 'get_description')
        search_fields = ('name_en',)

    class Meta:
        verbose_name_plural = 'categories'
