from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
import json
import os
from rest_framework import status
from rest_framework.generics import (RetrieveUpdateDestroyAPIView,
                                     ListCreateAPIView, ListAPIView)
from django.db.models import Q
from django.http import HttpResponseRedirect
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated
)
from rest_framework.decorators import api_view, permission_classes
from utils.client_permissions import IsownerOrReadOnly, IsClient
from transactions.models import (ClientAccount,
                                 Client,
                                 Deposit)
from authentication.permissions import IsCardOwner
from transactions.renderer import AccountDetailsJSONRenderer
from transactions.serializers import (
    ClientAccountSerializer,
    TransactionsSerializer,
    DepositSerializer,
    PinCardPaymentSerializer,
    ForeignCardPaymentSerializer,
    PaymentValidationSerializer,
    CardlessPaymentSerializer,
    CardInfoSerializer
)
from transactions.transaction_services import TransactionServices
from property.models import Property
from transactions.transaction_utils import save_deposit
from authentication.models import User, CardInfo
from rest_framework.exceptions import NotFound


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
                transactions__target_property__client__pk=client_company.pk)\
                .distinct()
        elif self.request.user.role == "LA":
            # return all property with transactions
            queryset = Property.active_objects.all_objects().filter(
                transactions__isnull=False).distinct()
        else:
            # return all property for which the logged-in user has
            # transactions with
            queryset = Property.active_objects.all_objects().filter(
                transactions__buyer__pk=self.request.user.pk).distinct()
        return queryset

    def get(self, request):
        """
        Endpoint to fetch all the property transactions of the logged-in
        user
        """
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
        purpose = str(serializer.validated_data.get('purpose'))
        property_id = serializer.validated_data.get('property_id')
        if purpose == 'Buying':
            get_object_or_404(Property, pk=property_id)
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
        pay_data['purpose'] = purpose
        pay_data['property_id'] = property_id
        auth_resp = TransactionServices.authenticate_card_payment(pay_data)
        if auth_resp.get('status') == 'success':
            return Response(
                {
                    'message': auth_resp['data']['authurl'],
                    'txRef': auth_resp.get('data').get('txRef')
                },
                status=status.HTTP_200_OK)
        else:
            return Response(
                {'message': auth_resp.get('message')},
                status=status.HTTP_400_BAD_REQUEST
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
            'lastname': user.last_name
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
    property = None
    purpose = None
    serializer = PaymentValidationSerializer(data=data)
    if serializer.is_valid():
        purpose = str(serializer.validated_data.get('purpose'))
        property_id = serializer.validated_data.get('property_id')
    else:
        return Response({'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)
    if purpose == 'Buying':
        property = get_object_or_404(Property, pk=property_id)
    resp = TransactionServices.validate_card_payment(flwref, otp)
    if resp.get('status') == 'error':
        return Response(
            {'message': resp.get('message')},
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        txRef = resp['data']['tx']['txRef']
        verify_resp = TransactionServices.verify_payment(txRef)
        email = verify_resp['data']['custemail']
        user = User.objects.get(email=email)
        if verify_resp.get('data').get('status') == 'successful':
            save_card = verify_resp['data']['meta'][0]['metavalue']
            message = verify_resp['data']['vbvmessage']
            if int(save_card) == 1:
                message += TransactionServices.save_card(verify_resp)
            data = resp.get('data').get('tx')
            references = {k: v for k, v in data.items() if k.endswith('Ref')}
            amount = data.get('amount', 0)
            save_deposit(purpose,
                         references,
                         amount,
                         user,
                         property)
        else:
            return Response({'message': verify_resp.get('message')},
                            status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': resp['message']}, status=resp['status_code'])


@api_view(['GET'])
def foreign_card_validation_response(request):
    """
    Endpoint for handling foreign card validation response. It uses the
    response to verify the payment and save the card token, if requested
    :param request: DRF request object
    :return: JSON response
    """
    domain = os.environ.get('FRONT_END_INTPAYMENT_URL')

    resp = json.loads(request.query_params['response'])
    verify_resp = TransactionServices.verify_payment(resp['txRef'])
    email = verify_resp['data']['custemail']
    user = User.objects.get(email=email)
    if verify_resp.get('status') == 'success':
        message = verify_resp['data']['vbvmessage']
        meta_data = verify_resp.get('data').get('meta')
        save_card = meta_data[0]['metavalue']
        purpose = meta_data[1]['metavalue']
        property_id = None
        property = None
        if purpose == 'Buying':
            property_id = meta_data[2]['metavalue']
            property = get_object_or_404(Property, pk=property_id)
        if int(save_card):
            message += TransactionServices.save_card(verify_resp)
        data = verify_resp.get('data')
        references = {k: v for k, v in data.items() if k.endswith('ref')}
        amount = data.get('amount', 0)
        save_deposit(purpose, references, amount, user, property)

    else:
        return HttpResponseRedirect(
            f"{domain}" +
            f"?message={verify_resp.get('message')}&status=failure"
        )

    return HttpResponseRedirect(
        f"{domain}"
        + f"?message={message}&status=success"
    )


@swagger_auto_schema(method='post', request_body=CardlessPaymentSerializer)
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def tokenized_card_payment(request, **kwargs):
    """
    Endpoint for handling payment using tokenized cards. The user makes
    payment by providing saved card ID
    :param request:
    :param saved_card_id:
    :return: JSON response
    """
    data = request.data
    user = request.user
    serializer = CardlessPaymentSerializer(data=data)
    if serializer.is_valid():
        try:
            card = CardInfo.objects.get(
                id=kwargs.get('saved_card_id')
            )
        except CardInfo.DoesNotExist:
            return Response(
                {'errors':
                 'The card you specified does not exist, try a different card'},
                status=status.HTTP_404_NOT_FOUND)
        amount = serializer.validated_data.get('amount')
        resp = TransactionServices.pay_with_saved_card(user, amount, card)
        return Response(
            {'message': resp.get('data').get('status')},
            status=resp.get('data').get('status_code')
        )
    else:
        return Response({'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class RetrieveDepositsApiView(ListAPIView):
    serializer_class = DepositSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """
        This view should return a list of all the  deposits
        for the currently authenticated user.
        if the user is a buyer he gets his own deposit
        if the user is a client admin he get all deposit made for properties
        belonging to his company
        if he is a Landville admin he gets all deposits
        """

        user = self.request.user
        if user.role == 'CA':
            query = Deposit.objects.select_related(
                'transaction',
                'transaction__target_property')
            query = query.filter(
                transaction__target_property__client_id=user.employer.
                first().id)
        elif user.role == 'LA':
            query = Deposit.objects.select_related('transaction',
                                                   'account').all()
        else:
            query = Deposit.objects.select_related(
                'transaction', 'account').filter(
                Q(transaction__buyer__id=user.id)
                | Q(account__owner__id=user.id))
        return query


class SavedCardsListView(generics.GenericAPIView):
    """get all a  cards for authenticated user"""

    permission_classes = (IsAuthenticated,)
    serializer_class = CardInfoSerializer
    def get_queryset(self):

        user = self.request.user
        return CardInfo.active_objects.all_objects().filter(user_id=user.id)

    def get(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        if not serializer.data:
            response = {
                "data": {
                    "message": "You don't have any card saved"
                }
            }
            status_code = status.HTTP_404_NOT_FOUND
        else:
            response = {
                "data": {
                    "saved_cards": serializer.data,
                    "message": "Cards retrieved",
                }
            }
            status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


class DeleteSavedCardView(generics.GenericAPIView):
    """ Remove existing card """

    permission_classes = (IsAuthenticated, IsCardOwner)

    def get_object(self, request, card_info_id):
        """
        Handles getting a specific card

        :param request:
        :param user_id:
        :return: Object
        """
        try:
            card = CardInfo.active_objects.all_objects().get(id=card_info_id)
            return card
        except CardInfo.DoesNotExist:
            raise NotFound(detail={"errors": "Card not found"},
                           code=status.HTTP_404_NOT_FOUND)

    def delete(self, request, **kwargs):
        """
        Handles removing a saved card
        :param request:
        :return:
        """
        card = self.get_object(request, self.kwargs['id'])
        card.soft_delete()
        return Response({
            "message": "Card Deleted Successfully"
        }, status=status.HTTP_200_OK)
