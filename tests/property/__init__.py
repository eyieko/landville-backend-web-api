from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from tests.factories.authentication_factory import UserFactory, ClientFactory
from tests.factories.property_factory import (
    PropertyFactory, PropertyEnquiryFactory, PropertyInspectionFactory,
    PropertyReviewFactory, BuyerPropertyListFactory)
from property.renderers import PropertyJSONRenderer


class BaseTest(TestCase):
    """Base test for all property tests"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.user1.role = 'CA'
        self.user1.save()
        self.user2 = UserFactory.create()
        self.buyer1 = UserFactory.create(role='BY')

        self.admin = UserFactory.create()
        self.admin.is_staff = True
        self.admin.role = 'LA'
        self.admin.save()

        self.client1 = ClientFactory.create(
            client_admin=self.user1, approval_status='approved')
        self.client2 = ClientFactory.create(client_admin=self.user2)

        self.property1 = PropertyFactory.create(client=self.client1)
        self.property1.soft_delete()
        self.property11 = PropertyFactory.create(client=self.client1)
        self.review1 = PropertyReviewFactory(
            reviewer=self.user1, target_property=self.property1)
        self.enquiry1 = PropertyEnquiryFactory(
            enquirer_name='Liz Kiherehere', target_property=self.property1)
        self.inspection1 = PropertyInspectionFactory(
            requester=self.user1, target_property=self.property1)

        self.property2 = PropertyFactory.create(
            client=self.client2, title='HardCoded Title Block')
        self.property2.is_published = True
        self.property2.save()

        self.property4 = PropertyFactory.create(
            client=self.client2,
            title='HardCoded Title Block',
            is_published=True)

        self.property3 = PropertyFactory.create(client=self.client2)
        self.buyerpropertylist = BuyerPropertyListFactory.create(
            buyer=self.buyer1, listed_property=self.property2)
        self.property_data = {
            "title": "Test Property",
            "address": {"City": "Lagos",
                        "State": "Greater Lagos", "Street": "Lagos St"},
            "coordinates": {"lat": 1234234.43, "lon": 324534554.45},
            "client": self.client1.pk,
            "description": "This is a dummy propery. Duh",
            "price": 999999.99,
            "lot_size": 342.43,
            "image_main": "https://www.dope.image/main",
            "purchase_plan": "I"
        }

        self.factory = APIRequestFactory()

        self.create_list_url = reverse('property:create_and_list_property')
        self.get_buyer_list_url = reverse('property:get_buyer_list')

        self.property_update = {
            "price": 99999999.99, "bathrooms": 3, "garages": 4,
            "title": "Updated Super Lot",
            "image_others":
            ["http://www.example.com", "http://wwww.dopest.house"]
        }

        self.invalid_address_update = {
            "address": {
                "City": "", "State": "TestVille",
                "Street": "Tee Street"},
        }

        self.property_renderer = PropertyJSONRenderer()

        self.serialized_property_sample = '{ "data":{"properties": {"results": [{"price": 999999.99, "lot_size": 342.43, "address": {"City": "Lagos", "State": "Greater Lagos", "Street": "Lagos St"}, "coordinates": {"lat": 1234234.43, "lon": 324534554.45}, "title": "Test Property", "description": "This is a dummy propery. Duh", "bedrooms": null, "bathrooms": null, "garages": null, "image_main": "https://www.dope.image/main", "purchase_plan": "I", "client": 1}]}}}'  # noqa
