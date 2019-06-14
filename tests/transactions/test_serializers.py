from tests.transactions import BaseTest
from transactions.views import ClientAccountAPIView
from rest_framework import status
from django.urls import reverse
from rest_framework.test import force_authenticate

ACCOUNT_DETAIL_URL = reverse("transactions:all-accounts")


def single_detail_url(account_number):
    return reverse("transactions:single-account", args=[account_number])


class TestSerializers(BaseTest):
    def test_error_when_you_post_with_invalid_account_number(self):
        """ you get an error when you upload with an a non interger acc number """

        view = ClientAccountAPIView.as_view()

        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.invalid_details, format='json')
        force_authenticate(request, user=self.user1,
                           token=None)
        resp = view(request)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'Your account number must be 10 digits and only intergers', str(resp.data))

    def test_error_when_you_post_with_invalid_swift_code(self):
        """ you get an error when you upload with an a non letter swift code """

        view = ClientAccountAPIView.as_view()

        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.invalid_swift_code, format='json')
        force_authenticate(request, user=self.user1,
                           token=None)
        resp = view(request)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'Swift code must only be letters characters', str(resp.data))
