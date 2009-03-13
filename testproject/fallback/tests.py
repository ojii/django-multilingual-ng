from django.test import TestCase
import multilingual

from testproject.fallback.models import Article
from testproject.fallback.models import Comment

class FallbackTestCase(TestCase):
    def test_fallback(self):
        # sanity check first
        self.assertEqual(multilingual.FALLBACK_LANGUAGES,
                         ['zh-cn', 'pl'])

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
        
        #create test comment without translations
        Comment.objects.all().delete()
        Comment.objects.create(username='theuser')
        
        # set english as the default language
        multilingual.languages.set_default_language('en')
        
        # fallback should not fail if instance has no translations
        c = Comment.objects.get(username='theuser')
        self.assertTrue(c.body_any is None)

        # the tests
        a = Article.objects.get(title_zh_cn='zh-cn title 1')
        self.assertEqual(a.title_any, 'zh-cn title 1')
        self.assertEqual(a.content_any, 'zh-cn content 1')
        self.assertEqual(a.title_en, None)
        self.assertEqual(a.title_en_any, 'zh-cn title 1')
        self.assertEqual(a.content_en, None)
        self.assertEqual(a.content_en_any, 'zh-cn content 1')
        self.assertEqual(a.title_pl_any, 'pl title 1')
        self.assertEqual(a.content_pl_any, 'pl content 1')
        
        a = Article.objects.get(title_zh_cn='zh-cn title 2')
        self.assertEqual(a.title_any, 'zh-cn title 2')
        self.assertEqual(a.content_any, 'zh-cn content 2')
        self.assertEqual(a.title_en, None)
        self.assertEqual(a.title_en_any, 'zh-cn title 2')
        self.assertEqual(a.content_en, None)
        self.assertEqual(a.content_en_any, 'zh-cn content 2')
        self.assertEqual(a.title_pl_any, 'pl title 2')
        self.assertEqual(a.content_pl_any, '')

