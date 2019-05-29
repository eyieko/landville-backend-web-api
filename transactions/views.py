from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from utils.client_permissions import IsownerOrReadOnly, IsClient
from transactions.models import ClientAccount, Client
from transactions.renderer import AccountDetailsJSONRenderer
from transactions.serializers import ClientAccountSerializer


class ClientAccountAPIView(ListCreateAPIView):
    """ Create an entry on account details and get one entry """

    permission_classes = (IsAuthenticatedOrReadOnly, IsClient)
    renderer_classes = (AccountDetailsJSONRenderer,)
    serializer_class = ClientAccountSerializer

    def check_client_account_details_exists(self, owner):
        """check if user has already submitted client account details"""
        return bool(ClientAccount.active_objects.not_deleted(owner=owner))

    def check_if_client_exists(self, _id):
        """check if client admin has a company"""
        return bool(Client.active_objects.filter(client_admin_id=_id).exists())

    def get_queryset(self):
        """ return different details by first checking who is making the request """

        user = self.request.user

        if user.role == 'LA':
            return ClientAccount.objects.all()

        user.is_authenticated and user.employer.first()
        # see the non deleted records if a user is a client admin or client
        owner = user.employer.first()
        return ClientAccount.active_objects.not_deleted(owner=owner)

    def get(self, request):
        """ get client accounts """
        user = request.user
        serializer = self.serializer_class(self.get_queryset(), many=True)
        if len(serializer.data) == 0 and user.role == 'LA':
            response = {"message": "There are no details posted by any client so far"
                        }
        elif len(serializer.data) == 0 and user.role == 'CA':
            response = {"message": "You have no account details posted"}

        else:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(response, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):

        user = request.user

        account_details = request.data
        if not self.check_if_client_exists(user.id):
            return Response({"message": "you must have a client company to submit account details"}, status=status.HTTP_400_BAD_REQUEST)
        if self.check_client_account_details_exists(user.employer.first()):
            return Response({"message": "You have already submitted your account details"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(
            data=account_details)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            owner=user.employer.first())
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RetrieveUpdateDeleteAccountDetailsAPIView(RetrieveUpdateDestroyAPIView):
    """ GET,DELETE and UPDATE one one entry of account details """

    serializer_class = ClientAccountSerializer
    renderer_classes = (AccountDetailsJSONRenderer,)
    permission_classes = (IsownerOrReadOnly, IsAuthenticatedOrReadOnly)
    lookup_field = 'account_number'

    def get_queryset(self):
        """ return different details by first checking who is making the request """

        user = self.request.user

        if user.role == 'LA':
            return ClientAccount.objects.all()

        if user.is_authenticated and user.employer.first():
            # see the non deleted records if a user is a client admin or client
            owner = user.employer.first()
            return ClientAccount.active_objects.not_deleted(owner=owner)
        return ClientAccount.active_objects.all_objects()

    def get(self, request, account_number):
        account = self.get_object()
        serializer = self.serializer_class(account)
        return Response(serializer.data)

    def destroy(self, request, account_number):

        account_details = self.get_object()
        self.check_object_permissions(request, account_details)
        account_details.soft_delete()
        response = {"message": "Account details successfully deleted"}
        return Response({"data": response}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, account_number):

        account = self.get_object()
        self.check_object_permissions(request, account)
        serializer = self.serializer_class(
            account, data=request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
