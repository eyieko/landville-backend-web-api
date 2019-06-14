from django.test import TestCase
from transactions.renderer import AccountDetailsJSONRenderer


class PropertyJSONRendererTest(TestCase):
    """all the unittest for PropertyJSONRenderer """

    def setUp(self):
        self.renderer = AccountDetailsJSONRenderer()

    def test_that_account_details_are_rendered_properly(self):
        """test that account details are rendered correctly"""

        account_details = {"account_number": "2324342342323242"}
        rendered_data = self.renderer.render(account_details)

        expected_data = '{"data": {"account_detail(s)": {"account_number": "2324342342323242"}}}'
        self.assertEqual(rendered_data, expected_data)

    def test_that_errors_are_rendered_as_expected(self):
        """Test that errors are rendered correctly"""

        error_dict = {"errors": "this are errors"
                      }
        rendered_data = self.renderer.render(error_dict)

        expected_data = b'{"errors":"this are errors"}'
        self.assertEqual(rendered_data, expected_data)

    def test_data_as_list_is_rendered_correctly(self):
        """test that data in  a list is rendered correctly"""
        data_in_list_format = ["this", "might", "get", "a", "list"]
        rendered_data = self.renderer.render(data_in_list_format)

        expected_data = '{"data": {"account_detail(s)": ["this", "might", "get", "a", "list"]}}'
        self.assertEqual(rendered_data, expected_data)
