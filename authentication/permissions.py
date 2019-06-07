from rest_framework.permissions import BasePermission


class IsClientAdmin(BasePermission):
    """Grants client admins full access"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'CA'
