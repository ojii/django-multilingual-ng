"""
Models and unit tests for issues reported in the tracker.

# test for issue #15, it will fail on unpatched Django
# http://code.google.com/p/django-multilingual/issues/detail?id=15

>>> from multilingual import set_default_language

# Note: the to_str() calls in all the tests are here only to make it
# easier to test both pre-unicode and current Django.
>>> from testproject.utils import to_str

>>> set_default_language('pl')
>>> g = Gallery.objects.create(id=2, ref_id=2, title_pl='Test polski', title_en='English Test')
>>> to_str(g.title)
'Test polski'
>>> to_str(g.title_en)
'English Test'
>>> g = Gallery.objects.select_related(depth=1).get(id=2)
>>> to_str(g.title)
'Test polski'
>>> to_str(g.title_en)
'English Test'
"""

from django.db import models
import multilingual

try:
    from django.utils.translation import ugettext as _
except:
    # if this fails then _ is a builtin
    pass

class Gallery(models.Model):
    ref = models.ForeignKey('self', verbose_name=_('Parent gallery'))
    modified = models.DateField(_('Modified'), auto_now=True)

    class Translation(multilingual.Translation):
        title = models.CharField(_('Title'), max_length=50)
        description = models.TextField(_('Description'), blank=True)
