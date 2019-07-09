import datetime
from datetime import datetime as dt

from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import (
    generics,
    status,
)
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from rest_framework.permissions import (
    IsAuthenticated
)
from rest_framework.response import Response

from property.filters import PropertyFilter
from property.models import (
    BuyerPropertyList,
    Property,
    PropertyEnquiry,
)
from property.renderers import (
    PropertyEnquiryJSONRenderer,
    PropertyJSONRenderer,
)
from property.serializers import (
    BuyerPropertyListSerializer,
    PropertyEnquirySerializer,
    PropertySerializer,
)
from utils.media_handlers import CloudinaryResourceHandler
from utils.permissions import (
    CanEditProperty,
    IsBuyer,
    IsClientAdmin,
    IsOwner,
    ReadOnly,
)
from utils.tasks import send_email_notification


class ListCreateEnquiryAPIView(generics.ListCreateAPIView):
    """
    handle creation of a property enquiry where we
    we first pass the slug as the argument to fetch the property
    """
    serializer_class = PropertyEnquirySerializer
    permission_classes = (IsBuyer,)
    renderer_classes = (PropertyEnquiryJSONRenderer, )

    def get_queryset(self):
        """ return different results depending on who is making a request """

        user = self.request.user

        if user.is_authenticated and user.role == 'LA':
            # check if the user is a landville admin and return all records
            # even soft deleted ones
            return PropertyEnquiry.objects.all()

        if user.is_authenticated and user.role == 'CA':
            # if the user is a client admin, return only his records
            employer = user.employer.first()
            return PropertyEnquiry.active_objects.for_client(client=employer)

        # if the user is a buyer, return also only his enquiries
        return PropertyEnquiry.active_objects.for_user(user=user)

    def post(self, request, property_slug):
        """
        first find a property by slug, then post
         an enquiry for the property
         """
        user = request.user
        enquirer_name = user.first_name + ' ' + user.last_name
        enquiry = request.data

        enquiring_property = Property. \
            active_objects.published_and_unsold_property_by_slug(
                slug=property_slug).first()

        if enquiring_property is None:
            return Response({"errors": "we did not find the property"}, status=status.HTTP_404_NOT_FOUND)
        for user_enquiry in self.get_queryset():

            if user_enquiry.target_property.slug == enquiring_property.slug and \
                    user_enquiry.is_resolved is False:
                return Response({
                    "errors": "enquiry for this property already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=enquiry)
        serializer.is_valid(raise_exception=True)

        serializer.save(requester=user,
                        client_id=enquiring_property.client.pk,
                        target_property=enquiring_property)

        response = {
            "data": serializer.data,
            "message": f'you have succefully enquired about '
            f'{enquiring_property.title} Property owned by '
            f'{enquiring_property.client}'
        }
        payload1 = {
            "subject": "Landville Property Enquiry",
            "recipient": [user.email],
            "text_body": "email/authentication/base_email.txt",
            "html_body": "email/authentication/base_email.html",
            "context": {
                'title': "Hey there,",
                'message': "You are receiving this because you have enquired "
                           "about a property at Landville, a representative"
                           " from the Client will get to you soon. Thanks "
                           "for using Landville"
            }
        }
        payload2 = {
            "subject": "Landville Property Enquiry",
            "recipient": [enquiring_property.client.email],
            "text_body": "email/authentication/base_email.txt",
            "html_body": "email/authentication/base_email.html",
            "context": {
                'title': "Hey there,",
                'message': f"Hey {enquiring_property.client.client_name}, "
                f"somebody is enquiring about your property at LandVille, "
                f"kindly log into Landville get to know about the enquiry"
            }
        }
        send_email_notification.delay(payload1)
        send_email_notification.delay(payload2)
        return Response(response, status=status.HTTP_201_CREATED)


Uploader = CloudinaryResourceHandler()


class CreateAndListPropertyView(generics.ListCreateAPIView):
    """Handle requests for creation of property"""

    serializer_class = PropertySerializer
    permission_classes = (IsClientAdmin | ReadOnly,)
    renderer_classes = (PropertyJSONRenderer,)
    filter_class = PropertyFilter
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        """Change the queryset to use depending
        on the user making the request"""
        user = self.request.user

        if user.is_authenticated and user.role == 'LA':
            # admins view all property, no filtering
            return Property.objects.all()

        if user.is_authenticated and user.employer.first():
            # if the user is a client_admin, they see all published property
            # and also their client's published and unpublished property.
            client = user.employer.first()
            return Property.active_objects.all_published_and_all_by_client(
                client=client)

        # other users only see published property
        return Property.active_objects.all_published()

    def create(self, request, *args, **kwargs):
        """Create a property listing and save it to the database.
        We pass image and video files to be uploaded to Cloudinary
        we expect URLs to be returned. It is these URLs that we
        pass to be serialized and then saved if everything is okay.
        """
        # enable the request body to be mutable so that we can
        # modify the data to pass to the DB
        request.POST._mutable = True
        payload = request.data
        payload['client'] = request.user.employer.first().pk
        # upload the main image
        main_image_url = Uploader.upload_image_from_request(request)
        payload['image_main'] = main_image_url
        # upload other images
        image_url_list = Uploader.upload_image_batch(request)
        if image_url_list:
            payload.setlist('image_others', image_url_list)
        # upload videos
        video = Uploader.upload_video_from_request(request)
        payload['video'] = video
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            'data': {"property": serializer.data}
        }
        return Response(response, status=status.HTTP_201_CREATED)


class PropertyEnquiryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
     Handles request to view, delete or update a specific property Enquiry
    """

    serializer_class = PropertyEnquirySerializer
    renderer_classes = (PropertyEnquiryJSONRenderer,)
    permission_classes = (IsOwner, IsAuthenticated)
    lookup_field = 'enquiry_id'

    def get_queryset(self):
        """ return different results depending on who is making a request  """

        user = self.request.user

        if user.role == 'LA':
            return PropertyEnquiry.objects.all()

        # check if the user is a client admin
        # and return all enquiries made on his/her property
        if user.role == 'CA':
            return PropertyEnquiry.active_objects.for_client(
                client=user.employer.first())

        # else if the user is a buyer return only
        # the records that are associated with him/her
        return PropertyEnquiry.active_objects.for_user(user=user)

    def destroy(self, request, enquiry_id):
        """
        :param request:
        :param enquiry_id:
        :return: delete a specific enquiry
        """
        enquiry = self.get_object()
        self.check_object_permissions(request, enquiry)
        enquiry.soft_delete()
        response = {"message": "Enquiry deleted successfully"}
        return Response(response, status=status.HTTP_200_OK)

    def put(self, request, enquiry_id):
        """
        update an enquiry
        :param request:
        :param enquiry_id:
        :return: the updated enquiry
        """

        enquiry = self.get_object()
        self.check_object_permissions(request, enquiry)
        serializer = self.serializer_class(
            enquiry, data=request.data, context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(email=request.user.email)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Handles request to view, update or delete a specific property"""

    serializer_class = PropertySerializer
    permission_classes = (CanEditProperty,)
    renderer_classes = (PropertyJSONRenderer,)
    parser_classes = (MultiPartParser, FormParser)

    lookup_field = 'slug'

    def get_queryset(self):
        """Change the queryset to use depending
        on the user making the request"""
        user = self.request.user

        if user.is_authenticated and user.role == 'LA':
            return Property.objects.all()

        if user.is_authenticated and user.employer.first():
            client = user.employer.first()
            return Property.active_objects.all_published_and_all_by_client(
                client=client)

        return Property.active_objects.all_published()

    def retrieve(self, request, slug):
        """we increase the viewcount whenever property
        is successfully retrieved"""

        found_property = self.get_object()

        found_property.view_count += 1
        found_property.last_viewed = datetime.datetime.now()
        found_property.save()
        serializer = self.get_serializer(found_property)
        response = {
            'data': {"property": serializer.data}
        }
        return Response(response)

    def destroy(self, request, slug):
        """
        We override this method so that
        objects are only soft_deleted
        """
        found_property = self.get_object()

        # only landville staff can view deleted property.
        # They should be notified if they try deleting
        # property that is already soft deleted.
        if found_property.is_deleted:
            return Response({
                'errors': 'Not allowed! This property is already deleted.'
            }, status=status.HTTP_400_BAD_REQUEST)
        found_property.soft_delete()
        return Response({
            "message": "Successfully deleted the property"
        }, status=status.HTTP_200_OK)

    def patch(self, request, slug, **kwargs):
        """The `client` field is writable. We should not allow users to
        change this field when making updates."""
        request.POST._mutable = True
        payload = request.data
        payload.pop('client', None)
        obj = self.get_object()
        # update main image
        updated_main_image = Uploader.upload_image_from_request(request)
        if updated_main_image:
            payload['image_main'] = updated_main_image
        # update image list
        updated_image_list = Uploader.upload_image_batch(
            request, instance=obj)
        if updated_image_list:
            payload.setlist('image_others', updated_image_list)
        # update videos
        video = Uploader.upload_video_from_request(request)
        if video:
            payload['video'] = video
        serializer = self.serializer_class(obj, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(obj, payload)
        response = {
            "data": {"property": serializer.data},
            "message": "Successfully updated your property"

        }
        return Response(response)


class DeleteCloudinaryResourceView(generics.DestroyAPIView):
    """Handle all requests for deleting Cloudinary Resources, ie
    Cloudinary images and Cloudinary Videos """

    permission_classes = (CanEditProperty,)
    serializer_class = PropertySerializer
    renderer_classes = (PropertyJSONRenderer,)
    lookup_field = 'slug'

    def get_queryset(self):
        """Change the queryset to use depending on the user making
        the request """
        user = self.request.user

        if user.is_authenticated and user.role == 'LA':
            return Property.objects.all()

        if user.is_authenticated and user.employer.first():
            client = user.employer.first()
            return Property.active_objects.all_published_and_all_by_client(
                client=client)

        return Property.active_objects.all_published()

    def destroy(self, request, slug):
        obj = self.get_object()

        payload = request.data

        updated_fields = Uploader.delete_cloudinary_resource(obj, payload)
        serializer = self.serializer_class(
            obj, data=updated_fields, partial=True)
        serializer.is_valid(raise_exception=True)
        response = {
            "data": {"property": serializer.data},
            "message": "Successfully updated your property"
        }
        return Response(response)


class BuyerPropertyListView(generics.ListCreateAPIView):
    """
    Class defining views for retrieving and deleting
    properties inside a buyer's list of properties.
    """
    permission_classes = (IsBuyer,)
    serializer_class = BuyerPropertyListSerializer
    renderer_classes = (PropertyJSONRenderer,)
    lookup_field = 'slug'

    def get(self, request):
        """
        Retrieves a list of properties in current user's list.
        since we already have the property serializer,
        we first convert the list to instances of Property
        model before we can pass it to the PropertySerializer
        """
        user = request.user
        properties = []
        properties_of_interest = user.property_of_interest.all()
        for property_of_interest in properties_of_interest:
            properties.append(property_of_interest.listed_property)
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data)

    def _get_current_property(self, request, slug):
        """
        check if property exists given a slug
        then return the object and title
        """
        try:
            current_property = Property.active_objects.all_published().get(
                slug=slug)
            property_of_interest = BuyerPropertyList.active_objects.filter(
                buyer=request.user, listed_property=current_property)
            title = current_property.title

            return {
                'current_property': current_property,
                'property': property_of_interest,
                'title': title
            }

        except Property.DoesNotExist:
            return None

    def create(self, request, slug):
        """
        Add property to the current buyer's list
        we first check if the property exists in
        the current user's list
        """

        result = self._get_current_property(request, slug)

        if not result:
            return Response({
                "errors": "Property not found"
            }, status=status.HTTP_404_NOT_FOUND)
        if result['property'].exists():
            return Response({
                'errors': result['title'] + ' is already in your buy list'
            }, status=status.HTTP_400_BAD_REQUEST)
        data = {
            'buyer': request.user.id,
            'listed_property': result['current_property'].id
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        message = result['title'] + \
            ' has been successfully added to your buy list'
        return Response({
            'data': message
        })

    def delete(self, request, slug):
        """
        remove a property from current user list
        this works by first checking whether the
        property in question does exist in the
        current user's list
        """
        result = self._get_current_property(request, slug)
        if not result:
            return Response({
                "errors": "Property not found"
            }, status=status.HTTP_404_NOT_FOUND)
        if not result['property'].exists():
            return Response({
                'errors': result['title'] + ' is not in your buy list'
            }, status=status.HTTP_400_BAD_REQUEST)

        result['property'].delete()
        message = result['title'] + \
            ' has been successfully removed from your buy list'
        return Response({
            'data': message
        })


class TrendingPropertyView(generics.ListAPIView):
    """
    Holds getting trending properties based
    on most views and last_viewed time
    """
    serializer_class = PropertySerializer
    renderer_classes = (PropertyJSONRenderer,)
    pagination_class = None

    def get_queryset(self):
        """
        this method get_queryset to allow users
        get Published properties in a
        specific location and which are not sold, a user
        is given a chance to select a date, if a date
        is not selected,the query will return trending
        properties in the last 30 days
        """

        string_date = self.request.query_params.get('date', dt.strftime(
            (dt.now() - datetime.timedelta(30)
             ).date(), '%Y-%m-%d'))
        date = dt.strptime(string_date, '%Y-%m-%d')
        city = self.request.query_params['city']
        query_results = Property.active_objects.filter(
            address__City__icontains=city,
            last_viewed__date__gte=date,
            is_published=True,
            is_sold=False,
            view_count__gte=1).order_by('-view_count', 'last_viewed')
        return query_results[:10]

    def list(self, request):
        """
        This list method lists the data
        from the query after the handling the exception
        """
        try:
            queryset = self.get_queryset()
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)
        # This try catches an exception of MultiValueDictKeyError
        # which then returns an error message in case a user
        # does not specific
        # location/city where he wants to see properties trending
        except MultiValueDictKeyError:
            return Response({'errors': 'Please specify a city'},
                            status=status.HTTP_400_BAD_REQUEST)
