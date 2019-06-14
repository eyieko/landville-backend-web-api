from tests.property import BaseTest
from property.serializers import PropertySerializer
from property.models import Property


class PropertyJSONRendererTest(BaseTest):
    """Define unit tests for the PropertyJSONRenderer"""

    def test_that_renderer_properly_renders_property_dictionary_data(self):

        serializer = PropertySerializer(
            data=self.property_data)
        serializer.is_valid()
        rendered_property = self.property_renderer.render(serializer.data)
        self.assertIn("property", rendered_property)

    def test_that_users_see_readable_values_for_fields_with_choices(self):
        """Users should see human readable values for fields that have choices"""

        serializer = PropertySerializer(
            data=self.property_data)
        serializer.is_valid()
        listing = Property.objects.filter(
            client_id=serializer.data.get('client')).first()
        data = serializer.data
        # we need to pass the `id` to simulate a response from the database
        data['id'] = listing.pk
        rendered_property = self.property_renderer.render(data)
        self.assertIn("Building", rendered_property)
        self.assertIn("Installments", rendered_property)

    def test_that_users_see_readable_values_for_fields_with_choices_in_lists(self):
        """Users should see human readable values for fields that have choices"""

        listings = Property.objects.all()

        serializer = PropertySerializer(
            data=list(listings), many=True)
        serializer.is_valid()

        data = {"results": serializer.data}

        rendered_property = self.property_renderer.render(data)
        self.assertIn("property", rendered_property)

    def test_that_errors_are_rendered_as_expected(self):
        dict_data = {"errors": "This error should be properly rendered"
                     }
        rendered_data = self.property_renderer.render(dict_data)

        expected_data = b'{"errors":"This error should be properly rendered"}'
        self.assertEqual(rendered_data, expected_data)

    def test_that_data_of_list_types_are_rendered_as_expected(self):
        serializer = PropertySerializer(
            data=self.property_data)
        serializer.is_valid()
        data = serializer.data
        data['client'] = 1
        list_data = [data]
        data = {'results': list_data}
        rendered_data = self.property_renderer.render(data)
        self.assertIn("properties", rendered_data)
