import unittest
from django.template import Template, Context
from multilingual.flatpages.models import MultilingualFlatPage

class TemplateTestCase(unittest.TestCase):
    fixtures = ['testdata.json']
    def test_gll(self):
        mfp = MultilingualFlatPage.objects.get(url='/test1/')
        ctx = Context({'page': mfp})
        tpl = Template('{% load multilingual_tags %}{% gll "en" %}{{ page.title }}{% endgll %}')
        result = tpl.render(ctx)
        self.assertEqual(result, 'MLFP-Title1-en')
        tpl = Template('{% load multilingual_tags %}{% gll "ja" %}{{ page.title }}{% endgll %}')
        result = tpl.render(ctx)
        self.assertEqual(result, 'MLFP-Title1-ja')