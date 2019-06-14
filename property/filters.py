from django_filters import FilterSet
from django_filters import rest_framework as filters
from property.models import Property


class PropertyFilter(FilterSet):
    """
    Create a filter class that inherits from FilterSet. This class will help
    us search for properties using specified fields.
    """
    city = filters.CharFilter('address__City', lookup_expr='icontains')
    street = filters.CharFilter('address__Street', lookup_expr='icontains')
    state = filters.CharFilter('address__State', lookup_expr='icontains')
    company = filters.CharFilter(
        'client__client_name', lookup_expr='icontains')
    title = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    property_type = filters.CharFilter(lookup_expr='icontains')
    purchase_plan = filters.CharFilter(lookup_expr='icontains')
    price = filters.RangeFilter()

    class Meta:
        model = Property
        fields = (
            'title',
            'description',
            'company',
            'city',
            'street',
            'state',
            'property_type',
            'purchase_plan',
            'garages',
            'bedrooms',
            'bathrooms',
            'lot_size',
            'price',
        )
