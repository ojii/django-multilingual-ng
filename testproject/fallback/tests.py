from django.test import TestCase
import multilingual

from testproject.fallback.models import Article

class FallbackTestCase(TestCase):
    def test_fallback(self):
        # sanity check first
        self.assertEqual(multilingual.FALLBACK_LANGUAGES,
                         ['pl', 'zh-cn'])

        # create test articles
        Article.objects.all().delete()
        Article.objects.create(title_pl = 'pl title 1',
                               content_pl = 'pl content 1',
                               title_zh_cn = 'zh-cn title 1',
                               content_zh_cn = 'zh-cn content 1')
        Article.objects.create(title_pl = 'pl title 2',
                               content_pl = '',
                               title_zh_cn = 'zh-cn title 2',
                               content_zh_cn = 'zh-cn content 2')
        
        # the tests
        a = Article.objects.get(title_pl='pl title 1')
        self.assertEqual(a.title_any, 'pl title 1')
        self.assertEqual(a.content_any, 'pl content 1')
        self.assertEqual(a.title_en, None)
        self.assertEqual(a.title_en_any, 'pl title 1')
        self.assertEqual(a.content_en, None)
        self.assertEqual(a.content_en_any, 'pl content 1')
        self.assertEqual(a.title_zh_cn_any, 'zh-cn title 1')
        self.assertEqual(a.content_zh_cn_any, 'zh-cn content 1')
        
        a = Article.objects.get(title_pl='pl title 2')
        self.assertEqual(a.title_any, 'pl title 2')
        self.assertEqual(a.content_any, '')
        self.assertEqual(a.title_en, None)
        self.assertEqual(a.title_en_any, 'pl title 2')
        self.assertEqual(a.content_en, None)
        self.assertEqual(a.content_en_any, '')
        self.assertEqual(a.title_zh_cn_any, 'zh-cn title 2')
        self.assertEqual(a.content_zh_cn_any, 'zh-cn content 2')
        
