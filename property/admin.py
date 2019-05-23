from django.contrib import admin

from .models import Property, PropertyReview, PropertyInspection, PropertyEnquiry

admin.site.register(Property)
admin.site.register(PropertyReview)
admin.site.register(PropertyEnquiry)
admin.site.register(PropertyInspection)
