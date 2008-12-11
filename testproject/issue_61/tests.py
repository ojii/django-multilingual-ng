from testproject.utils import AdminTestCase

class TestIssue61(AdminTestCase):
    def test_the_issue(self):
        resp = self.client.get('/admin/issue_61/othermodel/')
        self.assertEqual(resp.status_code, 200)

        # the next line failed in #61
        resp = self.client.get('/admin/issue_61/othermodel/add/')
        self.assertEqual(resp.status_code, 200)
