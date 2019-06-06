from tests.authentication.client.test_base import BaseTest
from authentication.models import User

class TestUtils(BaseTest):
    
    def set_token(self):
        """
        Set a jwt token in Authorization headers during testing
        """
        user_data = self.client.post(
            self.registration_url, self.new_user, format="json")
        user = User.objects.filter(email=user_data.data['data']['user']['email']).first()
        user.is_verified=True
        user.save()
        response = self.client.post(self.login_url, self.new_user,format="json")
        token = response.data['data']['user']['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
