import jwt
from utils import BaseUtils
from authentication.renderer import UserJSONRenderer
from rest_framework.views import APIView
from authentication.serializers import (
    GoogleAuthSerializer, FacebookAuthAPISerializer, PasswordResetSerializer,
    TwitterAuthAPISerializer, RegistrationSerializer, LoginSerializer,
    ClientSerializer, ChangePasswordSerializer,
    ProfileSerializer,)
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from authentication.email_helper import EmailHelper
from django.conf import settings
from authentication.models import User, Client, UserProfile
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from property.validators import validate_image
from authentication.permissions import IsProfileOwner, IsClientAdmin
from django.forms.models import model_to_dict
from cloudinary.api import Error
import cloudinary.uploader as uploader
from rest_framework import mixins
from rest_framework.exceptions import ValidationError
from utils.media_handlers import CloudinaryResourceHandler

Uploader = CloudinaryResourceHandler()
from rest_framework import (
    generics,
    status,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.authorization_helper import generate_validation_url
from authentication.models import (
    Client,
    User,
)
from authentication.permissions import IsClientAdmin
from authentication.renderer import UserJSONRenderer
from authentication.serializers import (
    ChangePasswordSerializer,
    ClientSerializer,
    FacebookAuthAPISerializer,
    GoogleAuthSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    RegistrationSerializer,
    TwitterAuthAPISerializer,
)
from utils import BaseUtils
from utils.tasks import send_email_notification


class RegistrationAPIView(generics.GenericAPIView):
    """Register new users."""
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
        url = generate_validation_url(message)

        payload = {
            "subject": "Welcome to Landville, Verify your Account",
            "recipient": [user_data["email"]],
            "text_body": "email/authentication/activate_account.txt",
            "html_body": "email/authentication/activate_account.html",
            "context": {
                'username': user_data['first_name'],
                'url': url
            }
        }
        send_email_notification.delay(payload)
        response = {
            "data": {
                "user": dict(user_data),
                "message": "Account created successfully,please check your "
                           "mailbox to activate your account ",
                "status": "success"
            }
        }
        return Response(response, status=status.HTTP_201_CREATED)


class LoginAPIView(generics.GenericAPIView):
    """login a user via email"""
    serializer_class = LoginSerializer
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.data
        response = {
            "data": {
                "user": dict(user_data),
                "message": "You have successfully logged in",
                "status": "success"
            }
        }
        return Response(response, status=status.HTTP_200_OK)


class EmailVerificationView(generics.GenericAPIView):
    """Verify the users email."""

    def get(self, request):
        token, user_id = request.GET.get("token").split("~")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.exceptions.DecodeError:
            return self.sendResponse("verification link is invalid",
                                     status.HTTP_400_BAD_REQUEST)
        except jwt.ExpiredSignatureError:
            url = generate_validation_url([request], user_id=user_id)
            user = User.objects.filter(id=user_id).first()
            payload = {
                "subject": "Landville, Verify your Account",
                "recipient": [user.email],
                "text_body": "email/authentication/activate_account.txt",
                "html_body": "email/authentication/activate_account.html",
                "context": {
                    'username': user.first_name,
                    'url': url
                }
            }
            send_email_notification.delay(payload)

            message = "verification link is expired, we have " \
                      "sent you a new one."
            return self.sendResponse(message, status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=payload.get("email")).first()
        if user.is_verified:
            return self.sendResponse("Account is already activated")

        user.is_verified = True
        user.save()
        return self.sendResponse("Email has been verified")

    def sendResponse(self, message, status=status.HTTP_200_OK):
        return Response({"message": message}, status)


class GoogleAuthAPIView(APIView):
    """
    Manage Google Login
    """
    renderer_classes = (UserJSONRenderer,)
    serializer_class = GoogleAuthSerializer

    def post(self, request):
        """
        Create a user is not exist
        Retrieve and return authenticated user token
        :param request:
        :return: token
        """
        serializer = self.serializer_class(data=request.data.get('google', {}))
        serializer.is_valid(raise_exception=True)
        return Response({
            'token': serializer.data.get('access_token')
        }, status=status.HTTP_200_OK)


class FacebookAuthAPIView(APIView):
    """
    Manage Facebook Login
    """
    renderer_classes = (UserJSONRenderer,)
    serializer_class = FacebookAuthAPISerializer

    def post(self, request):
        """
        Create a user is not exist
        Retrieve and return authenticated user token
        :param request:
        :return: token
        """
        serializer = self.serializer_class(
            data=request.data.get('facebook', {}))
        serializer.is_valid(raise_exception=True)
        return Response({
            'token': serializer.data.get('access_token')
        }, status=status.HTTP_200_OK)


class TwitterAuthAPIView(APIView):
    """
    Manage Twitter Login
    """
    renderer_classes = (UserJSONRenderer,)
    serializer_class = TwitterAuthAPISerializer

    def post(self, request):
        """
        Create a user is not exist
        Retrieve and return authenticated user token
        :param request:
        :return: token
        """
        serializer = self.serializer_class(
            data=request.data.get('twitter', {}))
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        return Response({"token": token}, status=status.HTTP_200_OK)


class ClientCreateView(generics.GenericAPIView, BaseUtils):
    """
    Register new client company by client admin
    """
    serializer_class = ClientSerializer
    renderer_classes = (UserJSONRenderer,)
    permission_classes = (IsClientAdmin,)

    def get_queryset(self):
        return Client.active_objects.filter(client_admin=self.request.user.pk)

    def get(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        if len(serializer.data) == 0:
            response = {
                "data": {
                    "message": "You don't have a client company created"
                }
            }
            status_code = status.HTTP_404_NOT_FOUND
        else:
            response = {
                "data": {
                    "client_company": serializer.data[0],
                    "message": "You have retrieved your client company",
                }
            }
            status_code = status.HTTP_200_OK
        return Response(response, status=status_code)

    """
    Register new client company by client admin
    """

    def post(self, request):
        data = request.data
        data["client_admin"] = request.user.id
        data["client_name"] = self.remove_redundant_spaces(data["client_name"])

        if self.check_client_admin_has_company(request.user.id):
            return Response({'error': 'You cannot be admin of more than'
                                      ' one client client'},
                            status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        company = serializer.validated_data['client_name']
        admin = serializer.validated_data['client_admin']

        recipient = list(
            User.active_objects.filter(role="LA").values_list('email',
                                                              flat=True))

        serializer.save()

        payload = {
            "subject": "Landville client company review",
            "recipient": recipient,
            "message": "",
            "text_body": "email/authentication/company_registration.txt",
            "html_body": "email/authentication/company_registration.html",
            "context": {
                company,
                admin,
            }
        }
        send_email_notification.delay(payload)

        response = {
            "data": {
                "client_company": serializer.data,
                "message": "Your request to create a company has been "
                           "received, please wait for approval from "
                           "landville admin."
            }
        }

        return Response(response, status=status.HTTP_201_CREATED)

    def check_client_admin_has_company(self, id_value):
        """
        Checks if client admin admin already has a company
        """
        return bool(Client.active_objects.filter(client_admin_id=id_value))


class PasswordResetView(APIView):
    """Handle resetting a forgotten password."""
    renderer_classes = (UserJSONRenderer,)
    serializer_class = PasswordResetSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(
            data=data)
        serializer.is_valid(raise_exception=True)
        response = {
            "data": serializer.validated_data
        }
        return Response(response, status=status.HTTP_200_OK)

    def patch(self, request):
        """
         patch:
             Update a user's password with a new password.
         """
        data = request.data
        token = request.query_params['token']
        data['token'] = token
        serializer = ChangePasswordSerializer(
            data=data)
        serializer.is_valid(raise_exception=True)
        response = {
            "data": serializer.validated_data
        }
        return Response(response, status=status.HTTP_200_OK)


class ProfileView(generics.GenericAPIView):
    """
    This View handles retreiving and updating of users profile including
    updating the users initial profile image
    """
    permission_classes = (IsAuthenticated, IsProfileOwner)
    serializer_class = ProfileSerializer

    def get(self, request):
        """
        Retreive a users profile without their security answer and question
        """
        user_object = User.objects.get(pk=request.user.pk)
        user_data = model_to_dict(
            user_object, fields=['id', 'email', 'first_name', 'last_name', 'role'])

        profile = UserProfile.objects.get(user=request.user)
        profile_data = model_to_dict(
            profile, exclude=['security_question', 'security_answer', 'is_deleted'])

        profile_data['user'] = user_data
        data = {"data": {"profile": profile_data},
                "message": "Profile retreived successfully"}
        return Response(data, status=status.HTTP_200_OK)

    def upload_image(self, image):
        """
        Validate and upload an image to cloudinary and return a url
        """
        validate_image(image)
        result = uploader.upload(image)
        url = result.get('url')
        return url

    def patch(self, request):
        """
        Update a users  profile
        """
        profile = UserProfile.objects.get(user=request.user)
        self.check_object_permissions(request, profile)
        profile_data = request.data
        if request.FILES:
            url = self.upload_image(request.FILES['image'])
            if url:
                profile_data["image"] = url

        serializer = self.serializer_class(
            profile, data=profile_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        updated_profile = dict(serializer.data)
        response = {
            "data": {
                "profile": updated_profile,
                "message": "Profile updated successfully"
            }
        }
        return Response(response, status=status.HTTP_200_OK)


class AddReasonView(View):
    """A view that enables admins to add a reason for the performed action."""

    def get(self, request):
        """
        Render a form.

        Enable admins to add a reason for the performed action.
        """
        return render(request, 'admin/add_notes.html', {
            "client": request.GET['client'],
            "status": request.GET['status']
        })

    def post(self, request):
        """
        Submit a form that adds a reason for the performed action.

        Sends an email to the company client admin.
        """
        notes = request.POST['notes']
        client = request.POST['client'],
        status = request.POST['status']
        messages.info(request, 'Client record has been updated')
        message = ''
        if status == "revoked":
            message = 'Hey there,\n\nyour approval for LandVille was revoked\
        ,for the following reason \n\n{}'.format(notes)
        elif status == 'rejected':
            message = 'Hey there,\n\nyour application for LandVille was not accepted\
            ,for the following reason \n\n{}'.format(notes)
        client = Client.objects.filter(client_admin=User.objects.filter(
            email=client[0]).first()).first()
        client.approval_status = status
        client.save()
        self.notify_user(message, client.email)
        return HttpResponseRedirect("/landville/adm/authentication/client/")

    def notify_user(self, message, email):
        """Send an email message to the provided email."""
        payload = {
            "subject": "Landville Application Status",
            "recipient": [email],
            "text_body": "email/authentication/base_email.txt",
            "html_body": "email/authentication/base_email.html",
            "context": {
                'title': "Hey there,",
                'message': message
            }
        }
        send_email_notification.delay(payload)
