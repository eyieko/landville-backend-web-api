"""Saved cards tests."""
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import force_authenticate


from tests.utils.utils import TestUtils
from authentication.models import CardInfo
from transactions.views import (DeleteSavedCardView, SavedCardsListView)
from tests.factories.authentication_factory import (CardInfoFactory)


class SavedCardsTest(TestUtils):
    """Contains saved cards test methods."""

    def test_get_all_saved_cards(self):
        """Get all saved cards"""

        view = SavedCardsListView.as_view()
        response = self.factory.get(self.saved_card_url)
        force_authenticate(response, user=self.user)
        res = view(response)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_when_no_saved_card(self):
        """Retrieve when no saved cards"""

        self.set_token()
        response = self.client.get(
            self.saved_card_url, format="json")
        self.assertIn("You don't have any card saved",
                      str(response.data))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_delete_their_saved_card(self):
        """ can delete their saved card """

        view = DeleteSavedCardView.as_view()
        url = reverse("transactions:saved-card", args=[self.saved_card.id])
        response = self.factory.delete(url)
        force_authenticate(response, user=self.user)
        res = view(response, id=self.saved_card.id)

        self.assertEqual('Card Deleted Successfully', res.data['message'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    @patch('transactions.transaction_services.CardInfo.active_objects.all_objects')
    def test_cannot_delete_others_saved_card(self, mock_filter):
        """ can delete others saved card """

        mock_filter.side_effect = CardInfo.DoesNotExist

        view = DeleteSavedCardView.as_view()
        url = reverse("transactions:saved-card", args=[self.saved_card2.id])
        response = self.factory.delete(url)
        force_authenticate(response, user=self.user)
        resp = view(response, id=self.saved_card2.id)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
