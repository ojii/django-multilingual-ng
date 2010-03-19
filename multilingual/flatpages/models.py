from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from multilingual.translation import Translation as TranslationBase
from multilingual.exceptions import TranslationDoesNotExist
from multilingual.manager import MultilingualManager


class MultilingualFlatPage(models.Model):
    # non-translatable fields first
    url = models.CharField(_('URL'), max_length=100, db_index=True)
    enable_comments = models.BooleanField(_('enable comments'))
    template_name = models.CharField(_('template name'), max_length=70, blank=True,
        help_text=_("Example: 'flatpages/contact_page.html'. If this isn't provided, the system will use 'flatpages/default.html'."))
    registration_required = models.BooleanField(_('registration required'), help_text=_("If this is checked, only logged-in users will be able to view the page."))
    sites = models.ManyToManyField(Site)
    
    objects = MultilingualManager()

    # And now the translatable fields
    class Translation(TranslationBase):
        """
        The definition of translation model.

        The multilingual machinery will automatically add these to the
        Category class:

         * get_title(language_id=None)
         * set_title(value, language_id=None)
         * get_content(language_id=None)
         * set_content(value, language_id=None)
         * title and content properties using the methods above
        """
        title = models.CharField(_('title'), max_length=200)
        content = models.TextField(_('content'), blank=True)

    class Meta:
        db_table = 'multilingual_flatpage'
        verbose_name = _('multilingual flat page')
        verbose_name_plural = _('multilingual flat pages')
        ordering = ('url',)

    def __unicode__(self):
        # note that you can use name and description fields as usual
        try:
            return u"%s -- %s" % (self.url, self.title)
        except TranslationDoesNotExist:
            return u"-not-available-"

    def get_absolute_url(self):
        return self.url
