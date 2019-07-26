from unittest.mock import patch

from authentication.models import User
from tests.authentication.client.test_base import BaseTest


class TestUtils(BaseTest):

    @patch('utils.tasks.send_email_notification.delay')
    def set_token(self, mock_email):
        """
        Set a jwt token in Authorization headers during testing
        """
        mock_email.return_value = True
        user_data = self.client.post(
            self.registration_url, self.new_user, format="json")
        user = User.objects.filter(email=user_data.data['data']['user']['email']).first()
        user.is_verified=True
        user.save()
        response = self.client.post(self.login_url, self.new_user,format="json")
        token = response.data['data']['user']['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
