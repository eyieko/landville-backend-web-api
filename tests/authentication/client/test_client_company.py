"""User registration tests."""
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import force_authenticate

from authentication.models import Client
from authentication.views import (ClientReviewsView, ReplyView,
                                  ReviewDetailView, UserReviewsView)
from tests.factories.authentication_factory import (ClientReviewsFactory,
                                                    ReplyReviewsFactory)
from tests.utils.utils import TestUtils


def client_review_url(client_id):
    return reverse("auth:add-reviews", args=[client_id])


def review_url(review_id):
    return reverse("auth:manage-reviews", args=[review_id])


def reply_url(pk):
    return reverse("auth:replies", args=[pk])


class ClientCompanyTest(TestUtils):
    """Contains user registration test methods."""

    @patch('utils.tasks.send_email_notification.delay')
    def test_create_client_company_with_no_data(self, mock_email):
        """
        Create a client company with empty data(object)
        """
        self.set_token()
        response = self.client.post(
            self.client_url, self.client_with_empty_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "This field is required.",
            str(response.data)
        )

    @patch('utils.tasks.send_email_notification.delay')
    def test_create_client_company_with_invalid_phone_number(self, mock_email):
        """
        Create a client company account with invalid phone number.
        """
        self.set_token()
        mock_email.return_value = True
        self.valid_client_data["phone"] = "345"
        response = self.client.post(
            self.client_url, self.valid_client_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Phone number must be of the format +234 123 4567890",
            str(response.data)
        )

    @patch('utils.tasks.send_email_notification.delay')
    def test_create_client_company_with_invalid_address(self, mock_email):
        """
        Create a client company account with invalid address.
        """
        self.set_token()
        mock_email.return_value = True
        self.valid_client_data["address"] = "address"
        response = self.client.post(
            self.client_url, self.client_with_invalid_address, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Company address should contain State, City and\
                    Street",
            str(response.data)
        )

    @patch('utils.tasks.send_email_notification.delay')
    def test_create_client_company_with_address_with_no_street(self,
                                                               mock_email):
        """
        Create a client company account with no street.
        """
        self.set_token()
        mock_email.return_value = True
        response = self.client.post(
            self.client_url, self.client_with_no_street, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Street is required in address", str(response.data))

    @patch('utils.tasks.send_email_notification.delay')
    def test_create_client_company_with_address_with_no_city(self, mock_email):
        """
        Create a client company account with no city.
        """
        self.set_token()
        mock_email.return_value = True
        response = self.client.post(
            self.client_url, self.client_with_no_city, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("City is required in address", str(response.data))

    @patch('utils.tasks.send_email_notification.delay')
    def test_create_client_company_with_address_with_no_state(self,
                                                              mock_email):
        """
        Create a client company account with no state.
        """
        self.set_token()
        mock_email.return_value = True
        response = self.client.post(
            self.client_url, self.client_with_no_state, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("State is required in address", str(response.data))

    @patch('utils.tasks.send_email_notification.delay')
    def test_create_client_company_with_address_with_invalid_state(self,
                                                                   mock_email):
        """
        Create a client company account with invalid state.
        """
        self.set_token()
        mock_email.return_value = True
        response = self.client.post(
            self.client_url, self.client_with_invalid_state, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("State must be a string", str(response.data))

    @patch('utils.tasks.send_email_notification.delay')
    def test_create_client_company_with_address_with_invalid_city(self,
                                                                  mock_email):
        """
        Create a client company account with invalid city.
        """
        self.set_token()
        mock_email.return_value = True
        response = self.client.post(
            self.client_url, self.client_with_invalid_city, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("City must be a string", str(response.data))

    @patch('utils.tasks.send_email_notification.delay')
    def test_create_client_company_with_invalid_street(self, mock_email):
        """
        Create a client company account with invalid street.
        """
        self.set_token()
        mock_email.return_value = True
        response = self.client.post(
            self.client_url, self.client_with_invalid_street, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Street must be a string", str(response.data))

    @patch('utils.tasks.send_email_notification.delay')
    def test_user_should_create_a_client_company(self, mock_email):
        """Create a client company account."""
        self.set_token()
        mock_email.return_value = True
        response = self.client.post(
            self.client_url, self.valid_client_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('utils.tasks.send_email_notification.delay')
    def test_user_should_not_create_a_second_client_company(self, mock_email):
        """
        Client admin should not create a second company account.
        """
        self.set_token()
        mock_email.return_value = True
        self.client.post(self.client_url, self.valid_client_data,
                         format="json")
        response = self.client.post(
            self.client_url, self.valid_client_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            "You cannot be admin of more than one client",
            str(response.data)
        )

    @patch('utils.tasks.send_email_notification.delay')
    def test_get_client_company_with_no_company(self, mock_email):
        """Retrieve company when no company is created"""
        self.set_token()
        mock_email.return_value = True
        response = self.client.get(
            self.client_url, format="json")
        self.assertIn("You don't have a client company created",
                      str(response.data))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('utils.tasks.send_email_notification.delay')
    def test_get_client_company(self, mock_email):
        """Get client a company account."""
        self.set_token()
        mock_email.return_value = True
        self.client.post(
            self.client_url, self.valid_client_data, format="json")
        response = self.client.get(
            self.client_url, format="json")
        self.assertIn("You have retrieved your client company",
                      str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_clients_list_unauthenticated(self):
        """Get clients when user is not authenticated."""
        response = self.client.get(
            self.clients_list_url, format="json")
        self.assertIn("Please log in to proceed.",
                      str(response.data))

    def test_get_clients_list(self):
        """Get clients when user is authenticated."""
        self.set_token()
        self.client.post(
            self.client_url, self.valid_client_data, format="json")
        response = self.client.get(
            self.clients_list_url, format="json")
        self.assertIn("You have retrieved all clients",
                      str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_empty_clients_list(self):
        """Retrieve clients list when no company is created"""
        self.set_token()
        Client.objects.all().delete()
        response = self.client.get(
            self.clients_list_url, format="json")
        self.assertIn("There are no clients at the moment.",
                      str(response.data))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('utils.tasks.send_email_notification.delay')
    def test_create_client_company_with_address_with_empty_street(self,
                                                                  mock_email):
        """
        Create a client company account with no street.
        """
        self.set_token()
        mock_email.return_value = True
        response = self.client.post(
            self.client_url, self.client_with_empty_street, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Street value can not be empty", str(response.data))

    @patch('utils.tasks.send_email_notification.delay')
    def test_create_client_company_with_address_with_empty_city(self,
                                                                mock_email):
        """
        Create a client company account with no street.
        """
        self.set_token()
        mock_email.return_value = True
        response = self.client.post(
            self.client_url, self.client_with_empty_city, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("City value can not be empty", str(response.data))

    @patch('utils.tasks.send_email_notification.delay')
    def test_create_client_company_with_address_with_empty_state(self,
                                                                 mock_email):
        """
        Create a client company account with no street.
        """
        self.set_token()
        mock_email.return_value = True
        response = self.client.post(
            self.client_url, self.client_with_empty_state, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("State value can not be empty", str(response.data))

    def test_user_can_add_a_review(self):
        """ can add a review on a client """

        view = ClientReviewsView.as_view()
        url = reverse("auth:add-reviews", args=[self.company.pk])
        response = self.factory.post(
            url, self.review_data, format="json")
        force_authenticate(response, user=self.user1)
        res = view(response, client_id=self.company1.pk)
        self.assertEqual(res.data['message'], 'Your review has been added')

    def test_CA_cannot_add_a_review(self):
        """ Client Admin cannot add a review on a client """
        view = ClientReviewsView.as_view()
        url = reverse("auth:add-reviews", args=[self.company1.pk])
        response = self.factory.post(
            url, self.review_data, format="json")
        force_authenticate(response, user=self.user2)
        res = view(response, client_id=self.company1.pk)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_add_a_review_for_unapproved_client(self):
        """ Client Admin cannot add a review on a client """
        view = ClientReviewsView.as_view()
        url = reverse("auth:add-reviews", args=[self.company.pk])
        response = self.factory.post(
            url, self.review_data, format="json")
        force_authenticate(response, user=self.user1)
        res = view(response, client_id=self.company.pk)
        self.assertEqual(res.data['errors'], 'Client not found')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_reviewer_can_get_all_reviews_on_client(self):
        """Get all reviews of a client"""

        self.set_token()
        client_id = self.company.pk
        response = self.client.get(
            client_review_url(client_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reviewer_can_get_one_review_on_client(self):
        """ get one review """

        self.set_token()
        review_id = self.review.pk
        response = self.client.get(
            review_url(review_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], review_id)

    def test_reviewer_can_delete_their_review_on_client(self):
        """ can delete their review """

        review_id = self.review.pk
        view = ReviewDetailView.as_view()
        url = reverse("auth:manage-reviews", args=[review_id])
        response = self.factory.delete(url)
        force_authenticate(response, user=self.user1)
        res = view(response, pk=review_id)
        self.assertEqual(res.data['message'], 'You have deleted this review')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_reviewer_cannot_delete_another_users_review_on_client(self):
        """ cannot delete another user's review """
        self.set_token()
        review_id = self.review.pk
        response = self.client.delete(
            review_url(review_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviewer_can_update_their_own_review(self):
        """ can only update their review """
        review = ClientReviewsFactory.create(
            reviewer=self.n_user)
        view = ReviewDetailView.as_view()
        url = reverse('auth:manage-reviews', args=[review.pk])
        response = self.factory.patch(
            url, self.update_review_data, format="json")
        force_authenticate(response, user=self.n_user)
        res = view(response, pk=review.pk)
        self.assertEqual("Successfully updated your Review",
                         res.data['message'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_reviewer_cannot_update_other_users_review(self):
        """ cannot  update a review made by another user """
        self.set_token()
        review_id = self.review.pk
        response = self.client.put(
            review_url(review_id), self.update_review_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_reply_a_review(self):
        """ can reply to a review """
        self.set_token()
        review_id = self.review.pk
        url = reply_url(review_id)
        response = self.client.post(url, self.reply_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Your reply has been added", str(response.data))

    def test_reviewer_can_delete_their_reply_on_review(self):
        """ can delete a reply """
        reply = ReplyReviewsFactory.create(
            reviewer=self.n_user, review=self.review)
        view = ReplyView.as_view()
        url = reverse('auth:replies', args=[reply.pk])
        response = self.factory.delete(url)
        force_authenticate(response, user=self.n_user)
        res = view(response, pk=reply.pk)

        self.assertEqual("You have deleted this reply", res.data['message'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_cannot_add_reply_to_non_existent_review(self):
        """ cannot reply to a review that does not exist """
        self.set_token()
        review_id = self.review_1.pk
        url = reply_url(review_id)
        response = self.client.post(url, self.reply_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Review does not exist", str(response.data['errors']))

    def test_reply_does_not_exist_for_deleted_a_reply(self):
        """ can delete a reply """

        view = ReplyView.as_view()
        url = reverse('auth:replies', args=[self.reply_1.pk])
        response = self.factory.delete(url)
        force_authenticate(response, user=self.n_user)
        res = view(response, pk=self.reply_1.pk)
        self.assertEqual("Reply does not exist", res.data['errors'])
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_reviewer_cannot_delete_another_users_reply_on_review(self):
        """ cannot delete another user's reply """
        self.set_token()
        reply_id = self.reply.pk
        response = self.client.delete(
            reply_url(reply_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviewer_can_update_their_reply_on_review(self):
        """ can update a reply """
        reply = ReplyReviewsFactory.create(
            reviewer=self.n_user, review=self.review)
        view = ReplyView.as_view()
        url = reverse('auth:replies', args=[reply.pk])
        response = self.factory.put(url, self.reply_data, format="json")
        force_authenticate(response, user=self.n_user)
        res = view(response, pk=reply.pk)
        self.assertEqual("Successfully updated your reply",
                         res.data['message'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_reviewer_cannot_update_another_users_reply_on_review(self):
        """ cannot update another user's reply """
        self.set_token()
        reply_id = self.reply.pk
        response = self.client.put(
            reply_url(reply_id), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleted_reply_cannot_be_updated(self):
        """ can delete a reply """

        view = ReplyView.as_view()
        url = reverse('auth:replies', args=[self.reply_1.pk])
        response = self.factory.put(url)
        force_authenticate(response, user=self.n_user)
        res = view(response, pk=self.reply_1.pk)
        self.assertEqual("Reply does not exist", res.data['errors'])
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_get_all_reviews_made_by_a_user(self):
        """user can get all their reviews"""

        reviewer_id = self.review.reviewer_id
        view = UserReviewsView.as_view()
        url = reverse('auth:user-reviews', args=[reviewer_id])
        response = self.factory.get(url)
        force_authenticate(response, user=self.user1)
        res = view(response, reviewer_id=reviewer_id)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_cannot_get_deleted_reviews(self):
        """ user cannot get reviews that have been deleted """

        client_id = self.company1.pk
        view = ClientReviewsView.as_view()
        url = reverse('auth:add-reviews', args=[client_id])
        response = self.factory.get(url)
        force_authenticate(response, user=self.user1)
        res = view(response, client_id=client_id)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
