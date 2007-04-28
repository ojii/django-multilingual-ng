"""
Test for issue #16

http://code.google.com/p/django-multilingual/issues/detail?id=16

# The next line triggered an OperationalError before fix for #16
>>> c = Category.objects.create(name='The Name')
>>> c = Category.objects.get(id=c.id)
>>> c.name
'The Name'


"""

from category import Category
from page import Page
