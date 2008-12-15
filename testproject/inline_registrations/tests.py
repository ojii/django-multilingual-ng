from testproject.utils import AdminTestCase
from testproject.inline_registrations.models import (ArticleWithSimpleRegistration,
                                                     ArticleWithExternalInline,
                                                     ArticleWithInternalInline)

class SimpleRegistrationTestCase(AdminTestCase):
    def test_add(self):
        ArticleWithSimpleRegistration.objects.all().delete()
        
        path = '/admin/inline_registrations/articlewithsimpleregistration/'

        # get the list
        resp = self.client.get(path)
        self.assertEqual(resp.status_code, 200)

        # check the 'add' form
        resp = self.client.get(path + 'add/')
        self.assertEqual(resp.status_code, 200)
        self.assert_('adminform' in resp.context[0])

        # submit a new article
        resp = self.client.post(path + 'add/',
                                {'slug_global': 'new-article',
                                 'translations-TOTAL_FORMS': '3',
                                 'translations-INITIAL_FORMS': '0',
                                 'translations-0-slug_local': 'slug-en',
                                 'translations-0-title': 'title en',
                                 'translations-0-contents': 'contents en',
                                 'translations-0-language_id': '1',
                                 'translations-1-slug_local': 'slug-pl',
                                 'translations-1-title': 'title pl',
                                 'translations-1-contents': 'contents pl',
                                 'translations-1-language_id': '2',
                                 'translations-2-slug_local': 'slug-cn',
                                 'translations-2-title': 'title cn',
                                 'translations-2-contents': 'contents cn',
                                 'translations-2-language_id': '3',
                                 })
        # a successful POST ends with a 302 redirect
        self.assertEqual(resp.status_code, 302)
        art = ArticleWithSimpleRegistration.objects.all()[0]
        self.assertEqual(art.slug_global, 'new-article')
        self.assertEqual(art.slug_local_en, 'slug-en')
        self.assertEqual(art.slug_local_pl, 'slug-pl')
        self.assertEqual(art.slug_local_zh_cn, 'slug-cn')

        
class ExternalInlineTestCase(AdminTestCase):
    def test_add(self):
        ArticleWithExternalInline.objects.all().delete()
        
        path = '/admin/inline_registrations/articlewithexternalinline/'

        # get the list
        resp = self.client.get(path)
        self.assertEqual(resp.status_code, 200)

        # check the 'add' form
        resp = self.client.get(path + 'add/')
        self.assertEqual(resp.status_code, 200)
        self.assert_('adminform' in resp.context[0])

        # make sure it contains the JS code for prepopulated_fields
        self.assertContains(resp,
                            'getElementById("id_translations-0-slug_local").onchange')
        self.assertContains(resp,
                            'getElementById("id_translations-1-slug_local").onchange')
        self.assertContains(resp,
                            'getElementById("id_translations-2-slug_local").onchange')
                            
        # submit a new article
        resp = self.client.post(path + 'add/',
                                {'slug_global': 'new-article',
                                 'translations-TOTAL_FORMS': '3',
                                 'translations-INITIAL_FORMS': '0',
                                 'translations-0-slug_local': 'slug-en',
                                 'translations-0-title': 'title en',
                                 'translations-0-contents': 'contents en',
                                 'translations-0-language_id': '1',
                                 'translations-1-slug_local': 'slug-pl',
                                 'translations-1-title': 'title pl',
                                 'translations-1-contents': 'contents pl',
                                 'translations-1-language_id': '2',
                                 'translations-2-slug_local': 'slug-cn',
                                 'translations-2-title': 'title cn',
                                 'translations-2-contents': 'contents cn',
                                 'translations-2-language_id': '3',
                                 })
        # a successful POST ends with a 302 redirect
        self.assertEqual(resp.status_code, 302)
        art = ArticleWithExternalInline.objects.all()[0]
        self.assertEqual(art.slug_global, 'new-article')
        self.assertEqual(art.slug_local_en, 'slug-en')
        self.assertEqual(art.slug_local_pl, 'slug-pl')
        self.assertEqual(art.slug_local_zh_cn, 'slug-cn')

        
        
class InternalInlineTestCase(AdminTestCase):
    def test_add(self):
        ArticleWithInternalInline.objects.all().delete()
        
        path = '/admin/inline_registrations/articlewithinternalinline/'

        # get the list
        resp = self.client.get(path)
        self.assertEqual(resp.status_code, 200)

        # check the 'add' form
        resp = self.client.get(path + 'add/')
        self.assertEqual(resp.status_code, 200)
        self.assert_('adminform' in resp.context[0])

        # make sure it contains the JS code for prepopulated_fields
        self.assertContains(resp,
                            'getElementById("id_translations-0-slug_local").onchange')
        self.assertContains(resp,
                            'getElementById("id_translations-1-slug_local").onchange')
        self.assertContains(resp,
                            'getElementById("id_translations-2-slug_local").onchange')
                            
        # submit a new article
        resp = self.client.post(path + 'add/',
                                {'slug_global': 'new-article',
                                 'translations-TOTAL_FORMS': '3',
                                 'translations-INITIAL_FORMS': '0',
                                 'translations-0-slug_local': 'slug-en',
                                 'translations-0-title': 'title en',
                                 'translations-0-contents': 'contents en',
                                 'translations-0-language_id': '1',
                                 'translations-1-slug_local': 'slug-pl',
                                 'translations-1-title': 'title pl',
                                 'translations-1-contents': 'contents pl',
                                 'translations-1-language_id': '2',
                                 'translations-2-slug_local': 'slug-cn',
                                 'translations-2-title': 'title cn',
                                 'translations-2-contents': 'contents cn',
                                 'translations-2-language_id': '3',
                                 })
        # a successful POST ends with a 302 redirect
        self.assertEqual(resp.status_code, 302)
        art = ArticleWithInternalInline.objects.all()[0]
        self.assertEqual(art.slug_global, 'new-article')
        self.assertEqual(art.slug_local_en, 'slug-en')
        self.assertEqual(art.slug_local_pl, 'slug-pl')
        self.assertEqual(art.slug_local_zh_cn, 'slug-cn')

        
