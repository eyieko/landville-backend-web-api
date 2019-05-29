
from tests.transactions import BaseTest
from transactions.views import ClientAccountAPIView
from django.urls import reverse
from rest_framework.test import force_authenticate
from rest_framework.views import status
import json


ACCOUNT_DETAIL_URL = reverse("transactions:all-accounts")


def single_detail_url(account_number):
    return reverse("transactions:single-account", args=[account_number])


class TestClientAccountDetailsViews(BaseTest):

    def test_user_must_have_client_to_post_account_details(self):
        view = ClientAccountAPIView.as_view()
        self.user3.role = 'CA'
        self.user3.save()
        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.acc_details3, format='json')
        force_authenticate(request, user=self.user3)
        res = view(request)
        self.assertIn(
            'you must have a client company to submit account details', str(res.data))

    def test_staff_can_get_even_deleted_account_details(self):
        """ a staff can get even deleted items """
        view = ClientAccountAPIView.as_view()
        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)
        res = view(request)
        account_number = res.data['account_number']
        request2 = self.factory.delete(
            single_detail_url(account_number), format='json')
        request3 = self.factory.get(
            single_detail_url(account_number), format='json')
        self.user2.role = 'LA'
        self.user2.save()
        force_authenticate(request3, user=self.user2)

        res = self.view2(request3, account_number=account_number)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_view_all_details_successfully(self):
        """ client admin view all the details successfully """

        view = ClientAccountAPIView.as_view()
        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)
        resp = view(request)

        request2 = self.factory.get(ACCOUNT_DETAIL_URL)
        self.user1.role = 'CA'
        self.user1.save()
        force_authenticate(request2, user=self.user1)
        resp2 = view(request2)

        self.assertEqual(resp2.status_code, status.HTTP_200_OK)

    def test_staff_gets_the_correct_message_no_details_posted(self):
        """ staff should be able to get the right details when no details are posted"""

        view = ClientAccountAPIView.as_view()
        request = self.factory.get(ACCOUNT_DETAIL_URL)
        self.user3.role = 'LA'
        self.user3.save()
        force_authenticate(request, user=self.user3)
        resp = view(request)
        self.assertIn(
            'There are no details posted by any client so far', str(resp.data))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_success_details_uploaded(self):
        """ test successfully upload your account details """

        view = ClientAccountAPIView.as_view()

        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1,
                           token=None)
        resp = view(request)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_client_admin_gets_the_appropriate_message_no_records_posted(self):
        """ client admin can be able to only view the accounts """
        view = ClientAccountAPIView.as_view()

        request2 = self.factory.get(
            ACCOUNT_DETAIL_URL, format='json')
        force_authenticate(request2, user=self.user1)

        res = view(request2)
        self.assertIn("You have no account details posted", str(res.data))

    def test_get_one_account(self):
        """ test when viewing one specific account """
        view = ClientAccountAPIView.as_view()

        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)
        actual_res = view(request)
        account_number = actual_res.data['account_number']

        request2 = self.factory.get(
            single_detail_url(account_number), format='json')
        force_authenticate(request2, user=self.user4)

        res = self.view2(request2, account_number=account_number)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_not_existing_account_details(self):
        """ test for account details not found """
        view = ClientAccountAPIView.as_view()

        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)
        actual_res = view(request)
        account_number = 'djsdjshdsjdhskddkjwfsjkdfeghfjkas'

        request2 = self.factory.get(
            single_detail_url(account_number), format='json')
        force_authenticate(request2, user=self.user1)

        res = self.view2(request2, account_number=account_number)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_account_details(self):
        """ test for deleting account details """
        view = ClientAccountAPIView.as_view()

        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)
        actual_res = view(request)
        account_number = actual_res.data['account_number']

        request2 = self.factory.delete(
            single_detail_url(account_number), format='json')
        force_authenticate(request2, user=self.user1)

        res = self.view2(request2, account_number=account_number)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn('Account details successfully deleted', str(res.data))

    def test_delete_account_details_non_existent(self):
        """ test that non existent details won't be found while deleting """

        account_number = 'shdskdhsdhsdjsdkashdksjdhkddj'

        request2 = self.factory.delete(
            single_detail_url(account_number), format='json')
        force_authenticate(request2, user=self.user1)

        res = self.view2(request2, account_number=account_number)

        self.assertIn(
            'Not found',
            str(res.data))

    def test_update_account_details(self):
        """ test account details updated successfully """

        view = ClientAccountAPIView.as_view()

        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)
        actual_res = view(request)
        account_number = actual_res.data['account_number']

        request2 = self.factory.put(
            single_detail_url(account_number), self.account_details,
            format='json')
        force_authenticate(request2, user=self.user1)

        res = self.view2(request2, account_number=account_number)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_account_details_not_found(self):
        """ account details that cannot be found can't be updated """

        account_number = 'ksjdksjdksjdksjdksjdsdsdsjdsjsdjk'

        request2 = self.factory.put(
            single_detail_url(account_number), self.account_details2,
            format='json')
        force_authenticate(request2, user=self.user1)

        res = self.view2(request2, account_number=account_number)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_details_no_permission(self):
        """you can't post without the correct credentialsi.e without login """

        res = self.client.post(ACCOUNT_DETAIL_URL,
                               self.account_details, format='json')

        result = json.loads(res.content)
        self.assertIn(
            'Authentication credentials were not provided.', str(result))

    def test_account_number_must_be_unique(self):
        """ test that an account shoudl be unique """

        view = ClientAccountAPIView.as_view()
        request = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request, user=self.user1)

        actual_res = view(request)

        request2 = self.factory.post(
            ACCOUNT_DETAIL_URL, self.account_details, format='json')
        force_authenticate(request2, user=self.user1)

        actual_response = view(request2)

        self.assertEqual(actual_response.status_code,
                         status.HTTP_400_BAD_REQUEST)
