from django.test import TestCase
from django.contrib.sites.models import Site
from multilingual.flatpages.models import MultilingualFlatPage

class FlatpagesTestCase(TestCase):
    fixtures = ['testdata.json']
        
    def test_page(self):
        response = self.client.get('/test1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test2/')
        self.assertEqual(response.status_code, 200)
        
    def test_language(self):
        response = self.client.get('/test1/', HTTP_ACCEPT_LANGUAGE='en')
        self.assertTrue('MLFP-Title1-en' in response.content and 'MLFP-Content1-en' in response.content)
        response = self.client.get('/test1/', HTTP_ACCEPT_LANGUAGE='ja')
        self.assertTrue('MLFP-Title1-ja' in response.content and 'MLFP-Content1-ja' in response.content)