from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import GoogleAuthSerializer, FacebookAuthAPISerializer, TwitterAuthAPISerializer
from .renderers import UserJSONRenderer
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


class GoogleAuthAPIView(APIView):
    """
    Manage Google Login
    """
    permission_classes = (AllowAny,)
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
    permission_classes = (AllowAny,)
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
    permission_classes = (AllowAny,)
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
