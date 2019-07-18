from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
import json
from rest_framework import status
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView
)
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from utils.client_permissions import IsownerOrReadOnly, IsClient
from transactions.models import ClientAccount, Client
from transactions.renderer import AccountDetailsJSONRenderer
from transactions.serializers import ClientAccountSerializer, TransactionsSerializer
from transactions.transaction_services import TransactionServices
from transactions.serializers import (
    PinCardPaymentSerializer,
    ForeignCardPaymentSerializer,
    PaymentValidationSerializer,
    CardlessPaymentSerializer
)
from property.models import Property


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
        """
        return different details by first checking who is making the request
        """

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
            response = {
                "message": "There are no details posted by any client so far"
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
            return Response({
                "message": "you must have a client company to submit account "
                           "details"},
                status=status.HTTP_400_BAD_REQUEST)
        if self.check_client_account_details_exists(user.employer.first()):
            return Response({
                "message": "You have already submitted your account details"},
                status=status.HTTP_400_BAD_REQUEST
            )

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
        """
        return different details by first checking who is making the request
        """

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
        return Response({"data": response}, status=status.HTTP_200_OK)

    def put(self, request, account_number):

        account = self.get_object()
        self.check_object_permissions(request, account)
        serializer = self.serializer_class(
            account, data=request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class RetreiveTransactionsAPIView(generics.GenericAPIView):
    """View class used to GET users transactions"""
    permission_classes = (IsAuthenticated,)
    serializer_class = TransactionsSerializer

    def get_queryset(self):
        """Get queryset based on type/role of user currently logged in"""
        if self.request.user.role == 'CA':
            client_company = get_object_or_404(
                Client, client_admin__pk=self.request.user.pk)
            # return all the client property that have transactions
            queryset = Property.active_objects.all_objects().filter(
                transactions__target_property__client__pk=client_company.pk).distinct()
        elif self.request.user.role == "LA":
            # return all property with transactions
            queryset = Property.active_objects.all_objects().filter(
                transactions__isnull=False).distinct()
        else:
            # return all property for which the logged-in user has transactions with
            queryset = Property.active_objects.all_objects().filter(
                transactions__buyer__pk=self.request.user.pk).distinct()
        return queryset

    def get(self, request):
        """Endpoint to fetch all the property transactions of the logged-in user"""
        queryset = self.get_queryset()
        if queryset:
            serializer = self.serializer_class(
                queryset, many=True, context={'request': request})
        else:
            return Response({"errors": "No transactions available"},
                            status=status.HTTP_404_NOT_FOUND)

        data = {"data": {"transactions": serializer.data},
                "message": "Transaction(s) retrieved successfully"}
        return Response(data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='post', request_body=ForeignCardPaymentSerializer)
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def card_foreign_payment(request):
    """
    Endpoint for initiating foreign card payment. It gets the user and card
    information from the request object and uses this to make payment request
    to rave
    :param request: DRF request object
    :return: JSON response
    """
    data = request.data
    user = request.user
    serializer = ForeignCardPaymentSerializer(data=data)
    if serializer.is_valid():

        pay_data = {
            'cardno': serializer.validated_data.get('cardno'),
            'cvv': serializer.validated_data.get('cvv'),
            'expirymonth': serializer.validated_data.get('expirymonth'),
            'expiryyear': serializer.validated_data.get('expiryyear'),
            'country': serializer.validated_data.get('country', 'NG'),
            'amount': str(serializer.validated_data.get('amount')),
            'save_card': serializer.validated_data.get('save_card'),
            'email': user.email,
            'firstname': user.first_name,
            'lastname': user.last_name,
        }

        init_resp = TransactionServices.initiate_card_payment(pay_data)
        if init_resp.get('status') == 'error':
            return Response(
                {'message': init_resp.get('message')},
                status=status.HTTP_400_BAD_REQUEST
            )
        auth_dict = {
            'suggested_auth': 'NOAUTH_INTERNATIONAL',
            'billingzip': serializer.validated_data.get('billingzip'),
            'billingcity': serializer.validated_data.get('billingcity'),
            'billingaddress': serializer.validated_data.get('billingaddress'),
            'billingstate': serializer.validated_data.get('billingstate'),
            'billingcountry': serializer.validated_data.get('billingcountry'),
        }
        pay_data['auth_dict'] = auth_dict

        auth_resp = TransactionServices.authenticate_card_payment(pay_data)

        if auth_resp.get('status') == 'error':
            return Response(
                {'message': auth_resp.get('message')},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'message': auth_resp['data']['authurl']},
            status=status.HTTP_200_OK
        )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post', request_body=PinCardPaymentSerializer)
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def card_pin_payment(request):
    """
    Endpoint for initiating local card payment with PIN. It gets the user and
    card information from the request object and uses this to make payment
    request to rave
    :param request: DRF request object
    :return: JSON response
    """
    data = request.data
    user = request.user
    serializer = PinCardPaymentSerializer(data=data)
    if serializer.is_valid():

        pay_data = {
            'cardno': serializer.validated_data.get('cardno'),
            'cvv': serializer.validated_data.get('cvv'),
            'expirymonth': serializer.validated_data.get('expirymonth'),
            'expiryyear': serializer.validated_data.get('expiryyear'),
            'country': serializer.validated_data.get('country', 'NG'),
            'amount': str(serializer.validated_data.get('amount')),
            'save_card': serializer.validated_data.get('save_card'),
            'email': user.email,
            'firstname': user.first_name,
            'lastname': user.last_name,
        }

        init_resp = TransactionServices.initiate_card_payment(pay_data)
        if init_resp.get('status') == 'error':
            return Response(
                {'message': init_resp.get('message')},
                status=status.HTTP_400_BAD_REQUEST
            )

        auth_dict = {
            'suggested_auth': 'PIN',
            'pin': serializer.validated_data.get('pin')
        }
        pay_data['auth_dict'] = auth_dict

        auth_resp = TransactionServices.authenticate_card_payment(pay_data)

        if auth_resp.get('status') == 'error':
            return Response(
                {'message': auth_resp.get('message')},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'message': 'Kindly input the OTP sent to you',
                'flwRef': auth_resp['data']['flwRef']
            }, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post', request_body=PaymentValidationSerializer)
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def validate_payment(request):
    """
    Endpoint for handling card payment validation. It gets transaction
    reference and OTP from the request object and uses this to make payment
    request to rave
    :param request: DRF request object
    :return: JSON response
    """
    data = request.data
    flwref = data.get('flwRef')
    otp = data.get('otp')

    resp = TransactionServices.validate_card_payment(flwref, otp)
    txRef = resp['data']['tx']['txRef']
    verify_resp = TransactionServices.verify_payment(txRef)
    save_card = verify_resp['data']['meta'][0]['metavalue']
    message = verify_resp['data']['vbvmessage']
    if verify_resp['data']['status'] == 'successful' and int(save_card) == 1:
        message += TransactionServices.save_card(verify_resp)

    return Response({'message': message})


@api_view(['GET'])
def foreign_card_validation_response(request):
    """
    Endpoint for handling foreign card validation response. It uses the
    response to verify the payment and save the card token, if requested
    :param request: DRF request object
    :return: JSON response
    """
    resp = json.loads(request.query_params['response'])
    verify_resp = TransactionServices.verify_payment(resp['txRef'])

    save_card = verify_resp['data']['meta'][0]['metavalue']
    message = verify_resp['data']['vbvmessage']
    if verify_resp['data']['status'] == 'successful' and int(save_card) == 1:
        message += TransactionServices.save_card(verify_resp)

    return Response({'message': message})


@swagger_auto_schema(method='post', request_body=CardlessPaymentSerializer)
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def tokenized_card_payment(request):
    """
    Endpoint for handling payment using tokenized cards. The user makes payment
    without providing card details
    :param request: DRF request object
    :return: JSON response
    """
    data = request.data
    user = request.user
    serializer = CardlessPaymentSerializer(data=data)
    if serializer.is_valid():
        amount = serializer.validated_data.get('amount')
        resp = TransactionServices.pay_with_saved_card(user, amount)

    return Response({'message': resp['data']['status']})
