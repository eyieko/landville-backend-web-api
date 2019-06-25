from django.test import TestCase, Client, override_settings
from django.urls import reverse
from tests.factories.authentication_factory import ClientFactory, UserFactory
from rest_framework import status
from authentication.views import AddReasonView
from rest_framework.test import APIRequestFactory, force_authenticate

class ApprovalStatusChangeTest(TestCase):
    """Contains test methods for changing client company approval status."""

    def setUp(self):
        """Add variables needed for every test."""
        self.approvals_url = reverse("auth:add-notes")
        self.user = UserFactory(role="CA", email="test@gmail.com")
        self.client1 = ClientFactory(client_admin=self.user)

    def test_submit_notes_with_revoked_message_redirect(self):
        """Test user is redirected after when they revoke an approval."""
        res = self.client.post(self.approvals_url, {
            "notes": 'notes is here', "client": 'test@gmail.com',
            "status": 'revoked',
        }, format="text/html")
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_submit_notes_with_reject_message_redirect(self):
        """Test user is redirected after when they reject an approval."""
        res = self.client.post(self.approvals_url, {
            "notes": 'notes is here', "client": 'test@gmail.com',
            "status": 'rejected',
        }, format="text/html")
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)


    def test_AddReasonView_status_code(self):
        self.factory = APIRequestFactory()
        url = self.approvals_url+'?client=2&status=approved'
        res = self.factory.get(url)
        force_authenticate(res, self.user)
        view = AddReasonView.as_view()
        response = view(res)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
