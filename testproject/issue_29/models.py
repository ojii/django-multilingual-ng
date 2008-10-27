"""
Models and unit tests for issues reported in the tracker.

>>> from multilingual import set_default_language

# test for issue #15
# http://code.google.com/p/django-multilingual/issues/detail?id=15

>>> set_default_language('pl')
>>> g = Gallery.objects.create(id=2, title_pl='Test polski', title_en='English Test')
>>> g.title
'Test polski'
>>> g.title_en
'English Test'
>>> g.save()
>>> g.title_en = 'Test polski'
>>> g.save()
>>> try:
...     g = Gallery.objects.create(id=3, title_pl='Test polski')
... except: print "ERROR"
... 
ERROR
>>> 
"""

from django.db import models
import multilingual
try:
    from django.utils.translation import ugettext as _
except ImportError:
    pass

class Gallery(models.Model):
    class Admin:
        pass
    ref = models.ForeignKey('self', verbose_name=_('Parent gallery'),
                            blank=True, null=True)
    modified = models.DateField(_('Modified'), auto_now=True)

    class Translation(multilingual.Translation):
        title = models.CharField(_('Title'), max_length=50, unique = True)
        description = models.TextField(_('Description'), blank=True)
