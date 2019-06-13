from collections import OrderedDict

from tests.property import BaseTest
from property.serializers import PropertySerializer


class PropertyJSONRendererTest(BaseTest):
    """Define unit tests for the PropertyJSONRenderer"""

    def test_that_renderer_properly_renders_property_dictionary_data(self):

        serializer = PropertySerializer(
            data=self.property_data)
        serializer.is_valid()
        payload = serializer.data
        payload['id'] = self.property2.pk
        response = {"data": {"property": payload}}
        rendered_property = self.property_renderer.render(response)
        self.assertIn("property", rendered_property)
        # the fields with choices are rendered with human-readable values
        self.assertIn("Building", rendered_property)

    def test_that_errors_are_rendered_as_expected(self):
        dict_data = {"errors": "This error should be properly rendered"
                     }
        rendered_data = self.property_renderer.render(dict_data)

        expected_data = b'{"errors":"This error should be properly rendered"}'
        self.assertEqual(rendered_data, expected_data)

    def test_that_data_of_list_types_are_rendered_as_expected(self):
        dummy_data = self.property_data
        dummy_data['address'] = self.property2.address
        dummy_data['coordinates'] = self.property2.coordinates
        serializer = PropertySerializer(
            data=dummy_data)
        serializer.is_valid()
        data = serializer.data
        data['id'] = self.property2.pk
        # The renderer expects serialized data that is an ordered dictionary
        ordered = OrderedDict(data)
        list_data = [ordered]
        payload = OrderedDict({'results': list_data})
        rendered_data = self.property_renderer.render(payload)
        self.assertIn("properties", rendered_data)
        # choices are properly rendered as human-readable values
        self.assertIn("Installments", rendered_data)
