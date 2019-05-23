from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegistrationSerializer
from rest_framework.response import Response
from rest_framework import status
from .renderer import UserJSONRenderer
from .email_helper import EmailHelper
import jwt
from django.conf import settings
from .models import User


class RegistrationAPIView(generics.GenericAPIView):
    """Register new users."""

    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        message = [
            request,
            user_data["email"]
        ]
        EmailHelper.send_verification_email(message)
        response = {
            "data": {
                "user": dict(user_data),
                "message": "Account created successfully,please check your mailbox to activate your account ",
                "status": "success"
            }
        }
        return Response(response, status=status.HTTP_201_CREATED)


class EmailVerificationView(generics.GenericAPIView):
    """Verify the users email."""

    def get(self, request):
        token, user = request.GET.get("token").split("~")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.exceptions.DecodeError:
            return self.sendResponse("verification link is invalid")

        except jwt.ExpiredSignatureError:
            EmailHelper.send_verification_email([request], user_id=user)
            message = "verification link is expired, we have sent you a new one."
            return self.sendResponse(message, 200)
        user = User.objects.filter(email=payload.get("email")).first()
        if user.is_verified:
            return self.sendResponse("Account is already activated", 200)
        user.is_verified = True
        user.save()
        return self.sendResponse("Email has been verified", status.HTTP_200_OK)

    def sendResponse(self, message, status=status.HTTP_400_BAD_REQUEST):
        return Response({"message": message}, status)
