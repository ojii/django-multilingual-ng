"""
Test for issue #16

http://code.google.com/p/django-multilingual/issues/detail?id=16

# Note: the to_str() calls in all the tests are here only to make it
# easier to test both pre-unicode and current Django.
>>> from testproject.utils import to_str

# The next line triggered an OperationalError before fix for #16
>>> c = Category.objects.create(name=u'The Name')
>>> c = Category.objects.get(id=c.id)
>>> to_str(c.name)
'The Name'
"""

from issue_16.models.category import Category
from issue_16.models.page import Page
