from django.test import TestCase
from multilingual.flatpages.models import MultilingualFlatPage
from multilingual.utils import GLL
from multilingual import languages

class CoreTestCase(TestCase):
    fixtures = ['testdata.json']
    
    def test_read(self):
        mfp = MultilingualFlatPage.objects.get(url='/test1/')
        self.assertEqual(mfp.title_en, 'MLFP-Title1-en')
        self.assertEqual(mfp.title_ja, 'MLFP-Title1-ja')
        self.assertEqual(mfp.content_en, 'MLFP-Content1-en')
        self.assertEqual(mfp.content_ja, 'MLFP-Content1-ja')
        
    def test_gll(self):
        mfp = MultilingualFlatPage.objects.get(url='/test2/')
        GLL.lock('en')
        self.assertEqual(mfp.title, None)
        self.assertEqual(mfp.content, None)
        GLL.release()
        GLL.lock('ja')
        self.assertEqual(mfp.title, 'MLFP-Title2-ja')
        self.assertEqual(mfp.content, 'MLFP-Content2-ja')
        GLL.release()
        
    def test_fallbacks(self):
        mfp = MultilingualFlatPage.objects.get(url='/test2/')
        self.assertEqual(mfp.title_ja_any, mfp.title_en_any)
        
    def test_magical_methods(self):
        # default lang is 'en'
        mfp = MultilingualFlatPage.objects.get(url='/test2/')
        self.assertEqual(mfp.title, mfp.title_en_any)
        self.assertNotEqual(mfp.title_en, mfp.title_en_any)
        
    def test_default_language(self):
        self.assertEqual(languages.get_default_language(), 'en')
        languages.set_default_language('ja')
        self.assertEqual(languages.get_default_language(), 'ja')
        
    def test_get_fallbacks(self):
        self.assertEqual(languages.get_fallbacks('en'), ['en', 'ja'])
        self.assertEqual(languages.get_fallbacks('ja'), ['ja', 'en'])
        
    def test_implicit_fallbacks(self):
        self.assertEqual(languages.get_fallbacks('en-us'), ['en-us', 'en'])