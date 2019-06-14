from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    """Allow ReadOnly permissions if the request is a safe method"""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class CanEditProperty(BasePermission):
    """Client admins should be able to edit property they own"""

    def has_object_permission(self, request, view, obj):

        user = request.user
        if request.method in SAFE_METHODS:
            return True
        if user.is_authenticated and user.role == 'CA':
            return user == obj.client.client_admin
        if user.is_authenticated and user.role == 'LA':
            return True
        return False


class IsClientAdmin(BasePermission):
    """Grants client admins full access"""

    def has_permission(self, request, view):
        user = request.user if request.user.is_authenticated else None
        if user:
            client = user.employer.first()
            return bool(
                client and user.role == 'CA' and client.is_approved)
