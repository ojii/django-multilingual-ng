"""
Models and unit tests for issues reported in the tracker.

>>> from multilingual import set_default_language
>>> from testproject.utils import to_str

# test for issue #37
# http://code.google.com/p/django-multilingual/issues/detail?id=37

>>> set_default_language('en')
>>> x = ModelWithCustomPK.objects.create(custompk='key1', title=u'The English Title')
>>> set_default_language('pl')
>>> x.title = u'The Polish Title'
>>> x.save()
>>> x = ModelWithCustomPK.objects.get(pk='key1')
>>> to_str(x.title)
'The Polish Title'
>>> set_default_language('en')
>>> to_str(x.title)
'The English Title'
"""

from django.db import models
import multilingual
try:
    from django.utils.translation import ugettext as _
except ImportError:
    pass

class ModelWithCustomPK(models.Model):
    custompk = models.CharField(max_length=5, primary_key=True)

    class Translation(multilingual.Translation):
        title = models.CharField(_('Title'), max_length=50, unique = True)
