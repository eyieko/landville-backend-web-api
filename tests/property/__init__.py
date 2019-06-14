import json

from django.urls import reverse
from django.conf import settings
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from tests.factories.authentication_factory import UserFactory, ClientFactory
from tests.factories.property_factory import (
    PropertyFactory, PropertyEnquiryFactory, PropertyInspectionFactory,
    PropertyReviewFactory, BuyerPropertyListFactory)

from property.renderers import (
    PropertyJSONRenderer, PropertyEnquiryJSONRenderer)


class BaseTest(APITestCase):
    """Base test for all property tests"""

    def setUp(self):
        self.user1 = UserFactory.create()
        self.user2 = UserFactory.create()
        self.buyer1 = UserFactory.create(role='BY')

        self.admin = UserFactory.create(is_staff=True, role='LA')
        self.user3 = UserFactory.create()
        self.user3.role = 'BY'
        self.user3.save()

        self.client1 = ClientFactory.create(
            client_admin=self.user1, approval_status='approved')
        self.client2 = ClientFactory.create(client_admin=self.user2)

        self.property1 = PropertyFactory.create(client=self.client1)
        self.property1.soft_delete()
        self.property11 = PropertyFactory.create(client=self.client1)
        self.review1 = PropertyReviewFactory(
            reviewer=self.user1, target_property=self.property1)
        self.enquiry1 = PropertyEnquiryFactory(enquiry_id='this enquiry',
                                               requester=self.buyer1,
                                               target_property=self.property1)
        self.inspection1 = PropertyInspectionFactory(
            requester=self.user1, target_property=self.property1)

        self.property2 = PropertyFactory.create(
            client=self.client2, title='HardCoded Title Block',
            is_published=True)

        self.property4 = PropertyFactory.create(
            client=self.client2,
            title='HardCoded Title Block',
            is_published=True)
        self.property3 = PropertyFactory.create(client=self.client2)
        self.property_no_images = PropertyFactory.create(
            client=self.client2, image_others=[], video=None)

        self.property3 = PropertyFactory.create(client=self.client2)
        self.buyerpropertylist = BuyerPropertyListFactory.create(
            buyer=self.buyer1, listed_property=self.property2)
        self.property_data = {
            "title": self.property2.title,
            "address": json.dumps(self.property2.address),
            "coordinates": json.dumps(self.property2.coordinates),
            "client": self.client1.pk,
            "description": self.property2.description,
            "price": self.property2.price,
            "lot_size": self.property2.lot_size,
            "image_main": self.property2.image_main,
            "purchase_plan": self.property2.purchase_plan
        }
        self.property5 = PropertyFactory.create(client=self.client2,
                                                address={"City": "Lagos",
                                                         "State":
                                                         "Greater Lagos",
                                                         "Street":
                                                         "Lagos St"},
                                                view_count=4,
                                                is_published=True)

        self.property6 = PropertyFactory.create(client=self.client2,
                                                address={"City": "Lagos",
                                                         "State":
                                                         "Greater Lagos",
                                                         "Street":
                                                         "Lagos St"},
                                                view_count=10,
                                                is_published=True)

        self.enquiry_data = {
            "enquiry_id": "we-love-landville-we-love-landville",
            "visit_date": "2030-09-03T00:00:00.000Z",
            "message": "I love this propery"
        }

        self.enquiry_data_update = {

            "enquiry_id": "we-love-landville-we-love-landville",
            "visit_date": "2030-09-03T00:00:00.000Z",
            "message": "We are from Landville"

        }

        self.enquiry_with_past_date = {

            "enquiry_id": "we-love-landville-we-love-landville",
            "visit_date": "1990-09-03T00:00:00.000Z",
            "message": "We are from Landville"

        }

        self.enquiry_renderer = PropertyEnquiryJSONRenderer()

        self.factory = APIRequestFactory()

        self.create_list_url = reverse('property:create_and_list_property')
        self.get_buyer_list_url = reverse('property:get_buyer_list')

        self.property_update = {
            "price": 99999999.99, "bathrooms": 3, "garages": 4,
            "title": "Updated Super Lot", "image_others": [
                "http://www.example.com", "http://wwww.dopest.house"]
        }

        self.invalid_address_update = {
            "City": "", "State": "TestVille", "Street": "Tee Street"}
        self.property_renderer = PropertyJSONRenderer()

        self.serialized_property_sample = (
            '{"data": {"properties": {"results":[{"price": 999999.99,'
            '"lot_size": 342.43, "address": {"City": "Lagos", "State":'
            '"Greater Lagos", "Street": "Lagos St"},'
            '"coordinates": {"lat": 1234234.43, "lon": 324534554.45},'
            '"title": "Test Property",'
            '"description": "This is a dummy propery. Duh",'
            '"bedrooms": null, "bathrooms": null, "garages": null,'
            '"image_main": "https://www.dope.image/main",'
            '"purchase_plan": "I", "client": 1}]}}}')

        self.cloudinary_image_url1, self.cloudinary_image_url2 = [
            f'http://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/v1560508753/s3nitpim2sxydceg8zjy.jpg',  # noqa
            f'http://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/v1560508754/or4ocyg1jsn7n0omyywz.jpg']  # noqa

        self.cloudinary_video_url1, self.cloudinary_video_url2 = [
            f'http://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/video/upload/v1560508758/tlnth1foqciqdbdginmp.mp4',  # noqa
            f'http://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/video/upload/v1560508758/tlnthytoqciqdbdginmp.mp4']  # noqa
