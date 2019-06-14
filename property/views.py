from rest_framework import generics, status
from rest_framework.response import Response

from property.models import Property
from property.serializers import PropertySerializer
from authentication.models import User
from utils.permissions import ReadOnly, IsClientAdmin, CanEditProperty
from property.renderers import PropertyJSONRenderer


class CreateAndListPropertyView(generics.ListCreateAPIView):
    """Handle requests for creation of property"""

    serializer_class = PropertySerializer
    permission_classes = (IsClientAdmin | ReadOnly,)
    renderer_classes = (PropertyJSONRenderer,)

    def get_queryset(self):
        """Change the queryset to use depending on the user making the request"""
        user = self.request.user

        if user.is_authenticated and user.role == 'LA':
            # admins view all property, no filtering
            return Property.objects.all()

        if user.is_authenticated and user.employer.first():
            # if the user is a client_admin, they see all published property
            # and also their client's published and unpublished property.
            client = user.employer.first()
            return Property.active_objects.all_published_and_all_by_client(client=client)

        # other users only see published property
        return Property.active_objects.all_published()

    def create(self, request, *args, **kwargs):
        payload = request.data

        payload['client'] = request.user.employer.first().pk
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        property_data = serializer.data
        return Response(property_data, status=status.HTTP_201_CREATED)


class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Handles request to view, update or delete a specific property"""

    serializer_class = PropertySerializer
    permission_classes = (CanEditProperty,)
    renderer_classes = (PropertyJSONRenderer,)
    lookup_field = 'slug'

    def get_queryset(self):
        """Change the queryset to use depending on the user making the request"""
        user = self.request.user

        if user.is_authenticated and user.role == 'LA':
            return Property.objects.all()

        if user.is_authenticated and user.employer.first():
            client = user.employer.first()
            return Property.active_objects.all_published_and_all_by_client(client=client)

        return Property.active_objects.all_published()

    def retrieve(self, request, slug):
        """we increase the viewcount whenever property is successfully retrieved """

        found_property = self.get_object()

        found_property.view_count += 1
        found_property.save()
        serializer = self.get_serializer(found_property)
        return Response(serializer.data)

    def destroy(self, request, slug):
        """We override this method so that objects are only soft_deleted"""
        found_property = self.get_object()

        # only landville staff can view deleted property. They should be notified if they try deleting
        # property that is already soft deleted.
        if found_property.is_deleted:
            return Response({
                'errors': 'Not allowed! This property is already deleted.'
            }, status=status.HTTP_400_BAD_REQUEST)
        found_property.soft_delete()
        return Response({
            "message": "Successfully deleted the property"
        }, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, slug, **kwargs):
        """The `client` field is writable. We should not allow users to change this field when making updates."""
        request.data.pop('client', None)
        return super().patch(request, slug, **kwargs)
