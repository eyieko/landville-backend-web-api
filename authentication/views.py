import os

import cloudinary.uploader as uploader
import jwt
from django.conf import settings
from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View
from rest_framework import authentication
from rest_framework import (
    generics,
    status,
)
from rest_framework.exceptions import NotFound
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.authorization_helper import generate_validation_url
from authentication.models import (
    User, Client, UserProfile, ClientReview, ReplyReview)
from authentication.permissions import (
    IsClientAdmin,
    IsProfileOwner,
    IsOwnerOrAdmin)
from authentication.renderer import UserJSONRenderer, ClientJSONRenderer
from authentication.serializers import (
    GoogleAuthSerializer, FacebookAuthAPISerializer, PasswordResetSerializer,
    ProfileSerializer, TwitterAuthAPISerializer, RegistrationSerializer,
    LoginSerializer, ClientSerializer, ChangePasswordSerializer,
    ClientReviewSerializer, ReviewReplySerializer,
    BlackListSerializer)
from property.validators import validate_image
from utils import BaseUtils
from utils.media_handlers import CloudinaryResourceHandler
from utils.permissions import IsBuyerOrReadOnly, IsReviewer, IsAdmin
from utils.tasks import send_email_notification


Uploader = CloudinaryResourceHandler()


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
        domain = os.environ.get('FRONT_END_LOGIN_URL')
        token, user_id = request.GET.get("token").split("~")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.exceptions.DecodeError:
            return HttpResponseRedirect(
                domain + '?verified_status=invalid_link')  # noqa
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
        return HttpResponseRedirect(domain)

    def sendResponse(self, message, status=status.HTTP_200_OK):
        return Response({
            "message": message
        }, status)


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
            'token': serializer.validated_data['token'],
            'user_exists': serializer.validated_data['user_exists'],
            "message": serializer.validated_data['message']
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
            'token': serializer.validated_data['token'],
            'user_exists': serializer.validated_data['user_exists'],
            "message": serializer.validated_data['message']
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

        return Response({
            "token": token,
            "user_exists": serializer.validated_data['user_exists'],
            "message": serializer.validated_data['message']
        }, status=status.HTTP_200_OK)


class ClientCreateView(generics.GenericAPIView, BaseUtils):
    """
    Register new client company by client admin
    """
    serializer_class = ClientSerializer
    renderer_classes = (ClientJSONRenderer,)
    permission_classes = (IsClientAdmin,)

    def get_queryset(self):
        user = self.request.user
        return Client.active_objects.filter(client_admin=user.id)

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
        if self.check_client_admin_has_company(request.user.id):
            return Response(
                {'error': 'You cannot be admin of more than one client'},
                status.HTTP_403_FORBIDDEN
            )
        data["client_admin"] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        subject = "Landville client company review"
        company = serializer.validated_data['client_name']
        admin = serializer.validated_data['client_admin']

        recipient = list(
            User.active_objects.filter(role="LA").values_list('email',
                                                              flat=True))
        payload = {
            "subject": subject,
            "recipient": recipient,
            "message": "",
            "text_body": "email/authentication/company_registration.txt",
            "html_body": "email/authentication/company_registration.html",
            "context": {
                "company": company,
                "admin": admin.email,
            }
        }
        send_email_notification.delay(payload)

        response = {
            "client_company": serializer.data,
            "message": "Your request to create a company has been "
                       "received, please wait for approval from landville "
                       "admin."
        }

        return Response(response, status=status.HTTP_201_CREATED)

    @staticmethod
    def check_client_admin_has_company(id_value):
        """
        Checks if client admin admin already has a company
        """
        return bool(Client.active_objects.filter(client_admin_id=id_value))

    def patch(self, request):
        """
        Handle Update a user's company details once created.
        :param request:
        :return: company Details
        """
        data = request.data
        company = self.get_queryset()
        serializer = self.serializer_class(company[0], data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "client_company": serializer.data,
            "message": "Successfully Updated client company details."
        }

        return Response(response, status=status.HTTP_200_OK)

    def delete(self, request):
        """
        Handles deleting a client company
        :param request:
        :return:
        """
        company = self.get_queryset()
        if not company:
            return Response({"errors": "Client Company Does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        company[0].delete()
        return Response("Company Deleted Successfully", status.HTTP_200_OK)


class ClientListView(generics.GenericAPIView):
    """
    Return a list of registered clients
    """
    serializer_class = ClientSerializer
    renderer_classes = (ClientJSONRenderer,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """ Returns all active client companies  """

        return Client.active_objects.all_approved()

    def get(self, request):
        """ Handles retrieving all existing client companies """

        serializer = self.serializer_class(self.get_queryset(), many=True)
        if not serializer.data:
            response = {
                "message": "There are no clients at the moment."
            }
            status_code = status.HTTP_404_NOT_FOUND
        else:
            response = {
                "client_companies": serializer.data,
                "message": "You have retrieved all clients",
            }
            status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


class RetrieveUpdateDeleteClientView(APIView):
    """
    Handles viewing, updating and deleting of a
    specific client company if authenticated as an admin
    """
    serializer_class = ClientSerializer
    renderer_classes = (ClientJSONRenderer,)
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin,)

    def get_object(self, request, company_id):
        """
        Handles retrieving client company

        :param request:
        :param company_id:
        :return: Object
        """
        try:
            company = Client.objects.get(id=company_id)
            self.check_object_permissions(request, company)
            return company
        except Client.DoesNotExist:
            raise NotFound(detail={"errors": "Client Company Does not exist"},
                           code=status.HTTP_404_NOT_FOUND)

    def get(self, request, **kwargs):
        """
        Handles retrieving a specific client company

        :param request:
        :param kwargs:
        :return:
        """
        company = self.get_object(request, self.kwargs['id'])
        serializer = self.serializer_class(company)
        return Response({
            "client_company": serializer.data,
            "message": "You have retrieved your client company",
        }, status=status.HTTP_200_OK)

    def patch(self, request, **kwargs):
        """
        Handle Update a user's company details once created.
        :param request:
        :return: company Details
        """
        data = request.data

        company = self.get_object(request, self.kwargs['id'])

        serializer = self.serializer_class(company, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "client_company": serializer.data,
            "message": "Successfully Update to company."
        }

        return Response(response, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        """
        Handles deleting a client company
        :param request:
        :return:
        """
        company = self.get_object(request, self.kwargs['id'])
        company.delete()
        return Response("Company Deleted Successfully", status.HTTP_200_OK)


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
            user_object,
            fields=['id', 'email', 'first_name', 'last_name', 'role'])

        card_info = model_to_dict(
            user_object,
            fields=['card_info']
        )

        profile = UserProfile.objects.get(user=request.user)
        profile_data = model_to_dict(
            profile,
            exclude=['security_question', 'security_answer', 'is_deleted'])

        profile_data['user'] = user_data
        profile_data['card_info'] = card_info
        data = {
            "data": {
                "profile": profile_data
            },
            "message": "Profile retreived successfully"
        }
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
        return render(
            request, 'admin/add_notes.html',
            {
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
            message = 'Hey there,\n\nyour approval for LandVille was revoked'\
                ',for the following reason \n\n{}'                                                                                     .format(
                    notes)
        elif status == 'rejected':
            message = 'Hey there,\n\nyour application for LandVille was not '\
                      'accepted\
            ,for the following reason \n\n{}'                                                                                                                                                                                    .format(notes)
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


class ClientReviewsView(generics.ListCreateAPIView):
    """
     Handles request and get client Reviews
    """
    serializer_class = ClientReviewSerializer
    permission_classes = (IsBuyerOrReadOnly,)

    def get_queryset(self, **kwargs):
        client = get_object_or_404(Client, pk=self.kwargs.get('client_id'))
        queryset = ClientReview.active_objects.all_objects().filter(
            client=client)
        if queryset:
            return queryset
        else:
            raise Http404

    def create(self, request, *args, **kwargs):
        """ allows buyers to add reviews to a client """

        try:
            Client.active_objects.all_approved().get(
                pk=kwargs.get('client_id'))
        except Client.DoesNotExist:
            return Response({
                "errors": "Client not found"
            }, status=status.HTTP_404_NOT_FOUND)

        payload = request.data
        payload['client'] = kwargs.get('client_id')
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save(reviewer=request.user)
        response = {
            "message": "Your review has been added"
        }
        return Response(response, status.HTTP_201_CREATED)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
     Handles request to view, delete or update a review
    """
    serializer_class = ClientReviewSerializer
    permission_classes = (IsReviewer | IsAdmin, IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

    def get_queryset(self):
        """ returns different results depending on who is making a request """

        return ClientReview.active_objects.all_objects()

    def destroy(self, request, pk):
        """
        :param request:
        :param pk:
        :return: delete a specific review
        """

        review = self.get_object()
        review.soft_delete()
        return Response({
            "message": "You have deleted this review"
        }, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """  allows user to update only their own review """

        payload = request.data
        review = self.get_object()
        serializer = self.serializer_class(
            review, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(review, payload)
        response = {
            "data": serializer.data,
            "message": "Successfully updated your Review"
        }
        return Response(response, status=status.HTTP_200_OK)


class ReplyView(generics.GenericAPIView):
    """
     Handles request to create, delete or update a reply on a review
    """
    serializer_class = ReviewReplySerializer
    permission_classes = (IsReviewer | IsAdmin, IsAuthenticated,)

    def post(self, request, **kwargs):
        """ allow users add replies to reviews """

        try:
            review = ClientReview.active_objects.all_objects().get(
                pk=kwargs.get('pk'))
        except ClientReview.DoesNotExist:
            return Response({
                "errors": "Review does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

        payload = request.data
        review.replies.create(
            reply=payload['reply'],
            reviewer=request.user
        )
        response = {
            "message": "Your reply has been added"
        }
        return Response(response, status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        """ allow users delete only their replies """

        try:
            reply = ReplyReview.active_objects.all_objects().get(
                pk=kwargs.get('pk'))
        except ReplyReview.DoesNotExist:
            return Response({
                "errors": "Reply does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(self.request, reply)

        reply.soft_delete()
        return Response({
            "message": "You have deleted this reply"
        }, status=status.HTTP_200_OK)

    def put(self, request, **kwargs):
        """ allow users update only their replies """

        try:
            reply = ReplyReview.active_objects.all_objects().get(
                pk=kwargs.get('pk'))
        except ReplyReview.DoesNotExist:
            return Response({
                "errors": "Reply does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(self.request, reply)

        payload = request.data
        serializer = self.serializer_class(
            reply, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(reply, payload)
        response = {
            "message": "Successfully updated your reply",
            "data": {"review": serializer.data}
        }
        return Response(response, status=status.HTTP_200_OK)


class UserReviewsView(generics.GenericAPIView):
    """
    get all a user's reviews for same or different clients
    """

    serializer_class = ClientReviewSerializer
    permission_classes = (IsAuthenticated, IsReviewer)

    def get(self, request, **kwargs):
        reviews = ClientReview.active_objects.all_objects().filter(
            reviewer__pk=kwargs.get('reviewer_id'))
        serializer = self.serializer_class(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(generics.CreateAPIView):
    """
    This class deals with logging out a user by
    creating blacklist tokens
    """
    serializer_class = BlackListSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, **args):
        """
        This method creates a blacklist token
        """

        auth_header = authentication.get_authorization_header(request).split()
        token = auth_header[1].decode('utf-8')
        data = {'token': token}

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'data':
                    {"message": "Successfully logged out"}
            },
            status=status.HTTP_200_OK
        )
