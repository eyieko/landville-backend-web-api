"""This module handles tests for exception handling"""
from tests.property import BaseTest
from utils import views, exception_handler


class TestErrorHandler(BaseTest):

    """This class will test custom handling of exceptions"""

    def test_500_page(self):
        """test for internal server error """
        response = self.client.get('/')
        error_response = views.error_500(response)
        self.assertEqual(error_response.status_code, 500)

    def test_none_response_from_server(self):
        """test for server returning none"""
        error_response = exception_handler.custom_exception_handler(None, None)
        self.assertEqual(error_response, None)
