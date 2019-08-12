from tests.pages.test_base import TermsTestBase
from rest_framework import status


class TestViews(TermsTestBase):
    def test_user_view_terms(self):
        response = self.client.get(self.terms_url, format="json")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIn("last_updated_at", str(response.data))
