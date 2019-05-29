from rest_framework.permissions import BasePermission, SAFE_METHODS
from authentication.models import User
from rest_framework.permissions import BasePermission
from transactions.models import ClientAccount
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


class IsownerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read only permission is allowed to any request
        if request.method in SAFE_METHODS:
            return True

        # write permission allowed only to the owner of account details
        # Here now only a client that is associated with this account can be
        # able to edit/write this account details,but note that since we are
        # making this product for people to use,they can be able to see this
        # details and we are not restricting them here
        return obj.owner == request.user.employer.first()


class IsClient(BasePermission):
    """Grant access if the person is a client"""

    def has_permission(self, request, view):

        if request.method == 'POST':
            return request.user.role == 'CA'
        if request.method == 'GET':
            return request.user.role == 'LA' or request.user.role == 'CA'
        return False
