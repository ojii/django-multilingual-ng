from django.contrib.auth.models import User
from testproject.utils import AdminTestCase

class TestIssue23(AdminTestCase):
    def test_issue_23(self):
        # the next line failed with "Key 'title_en' not found in Form"
        resp = self.client.get('/admin/issue_23/articlewithslug/add/')
        self.assertEqual(resp.status_code, 200)

