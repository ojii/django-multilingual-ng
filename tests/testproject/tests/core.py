from django.test import TestCase
from multilingual.flatpages.models import MultilingualFlatPage
from multilingual.utils import GLL

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
        self.assertEqual(mfp.title, 'MLFP-Title2-en')
        self.assertEqual(mfp.content, 'MLFP-Content2-en')
        GLL.release()
        GLL.lock('ja')
        self.assertEqual(mfp.title, 'MLFP-Title2-ja')
        self.assertEqual(mfp.content, 'MLFP-Content2-ja')
        GLL.release()