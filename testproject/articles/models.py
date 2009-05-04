"""
Test models for the multilingual library.

# Note: the to_str() calls in all the tests are here only to make it
# easier to test both pre-unicode and current Django.
>>> from testproject.utils import to_str

# make sure the settings are right
>>> from multilingual.languages import LANGUAGES
>>> LANGUAGES
[['en', 'English'], ['pl', 'Polish'], ['zh-cn', 'Simplified Chinese']]

>>> from multilingual import set_default_language
>>> from django.db.models import Q
>>> set_default_language(1)

### Check the table names

>>> Category._meta.translation_model._meta.db_table
'category_language'
>>> Article._meta.translation_model._meta.db_table
'articles_article_translation'

### Create the test data

# Check both assigning via the proxy properties and set_* functions

>>> c = Category()
>>> c.name_en = 'category 1'
>>> c.name_pl = 'kategoria 1'
>>> c.save()

>>> c = Category()
>>> c.set_name('category 2', 'en')
>>> c.set_name('kategoria 2', 'pl')
>>> c.save()

### See if the test data was saved correctly
### Note: first object comes from the initial fixture.

>>> c = Category.objects.all().order_by('id')[1]
>>> to_str((c.name, c.get_name(1), c.get_name(2)))
('category 1', 'category 1', 'kategoria 1')
>>> c = Category.objects.all().order_by('id')[2]
>>> to_str((c.name, c.get_name(1), c.get_name(2)))
('category 2', 'category 2', 'kategoria 2')

### Check translation changes.
### Make sure the name and description properties obey
### set_default_language.

>>> c = Category.objects.all().order_by('id')[1]

# set language: pl
>>> set_default_language(2)
>>> to_str((c.name, c.get_name(1), c.get_name(2)))
('kategoria 1', 'category 1', 'kategoria 1')
>>> c.name = 'kat 1'
>>> to_str((c.name, c.get_name(1), c.get_name(2)))
('kat 1', 'category 1', 'kat 1')

# set language: en
>>> set_default_language('en')
>>> c.name = 'cat 1'
>>> to_str((c.name, c.get_name(1), c.get_name(2)))
('cat 1', 'cat 1', 'kat 1')
>>> c.save()

# Read the entire Category objects from the DB again to see if
# everything was saved correctly.
>>> c = Category.objects.all().order_by('id')[1]
>>> to_str((c.name, c.get_name('en'), c.get_name('pl')))
('cat 1', 'cat 1', 'kat 1')
>>> c = Category.objects.all().order_by('id')[2]
>>> to_str((c.name, c.get_name('en'), c.get_name('pl')))
('category 2', 'category 2', 'kategoria 2')

### Check ordering

>>> set_default_language(1)
>>> to_str([c.name for c in  Category.objects.all().order_by('name_en')])
['Fixture category', 'cat 1', 'category 2']

### Check ordering

# start with renaming one of the categories so that the order actually
# depends on the default language

>>> set_default_language(1)
>>> c = Category.objects.get(name='cat 1')
>>> c.name = 'zzz cat 1'
>>> c.save()

>>> to_str([c.name for c in  Category.objects.all().order_by('name_en')])
['Fixture category', 'category 2', 'zzz cat 1']
>>> to_str([c.name for c in  Category.objects.all().order_by('name')])
['Fixture category', 'category 2', 'zzz cat 1']
>>> to_str([c.name for c in  Category.objects.all().order_by('-name')])
['zzz cat 1', 'category 2', 'Fixture category']

>>> set_default_language(2)
>>> to_str([c.name for c in  Category.objects.all().order_by('name')])
['Fixture kategoria', 'kat 1', 'kategoria 2']
>>> to_str([c.name for c in  Category.objects.all().order_by('-name')])
['kategoria 2', 'kat 1', 'Fixture kategoria']

### Check filtering

# Check for filtering defined by Q objects as well.  This is a recent
# improvement: the translation fields are being handled by an
# extension of lookup_inner instead of overridden
# QuerySet._filter_or_exclude

>>> set_default_language('en')
>>> to_str([c.name for c in  Category.objects.all().filter(name__contains='2')])
['category 2']

>>> set_default_language('en')
>>> to_str([c.name for c in  Category.objects.all().filter(Q(name__contains='2'))])
['category 2']

>>> set_default_language(1)
>>> to_str([c.name for c in
...  Category.objects.all().filter(Q(name__contains='2')|Q(name_pl__contains='kat'))])
['Fixture category', 'zzz cat 1', 'category 2']

>>> set_default_language(1)
>>> to_str([c.name for c in  Category.objects.all().filter(name_en__contains='2')])
['category 2']

>>> set_default_language(1)
>>> to_str([c.name for c in  Category.objects.all().filter(Q(name_pl__contains='kat'))])
['Fixture category', 'zzz cat 1', 'category 2']

>>> set_default_language('pl')
>>> to_str([c.name for c in  Category.objects.all().filter(name__contains='k')])
['Fixture kategoria', 'kat 1', 'kategoria 2']

>>> set_default_language('pl')
>>> to_str([c.name for c in  Category.objects.all().filter(Q(name__contains='kategoria'))])
['Fixture kategoria', 'kategoria 2']

### Check specifying query set language
>>> c_en = Category.objects.all().for_language('en')
>>> c_pl = Category.objects.all().for_language(2)  # both ID and code work here
>>> to_str(c_en.get(name__contains='1').name)
'zzz cat 1'
>>> to_str(c_pl.get(name__contains='1').name)
'kat 1'

>>> to_str([c.name for c in  c_en.order_by('name')])
['Fixture category', 'category 2', 'zzz cat 1']
>>> to_str([c.name for c in c_pl.order_by('-name')])
['kategoria 2', 'kat 1', 'Fixture kategoria']

>>> c = c_en.get(id=2)
>>> c.name = 'test'
>>> to_str((c.name, c.name_en, c.name_pl))
('test', 'test', 'kat 1')

>>> c = c_pl.get(id=2)
>>> c.name = 'test'
>>> to_str((c.name, c.name_en, c.name_pl))
('test', 'zzz cat 1', 'test')

### Check filtering spanning more than one model

>>> set_default_language(1)

>>> cat_1 = Category.objects.get(name='zzz cat 1')
>>> cat_2 = Category.objects.get(name='category 2')

>>> a = Article(category=cat_1)
>>> a.set_title('article 1', 1)
>>> a.set_title('artykul 1', 2)
>>> a.set_contents('contents 1', 1)
>>> a.set_contents('zawartosc 1', 1)
>>> a.save()

>>> a = Article(category=cat_2)
>>> a.set_title('article 2', 1)
>>> a.set_title('artykul 2', 2)
>>> a.set_contents('contents 2', 1)
>>> a.set_contents('zawartosc 2', 1)
>>> a.save()

>>> to_str([a.title for a in Article.objects.filter(category=cat_1)])
['article 1']
>>> to_str([a.title for a in Article.objects.filter(category__name=cat_1.name)])
['article 1']
>>> to_str([a.title for a in Article.objects.filter(Q(category__name=cat_1.name)|Q(category__name_pl__contains='2')).order_by('-title')])
['article 2', 'article 1']

### Test the creation of new objects using keywords passed to the
### constructor

>>> set_default_language(2)
>>> c_n = Category.objects.create(name_en='new category', name_pl='nowa kategoria')
>>> to_str((c_n.name, c_n.name_en, c_n.name_pl))
('nowa kategoria', 'new category', 'nowa kategoria')
>>> c_n.save()

>>> c_n2 = Category.objects.get(name_en='new category')
>>> to_str((c_n2.name, c_n2.name_en, c_n2.name_pl))
('nowa kategoria', 'new category', 'nowa kategoria')

>>> set_default_language(2)
>>> c_n3 = Category.objects.create(name='nowa kategoria 2')
>>> to_str((c_n3.name, c_n3.name_en, c_n3.name_pl))
('nowa kategoria 2', None, 'nowa kategoria 2')

########################################
###### Check if the admin behaviour for categories with incomplete translations

>>> from django.contrib.auth.models import User
>>> User.objects.create_superuser('test', 'test_email', 'test_password') and None

>>> from django.test.client import Client
>>> c = Client()
>>> c.login(username='test', password='test_password')
True

# create a category with only 2 translations, skipping the
# first language
>>> resp = c.post('/admin/articles/category/add/',
...        {'creator': 1,
...         'translations-TOTAL_FORMS': '3',
...         'translations-INITIAL_FORMS': '0',
...         'translations-0-language_id': '1',
...         'translations-1-language_id': '2',
...         'translations-2-language_id': '3',
...         'translations-1-name': 'pl name',
...         'translations-2-name': 'zh-cn name',
...        })

>>> resp.status_code
302

>>> cat = Category.objects.order_by('-id')[0]
>>> cat.name_en

>>> cat.name_pl
u'pl name'
>>> cat.name_zh_cn
u'zh-cn name'

>>> cat.translations.count()
2
"""

from django.db import models
from django.contrib.auth.models import User
import multilingual

try:
    from django.utils.translation import ugettext as _
except:
    # if this fails then _ is a builtin
    pass

class Category(models.Model):
    """
    Test model for multilingual content: a simplified Category.
    """

    # First, some fields that do not need translations
    creator = models.ForeignKey(User, verbose_name=_("Created by"),
                                blank=True, null=True)
    created = models.DateTimeField(verbose_name=_("Created at"),
                                   auto_now_add=True)
    parent = models.ForeignKey('self', verbose_name=_("Parent category"),
                               blank=True, null=True)

    # And now the translatable fields
    class Translation(multilingual.Translation):
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
                                max_length=250)
        description = models.TextField(verbose_name=_("The description"),
                                       blank=True, null=False)

        class Meta:
            db_table = 'category_language'

    def get_absolute_url(self):
        return "/" + str(self.id) + "/"

    def __unicode__(self):
        # note that you can use name and description fields as usual
        try:
            return str(self.name)
        except multilingual.TranslationDoesNotExist:
            return "-not-available-"

    def __str__(self):
        # compatibility
        return str(self.__unicode__())

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ('id',)

class CustomArticleManager(multilingual.Manager):
    pass

class Article(models.Model):
    """
    Test model for multilingual content: a simplified article
    belonging to a single category.
    """

    # non-translatable fields first
    creator = models.ForeignKey(User, verbose_name=_("Created by"),
                                blank=False, null=True)
    created = models.DateTimeField(verbose_name=_("Created at"),
                                   auto_now_add=True)
    category = models.ForeignKey(Category, verbose_name=_("Parent category"),
                                 blank=True, null=True)

    objects = CustomArticleManager()

    # And now the translatable fields
    class Translation(multilingual.Translation):
        title = models.CharField(verbose_name=_("The title"),
                                blank=True, null=False, max_length=250)
        contents = models.TextField(verbose_name=_("The contents"),
                                    blank=True, null=False)
