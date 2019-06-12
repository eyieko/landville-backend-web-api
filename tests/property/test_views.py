from django.urls import reverse
from rest_framework import status
from rest_framework.test import force_authenticate

from tests.property import BaseTest
from tests.factories.authentication_factory import UserFactory, ClientFactory
from property.views import CreateAndListPropertyView, PropertyDetailView
from tests.factories.property_factory import PropertyFactory


class PropertyViewTests(BaseTest):
    """This class defines tests for the different property views"""

    def test_that_client_admins_can_create_property(self):
        """Admin Clients should be able to create property if
        they provide correct information """

        post_request = self.factory.post(
            self.create_list_url, self.property_data, format='json')
        force_authenticate(post_request, user=self.user1)
        view = CreateAndListPropertyView.as_view()
        response = view(post_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data.get('address'), {
                'City': 'Lagos', 'State': 'Greater Lagos', 'Street': 'Lagos St'
            }
        )

    def test_that_users_who_are_not_client_admins_cannot_create_property(self):
        """Only client admins should be able to create property"""

        self.user1.role = 'BY'

        request = self.factory.post(
            self.create_list_url, self.property_data, format='json')
        force_authenticate(request, user=self.user1)
        view = CreateAndListPropertyView.as_view()
        response = view(request, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_that_users_who_are_not_logged_in_cannot_create_property(self):
        """Only client admins should be able to create property"""

        request = self.factory.post(
            self.create_list_url, self.property_data, format='json')
        view = CreateAndListPropertyView.as_view()
        response = view(request, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_that_client_admins_can_view_all_their_undeleted_property(self):
        """Client admins should see all their property that is not deleted,
        regardless of whether the property is published or not """

        request = self.factory.get(
            self.create_list_url)
        force_authenticate(request, user=self.user1)
        view = CreateAndListPropertyView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 2)
        self.assertFalse(response.data.get('results')[0].get(
            'is_published') and response.data.get('results')[1].get('is_published'))

    def test_that_buyers_can_see_only_published_properties_that_are_not_deleted(self):
        """Buyers should only be able to see property that is published and not deleted"""
        buyer = UserFactory.create()

        request = self.factory.get(
            self.create_list_url)
        force_authenticate(request, user=buyer)
        view = CreateAndListPropertyView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # only one property is published and not deleted
        self.assertEqual(len(response.data.get('results')), 1)
        self.assertEqual(response.data.get('results')[0].get(
            'title'), 'HardCoded Title Block')

    def test_that_admins_can_view_all_property(self):
        """Admins should be able to see all property regardless of whether it is published or soft deleted"""

        request = self.factory.get(
            self.create_list_url)
        self.user1.role = 'LA'
        self.user1.save()
        force_authenticate(request, user=self.user1)
        view = CreateAndListPropertyView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        # admin can view unpublished property
        self.assertFalse(response.data.get('results')[3].get('is_published'))

    def test_that_only_client_admins_can_create_property(self):
        """Only client admins who currently have client companies can create property"""

        non_client_admin = UserFactory.create()

        post_request = self.factory.post(
            self.create_list_url, self.property_data, format='json')
        force_authenticate(post_request, user=non_client_admin)
        view = CreateAndListPropertyView.as_view()
        response = view(post_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_that_client_admins_can_view_a_specific_unpublished_property_that_they_own(self):
        """Client admins should be able to view a specific property
        they own regardless of whether it is published or not.
        They cannot view property that is deleted, however """

        # self.property1 is not published
        url = reverse('property:single_property', args=[self.property11.slug])
        request = self.factory.get(url)
        force_authenticate(request, user=self.user1)
        view = PropertyDetailView.as_view()
        response = view(request, slug=self.property11.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data.get('is_published'))

    def test_that_client_admins_can_update_their_property(self):
        """Client admins should be able to update their property"""

        url = reverse('property:single_property', args=[self.property11.slug])
        request = self.factory.patch(
            url, self.property_update, format='json'
        )
        force_authenticate(request, user=self.user1)
        view = PropertyDetailView.as_view()
        response = view(
            request, slug=self.property11.slug, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('price'), 99999999.99)
        self.assertEqual(response.data.get('title'), 'Updated Super Lot')

    def test_client_admin_cannot_view_property_that_is_not_published(self):
        """A client admin should not be able to view property belonging to different
        clients if the property is not published"""

        url = reverse('property:single_property', args=[self.property11.slug])

        request = self.factory.get(url)
        force_authenticate(request, user=self.user2)
        view = PropertyDetailView.as_view()
        response = view(request, slug=self.property11.slug)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_client_admins_cannot_update_property_belonging_to_other_clients(self):
        """Client admins shouldn't be able to update property belonging to different companies"""

        view = PropertyDetailView.as_view()

        url = reverse('property:single_property', args=[self.property2.slug])

        request = self.factory.patch(url, self.property_update, format='json')

        response2 = view(
            request, slug=self.property2.slug, format='json'
        )
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

        # if they try to view the published property, they surely can
        get_request = self.factory.get(url)
        force_authenticate(get_request, user=self.user2)
        response3 = view(
            get_request, slug=self.property2.slug
        )
        self.assertEqual(response3.status_code, status.HTTP_200_OK)

    def test_that_landville_staff_can_view_all_property(self):
        """LandVille staff should be able to view all property regardless of any parameters"""

        view = PropertyDetailView.as_view()

        url = reverse('property:single_property', args=[self.property1.slug])
        request = self.factory.get(url)
        force_authenticate(request, user=self.admin)
        response = view(request, slug=self.property1.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_that_client_admin_can_delete_their_property(self):
        """Client admins should be able to delete their property"""

        view = PropertyDetailView.as_view()

        url = reverse('property:single_property', args=[self.property11.slug])
        request = self.factory.delete(url)
        force_authenticate(request, user=self.user1)
        response = view(request, slug=self.property11.slug)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_that_client_admins_need_to_have_client_before_they_can_create_property(self):
        """Client admins should have the role `CA` and they should also have an employer
        before they can create property """

        post_request = self.factory.post(
            self.create_list_url, self.property_data, format='json')

        # this user has role `CA` but has no employer relationship
        fake_client = UserFactory.create()
        fake_client.role = 'CA'
        fake_client.save()
        force_authenticate(post_request, user=fake_client)
        view = CreateAndListPropertyView.as_view()
        response = view(post_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_that_landville_staff_can_update_property(self):
        """LandVille staff should be able to update the details of a property"""

        url = reverse('property:single_property', args=[self.property11.slug])
        request = self.factory.patch(
            url, self.property_update, format='json'
        )
        force_authenticate(request, user=self.admin)
        view = PropertyDetailView.as_view()
        response = view(
            request, slug=self.property11.slug, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('price'), 99999999.99)
        self.assertEqual(response.data.get('title'), 'Updated Super Lot')

    def test_that_landville_staff_cannot_delete_property_that_is_already_deleted(self):
        """Because LandVille staff can view property that is already deleted, they should not be
        able to delete that property again. """

        view = PropertyDetailView.as_view()

        # property1 is already soft deleted
        url = reverse('property:single_property', args=[self.property1.slug])
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        response = view(request, slug=self.property1.slug)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('errors'),
                         'Not allowed! This property is already deleted.')

    def test_users_should_pass_valid_address_values(self):
        """Users should not be able to send invalid addresses like numbers and empty strings"""

        url = reverse('property:single_property', args=[self.property11.slug])
        request = self.factory.patch(
            url, self.invalid_address_update, format='json'
        )
        force_authenticate(request, user=self.user1)
        view = PropertyDetailView.as_view()
        response = view(
            request, slug=self.property11.slug, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data.get('errors').get('address')[0]),
                         'City cannot be empty!')
