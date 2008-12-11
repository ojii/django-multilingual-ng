from django.contrib.auth.models import User
from django.test import TestCase

class TestIssue61(TestCase):
    def setUp(self):
        self.user = User.objects.get_or_create(username='admin',
                                               email='admin@test.elksoft.pl')[0]
        self.user.set_password('admin')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        
    def test_the_issue(self):
        self.client.login(username = 'admin', password = 'admin')
        resp = self.client.get('/admin/issue_61/othermodel/')
        self.assertEqual(resp.status_code, 200)

        # the next line failed in #61
        resp = self.client.get('/admin/issue_61/othermodel/add/')
        self.assertEqual(resp.status_code, 200)
