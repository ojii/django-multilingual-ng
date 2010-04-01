from django.test import TestCase
from multilingual.flatpages.models import MultilingualFlatPage
from multilingual.utils import GLL
from multilingual import languages
from django.utils.translation import activate

class CoreTestCase(TestCase):
    fixtures = ['testdata.json']
    
    def test_01_read(self):
        mfp = MultilingualFlatPage.objects.get(url='/test1/')
        self.assertEqual(mfp.title_en, 'MLFP-Title1-en')
        self.assertEqual(mfp.title_ja, 'MLFP-Title1-ja')
        self.assertEqual(mfp.content_en, 'MLFP-Content1-en')
        self.assertEqual(mfp.content_ja, 'MLFP-Content1-ja')
        
    def test_02_gll(self):
        mfp = MultilingualFlatPage.objects.get(url='/test2/')
        GLL.lock('en')
        self.assertEqual(mfp.title, None)
        self.assertEqual(mfp.content, None)
        GLL.release()
        GLL.lock('ja')
        self.assertEqual(mfp.title, 'MLFP-Title2-ja')
        self.assertEqual(mfp.content, 'MLFP-Content2-ja')
        GLL.release()
        
    def test_03_fallbacks(self):
        mfp = MultilingualFlatPage.objects.get(url='/test2/')
        self.assertEqual(mfp.title_ja_any, mfp.title_en_any)
        
    def test_04_magical_methods(self):
        # default lang is 'en'
        activate('en')
        mfp = MultilingualFlatPage.objects.get(url='/test2/')
        self.assertEqual(mfp.title, mfp.title_en_any)
        self.assertNotEqual(mfp.title_en, mfp.title_en_any)
        
    def test_05_default_language(self):
        self.assertEqual(languages.get_default_language(), 'en')
        languages.set_default_language('ja')
        self.assertEqual(languages.get_default_language(), 'ja')
        
    def test_06_get_fallbacks(self):
        self.assertEqual(languages.get_fallbacks('en'), ['en', 'ja'])
        self.assertEqual(languages.get_fallbacks('ja'), ['ja', 'en'])
        
    def test_07_implicit_fallbacks(self):
        self.assertEqual(languages.get_fallbacks('en-us'), ['en-us', 'en'])
        
    def test_08_get_current(self):
        mfp = MultilingualFlatPage.objects.get(url='/test1/')
        activate('ja')
        self.assertEqual(mfp.title_current, mfp.title_ja)
        self.assertEqual(mfp.title_current_any, mfp.title_ja)
        activate('en')
        self.assertEqual(mfp.title_current, mfp.title_en)
        self.assertEqual(mfp.title_current_any, mfp.title_en_any)
        mfp = MultilingualFlatPage.objects.get(url='/test2/')
        activate('en')
        self.assertEqual(mfp.title_current, None)
        self.assertEqual(mfp.title_current_any, mfp.title_ja)